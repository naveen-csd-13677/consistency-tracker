"""FastAPI main application."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.api.endpoints import (
    goals,
    duties,
    logs,
    analytics,
    upgrades,
    suggestions,
    config,
    export,
    dashboard,
    insights,
)

logger = logging.getLogger(__name__)

# Create database tables (fallback for development; prefer Alembic migrations in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personal Consistency Tracker",
    description="Track daily habits, compute consistency metrics, manage progressive difficulty upgrades, and get AI-powered suggestions.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(goals.router)
app.include_router(duties.router)
app.include_router(logs.router)
app.include_router(analytics.router)
app.include_router(upgrades.router)
app.include_router(suggestions.router)
app.include_router(config.router)
app.include_router(export.router)
app.include_router(dashboard.router)
app.include_router(insights.router)


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}
