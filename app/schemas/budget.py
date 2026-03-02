from pydantic import BaseModel


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

    class Config:
        from_attributes = True

