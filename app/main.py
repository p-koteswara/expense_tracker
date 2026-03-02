from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.api.routes import expenses, auth

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(
    expenses.router,
    prefix="/expenses",
    tags=["Expenses"]
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Auth"]
)

@app.get("/")
def root():
    return {"message": "API running"}