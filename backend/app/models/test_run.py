from typing import Optional, List, TYPE_CHECKING, Any
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from pydantic import validator

if TYPE_CHECKING:
    from app.models.test_operator import TestOperator
    from app.models.test_case_result import TestCaseResult, TestCaseResultRead


class TestRunBase(SQLModel):
    status: str  # Status of the test run
    operator_id: Optional[int] = Field(default=None, foreign_key="testoperator.id")  # Foreign key linking to the TestOperator table


class TestRun(TestRunBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=True)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, nullable=True, sa_column_kwargs={"onupdate": datetime.utcnow})
    operator: Optional["TestOperator"] = Relationship(back_populates="test_runs")
    test_case_results: List["TestCaseResult"] = Relationship(back_populates="test_run")


class TestRunCreate(TestRunBase):
    pass


class TestRunUpdate(SQLModel):
    status: Optional[str] = None
    operator_id: Optional[int] = None


# Define TestRunRead after importing TestCaseResultRead to avoid circular imports
class TestRunRead(TestRunBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    test_case_results: List[Any] = []  # Use Any to avoid circular import issues

    @validator('created_at', 'updated_at', pre=True)
    def default_datetime(cls, value):
        return value or datetime.utcnow()

# Import at the end to avoid circular imports
from app.models.test_case_result import TestCaseResultRead
TestRunRead.model_rebuild()  # Rebuild the model with proper types
