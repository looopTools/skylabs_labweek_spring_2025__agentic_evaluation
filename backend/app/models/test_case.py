from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.test_suite import TestSuite
    from app.models.test_case_result import TestCaseResult
    from app.models.test_run_template import TestRunTemplate


class TestCaseBase(SQLModel):
    title: str  # Title of the test case
    version: int  # Numeric version
    version_string: str  # Version in string format
    test_suite_id: str = Field(foreign_key="testsuite.id", sa_column_kwargs={"nullable": False})  # Foreign key linking to the TestSuite table
    applies_to: Optional[str] = None  # Field specifying what the test case applies to
    description: Optional[str] = None  # Detailed description of the test case
    steps: Optional[str] = None  # Steps involved in the test case
    precondition: Optional[str] = None  # Pre-conditions for the test case
    area: Optional[str] = None  # Textual description of what this test case is about
    automatability: Optional[str] = None  # Is it possible to automate this test case
    author: Optional[str] = None  # Person responsible for the test case
    material: Optional[str] = None  # Associated materials
    is_challenged: Optional[bool] = False  # Key indicating if the test case is challenged
    challenge_issue_url: Optional[str] = None  # URL of any associated issues
    case_id: str  # Test case identifier (renamed from id to avoid conflicts)


class TestCase(TestCaseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Database primary key
    test_suite: "TestSuite" = Relationship(back_populates="test_cases")
    test_case_results: List["TestCaseResult"] = Relationship(back_populates="test_case")
    test_run_templates: List["TestRunTemplate"] = Relationship(
        back_populates="test_cases",
        sa_relationship_kwargs={"secondary": "testruntemplate_testcase", "overlaps": "test_cases"}
    )


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseRead(TestCaseBase):
    id: int  # Database ID


class TestCaseUpdate(SQLModel):
    case_id: Optional[str] = None  # Test case identifier
    title: Optional[str] = None
    version: Optional[int] = None
    version_string: Optional[str] = None
    test_suite_id: Optional[str] = None
    applies_to: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[str] = None
    precondition: Optional[str] = None
    area: Optional[str] = None
    automatability: Optional[str] = None
    author: Optional[str] = None
    material: Optional[str] = None
    is_challenged: Optional[bool] = None
    challenge_issue_url: Optional[str] = None
