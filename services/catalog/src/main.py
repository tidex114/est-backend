from fastapi import FastAPI
from sqlalchemy import text

from services.catalog.src.core.db import engine
from services.catalog.src.core.settings import settings

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health():
    return {"status": "ok", "service": "catalog", "env": settings.env}


@app.get("/db/health")
def db_health():
    with engine.connect() as conn:
        conn.execute(text("select 1"))
    return {"db": "ok"}
