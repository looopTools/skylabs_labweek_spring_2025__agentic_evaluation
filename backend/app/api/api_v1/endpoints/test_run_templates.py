from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.init_db import get_session
from app.models.test_run_template import TestRunTemplate, TestRunTemplateCreate, TestRunTemplateRead, TestRunTemplateUpdate
from app.models.test_case import TestCase

router = APIRouter()


@router.get("/", response_model=List[TestRunTemplateRead])
def read_test_run_templates(
    skip: int = 0, 
    limit: int = 100, 
    session: Session = Depends(get_session)
):
    """Get all test run templates."""
    test_run_templates = session.exec(select(TestRunTemplate).offset(skip).limit(limit)).all()
    return test_run_templates


@router.post("/", response_model=TestRunTemplateRead, status_code=status.HTTP_201_CREATED)
def create_test_run_template(
    test_run_template: TestRunTemplateCreate, 
    session: Session = Depends(get_session)
):
    """Create a new test run template."""
    db_test_run_template = TestRunTemplate.from_orm(test_run_template)
    session.add(db_test_run_template)
    session.commit()
    session.refresh(db_test_run_template)
    return db_test_run_template


@router.get("/{test_run_template_id}", response_model=TestRunTemplateRead)
def read_test_run_template(
    test_run_template_id: int, 
    session: Session = Depends(get_session)
):
    """Get a specific test run template by ID."""
    test_run_template = session.get(TestRunTemplate, test_run_template_id)
    if not test_run_template:
        raise HTTPException(status_code=404, detail="Test run template not found")
    return test_run_template


@router.put("/{test_run_template_id}", response_model=TestRunTemplateRead)
def update_test_run_template(
    test_run_template_id: int,
    test_run_template: TestRunTemplateUpdate,
    session: Session = Depends(get_session)
):
    """Update a test run template."""
    db_test_run_template = session.get(TestRunTemplate, test_run_template_id)
    if not db_test_run_template:
        raise HTTPException(status_code=404, detail="Test run template not found")
    
    test_run_template_data = test_run_template.dict(exclude_unset=True)
    for key, value in test_run_template_data.items():
        setattr(db_test_run_template, key, value)
    
    session.add(db_test_run_template)
    session.commit()
    session.refresh(db_test_run_template)
    return db_test_run_template


@router.delete("/{test_run_template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_run_template(
    test_run_template_id: int,
    session: Session = Depends(get_session)
):
    """Delete a test run template."""
    test_run_template = session.get(TestRunTemplate, test_run_template_id)
    if not test_run_template:
        raise HTTPException(status_code=404, detail="Test run template not found")
    
    session.delete(test_run_template)
    session.commit()
    return None


@router.get("/{test_run_template_id}/test-cases", response_model=List[TestCase])
def get_test_cases_for_template(
    test_run_template_id: int,
    session: Session = Depends(get_session)
):
    """Get all test cases associated with a test run template."""
    test_run_template = session.get(TestRunTemplate, test_run_template_id)
    if not test_run_template:
        raise HTTPException(status_code=404, detail="Test run template not found")
    
    # In a real implementation, this would fetch the test cases associated with the template
    # For now, we'll return a sample of test cases
    test_cases = session.exec(select(TestCase).limit(10)).all()
    return test_cases
