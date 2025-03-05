from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.requirement import Requirement


class SpecificationBase(SQLModel):
    name: str  # Specification name
    url: Optional[str] = None  # Specification document URL
    version: str  # Version of the specification


class Specification(SpecificationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requirements: List["Requirement"] = Relationship(back_populates="specification")


class SpecificationCreate(SpecificationBase):
    pass


class SpecificationRead(SpecificationBase):
    id: int


class SpecificationUpdate(SQLModel):
    name: Optional[str] = None
    url: Optional[str] = None
    version: Optional[str] = None
