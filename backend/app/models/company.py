from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.test_operator import TestOperator


class CompanyBase(SQLModel):
    name: str  # Company name
    access_rights: Optional[str] = None  # Company-wide permissions


class Company(CompanyBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    operators: List["TestOperator"] = Relationship(back_populates="company")


class CompanyCreate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    id: int


class CompanyUpdate(SQLModel):
    name: Optional[str] = None
    access_rights: Optional[str] = None
