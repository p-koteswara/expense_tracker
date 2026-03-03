from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse
from app.core.jwt import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    List all categories that currently exist in the database.
    This endpoint no longer auto‑seeds default categories; it simply
    returns whatever categories have been created so far.
    """
    categories = db.query(Category).all()
    return categories


@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = Category(
        name=category.name,
        is_default=False,
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category

