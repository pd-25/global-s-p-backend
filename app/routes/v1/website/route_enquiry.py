from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.response import APIResponse
from app.schemas.enquiry_schema import CreateEnquirySchema, EnquiryResponseSchema
from app.services.enquiries.enquiry_service import create_enquiry_service

enquiry_router = APIRouter()


@enquiry_router.post(
    "/create",
    response_model=APIResponse[EnquiryResponseSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new enquiry",
    description="Create a new enquiry with optional attachments. Payload should be sent as multipart/form-data to support file uploads."
)
def create_enquiry(enquiry_data: CreateEnquirySchema = Depends(CreateEnquirySchema.as_form), db: Session = Depends(get_db)):
    try:
        new_enquiry = create_enquiry_service(enquiry_data=enquiry_data, db=db)
        return APIResponse(
            success=True,
            message="Enquiry created successfully.",
            data=new_enquiry
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating the response for creation."
        )
