"""
Database Connection and Session Management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.auth.src.core.settings import settings

_engine = None
_session_local = None

def get_engine():
    """Lazily create and return the database engine"""
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            echo=settings.env == "dev",
            future=True,
            pool_pre_ping=True,
        )
    return _engine

def get_session_local():
    """Lazily create and return the SessionLocal factory"""
    global _session_local
    if _session_local is None:
        engine = get_engine()
        _session_local = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _session_local

# For backwards compatibility - these will call the functions
# engine is kept as a callable for compatibility
engine = None  # Will be created lazily
SessionLocal = None  # Will be created lazily
