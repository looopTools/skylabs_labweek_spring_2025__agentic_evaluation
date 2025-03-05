# Import SQLModel first to avoid circular imports
from sqlmodel import SQLModel

# This ensures all models are properly registered with SQLModel
SQLModel.metadata

# Import all models - these are used by other modules
from app.models.test_suite import TestSuite, TestSuiteCreate, TestSuiteRead, TestSuiteUpdate
from app.models.test_case import TestCase, TestCaseCreate, TestCaseRead, TestCaseUpdate
from app.models.test_run import TestRun, TestRunCreate, TestRunRead, TestRunUpdate
from app.models.test_case_result import TestCaseResult, TestCaseResultCreate, TestCaseResultRead, TestCaseResultUpdate
from app.models.test_operator import TestOperator, TestOperatorCreate, TestOperatorRead, TestOperatorUpdate
from app.models.company import Company, CompanyCreate, CompanyRead, CompanyUpdate
from app.models.test_run_template import TestRunTemplate, TestRunTemplateCreate, TestRunTemplateRead, TestRunTemplateUpdate
from app.models.dut import DUT, DUTCreate, DUTRead, DUTUpdate
from app.models.capability import Capability, CapabilityCreate, CapabilityRead, CapabilityUpdate
from app.models.specification import Specification, SpecificationCreate, SpecificationRead, SpecificationUpdate
from app.models.requirement import Requirement, RequirementCreate, RequirementRead, RequirementUpdate
