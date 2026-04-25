from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, text, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stockmind.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite requires check_same_thread=False for FastAPI/multi-threading.
# Postgres (psycopg2) does not support this argument.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    market_name = Column(String, default="Unknown")
    country_flag = Column(String, default="🌐")
    currency = Column(String, default="USD")
    currency_symbol = Column(String, default="$")
    action = Column(String)
    confidence = Column(Float)
    reasoning = Column(Text)
    model_name = Column(String, default="Unknown")
    current_price = Column(Float)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Basket(Base):
    __tablename__ = "baskets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    tickers = Column(Text)  # Comma-separated tickers (legacy)
    data = Column(Text, default="[]")  # Full JSON payload
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def _ensure_columns():
    """Idempotently add new columns introduced after the initial schema."""
    inspector = inspect(engine)
    
    # recommendations table
    if "recommendations" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("recommendations")]
        with engine.begin() as conn:
            if "currency" not in columns:
                conn.execute(text("ALTER TABLE recommendations ADD COLUMN currency TEXT DEFAULT 'USD'"))
            if "currency_symbol" not in columns:
                conn.execute(text("ALTER TABLE recommendations ADD COLUMN currency_symbol TEXT DEFAULT '$'"))
            if "model_name" not in columns:
                conn.execute(text("ALTER TABLE recommendations ADD COLUMN model_name TEXT DEFAULT 'Unknown'"))

    # baskets table
    if "baskets" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("baskets")]
        with engine.begin() as conn:
            if "data" not in columns:
                conn.execute(text("ALTER TABLE baskets ADD COLUMN data TEXT DEFAULT '[]'"))


def _purge_ghost_rows():
    """Remove rows where the price never resolved (legacy bad inserts)."""
    inspector = inspect(engine)
    if "recommendations" in inspector.get_table_names():
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM recommendations WHERE current_price IS NULL OR current_price <= 0"))


def init_db():
    Base.metadata.create_all(bind=engine)
    _ensure_columns()
    _purge_ghost_rows()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
