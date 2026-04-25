from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stockmind.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
    with engine.begin() as conn:
        # recommendations table
        existing_rec = {row[1] for row in conn.execute(text("PRAGMA table_info(recommendations)"))}
        if "currency" not in existing_rec:
            conn.execute(text("ALTER TABLE recommendations ADD COLUMN currency TEXT DEFAULT 'USD'"))
        if "currency_symbol" not in existing_rec:
            conn.execute(text("ALTER TABLE recommendations ADD COLUMN currency_symbol TEXT DEFAULT '$'"))
        if "model_name" not in existing_rec:
            conn.execute(text("ALTER TABLE recommendations ADD COLUMN model_name TEXT DEFAULT 'Unknown'"))

        # baskets table
        existing_basket = {row[1] for row in conn.execute(text("PRAGMA table_info(baskets)"))}
        if "data" not in existing_basket:
            conn.execute(text("ALTER TABLE baskets ADD COLUMN data TEXT DEFAULT '[]'"))


def _purge_ghost_rows():
    """Remove rows where the price never resolved (legacy bad inserts)."""
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
