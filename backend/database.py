from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./stockmind.db"

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
    current_price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


def _ensure_columns():
    """Idempotently add new columns introduced after the initial schema."""
    with engine.begin() as conn:
        existing = {row[1] for row in conn.execute(text("PRAGMA table_info(recommendations)"))}
        if "currency" not in existing:
            conn.execute(text("ALTER TABLE recommendations ADD COLUMN currency TEXT DEFAULT 'USD'"))
        if "currency_symbol" not in existing:
            conn.execute(text("ALTER TABLE recommendations ADD COLUMN currency_symbol TEXT DEFAULT '$'"))


def init_db():
    Base.metadata.create_all(bind=engine)
    _ensure_columns()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
