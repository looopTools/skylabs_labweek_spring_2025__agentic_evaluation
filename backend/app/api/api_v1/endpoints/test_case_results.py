from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.db.init_db import get_session
from app.models.test_case_result import TestCaseResult, TestCaseResultCreate, TestCaseResultRead, TestCaseResultUpdate

router = APIRouter()


@router.get("/", response_model=List[TestCaseResultRead])
def read_test_case_results(
    skip: int = 0, 
    limit: int = 100,
    test_run_id: Optional[int] = Query(None),
    test_case_id: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):
    query = select(TestCaseResult)
    
    if test_run_id is not None:
        query = query.where(TestCaseResult.test_run_id == test_run_id)
    
    if test_case_id is not None:
        query = query.where(TestCaseResult.test_case_id == test_case_id)
    
    results = session.exec(query.offset(skip).limit(limit)).all()
    return results


@router.post("/", response_model=TestCaseResultRead, status_code=status.HTTP_201_CREATED)
def create_test_case_result(
    result: TestCaseResultCreate, 
    session: Session = Depends(get_session)
):
    db_result = TestCaseResult.from_orm(result)
    session.add(db_result)
    session.commit()
    session.refresh(db_result)
    return db_result


@router.get("/{result_id}", response_model=TestCaseResultRead)
def read_test_case_result(
    result_id: int, 
    session: Session = Depends(get_session)
):
    result = session.get(TestCaseResult, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Test case result not found")
    return result


@router.patch("/{result_id}", response_model=TestCaseResultRead)
def update_test_case_result(
    result_id: int,
    result: TestCaseResultUpdate,
    session: Session = Depends(get_session)
):
    db_result = session.get(TestCaseResult, result_id)
    if not db_result:
        raise HTTPException(status_code=404, detail="Test case result not found")
    
    result_data = result.dict(exclude_unset=True)
    for key, value in result_data.items():
        setattr(db_result, key, value)
    
    session.add(db_result)
    session.commit()
    session.refresh(db_result)
    return db_result


@router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_case_result(
    result_id: int,
    session: Session = Depends(get_session)
):
    result = session.get(TestCaseResult, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Test case result not found")
    
    session.delete(result)
    session.commit()
    return None
