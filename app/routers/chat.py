import json
from datetime import datetime

import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import GEMINI_API_KEY
from app.core.jwt import get_current_user
from app.db.models.budget import Budget
from app.db.models.category import Category
from app.db.models.expense import Expense
from app.db.session import SessionLocal

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _extract_json_payload(raw_text: str) -> dict | None:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        return None
    try:
        return json.loads(cleaned[start_idx : end_idx + 1])
    except json.JSONDecodeError:
        return None


@router.post("")
@router.post("/")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured")

    today = datetime.utcnow()
    month = today.month
    year = today.year

    expenses = (
        db.query(Expense)
        .join(Category, Category.id == Expense.category_id)
        .filter(
            Expense.user_id == current_user.id,
            func.extract("month", Expense.date) == month,
            func.extract("year", Expense.date) == year,
        )
        .order_by(Expense.date.desc())
        .all()
    )

    expense_lines = [
        f"- ${expense.amount:.2f} | {expense.description} | {expense.category.name} | {expense.date.strftime('%Y-%m-%d')}"
        for expense in expenses
    ]
    expense_context = "\n".join(expense_lines) if expense_lines else "- No expenses recorded this month"

    budgets = (
        db.query(Budget)
        .join(Category, Category.id == Budget.category_id)
        .filter(Budget.user_id == current_user.id)
        .all()
    )

    budget_lines = []
    for budget in budgets:
        spent = (
            db.query(func.sum(Expense.amount))
            .filter(
                Expense.user_id == current_user.id,
                Expense.category_id == budget.category_id,
                func.extract("month", Expense.date) == budget.month,
                func.extract("year", Expense.date) == budget.year,
            )
            .scalar()
            or 0
        )
        budget_lines.append(
            f"- {budget.category.name} | limit: ${budget.limit_amount:.2f} | amount spent: ${float(spent):.2f} | period: {budget.month}/{budget.year}"
        )
    budget_context = "\n".join(budget_lines) if budget_lines else "- No budgets found"

    context = f"""You are Cashually AI, a personal spending coach built into a budget tracking app.
You have two jobs:
1. Answer questions about the user's spending and give financial advice based on their data
2. If the user says something like "spent $30 on lunch today" or "add $50 for groceries",
   extract the expense details and return a JSON object in this exact format:
   {{"action": "add_expense", "amount": 50, "description": "groceries", "category": "Food", "date": "today's date"}}
   For all other messages return: {{"action": "chat", "response": "your response here"}}

Today's date is: {today.strftime('%Y-%m-%d')} (YYYY-MM-DD). Use this for any "today", "yesterday", or date-related processing.

Here is the user's current financial data:
- Expenses this month:
{expense_context}
- Budgets:
{budget_context}

Return only valid JSON."""

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        result = model.generate_content(f"{context}\n\nUser message: {request.message}")
        raw_output = (result.text or "").strip()
    except Exception as e:
        return {"action": "chat", "response": f"Sorry, I am having trouble connecting to my AI brain. Error: {str(e)}"}

    payload = _extract_json_payload(raw_output)
    if not payload:
        return {"action": "chat", "response": raw_output or "I'm here to help you manage your money. How can I assist you today?"}

    if payload.get("action") == "add_expense":
        return {
            "action": "add_expense",
            "amount": payload.get("amount"),
            "description": payload.get("description"),
            "category": payload.get("category"),
            "date": payload.get("date"),
        }

    return {"action": "chat", "response": payload.get("response", raw_output)}
