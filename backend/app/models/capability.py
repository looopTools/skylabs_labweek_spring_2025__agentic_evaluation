from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.dut import DUT, DUTCapability


class CapabilityBase(SQLModel):
    name: str  # Capability name
    category: str  # Category of the capability
    version: int  # Numeric version
    version_string: str  # String version of the capability


class Capability(CapabilityBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    duts: List["DUT"] = Relationship(
        back_populates="capabilities",
        sa_relationship_kwargs={"secondary": "dut_capability", "overlaps": "capabilities"}
    )


class CapabilityCreate(CapabilityBase):
    pass


class CapabilityRead(CapabilityBase):
    id: int


class CapabilityUpdate(SQLModel):
    name: Optional[str] = None
    category: Optional[str] = None
    version: Optional[int] = None
    version_string: Optional[str] = None
