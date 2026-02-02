"""
EST Auth Service - Main FastAPI Application
"""
from fastapi import FastAPI
from sqlalchemy import text

from services.auth.src.core.db import engine
from services.auth.src.core.settings import settings
from services.auth.src.api import router as auth_router


app = FastAPI(
    title=settings.app_name,
    description="Authentication service for EST - Food at Lower Prices",
    version="1.0.0",
)

# Include routers
app.include_router(auth_router)


@app.get("/health")
def health():
    """Service health check"""
    return {
        "status": "ok",
        "service": "auth",
        "env": settings.env,
    }


@app.get("/db/health")
def db_health():
    """Database connection health check"""
    try:
        with engine.connect() as conn:
            conn.execute(text("select 1"))
        return {"db": "ok"}
    except Exception as e:
        return {"db": "error", "detail": str(e)}
