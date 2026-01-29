
from datetime import datetime
from typing import Optional
from pydantic import BaseModel



class CategoryBase(BaseModel):
    id: int
    slug: str
    created_at: Optional[datetime] = None
    

class CategoryResponseSchema(CategoryBase):
    name: str
    image: Optional[str]

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models