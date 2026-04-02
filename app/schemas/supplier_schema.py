from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ValidationError, field_validator
from fastapi import UploadFile, File, Form, HTTPException, status
from app.schemas.supplier_type_schema import SupplierTypeResponseSchema
from app.schemas.country_schema import CountryNestedSchema
import re


# Response schema for supplier
class SupplierResponseSchema(BaseModel):
    id: int
    slug: str
    name: str
    about: Optional[str] = None
    logo: Optional[str] = None
    zipcode: Optional[str] = None
    city: Optional[str] = None
    country_id: Optional[int] = None
    address: Optional[str] = None
    delivery_area: Optional[str] = None
    founded_year: Optional[int] = None
    employee_strength: Optional[str] = None
    supplier_type_id: Optional[int] = None
    is_verified: Optional[bool] = False
    vat_number: Optional[str] = None
    company_site: Optional[str] = None
    company_phone_number: Optional[str] = None
    company_email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    supplier_type: Optional[SupplierTypeResponseSchema] = None
    country: Optional[CountryNestedSchema] = None

    class Config:
        from_attributes = True


# Filter/pagination schema for listing suppliers
class SupplierFilterSchema(BaseModel):
    search_string: Optional[str] = None
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    country_id: Optional[int] = None
    supplier_type_id: Optional[int] = None
    is_verified: Optional[bool] = None


# Schema for creating a supplier (multipart form data because of logo upload)
class CreateSupplierSchema(BaseModel):
    name: str
    about: Optional[str] = None
    logo: Optional[UploadFile] = None
    zipcode: Optional[str] = None
    city: Optional[str] = None
    country_id: Optional[int] = None
    address: Optional[str] = None
    address_two: Optional[str] = None
    business_sector: Optional[str] = None
    delivery_area: Optional[str] = None
    founded_year: Optional[int] = None
    employee_strength: Optional[str] = None
    supplier_type_id: Optional[int] = None
    is_verified: Optional[bool] = False
    vat_number: Optional[str] = None
    company_site: Optional[str] = None
    company_phone_number: Optional[str] = None
    company_email: Optional[str] = None
    is_accept_terms: bool

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        v = v.strip()
        if not (2 <= len(v) <= 255):
            raise ValueError('Supplier name must be between 2 and 255 characters')
        return v

    @field_validator('company_email')
    @classmethod
    def validate_email(cls, v):
        if v is not None and v.strip():
            v = v.strip()
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', v):
                raise ValueError('Invalid email format')
        return v

    @field_validator('founded_year')
    @classmethod
    def validate_founded_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if not (1800 <= v <= current_year):
                raise ValueError(f'Founded year must be between 1800 and {current_year}')
        return v

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        about: Optional[str] = Form(None),
        logo: Optional[UploadFile] = File(None),
        zipcode: Optional[str] = Form(None),
        city: Optional[str] = Form(None),
        country_id: Optional[int] = Form(None),
        address: Optional[str] = Form(None),
        address_two: Optional[str] = Form(None),
        business_sector: Optional[str] = Form(None),
        delivery_area: Optional[str] = Form(None),
        founded_year: Optional[int] = Form(None),
        employee_strength: Optional[str] = Form(None),
        supplier_type_id: Optional[int] = Form(None),
        is_verified: Optional[bool] = Form(False),
        vat_number: Optional[str] = Form(None),
        company_site: Optional[str] = Form(None),
        company_phone_number: Optional[str] = Form(None),
        company_email: Optional[str] = Form(None),
        is_accept_terms: bool = Form(...)
    ) -> "CreateSupplierSchema":
        try:
            return cls(
                name=name,
                about=about,
                logo=logo,
                zipcode=zipcode,
                city=city,
                country_id=country_id,
                address=address,
                address_two=address_two,
                business_sector=business_sector,
                delivery_area=delivery_area,
                founded_year=founded_year,
                employee_strength=employee_strength,
                supplier_type_id=supplier_type_id,
                is_verified=is_verified,
                vat_number=vat_number,
                company_site=company_site,
                company_phone_number=company_phone_number,
                company_email=company_email,
                is_accept_terms=is_accept_terms
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


# Schema for updating a supplier
class UpdateSupplierSchema(CreateSupplierSchema):
    pass


# --- Website Schemas ---

class ValuablePartnerSchema(BaseModel):
    """Lightweight schema for valuable partners — only name and logo."""
    id: int
    slug: str
    name: str
    logo: Optional[str] = None

    class Config:
        from_attributes = True
