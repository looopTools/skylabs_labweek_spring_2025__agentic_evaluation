from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.test_case import TestCase

class TestSuiteBase(SQLModel):
    id: str  # TestSuite_ID (primary identifier used by frontend)
    name: str  # Name of the test suite
    url: Optional[str] = None  # URL associated with the suite
    format: str  # Format determining if a test suite can be read/automated
    version: int  # Numeric version of the suite
    version_string: str  # String representation of the version
    is_final: bool = False  # Boolean indicating whether this is the final version


class TestSuite(TestSuiteBase, table=True):
    __tablename__ = "testsuite"
    db_id: Optional[int] = Field(default=1, primary_key=True, sa_column_kwargs={"autoincrement": True})  # Database primary key with default value
    test_cases: List["TestCase"] = Relationship(back_populates="test_suite")
    
    class Config:
        arbitrary_types_allowed = True
        
    def __init__(self, **data):
        # Handle case where db_id is provided as string
        if "db_id" in data and isinstance(data["db_id"], str):
            try:
                data["db_id"] = int(data["db_id"])
            except (ValueError, TypeError):
                pass
        super().__init__(**data)


class TestSuiteCreate(TestSuiteBase):
    pass


class TestSuiteRead(TestSuiteBase):
    db_id: Optional[int] = None  # Database ID


class TestSuiteUpdate(SQLModel):
    id: Optional[str] = None  # TestSuite_ID
    name: Optional[str] = None
    url: Optional[str] = None
    format: Optional[str] = None
    version: Optional[int] = None
    version_string: Optional[str] = None
    is_final: Optional[bool] = None
