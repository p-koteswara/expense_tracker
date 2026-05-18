from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExpenseBase(BaseModel):
    description: str
    amount: float
    category_id: int
    date: Optional[datetime] = None
    note: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseResponse(ExpenseBase):
    id: int
    category_name: Optional[str] = None
    category_emoji: Optional[str] = None

    class Config:
        from_attributes = True

class ExpenseUpdate(ExpenseBase):
    pass


class ExpenseSummaryResponse(BaseModel):
    total_spent: float = 0
    transaction_count: int = 0


class PaginatedExpenseResponse(BaseModel):
    items: list[ExpenseResponse]
    total: int
    page: int
    size: int
    pages: int
