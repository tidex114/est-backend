"""
EST Auth Service - Main FastAPI Application
"""
import logging
import time
from fastapi import FastAPI, Request
from sqlalchemy import text

from services.auth.src.core.db import get_engine
from services.auth.src.core.settings import settings
from services.auth.src.api import router as auth_router


app = FastAPI(
    title=settings.app_name,
    description="Authentication service for EST - Food at Lower Prices",
    version="1.0.0",
)

logger = logging.getLogger("auth.request")

# Include routers
app.include_router(auth_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


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
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("select 1"))
        return {"db": "ok"}
    except Exception as e:
        return {"db": "error", "detail": str(e)}
