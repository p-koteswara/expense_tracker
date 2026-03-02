from sqlalchemy import Column, Integer, String, Boolean

from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

