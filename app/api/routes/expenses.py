from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
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
    db_expense = Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.get("/", response_model=list[ExpenseResponse])
def get_expenses(
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "id",
    order: str = "asc",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    
    query = db.query(Expense)

    # Validate sortable fields
    if not hasattr(Expense, sort_by):
        raise HTTPException(status_code=400, detail="Invalid sort field")

    column = getattr(Expense, sort_by)

    if order == "desc":
        query = query.order_by(desc(column))
    else:
        query = query.order_by(asc(column))

    expenses = query.offset(skip).limit(limit).all()

    return expenses


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    updated_data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    expense.title = updated_data.title
    expense.amount = updated_data.amount
    expense.category = updated_data.category

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()

    return {"message": "Expense deleted"}