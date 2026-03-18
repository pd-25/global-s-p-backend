from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ValidationError
from fastapi import UploadFile, File, Form, HTTPException, status

class EnquiryFileResponseSchema(BaseModel):
    id: int
    file: str
    is_preview: Optional[bool] = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EnquiryResponseSchema(BaseModel):
    id: int
    reason_for_contacting: str
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

class CreateEnquirySchema(BaseModel):
    reason_for_contacting: str
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
    files: Optional[List[UploadFile]] = None

    @classmethod
    def as_form(
        cls,
        reason_for_contacting: str = Form(...),
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
