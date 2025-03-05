from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.test_case import TestCase
    from app.models.test_run import TestRun


class TestCaseResultBase(SQLModel):
    result: str  # Outcome of the test case (pass/fail)
    logs: Optional[str] = None  # Test run logs
    comment: Optional[str] = None  # Comments on the result
    artifacts: Optional[str] = None  # Related files or evidence of the test run
    test_case_id: int = Field(foreign_key="testcase.id")  # Foreign key linking to the TestCase table
    test_run_id: int = Field(foreign_key="testrun.id")  # Foreign key linking to the TestRun table


class TestCaseResult(TestCaseResultBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    test_case: "TestCase" = Relationship(back_populates="test_case_results")
    test_run: "TestRun" = Relationship(back_populates="test_case_results")


class TestCaseResultCreate(TestCaseResultBase):
    pass


class TestCaseResultRead(TestCaseResultBase):
    id: int


class TestCaseResultUpdate(SQLModel):
    result: Optional[str] = None
    logs: Optional[str] = None
    comment: Optional[str] = None
    artifacts: Optional[str] = None
