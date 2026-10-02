from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# pool_pre_ping: checks a connection is alive before handing it out
# (catches a connection that died while idle). pool_recycle: forces a
# connection to be replaced after 5 minutes regardless -- Neon (and
# most serverless Postgres) can close idle connections from its side
# without warning; recycling proactively avoids relying on pre_ping to
# catch every case.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
