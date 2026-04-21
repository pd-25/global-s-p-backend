from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError
from fastapi import UploadFile, File, Form, HTTPException, status
from app.schemas.supplier_schema import SupplierResponseSchema

class ProductBasicSchema(BaseModel):
    id: int
    title: str
    slug: str
    preview_image: Optional[str] = None

    class Config:
        from_attributes = True

class ProductSupplierDataSchema(BaseModel):
    product: Optional[ProductBasicSchema] = None
    supplier: Optional[SupplierResponseSchema] = None

    class Config:
        from_attributes = True

class EnquiryFileResponseSchema(BaseModel):
    id: int| str
    file: str
    is_preview: Optional[bool] = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EnquiryResponseSchema(BaseModel):
    id: int
    reason_for_contacting: Optional[str] = None
    request_title: Optional[str] = None
    delivery_location: Optional[str] = None
    quantity: Optional[str] = None
    request_type: Optional[str] = None
    message: Optional[str] = None
    business_email: Optional[str] = None
    company_name: Optional[str] = None
    forward_to_other: Optional[bool] = False
    supplier_id: Optional[int] = None
    product_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    files: List[EnquiryFileResponseSchema] = []

    class Config:
        from_attributes = True

class EnquiryListResponseSchema(BaseModel):
    id: int
    enquiry_number: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    product_name: Optional[str] = None
    product_slug: Optional[str] = None
    product_image: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class EnquiryDetailResponseSchema(BaseModel):
    id: int
    enquiry_number: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    reason_for_contacting: Optional[str] = None
    request_title: Optional[str] = None
    delivery_location: Optional[str] = None
    quantity: Optional[str] = None
    request_type: Optional[str] = None
    message: Optional[str] = None
    business_email: Optional[str] = None
    company_name: Optional[str] = None
    forward_to_other: Optional[bool] = False
    supplier_id: Optional[int] = None
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    product_slug: Optional[str] = None
    product_image: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_slug: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class EnquiryFilterSchema(BaseModel):
    search_string: Optional[str] = None
    per_page: int = Field(default=10, ge=1, le=100)
    page: int = Field(default=1, ge=1)
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class CreateEnquirySchema(BaseModel):
    reason_for_contacting: Optional[str] = None
    request_title: Optional[str] = None
    delivery_location: Optional[str] = None
    quantity: Optional[str] = None
    request_type: Optional[str] = None
    message: Optional[str] = None
    business_email: Optional[str] = None
    company_name: Optional[str] = None
    forward_to_other: Optional[bool] = False
    supplier_id: Optional[int] = None
    supplier_type_ids: Optional[str] = None
    product_id: Optional[int] = None
    files: Optional[List[UploadFile]] = None

    @classmethod
    def as_form(
        cls,
        reason_for_contacting: Optional[str] = Form(None),
        request_title: Optional[str] = Form(None),
        delivery_location: Optional[str] = Form(None),
        quantity: Optional[str] = Form(None),
        request_type: Optional[str] = Form(None),
        message: Optional[str] = Form(None),
        business_email: Optional[str] = Form(None),
        company_name: Optional[str] = Form(None),
        forward_to_other: Optional[bool] = Form(False),
        supplier_id: Optional[int] = Form(None),
        supplier_type_ids: Optional[str] = Form(None),
        product_id: Optional[int] = Form(None),
        files: Optional[List[UploadFile]] = None,
    ) -> "CreateEnquirySchema":
        try:
            return cls(
                reason_for_contacting=reason_for_contacting,
                request_title=request_title,
                delivery_location=delivery_location,
                quantity=quantity,
                request_type=request_type,
                message=message,
                business_email=business_email,
                company_name=company_name,
                forward_to_other=forward_to_other,
                supplier_id=supplier_id,
                supplier_type_ids=supplier_type_ids,
                product_id=product_id,
                files=files,
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

class EnquiryUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    reason_for_contacting: Optional[str] = None
    request_title: Optional[str] = None
    delivery_location: Optional[str] = None
    quantity: Optional[str] = None
    request_type: Optional[str] = None
    message: Optional[str] = None
    business_email: Optional[str] = None
    company_name: Optional[str] = None
    forward_to_other: Optional[bool] = False
    supplier_id: Optional[int] = None
    product_id: Optional[int] = None
    status: Optional[str] = None
    
    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None),
        email: Optional[str] = Form(None),
        phone: Optional[str] = Form(None),
        reason_for_contacting: Optional[str] = Form(None),
        request_title: Optional[str] = Form(None),
        delivery_location: Optional[str] = Form(None),
        quantity: Optional[str] = Form(None),
        request_type: Optional[str] = Form(None),
        message: Optional[str] = Form(None),
        business_email: Optional[str] = Form(None),
        company_name: Optional[str] = Form(None),
        forward_to_other: Optional[bool] = Form(False),
        supplier_id: Optional[int] = Form(None),
        product_id: Optional[int] = Form(None),
        status: Optional[str] = Form(None),
    ) -> "EnquiryUpdateSchema":
        try:
            return cls(
                name=name,
                email=email,
                phone=phone,
                reason_for_contacting=reason_for_contacting,
                request_title=request_title,
                delivery_location=delivery_location,
                quantity=quantity,
                request_type=request_type,
                message=message,
                business_email=business_email,
                company_name=company_name,
                forward_to_other=forward_to_other,
                supplier_id=supplier_id,
                product_id=product_id,
                status=status,
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
