import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL
from app.db.base import Base

logger = logging.getLogger(__name__)

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Temporary startup visibility: confirms which DB target is actually in use.
logger.info("SQLAlchemy engine initialized for DATABASE_URL=%s", engine.url.render_as_string(hide_password=True))