from fastapi import FastAPI
from sqlalchemy import text

from services.catalog.src.core.db import engine
from services.catalog.src.core.settings import settings
from services.catalog.src.api.offers import router as offers_router

app = FastAPI(title=settings.app_name)

app.include_router(offers_router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "catalog", "env": settings.env}


@app.get("/db/health")
def db_health():
    with engine.connect() as conn:
        conn.execute(text("select 1"))
    return {"db": "ok"}
