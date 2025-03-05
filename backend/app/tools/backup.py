#!/usr/bin/env python3
import json
import os
import datetime
from pathlib import Path
from sqlmodel import Session, select

from app.db.init_db import engine
from app.models import (
    TestSuite, TestCase, TestRun, TestCaseResult,
    TestOperator, Company, TestRunTemplate,
    DUT, Capability, Specification, Requirement
)


def backup_database():
    """Backup all database tables to a JSON file."""
    backup_dir = Path(__file__).parent.parent.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"qa_database_backup_{timestamp}.json"
    
    with Session(engine) as session:
        # Get all data from all tables
        data = {
            "test_suites": [suite.dict() for suite in session.exec(select(TestSuite)).all()],
            "test_cases": [case.dict() for case in session.exec(select(TestCase)).all()],
            "test_runs": [run.dict() for run in session.exec(select(TestRun)).all()],
            "test_case_results": [result.dict() for result in session.exec(select(TestCaseResult)).all()],
            "test_operators": [operator.dict() for operator in session.exec(select(TestOperator)).all()],
            "companies": [company.dict() for company in session.exec(select(Company)).all()],
            "test_run_templates": [template.dict() for template in session.exec(select(TestRunTemplate)).all()],
            "duts": [dut.dict() for dut in session.exec(select(DUT)).all()],
            "capabilities": [capability.dict() for capability in session.exec(select(Capability)).all()],
            "specifications": [spec.dict() for spec in session.exec(select(Specification)).all()],
            "requirements": [req.dict() for req in session.exec(select(Requirement)).all()],
        }
    
    # Write to file
    with open(backup_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Database backup created at: {backup_file}")
    return backup_file


if __name__ == "__main__":
    backup_database()
