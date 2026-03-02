from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.budget import Budget
from app.db.models.category import Category
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from app.core.jwt import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[BudgetResponse])
def list_budgets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    return budgets


@router.post("/", response_model=BudgetResponse)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Ensure category exists
    category = db.query(Category).filter(Category.id == budget.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Optional: enforce one budget per (user, category, month, year)
    existing = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id,
            Budget.category_id == budget.category_id,
            Budget.month == budget.month,
            Budget.year == budget.year,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Budget for this category and month already exists",
        )

    new_budget = Budget(
        user_id=current_user.id,
        category_id=budget.category_id,
        month=budget.month,
        year=budget.year,
        limit_amount=budget.limit_amount,
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return new_budget


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    updated: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
        .first()
    )
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    budget.limit_amount = updated.limit_amount

    db.commit()
    db.refresh(budget)

    return budget

