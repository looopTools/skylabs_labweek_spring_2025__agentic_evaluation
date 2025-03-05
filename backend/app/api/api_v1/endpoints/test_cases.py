from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.init_db import get_session
from app.models.test_case import TestCase, TestCaseCreate, TestCaseRead, TestCaseUpdate

router = APIRouter()


@router.get("/", response_model=List[TestCaseRead])
def read_test_cases(
    skip: int = 0, 
    limit: int = 100, 
    session: Session = Depends(get_session)
):
    # Get unique test cases by case_id
    query = select(TestCase)
    
    # First get all test cases
    all_test_cases = session.exec(query).all()
    
    # Create a dictionary to store unique test cases by case_id
    unique_cases = {}
    for case in all_test_cases:
        if case.case_id not in unique_cases:
            unique_cases[case.case_id] = case
    
    # Convert dictionary values to list
    unique_test_cases = list(unique_cases.values())
    
    # Apply pagination
    start = min(skip, len(unique_test_cases))
    end = min(start + limit, len(unique_test_cases))
    
    return unique_test_cases[start:end]


@router.post("/", response_model=TestCaseRead, status_code=status.HTTP_201_CREATED)
def create_test_case(
    test_case: TestCaseCreate, 
    session: Session = Depends(get_session)
):
    db_test_case = TestCase.from_orm(test_case)
    session.add(db_test_case)
    session.commit()
    session.refresh(db_test_case)
    return db_test_case


@router.get("/{test_case_id}", response_model=TestCaseRead)
def read_test_case(
    test_case_id: int, 
    session: Session = Depends(get_session)
):
    test_case = session.get(TestCase, test_case_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case


@router.patch("/{test_case_id}", response_model=TestCaseRead)
def update_test_case(
    test_case_id: int,
    test_case: TestCaseUpdate,
    session: Session = Depends(get_session)
):
    db_test_case = session.get(TestCase, test_case_id)
    if not db_test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    test_case_data = test_case.dict(exclude_unset=True)
    for key, value in test_case_data.items():
        setattr(db_test_case, key, value)
    
    session.add(db_test_case)
    session.commit()
    session.refresh(db_test_case)
    return db_test_case


@router.delete("/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_case(
    test_case_id: int,
    session: Session = Depends(get_session)
):
    test_case = session.get(TestCase, test_case_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    try:
        # First delete any test case results associated with this test case
        from sqlalchemy import text
        session.exec(text(f"DELETE FROM testcaseresult WHERE test_case_id = {test_case_id}"))
        
        # Try to delete template associations, but catch and ignore specific errors
        try:
            # Check if the association table exists
            result = session.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='testruntemplate_testcase'")
            if result.fetchone():
                # Delete associations without using the template_id column
                session.exec(text(f"DELETE FROM testruntemplate_testcase WHERE test_case_id = {test_case_id}"))
        except Exception as template_error:
            # Log the error but continue with deletion
            print(f"Warning: Could not delete template associations: {template_error}")
        
        # Finally delete the test case itself
        session.delete(test_case)
        session.commit()
        return None
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting test case: {str(e)}"
        )


@router.delete("/clear-all/", status_code=status.HTTP_204_NO_CONTENT)
def clear_all_test_cases(
    session: Session = Depends(get_session)
):
    """Delete all test cases and their associated test case results."""
    try:
        from sqlalchemy import text
        
        # First delete all test case results
        session.exec(text("DELETE FROM testcaseresult"))
        
        # Try to delete all template associations
        try:
            # Check if the association table exists
            result = session.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='testruntemplate_testcase'")
            if result.fetchone():
                session.exec(text("DELETE FROM testruntemplate_testcase"))
        except Exception as template_error:
            # Log the error but continue with deletion
            print(f"Warning: Could not delete template associations: {template_error}")
        
        # Finally delete all test cases
        session.exec(text("DELETE FROM testcase"))
        
        session.commit()
        return None
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing test cases: {str(e)}"
        )
