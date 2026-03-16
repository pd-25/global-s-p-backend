from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError, field_validator
from fastapi import UploadFile, File, Form, HTTPException, status


# Response schema for product image
class ProductImageResponseSchema(BaseModel):
    id: int
    image: str
    is_preview: Optional[bool] = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Nested response schemas for relations
class CountryNestedSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class SupplierNestedSchema(BaseModel):
    id: int
    slug: str
    name: str

    class Config:
        from_attributes = True


class ProductTypeNestedSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class CategoryNestedSchema(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True


# Response schema for product (includes all relations)
class ProductResponseSchema(BaseModel):
    id: int
    slug: str
    title: str
    description: Optional[str] = None
    short_desc: Optional[str] = None
    currency: Optional[str] = None
    price: Optional[Decimal] = None
    price_per_measurement: Optional[str] = None
    min_order: Optional[int] = None
    country_id: Optional[int] = None
    supplier_id: Optional[int] = None
    product_type_id: Optional[int] = None
    category_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Relations
    country: Optional[CountryNestedSchema] = None
    supplier: Optional[SupplierNestedSchema] = None
    product_type: Optional[ProductTypeNestedSchema] = None
    category: Optional[CategoryNestedSchema] = None
    images: List[ProductImageResponseSchema] = []

    class Config:
        from_attributes = True


# Filter/pagination schema for admin product listing (uses FK ids)
class AdminProductFilterSchema(BaseModel):
    search_string: Optional[str] = None
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    country_id: Optional[int] = None
    supplier_id: Optional[int] = None
    product_type_id: Optional[int] = None
    category_id: Optional[int] = None


# Schema for creating a product (multipart form for multiple image uploads)
class CreateProductSchema(BaseModel):
    title: str
    description: Optional[str] = None
    short_desc: Optional[str] = None
    currency: Optional[str] = None
    price: Optional[Decimal] = None
    price_per_measurement: Optional[str] = None
    min_order: Optional[int] = None
    country_id: Optional[int] = None
    supplier_id: Optional[int] = None
    product_type_id: Optional[int] = None
    category_id: Optional[int] = None
    images: Optional[List[UploadFile]] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        v = v.strip()
        if not (2 <= len(v) <= 255):
            raise ValueError('Product title must be between 2 and 255 characters')
        return v

    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError('Price must be a positive number')
        return v

    @field_validator('min_order')
    @classmethod
    def validate_min_order(cls, v):
        if v is not None and v < 1:
            raise ValueError('Minimum order must be at least 1')
        return v

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: Optional[str] = Form(None),
        short_desc: Optional[str] = Form(None),
        currency: Optional[str] = Form(None),
        price: Optional[Decimal] = Form(None),
        price_per_measurement: Optional[str] = Form(None),
        min_order: Optional[int] = Form(None),
        country_id: Optional[int] = Form(None),
        supplier_id: Optional[int] = Form(None),
        product_type_id: Optional[int] = Form(None),
        category_id: Optional[int] = Form(None),
        images: Optional[List[UploadFile]] = File(None),
    ) -> "CreateProductSchema":
        try:
            return cls(
                title=title,
                description=description,
                short_desc=short_desc,
                currency=currency,
                price=price,
                price_per_measurement=price_per_measurement,
                min_order=min_order,
                country_id=country_id,
                supplier_id=supplier_id,
                product_type_id=product_type_id,
                category_id=category_id,
                images=images,
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Validation error",
                    "errors": [
                        {
                            "loc": error["loc"],
                            "msg": error["msg"],
                            "type": error["type"],
                        }
                        for error in e.errors()
                    ],
                },
            )


# Schema for updating a product
class UpdateProductSchema(CreateProductSchema):
    pass



class RecommendedProductImageSchema(BaseModel):
    image: str

    class Config:
        from_attributes = True


class RecommendedProductCountrySchema(BaseModel):
    country_flag: str

    class Config:
        from_attributes = True
class ProductListSupplierSchema(BaseModel):
    name: str
    class Config:
        from_attributes = True


class RecommendedProductSchema(BaseModel):
    """Lightweight product schema for website — only title, primary image, and country flag."""
    id: int
    slug: str
    title: str
    primary_image: Optional[RecommendedProductImageSchema] = None
    country: Optional[RecommendedProductCountrySchema] = None

    class Config:
        from_attributes = True
        
class ProductListingSchema(RecommendedProductSchema):
    supplier: Optional[ProductListSupplierSchema] = None

class ProductFilterSchema(BaseModel):
    search_string: Optional[str] = None
    per_page: int = Field(default=30, ge=1, le=100)
    page: int = Field(default=1, ge=1)
    country_code: Optional[str] = None          # ISO country code, e.g. "BD", "US"
    supplier_type_slug: Optional[str] = None    # slug-style, e.g. "raw-material"
    supplier_slug: Optional[str] = None    # slug-style, e.g. "raw-material"
    min_price: Optional[int] = None    # slug-style, e.g. "raw-material"
    max_price: Optional[int] = None    # slug-style, e.g. "raw-material"


