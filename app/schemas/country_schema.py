from datetime import datetime
from typing import Optional
from fastapi import UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel, Field, ValidationError, field_validator
import re


# Response schema for country
class CountryResponseSchema(BaseModel):
    id: int
    name: str
    country_flag: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Filter/pagination schema for listing countries
class CountryFilterSchema(BaseModel):
    search_string: Optional[str] = None
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


# Schema for creating a country
class CreateCountrySchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    country_flag: Optional[UploadFile] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        v = v.strip()
        if not re.match(r'^[a-zA-Z\s]+$', v):
            raise ValueError('Country name must contain only letters and spaces')
        if not (2 <= len(v) <= 255):
            raise ValueError('Country name must be between 2 and 255 characters')
        return v

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        country_flag: Optional[UploadFile] = File(None),
    ) -> "CreateCountrySchema":
        try:
            return cls(name=name, country_flag=country_flag)
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


# Schema for updating a country
class UpdateCountrySchema(CreateCountrySchema):
    pass
