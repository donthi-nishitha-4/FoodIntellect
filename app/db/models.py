from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from .session import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100))

    email = Column(String(150), unique=True)

    age = Column(Integer, nullable=True)

    dietary_preference = Column(String(100), nullable=True)

    allergies = Column(String(500), nullable=True)


class AnalysisHistory(Base):

    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer)

    product_name = Column(String(200))

    barcode = Column(String(100), nullable=True)

    ingredients = Column(Text, nullable=True)

    analysis = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )