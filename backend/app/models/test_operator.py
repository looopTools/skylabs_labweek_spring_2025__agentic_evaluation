from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.test_run import TestRun


class TestOperatorBase(SQLModel):
    name: str  # Operator's name
    mail: str  # Email address
    login: str  # Login username
    access_rights: Optional[str] = None  # Operator's permissions
    company_id: Optional[int] = Field(default=None, foreign_key="company.id")  # Foreign key linking to the Company table


class TestOperator(TestOperatorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company: Optional["Company"] = Relationship(back_populates="operators")
    test_runs: List["TestRun"] = Relationship(back_populates="operator")


class TestOperatorCreate(TestOperatorBase):
    pass


class TestOperatorRead(TestOperatorBase):
    id: int


class TestOperatorUpdate(SQLModel):
    name: Optional[str] = None
    mail: Optional[str] = None
    login: Optional[str] = None
    access_rights: Optional[str] = None
    company_id: Optional[int] = None
