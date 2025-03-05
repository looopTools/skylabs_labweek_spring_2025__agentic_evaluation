from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.init_db import get_session
from app.models.test_suite import TestSuite, TestSuiteCreate, TestSuiteRead, TestSuiteUpdate

router = APIRouter()


@router.get("/", response_model=List[TestSuiteRead])
def read_test_suites(
    skip: int = 0, 
    limit: int = 100,
    raw: bool = False,
    session: Session = Depends(get_session)
):
    try:
        # First try with a standard SQLModel query
        statement = select(TestSuite)
        test_suites = session.exec(statement.offset(skip).limit(limit)).all()
        
        if test_suites:
            print(f"Found {len(test_suites)} test suites with SQLModel query")
            return test_suites
        
        # If no results, try with a direct SQL query
        print("No test suites found with SQLModel query, trying direct SQL query")
        result = session.execute("SELECT * FROM testsuite LIMIT 100")
        rows = result.fetchall()
        print(f"Direct query found {len(rows)} rows in testsuite table")
        
        # Convert rows to TestSuite objects or dictionaries
        test_suites = []
        for row in rows:
            # Convert row to dict
            row_dict = {column: value for column, value in zip(result.keys(), row)}
            print(f"Row data: {row_dict}")
            
            if raw:
                # For raw mode, just return the dictionary
                test_suites.append(row_dict)
            else:
                # Create TestSuite object
                try:
                    test_suite = TestSuite(**row_dict)
                    test_suites.append(test_suite)
                except Exception as obj_error:
                    print(f"Error creating TestSuite object: {obj_error}")
                    # Fall back to returning the raw dict if object creation fails
                    test_suites.append(row_dict)
        
        # If still no test suites, create a default one
        if not test_suites:
            print("No test suites found, creating a default test suite")
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
        
        return test_suites
    except Exception as e:
        print(f"Error fetching test suites: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


@router.post("/", response_model=TestSuiteRead, status_code=status.HTTP_201_CREATED)
def create_test_suite(
    test_suite: TestSuiteCreate, 
    session: Session = Depends(get_session)
):
    try:
        db_test_suite = TestSuite.from_orm(test_suite)
        session.add(db_test_suite)
        session.commit()
        session.refresh(db_test_suite)
        return db_test_suite
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating test suite: {str(e)}"
        )


@router.get("/{test_suite_id}", response_model=TestSuiteRead)
def read_test_suite(
    test_suite_id: str, 
    session: Session = Depends(get_session)
):
    try:
        # First try to get by string ID
        test_suite = session.exec(select(TestSuite).where(TestSuite.id == test_suite_id)).first()
        
        if not test_suite:
            # Try to get by database ID if the string ID failed
            try:
                db_id = int(test_suite_id)
                test_suite = session.exec(select(TestSuite).where(TestSuite.db_id == db_id)).first()
            except ValueError:
                pass
        
        if not test_suite:
            # Try a direct SQL query as a last resort
            result = session.execute(f"SELECT * FROM testsuite WHERE id = '{test_suite_id}'").first()
            if result:
                # Convert row to dict
                row_dict = {column: value for column, value in zip(result.keys(), result)}
                print(f"Found test suite via direct SQL: {row_dict}")
                
                # Create TestSuite object from row
                test_suite = TestSuite(**row_dict)
        
        if not test_suite:
            raise HTTPException(status_code=404, detail="Test suite not found")
        
        return test_suite
    except Exception as e:
        print(f"Error in read_test_suite: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving test suite: {str(e)}")


@router.patch("/{test_suite_id}", response_model=TestSuiteRead)
def update_test_suite(
    test_suite_id: str,
    test_suite: TestSuiteUpdate,
    session: Session = Depends(get_session)
):
    # First try to get by string ID
    db_test_suite = session.exec(select(TestSuite).where(TestSuite.id == test_suite_id)).first()
    
    if not db_test_suite:
        # Try to get by database ID if the string ID failed
        try:
            db_id = int(test_suite_id)
            db_test_suite = session.exec(select(TestSuite).where(TestSuite.db_id == db_id)).first()
        except ValueError:
            pass
    
    if not db_test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    
    test_suite_data = test_suite.dict(exclude_unset=True)
    for key, value in test_suite_data.items():
        setattr(db_test_suite, key, value)
    
    session.add(db_test_suite)
    session.commit()
    session.refresh(db_test_suite)
    return db_test_suite


@router.delete("/{test_suite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_suite(
    test_suite_id: str,
    session: Session = Depends(get_session)
):
    # First try to get by string ID
    test_suite = session.exec(select(TestSuite).where(TestSuite.id == test_suite_id)).first()
    
    if not test_suite:
        # Try to get by database ID if the string ID failed
        try:
            db_id = int(test_suite_id)
            test_suite = session.exec(select(TestSuite).where(TestSuite.db_id == db_id)).first()
        except ValueError:
            pass
    
    if not test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    
    session.delete(test_suite)
    session.commit()
    return None
