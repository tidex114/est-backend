from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.catalog.src.core.settings import settings

_engine = None
_session_local = None

def get_engine():
    """Lazily create and return the database engine"""
    global _engine
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine

def get_session_local():
    """Lazily create and return the SessionLocal factory"""
    global _session_local
    if _session_local is None:
        _session_local = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _session_local

# For backwards compatibility - these will be created lazily
engine = None  # Will be created lazily
SessionLocal = None  # Will be created lazily
