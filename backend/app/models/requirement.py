from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.specification import Specification


class RequirementBase(SQLModel):
    field: str  # Key field for requirements
    specification_id: int = Field(foreign_key="specification.id")  # Foreign key linking to the Specification table


class Requirement(RequirementBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    specification: "Specification" = Relationship(back_populates="requirements")


class RequirementCreate(RequirementBase):
    pass


class RequirementRead(RequirementBase):
    id: int


class RequirementUpdate(SQLModel):
    field: Optional[str] = None
    specification_id: Optional[int] = None
