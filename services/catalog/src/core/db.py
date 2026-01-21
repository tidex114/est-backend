from sqlalchemy import create_engine

from services.catalog.src.core.settings import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
