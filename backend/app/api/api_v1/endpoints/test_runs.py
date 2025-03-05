import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Header
from sqlmodel import Session, select, func
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.models.test_run import TestRun, TestRunCreate, TestRunRead, TestRunUpdate
from app.models.test_case import TestCase
from app.models.test_case_result import TestCaseResult
from app.models.test_suite import TestSuite
from app.core.tasks import get_task_queue
from app.core.test_processing import process_test_results_file
from app.core.cache import cache_response, invalidate_cache
from .pagination import Page, PageParams

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=Page[TestRunRead])
@cache_response(ttl=60)  # Cache for 1 minute
async def read_test_runs(
    pagination: PageParams = Depends(),
    status: Optional[str] = None,
    operator_id: Optional[str] = None,
    session: Session = Depends(get_session)
) -> Page[TestRunRead]:
    """Get test runs with pagination and filtering"""
    try:
        # Build query with filters
        query = select(TestRun)
        if status:
            query = query.where(TestRun.status == status)
        if operator_id:
            query = query.where(TestRun.operator_id == operator_id)
        
        # Get total count for pagination
        count_query = select(func.count()).select_from(query)
        total = session.exec(count_query).one()
        
        # Apply pagination and eager loading
        query = (
            query
            .options(selectinload(TestRun.test_case_results))
            .order_by(TestRun.created_at.desc())
            .offset(pagination.offset)
            .limit(pagination.size)
        )
        
        # Execute query
        test_runs = session.exec(query).all()
        
        # Return paginated response
        return Page.create(
            items=test_runs,
            total=total,
            params=pagination
        )
    except Exception as e:
        logger.error(f"Error fetching test runs: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching test runs"
        )

@router.post("/", response_model=TestRunRead, status_code=status.HTTP_201_CREATED)
async def create_test_run(
    test_run: TestRunCreate, 
    session: Session = Depends(get_session)
):
    """Create a new test run"""
    try:
        db_test_run = TestRun.from_orm(test_run)
        session.add(db_test_run)
        session.commit()
        session.refresh(db_test_run)
        
        # Invalidate cache
        invalidate_cache("read_test_runs")
        
        return db_test_run
    except Exception as e:
        logger.error(f"Error creating test run: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Error creating test run"
        )

@router.get("/{test_run_id}", response_model=TestRunRead)
@cache_response(ttl=300)  # Cache for 5 minutes
async def read_test_run(
    test_run_id: int, 
    session: Session = Depends(get_session)
):
    """Get a single test run by ID"""
    try:
        # Get test run with eager loading
        test_run = session.exec(
            select(TestRun)
            .where(TestRun.id == test_run_id)
            .options(selectinload(TestRun.test_case_results))
        ).first()
        
        if not test_run:
            raise HTTPException(
                status_code=404,
                detail="Test run not found"
            )
        
        return test_run
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching test run: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching test run"
        )

@router.patch("/{test_run_id}", response_model=TestRunRead)
async def update_test_run(
    test_run_id: int,
    test_run: TestRunUpdate,
    session: Session = Depends(get_session)
):
    """Update a test run"""
    try:
        db_test_run = session.get(TestRun, test_run_id)
        if not db_test_run:
            raise HTTPException(
                status_code=404,
                detail="Test run not found"
            )
        
        # Update fields
        test_run_data = test_run.dict(exclude_unset=True)
        for key, value in test_run_data.items():
            setattr(db_test_run, key, value)
        
        session.add(db_test_run)
        session.commit()
        session.refresh(db_test_run)
        
        # Invalidate caches
        invalidate_cache("read_test_runs")
        invalidate_cache(f"read_test_run_{test_run_id}")
        
        return db_test_run
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating test run: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while updating test run"
        )

@router.delete("/{test_run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_run(
    test_run_id: int,
    session: Session = Depends(get_session)
):
    """Delete a test run and its associated results"""
    try:
        test_run = session.get(TestRun, test_run_id)
        if not test_run:
            raise HTTPException(
                status_code=404,
                detail="Test run not found"
            )
        
        # Delete associated test case results first
        results_statement = select(TestCaseResult).where(TestCaseResult.test_run_id == test_run_id)
        test_case_results = session.exec(results_statement).all()
        
        for result in test_case_results:
            session.delete(result)
        
        # Delete the test run
        session.delete(test_run)
        session.commit()
        
        # Invalidate caches
        invalidate_cache("read_test_runs")
        invalidate_cache(f"read_test_run_{test_run_id}")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting test run: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while deleting test run"
        )

@router.delete("/clear-all/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_test_runs(
    session: Session = Depends(get_session)
):
    """Delete all test runs and their associated test case results"""
    try:
        # Delete all test case results first
        session.exec("DELETE FROM testcaseresult")
        # Delete all test runs
        session.exec("DELETE FROM testrun")
        session.commit()
        
        # Invalidate all test run related caches
        invalidate_cache("read_test_runs")
        
        return None
    except Exception as e:
        session.rollback()
        logger.error(f"Error clearing test runs: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while clearing test runs"
        )

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_test_results(
    file: UploadFile = File(...),
    client_id: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """
    Upload test results from a file (JSON or Excel).
    This will create a new test run and process results in the background.
    """
    # Check file extension
    filename = file.filename.lower()
    if not filename.endswith('.json'):
        raise HTTPException(
            status_code=400,
            detail="Only JSON files are currently supported"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Create task for background processing
        task_queue = get_task_queue()
        task_id = await task_queue.add_task(
            "process_test_results",
            process_test_results_file,
            session,
            content,
            filename,
            client_id
        )
        
        return {
            "message": "Test results upload accepted for processing",
            "task_id": task_id,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error uploading test results: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error uploading test results"
        )