import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.test_run import TestRun
from app.models.test_case import TestCase
from app.models.test_case_result import TestCaseResult
from app.models.test_suite import TestSuite
from app.core.notifications import get_notification_manager

# Configure logging
logger = logging.getLogger(__name__)

async def process_test_suites(
    session: Session,
    test_suites: List[Dict],
    client_id: Optional[str] = None
) -> None:
    """Process test suites data"""
    notification_manager = get_notification_manager()
    
    for suite_data in test_suites:
        suite_id = suite_data.get("id")
        if not suite_id:
            continue
        
        try:
            # Try to find existing test suite
            test_suite = session.exec(
                select(TestSuite)
                .where(TestSuite.id == suite_id)
            ).first()
            
            if not test_suite:
                # Create new test suite
                test_suite_data = {
                    "id": suite_id,
                    "name": suite_data.get("name", f"Suite {suite_id}"),
                    "url": suite_data.get("url"),
                    "format": suite_data.get("format", "json"),
                    "version": suite_data.get("version", 1),
                    "version_string": suite_data.get("version_string", "1.0"),
                    "is_final": suite_data.get("is_final", False)
                }
                test_suite = TestSuite(**test_suite_data)
                session.add(test_suite)
                session.commit()
                session.refresh(test_suite)
                
                if client_id:
                    await notification_manager.send_notification(
                        client_id,
                        "test_suite_created",
                        f"Created test suite: {suite_id}",
                        {"suite_id": suite_id}
                    )
            else:
                # Update existing test suite if needed
                needs_update = False
                for field in ["name", "url", "format", "version", "version_string", "is_final"]:
                    if field in suite_data and getattr(test_suite, field) != suite_data[field]:
                        setattr(test_suite, field, suite_data[field])
                        needs_update = True
                
                if needs_update:
                    session.add(test_suite)
                    session.commit()
                    session.refresh(test_suite)
                    
                    if client_id:
                        await notification_manager.send_notification(
                            client_id,
                            "test_suite_updated",
                            f"Updated test suite: {suite_id}",
                            {"suite_id": suite_id}
                        )
        
        except Exception as e:
            logger.error(f"Error processing test suite {suite_id}: {e}", exc_info=True)
            session.rollback()
            if client_id:
                await notification_manager.send_notification(
                    client_id,
                    "error",
                    f"Error processing test suite {suite_id}",
                    {"error": str(e)}
                )

async def process_test_cases(
    session: Session,
    test_cases: List[Dict],
    client_id: Optional[str] = None
) -> None:
    """Process test cases data"""
    notification_manager = get_notification_manager()
    
    for case_data in test_cases:
        case_id = case_data.get("case_id")
        if not case_id:
            continue
        
        try:
            # Check if test case exists
            test_case = session.exec(
                select(TestCase)
                .where(TestCase.case_id == case_id)
            ).first()
            
            if not test_case:
                # Create new test case
                test_case = TestCase(
                    case_id=case_id,
                    title=case_data.get("title", f"Test Case {case_id}"),
                    version=case_data.get("version", 1),
                    version_string=case_data.get("version_string", "1.0"),
                    test_suite_id=case_data.get("test_suite_id", "default"),
                    applies_to=case_data.get("applies_to"),
                    description=case_data.get("description"),
                    steps=case_data.get("steps"),
                    precondition=case_data.get("precondition"),
                    area=case_data.get("area"),
                    automatability=case_data.get("automatability"),
                    author=case_data.get("author"),
                    material=case_data.get("material"),
                    is_challenged=case_data.get("is_challenged", False),
                    challenge_issue_url=case_data.get("challenge_issue_url")
                )
                session.add(test_case)
                session.commit()
                session.refresh(test_case)
                
                if client_id:
                    await notification_manager.send_notification(
                        client_id,
                        "test_case_created",
                        f"Created test case: {case_id}",
                        {"case_id": case_id}
                    )
        
        except Exception as e:
            logger.error(f"Error processing test case {case_id}: {e}", exc_info=True)
            session.rollback()
            if client_id:
                await notification_manager.send_notification(
                    client_id,
                    "error",
                    f"Error processing test case {case_id}",
                    {"error": str(e)}
                )

async def process_test_results(
    session: Session,
    test_run: TestRun,
    results_data: List[Dict],
    client_id: Optional[str] = None
) -> None:
    """Process test results data"""
    notification_manager = get_notification_manager()
    results = []
    processed = 0
    total = len(results_data)
    
    for item in results_data:
        try:
            # Handle different formats of test case ID
            test_case_id = item.get("test_case_id") or item.get("id")
            if not test_case_id:
                continue
            
            # Handle different formats of result
            result = item.get("result") or item.get("status", "Unknown")
            
            # Find or create test case
            test_case = None
            try:
                test_case = session.get(TestCase, test_case_id)
            except Exception:
                # Try to find by case_id if not found by ID
                stmt = select(TestCase).where(TestCase.case_id == str(test_case_id))
                test_case = session.exec(stmt).first()
            
            if not test_case:
                # Create a test case if it doesn't exist
                test_case = TestCase(
                    case_id=str(test_case_id),
                    title=item.get("title", f"Test Case {test_case_id}"),
                    version=1,
                    version_string="1.0",
                    test_suite_id="default"
                )
                session.add(test_case)
                session.commit()
                session.refresh(test_case)
            
            # Create test case result
            test_result = TestCaseResult(
                test_case_id=test_case.id,
                test_run_id=test_run.id,
                result=result,
                comment=item.get("comment", ""),
                logs=item.get("logs", ""),
                artifacts=item.get("artifacts", "")
            )
            results.append(test_result)
            
            processed += 1
            if processed % 10 == 0 and client_id:  # Send progress notification every 10 items
                await notification_manager.send_notification(
                    client_id,
                    "progress",
                    f"Processing test results: {processed}/{total}",
                    {
                        "processed": processed,
                        "total": total,
                        "percentage": (processed / total) * 100
                    }
                )
        
        except Exception as e:
            logger.error(f"Error processing test result for case {test_case_id}: {e}", exc_info=True)
            if client_id:
                await notification_manager.send_notification(
                    client_id,
                    "error",
                    f"Error processing test result for case {test_case_id}",
                    {"error": str(e)}
                )
    
    # Add all results to database
    if results:
        session.add_all(results)
        session.commit()
        
        if client_id:
            await notification_manager.send_notification(
                client_id,
                "complete",
                f"Completed processing {len(results)} test results",
                {"total_results": len(results)}
            )

async def process_test_results_file(
    session: Session,
    content: bytes,
    filename: str,
    client_id: Optional[str] = None
) -> TestRun:
    """Process test results from a file"""
    notification_manager = get_notification_manager()
    
    try:
        # Parse file content
        if filename.lower().endswith('.json'):
            data = json.loads(content.decode())
        else:
            raise HTTPException(
                status_code=400,
                detail="Only JSON files are currently supported"
            )
        
        # Create test run
        test_run = TestRun(status="Processing")
        session.add(test_run)
        session.commit()
        session.refresh(test_run)
        
        if client_id:
            await notification_manager.send_notification(
                client_id,
                "started",
                "Started processing test results file",
                {"test_run_id": test_run.id}
            )
        
        # Process test suites
        test_suites = data.get("test_suites", [])
        if test_suites:
            await process_test_suites(session, test_suites, client_id)
        
        # Process test cases
        test_cases = data.get("test_cases", [])
        if test_cases:
            await process_test_cases(session, test_cases, client_id)
        
        # Process test results
        test_results = data.get("test_case_results", data.get("results", []))
        if not test_results and isinstance(data, list):
            test_results = data
        
        if test_results:
            await process_test_results(session, test_run, test_results, client_id)
        
        # Update test run status
        test_run.status = "Completed"
        session.add(test_run)
        session.commit()
        session.refresh(test_run)
        
        if client_id:
            await notification_manager.send_notification(
                client_id,
                "completed",
                "Completed processing test results file",
                {"test_run_id": test_run.id}
            )
        
        return test_run
    
    except Exception as e:
        logger.error("Error processing test results file", exc_info=True)
        if 'test_run' in locals():
            test_run.status = "Failed"
            session.add(test_run)
            session.commit()
        
        if client_id:
            await notification_manager.send_notification(
                client_id,
                "error",
                "Failed to process test results file",
                {"error": str(e)}
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing test results: {str(e)}"
        )