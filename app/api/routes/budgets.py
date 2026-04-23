from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.db.session import SessionLocal
from app.db.models.budget import Budget
from app.db.models.category import Category
from app.db.models.expense import Expense
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
    
    # Enrich budgets with category info and calculate spent amount
    for budget in budgets:
        budget.category_name = budget.category.name
        budget.category_emoji = budget.category.emoji
        
        # Sum expenses for this user, category, and month/year
        spent = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            Expense.category_id == budget.category_id,
            extract('month', Expense.date) == budget.month,
            extract('year', Expense.date) == budget.year
        ).scalar() or 0
        
        budget.amount_spent = spent
        
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
    
    new_budget.category_name = category.name
    new_budget.category_emoji = category.emoji
    new_budget.amount_spent = 0

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
    
    budget.category_name = budget.category.name
    budget.category_emoji = budget.category.emoji
    
    spent = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.category_id == budget.category_id,
        extract('month', Expense.date) == budget.month,
        extract('year', Expense.date) == budget.year
    ).scalar() or 0
    budget.amount_spent = spent

    return budget


@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
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

    db.delete(budget)
    db.commit()

    return {"detail": "Budget deleted successfully"}
