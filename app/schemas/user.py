from pydantic import BaseModel, EmailStr
from app.db.base import Base

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str