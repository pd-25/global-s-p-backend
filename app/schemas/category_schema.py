from datetime import datetime
from typing import Annotated, Optional
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
        
        if not re.match(r'^[a-zA-Z0-9\s]+$', value):
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
    image: Optional[str]

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models


# class CreateCategorySchema(BaseModel):
    # name: str
    # description: str
    # image: UploadFile
    
    # def validate_alphanumeric_with_spaces(value: str, field_name: str, min_len: int, max_len: int) -> str:
    #     """Reusable validation function"""
    #     if not isinstance(value, str):
    #         raise ValueError(f'{field_name} must be a string')
        
    #     value = value.strip()
        
    #     if not (min_len <= len(value) <= max_len):
    #         raise ValueError(f'{field_name} must be between {min_len} and {max_len} characters')
        
    #     if not re.match(r'^[a-zA-Z0-9\s]+$', value):
    #         raise ValueError(f'{field_name} must be alphanumeric and can contain spaces, no special characters')
        
    #     return value

    # @classmethod
    # def as_form(
    #     cls,
    #     name: str = Form(...),
    #     description: str = Form(...),
    #     image: UploadFile = File(...)
    # ) -> "CreateCategorySchema":
    #     try:
    #         return cls(name=name, description=description, image=image)
    #     except ValidationError as e:
    #         raise HTTPException(
    #             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #             detail=e.errors()
    #         )

    # @field_validator('name')
    # @classmethod
    # def validate_name(cls, v):
    #     if not re.match(r'^[a-zA-Z0-9\s]+$', v):
    #         raise ValueError('Name must be alphanumeric and can contain spaces, no special characters')
    #     if not (2 <= len(v) <= 50):
    #         raise ValueError('Name must be between 2 and 50 characters')
    #     return v

    # @field_validator('description')
    # def validate_description(cls, v):
    #     if not re.match(r'^[a-zA-Z0-9\s]+$', v):
    #         raise ValueError('Description must be alphanumeric and can contain spaces, no special characters')
    #     if not (5 <= len(v) <= 500):
    #         raise ValueError('Description must be between 5 and 500 characters')
    #     return v

    # @field_validator('image')
    # def validate_image(cls, v: UploadFile):
    #     # 2 MB = 2 * 1024 * 1024 bytes
    #     # Note: UploadFile might not always have 'size' populated depending on the backend, 
    #     # but usually we can check. However, checking size without reading chunks might be tricky 
    #     # if the spool fits in memory. 
    #     # A common way is to check content-length header or read.
    #     # For simplicity in Pydantic validator, we might check file.size if available (Starlette/FastAPI)
    #     # But 'size' attribute isn't standard on UploadFile object without spooled file.
    #     # We'll try to check the request header content-length roughly if needed, 
    #     # but typically file validation logic is better done by reading.
    #     # Let's rely on checking the file.size or seeking.
        
    #     MAX_SIZE = 2 * 1024 * 1024
        
    #     # We can check the file's size by moving cursor to end
    #     v.file.seek(0, 2)
    #     file_size = v.file.tell()
    #     v.file.seek(0)  # reset cursor

    #     if file_size > MAX_SIZE:
    #          raise ValueError('Image size must be less than 2MB')
        
    #     return v


class CreateCategorySchema(BaseModel):
    name: Annotated[str, BeforeValidator(lambda v: validate_alphanumeric_with_spaces(v, 'Name', 2, 50))]
    description: Annotated[str, BeforeValidator(lambda v: validate_alphanumeric_with_spaces(v, 'Description', 5, 500))]
    image: UploadFile

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: str = Form(...),
        image: UploadFile = File(...)
    ) -> "CreateCategorySchema":
        try:
            return cls(name=name, description=description, image=image)
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
class UpdateCategorySchema(CreateCategorySchema):
    pass      
