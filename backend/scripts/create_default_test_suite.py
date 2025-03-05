#!/usr/bin/env python3
import sys
import os

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlmodel import Session, select
from app.db.init_db import engine, create_db_and_tables
from app.models.test_suite import TestSuite

def create_default_test_suite():
    """Create a default test suite if none exists."""
    create_db_and_tables()
    
    with Session(engine) as session:
        # Check if any test suites exist
        statement = select(TestSuite)
        existing_suites = session.exec(statement).all()
        
        if not existing_suites:
            print("No test suites found. Creating default test suite...")
            default_suite = TestSuite(
                id="DEFAULT",
                name="Default Test Suite",
                format="json",
                version=1,
                version_string="1.0",
                is_final=False,
                db_id=1  # Explicitly set the db_id to avoid NOT NULL constraint
            )
            session.add(default_suite)
            session.commit()
            print(f"Created default test suite with ID: {default_suite.id}")
        else:
            print(f"Found {len(existing_suites)} existing test suites. No need to create default.")

if __name__ == "__main__":
    create_default_test_suite()
