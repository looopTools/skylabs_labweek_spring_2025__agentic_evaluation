from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, Table, Column, ForeignKey

if TYPE_CHECKING:
    from app.models.capability import Capability

# Association table for many-to-many relationship between DUT and Capability
DUTCapability = Table(
    "dut_capability",
    SQLModel.metadata,
    Column("dut_id", ForeignKey("dut.id"), primary_key=True),
    Column("capability_id", ForeignKey("capability.id"), primary_key=True),
)


class DUTBase(SQLModel):
    product_name: str  # Name of the product
    make: str  # Manufacturer
    model: str  # Model name
    countries: Optional[str] = None  # Supported regions
    parent: Optional[str] = None  # Parent device (if any)


class DUT(DUTBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    capabilities: List["Capability"] = Relationship(
        back_populates="duts",
        sa_relationship_kwargs={"secondary": DUTCapability, "overlaps": "duts"}
    )


class DUTCreate(DUTBase):
    pass


class DUTRead(DUTBase):
    id: int


class DUTUpdate(SQLModel):
    product_name: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    countries: Optional[str] = None
    parent: Optional[str] = None
