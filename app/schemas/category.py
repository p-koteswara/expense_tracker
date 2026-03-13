from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    emoji: str = "💰"


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    is_default: bool

    class Config:
        from_attributes = True
