from fastapi import FastAPI
from app.db.session import engine
from app.db.models import Base
from app.api.routes import expenses

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(
    expenses.router,
    prefix="/expenses",
    tags=["Expenses"]
)


@app.get("/")
def root():
    return {"message": "API running"}