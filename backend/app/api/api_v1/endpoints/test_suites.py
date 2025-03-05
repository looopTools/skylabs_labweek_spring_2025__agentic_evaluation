import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from sqlalchemy.orm import selectinload

from app.db.session import get_session
from app.models.test_suite import TestSuite, TestSuiteCreate, TestSuiteRead, TestSuiteUpdate
from app.core.cache import cache_response, invalidate_cache
from .pagination import Page, PageParams

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=Page[TestSuiteRead])
@cache_response(ttl=300)  # Cache for 5 minutes
async def read_test_suites(
    pagination: PageParams = Depends(),
    name: Optional[str] = None,
    format: Optional[str] = None,
    version: Optional[int] = None,
    is_final: Optional[bool] = None,
    session: Session = Depends(get_session)
) -> Page[TestSuiteRead]:
    """
    Get test suites with pagination and filtering.
    Cached for 5 minutes to improve performance.
    """
    try:
        # Build query with filters
        query = select(TestSuite)
        if name:
            query = query.where(TestSuite.name.ilike(f"%{name}%"))
        if format:
            query = query.where(TestSuite.format == format)
        if version is not None:
            query = query.where(TestSuite.version == version)
        if is_final is not None:
            query = query.where(TestSuite.is_final == is_final)

        # Get total count for pagination
        count_query = select(func.count()).select_from(query)
        total = session.exec(count_query).one()

        # Apply pagination
        query = query.offset(pagination.offset).limit(pagination.size)
        
        # Execute query
        test_suites = session.exec(query).all()
        
        # If no test suites exist, create a default one
        if not test_suites and total == 0:
            default_suite = TestSuite(
                id="DEFAULT",
                name="Default Test Suite",
                format="json",
                version=1,
                version_string="1.0",
                is_final=False
            )
            session.add(default_suite)
            session.commit()
            session.refresh(default_suite)
            test_suites = [default_suite]
            total = 1
        
        # Return paginated response
        return Page.create(
            items=test_suites,
            total=total,
            params=pagination
        )
    except Exception as e:
        logger.error(f"Error fetching test suites: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching test suites"
        )


@router.post("/", response_model=TestSuiteRead, status_code=status.HTTP_201_CREATED)
async def create_test_suite(
    test_suite: TestSuiteCreate, 
    session: Session = Depends(get_session)
):
    """Create a new test suite and invalidate the cache"""
    try:
        db_test_suite = TestSuite.from_orm(test_suite)
        session.add(db_test_suite)
        session.commit()
        session.refresh(db_test_suite)
        
        # Invalidate the test suites cache
        invalidate_cache("read_test_suites")
        
        return db_test_suite
    except Exception as e:
        logger.error(f"Error creating test suite: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail="Error creating test suite"
        )


@router.get("/{test_suite_id}", response_model=TestSuiteRead)
@cache_response(ttl=300)  # Cache for 5 minutes
async def read_test_suite(
    test_suite_id: str, 
    session: Session = Depends(get_session)
):
    """Get a single test suite by ID with caching"""
    try:
        # First try to get by string ID
        test_suite = session.exec(
            select(TestSuite)
            .where(TestSuite.id == test_suite_id)
            .options(selectinload('*'))  # Eager load relationships
        ).first()
        
        if not test_suite:
            # Try to get by database ID if the string ID failed
            try:
                db_id = int(test_suite_id)
                test_suite = session.exec(
                    select(TestSuite)
                    .where(TestSuite.db_id == db_id)
                    .options(selectinload('*'))
                ).first()
            except ValueError:
                pass
        
        if not test_suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found"
            )
        
        return test_suite
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in read_test_suite: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving test suite"
        )


@router.patch("/{test_suite_id}", response_model=TestSuiteRead)
async def update_test_suite(
    test_suite_id: str,
    test_suite: TestSuiteUpdate,
    session: Session = Depends(get_session)
):
    """Update a test suite and invalidate related caches"""
    try:
        # First try to get by string ID
        db_test_suite = session.exec(
            select(TestSuite)
            .where(TestSuite.id == test_suite_id)
            .options(selectinload('*'))  # Eager load relationships
        ).first()
        
        if not db_test_suite:
            # Try to get by database ID if the string ID failed
            try:
                db_id = int(test_suite_id)
                db_test_suite = session.exec(
                    select(TestSuite)
                    .where(TestSuite.db_id == db_id)
                    .options(selectinload('*'))
                ).first()
            except ValueError:
                pass
        
        if not db_test_suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found"
            )
        
        # Update fields
        test_suite_data = test_suite.dict(exclude_unset=True)
        for key, value in test_suite_data.items():
            setattr(db_test_suite, key, value)
        
        try:
            session.add(db_test_suite)
            session.commit()
            session.refresh(db_test_suite)
            
            # Invalidate caches
            invalidate_cache("read_test_suites")
            invalidate_cache(f"read_test_suite_{test_suite_id}")
            
            return db_test_suite
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating test suite: {e}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail="Error updating test suite"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_test_suite: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while updating test suite"
        )


@router.delete("/{test_suite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_suite(
    test_suite_id: str,
    session: Session = Depends(get_session)
):
    """Delete a test suite and invalidate related caches"""
    try:
        # First try to get by string ID
        test_suite = session.exec(
            select(TestSuite)
            .where(TestSuite.id == test_suite_id)
        ).first()
        
        if not test_suite:
            # Try to get by database ID if the string ID failed
            try:
                db_id = int(test_suite_id)
                test_suite = session.exec(
                    select(TestSuite)
                    .where(TestSuite.db_id == db_id)
                ).first()
            except ValueError:
                pass
        
        if not test_suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found"
            )
        
        try:
            session.delete(test_suite)
            session.commit()
            
            # Invalidate caches
            invalidate_cache("read_test_suites")
            invalidate_cache(f"read_test_suite_{test_suite_id}")
            
            return None
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting test suite: {e}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail="Error deleting test suite"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_test_suite: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while deleting test suite"
        )
