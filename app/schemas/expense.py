from pydantic import BaseModel
from datetime import datetime

class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str

class ExpenseResponse(ExpenseCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ExpenseUpdate(BaseModel):
    title: str
    amount: float
    category: str