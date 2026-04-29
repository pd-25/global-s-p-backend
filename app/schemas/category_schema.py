from datetime import datetime
from typing import Annotated, Optional, List
from pydantic import BaseModel, BeforeValidator, Field, field_validator, ValidationError
from app.enums.enums import CategoryOrderBy, SortOrder
from fastapi import UploadFile, File, Form, HTTPException, status
import re

def validate_alphanumeric_with_spaces(value: str, field_name: str, min_len: int, max_len: int) -> str:
        """Reusable validation function"""
        if not isinstance(value, str):
            raise ValueError(f'{field_name} must be a string')
        
        value = value.strip()
        
        if not (min_len <= len(value) <= max_len):
            raise ValueError(f'{field_name} must be between {min_len} and {max_len} characters')
        
        if not re.match(r'^[a-zA-Z0-9\s.,""\'\'()]+$', value):
            raise ValueError(f'{field_name} must be alphanumeric and can contain spaces, no special characters')
        
        return value
class CategorySchema(BaseModel):
    id: int
    slug: str
    created_at: Optional[datetime] = None

#Filter validation od category list  
class CategoryFilterSchema(BaseModel):
    search_string: Optional[str] = None
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)  
    order_by_column: CategoryOrderBy = Field(default=CategoryOrderBy.id)
    sort_order: SortOrder = Field(default=SortOrder.desc)
 
 #admin list response of category   
class CategoryResponseSchema(CategorySchema):
    name: str
    description: Optional[str] = None
    image: Optional[str]
    parent_id: Optional[int] = None
    total_products: int = 0
    subcategories: List["CategoryResponseSchema"] = Field(default_factory=list, validation_alias="children")

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models



class CreateCategorySchema(BaseModel):
    name: Annotated[str, BeforeValidator(lambda v: validate_alphanumeric_with_spaces(v, 'Name', 2, 50))]
    description: Annotated[str, BeforeValidator(lambda v: validate_alphanumeric_with_spaces(v, 'Description', 5, 500))]
    image: UploadFile
    parent_id: Optional[int] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: str = Form(...),
        image: UploadFile = File(...),
        parent_id: Optional[int] = Form(None)
    ) -> "CreateCategorySchema":
        try:
            return cls(name=name, description=description, image=image, parent_id=parent_id)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Validation error",
                    "errors": [
                        {
                            "loc": error["loc"],
                            "msg": error["msg"],
                            "type": error["type"]
                        } for error in e.errors()
                    ]
                }
            )
class UpdateCategorySchema(BaseModel):
    # Fields are similar to CreateCategorySchema but image is optional for updates
    name: Annotated[str, BeforeValidator(lambda v: validate_alphanumeric_with_spaces(v, 'Name', 2, 50))]
    description: Annotated[str, BeforeValidator(lambda v: validate_alphanumeric_with_spaces(v, 'Description', 5, 500))]
    parent_id: Optional[int] = None
    image: Optional[UploadFile] = None

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: str = Form(...),
        image: Optional[UploadFile] = File(None),
        parent_id: Optional[int] = Form(None)
    ) -> "UpdateCategorySchema":
        try:
            return cls(name=name, description=description, image=image, parent_id=parent_id)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Validation error",
                    "errors": [
                        {
                            "loc": error["loc"],
                            "msg": error["msg"],
                            "type": error["type"]
                        } for error in e.errors()
                    ]
                }
            )      


# --- Category-wise Subcategories Schemas (Website) ---

class SubcategorySchema(BaseModel):
    """Lightweight schema for a subcategory."""
    id: int
    slug: str
    name: str
    image: Optional[str] = None
    total_products: int = 0

    class Config:
        from_attributes = True

class SingleSubcategorySchema(SubcategorySchema):
    description: str

class CategoryWiseSubcategoriesSchema(BaseModel):
    """A parent category with its list of subcategories."""
    id: int
    slug: str
    name: str
    image: Optional[str] = None
    total_products: int = 0
    subcategories: List[SubcategorySchema] = Field(default_factory=list, validation_alias="children")

    class Config:
        from_attributes = True

# class SingleCategoryWiseSubcategoriesSchema(CategoryWiseSubcategoriesSchema):
#     description: str
#     subcategories: List[SingleSubcategorySchema] = Field(default_factory=list, validation_alias="children")

class CategoryWiseSubcategoriesFilterSchema(BaseModel):
    limit: Optional[int] = None
    sub_cat_limit: Optional[int] = None