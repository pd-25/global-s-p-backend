from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


# Response schema for supplier type
class SupplierTypeResponseSchema(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Filter/pagination schema for listing supplier types
class SupplierTypeFilterSchema(BaseModel):
    search_string: Optional[str] = None
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


# Schema for creating a supplier type
class CreateSupplierTypeSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9\s]+$', v):
            raise ValueError('Supplier type name must be alphanumeric and can contain spaces')
        if not (2 <= len(v) <= 255):
            raise ValueError('Supplier type name must be between 2 and 255 characters')
        return v


# Schema for updating a supplier type
class UpdateSupplierTypeSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9\s]+$', v):
            raise ValueError('Supplier type name must be alphanumeric and can contain spaces')
        if not (2 <= len(v) <= 255):
            raise ValueError('Supplier type name must be between 2 and 255 characters')
        return v
