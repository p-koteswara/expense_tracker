from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine
from app.api.routes import expenses, auth, categories, budgets

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(
    expenses.router,
    prefix="/expenses",
    tags=["Expenses"],
)

app.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categories"],
)

app.include_router(
    budgets.router,
    prefix="/budgets",
    tags=["Budgets"],
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"],
)


@app.get("/")
def root():
    return {"message": "API running"}