from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.expense import Expense
from app.db.models.category import Category
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseResponse,
    ExpenseSummaryResponse,
    ExpenseUpdate,
)
from app.core.jwt import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ExpenseResponse)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Ensure category exists
    category = db.query(Category).filter(Category.id == expense.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db_expense = Expense(
        **expense.model_dump(),
        user_id=current_user.id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    # Return with category info
    db_expense.category_name = category.name
    db_expense.category_emoji = category.emoji
    return db_expense


@router.get("/summary", response_model=ExpenseSummaryResponse)
def get_expense_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total_spent = (
        db.query(func.sum(Expense.amount))
        .filter(Expense.user_id == current_user.id)
        .scalar()
        or 0
    )
    transaction_count = (
        db.query(func.count(Expense.id))
        .filter(Expense.user_id == current_user.id)
        .scalar()
        or 0
    )

    return ExpenseSummaryResponse(
        total_spent=float(total_spent),
        transaction_count=int(transaction_count),
    )


@router.get("/", response_model=list[ExpenseResponse])
def get_expenses(
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "date",
    order: str = "desc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    
    query = db.query(Expense).filter(Expense.user_id == current_user.id)

    # Join with Category to get name and emoji
    query = query.join(Category)

    # Validate sortable fields
    if not hasattr(Expense, sort_by) and sort_by != "id":
        sort_by = "date"

    column = getattr(Expense, sort_by)

    if order == "desc":
        query = query.order_by(desc(column))
    else:
        query = query.order_by(asc(column))

    expenses = query.offset(skip).limit(limit).all()

    # Add category details to response
    for exp in expenses:
        exp.category_name = exp.category.name
        exp.category_emoji = exp.category.emoji

    return expenses


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    expense.category_name = expense.category.name
    expense.category_emoji = expense.category.emoji
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    updated_data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for key, value in updated_data.model_dump().items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    
    expense.category_name = expense.category.name
    expense.category_emoji = expense.category.emoji
    return expense


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()

    return {"message": "Expense deleted"}
