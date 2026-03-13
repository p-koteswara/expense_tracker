from pydantic import BaseModel
from typing import Optional


class BudgetBase(BaseModel):
    category_id: int
    month: int  # 1-12
    year: int
    limit_amount: float


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    limit_amount: float


class BudgetResponse(BudgetBase):
    id: int
    amount_spent: float = 0
    category_name: Optional[str] = None
    category_emoji: Optional[str] = None

    class Config:
        from_attributes = True
