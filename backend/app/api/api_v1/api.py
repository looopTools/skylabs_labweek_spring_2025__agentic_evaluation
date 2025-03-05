from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    test_suites,
    test_cases,
    test_runs,
    test_case_results,
    test_run_templates,
    notifications,
    tasks,
)

api_router = APIRouter()
api_router.include_router(test_suites.router, prefix="/test-suites", tags=["test-suites"])
api_router.include_router(test_cases.router, prefix="/test-cases", tags=["test-cases"])
api_router.include_router(test_runs.router, prefix="/test-runs", tags=["test-runs"])
api_router.include_router(test_case_results.router, prefix="/test-case-results", tags=["test-case-results"])
api_router.include_router(test_run_templates.router, prefix="/test-run-templates", tags=["test-run-templates"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
