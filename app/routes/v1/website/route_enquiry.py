from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.response import APIResponse
from app.schemas.enquiry_schema import CreateEnquirySchema, EnquiryResponseSchema, ProductSupplierDataSchema
from app.services.enquiries.enquiry_service import create_enquiry_service, fetch_product_supplier_data_service

enquiry_router = APIRouter()


@enquiry_router.get(
    "/fetch-product-supplier-data",
    response_model=APIResponse[ProductSupplierDataSchema],
    status_code=status.HTTP_200_OK,
    summary="Fetch product and supplier data",
    description="Fetch product and supplier data for enquiry form based on slug and type (product or supplier)."
)
def fetch_product_supplier_data(
    slug: str,
    req_type: str,
    db: Session = Depends(get_db)
):
    try:
        product_supplier_data = fetch_product_supplier_data_service(db=db, slug=slug, req_type=req_type)
        return APIResponse(
            success=True,
            message="Product and supplier data fetched successfully.",
            data=product_supplier_data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating the response for fetching product and supplier data."
        )


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
