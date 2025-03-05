from contextlib import contextmanager
from typing import Generator
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, create_engine
from sqlalchemy.pool import QueuePool
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection configuration
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,  # Control SQL logging through settings
    poolclass=QueuePool,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # Enable connection health checks
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def get_db_connection():
    """Get a database connection with retry logic"""
    try:
        # Test the connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return engine
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        raise

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Get a database session with automatic cleanup"""
    session = Session(get_db_connection())
    try:
        yield session
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()

def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions"""
    with get_db_session() as session:
        yield session