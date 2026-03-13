from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import engine
from app.api.routes import expenses, auth, categories, budgets

app = FastAPI(title="Cashually API", description="Personal expense tracker backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://cashually.vercel.app"
    ]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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