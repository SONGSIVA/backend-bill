import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/billing_db"
)

# Render provides postgres:// URLs — SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,       # reconnect if DB connection drops
    pool_recycle=300,         # recycle connections every 5 minutes
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_logo_url_column():
    inspector = inspect(engine)
    if not inspector.has_table("company_settings"):
        return
    existing_columns = [column["name"] for column in inspector.get_columns("company_settings")]
    if "logo_url" not in existing_columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE company_settings ADD COLUMN IF NOT EXISTS logo_url VARCHAR(300);"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
