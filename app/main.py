import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.db.base import Base
from app.db import models  # Ensure model metadata is registered before create_all.
from app.db.session import engine, SessionLocal
from app.api.routes import expenses, auth, categories, budgets
from app.routers import chat

app = FastAPI(title="Cashually API", description="Personal expense tracker backend")
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://cashually.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def log_runtime_persistence_state() -> None:
    """Temporary diagnostics for DB target and user-table persistence."""
    db = SessionLocal()
    try:
        users_table_exists = inspect(engine).has_table("users")
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar() if users_table_exists else 0
        logger.info(
            "Startup DB check: url=%s users_table_exists=%s users_count=%s",
            engine.url.render_as_string(hide_password=True),
            users_table_exists,
            user_count,
        )
    finally:
        db.close()

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

app.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
)


@app.get("/")
def root():
    return {"message": "API running"}