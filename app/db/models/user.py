from sqlalchemy import Column, Integer, String
from app.db.models.base import Base  # adjust if your Base import differs

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)