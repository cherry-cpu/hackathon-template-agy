from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.db.base import Base

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session and safely closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Create all tables in the database and ensure schema migrations."""
    # Import all models so that Base.metadata knows about them
    from app.models import user, creator, portfolio, company, job, engagement, verification, company_view, sidecar  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Fool-proof auto-migration for existing databases: ensure views_count column exists
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if "company_profiles" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("company_profiles")]
        if "views_count" not in columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE company_profiles ADD COLUMN views_count INTEGER DEFAULT 0"))
                conn.commit()

