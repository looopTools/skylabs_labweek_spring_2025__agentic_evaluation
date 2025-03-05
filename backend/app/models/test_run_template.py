from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship, Table, Column, ForeignKey, String

if TYPE_CHECKING:
    from app.models.test_case import TestCase

# Association table for many-to-many relationship between TestRunTemplate and TestCase
TestRunTemplateTestCase = Table(
    "testruntemplate_testcase",
    SQLModel.metadata,
    Column("test_run_template_id", ForeignKey("testruntemplate.id"), primary_key=True),
    Column("test_case_id", ForeignKey("testcase.id"), primary_key=True),
)


class TestRunTemplateBase(SQLModel):
    template_id: str = Field(sa_column=Column(String, unique=True))  # TestRunTemplate_ID (renamed from id to avoid conflicts)
    name: str  # Test Run Template title
    description: Optional[str] = None  # Text description of the test run template
    field: Optional[str] = None  # A key field for template type (Release, Regression, etc.)


class TestRunTemplate(TestRunTemplateBase, table=True):
    __tablename__ = "testruntemplate"
    id: Optional[int] = Field(default=None, primary_key=True)  # Database primary key
    test_cases: List["TestCase"] = Relationship(
        back_populates="test_run_templates",
        sa_relationship_kwargs={"secondary": TestRunTemplateTestCase, "overlaps": "test_run_templates"}
    )


class TestRunTemplateCreate(TestRunTemplateBase):
    pass


class TestRunTemplateRead(TestRunTemplateBase):
    id: int  # Database ID


class TestRunTemplateUpdate(SQLModel):
    template_id: Optional[str] = None  # TestRunTemplate_ID
    name: Optional[str] = None
    description: Optional[str] = None
    field: Optional[str] = None
