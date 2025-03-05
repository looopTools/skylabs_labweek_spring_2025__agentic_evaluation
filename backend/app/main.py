import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.rate_limit import rate_limit_middleware
from app.db.session import get_db_connection, engine
from sqlmodel import SQLModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QA Database API",
    description="API for QA Database System",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Middleware to handle database sessions and errors"""
    try:
        # Apply rate limiting
        await rate_limit_middleware(request)
        response = await call_next(request)
        return response
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Include API router
app.include_router(api_router, prefix="/api")

from app.core.tasks import get_task_queue
from app.core.notifications import get_notification_manager

@app.on_event("startup")
async def on_startup():
    """Initialize application components"""
    try:
        # Test database connection
        get_db_connection()
        # Create tables
        SQLModel.metadata.create_all(engine)
        logger.info("Database initialized successfully")

        # Start task queue workers
        task_queue = get_task_queue()
        await task_queue.start_workers()
        logger.info("Task queue workers started")

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

@app.on_event("shutdown")
async def on_shutdown():
    """Cleanup on shutdown"""
    try:
        # Stop task queue workers
        task_queue = get_task_queue()
        await task_queue.stop_workers()
        logger.info("Task queue workers stopped")

        # Clean up old tasks and notifications
        task_queue.cleanup_completed_tasks()
        notification_manager = get_notification_manager()
        notification_manager.cleanup_old_notifications()
        logger.info("Old tasks and notifications cleaned up")

        # Close database connections
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/")
async def root():
    """API root endpoint with health check"""
    # Get task queue status
    task_queue = get_task_queue()
    active_tasks = len([t for t in task_queue.get_all_tasks() if t.status == "running"])
    
    return {
        "message": "Welcome to QA Database API. Visit /docs for API documentation.",
        "version": "1.0.0",
        "status": "healthy",
        "active_tasks": active_tasks,
        "features": {
            "websocket_notifications": True,
            "background_tasks": True,
            "caching": True,
            "rate_limiting": True
        }
    }
