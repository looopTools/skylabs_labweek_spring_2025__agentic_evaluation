from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.db.init_db import create_db_and_tables

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

# Include API router
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Welcome to QA Database API. Visit /docs for API documentation."}
