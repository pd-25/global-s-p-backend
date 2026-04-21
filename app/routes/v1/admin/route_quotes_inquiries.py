from app.services.enquiries.enquiry_service import update_enquiry_by_enquiry_number
from fastapi import Body
from app.schemas.enquiry_schema import EnquiryUpdateSchema
from app.enums.enums import EnquiryType
from typing import List
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.enquiry_schema import EnquiryListResponseSchema, EnquiryFilterSchema, EnquiryDetailResponseSchema
from app.schemas.response import APIResponse
from app.services.enquiries.enquiry_service import retrieve_all_enquiries, retrieve_enquiry_by_enquiry_number


quotes_inquiries_router = APIRouter()


@quotes_inquiries_router.get(
    "/inquiries",
    response_model=APIResponse[List[EnquiryListResponseSchema]],
    status_code=status.HTTP_200_OK,
    description="Returns a paginated list of inquiries (is_quote_form=False)",
)
def get_inquiries(
    filters: EnquiryFilterSchema = Depends(),
    db: Session = Depends(get_db),
):
    inquiries, total_count = retrieve_all_enquiries(filters=filters, db=db, is_quote_form=False)

    return APIResponse(
        success=True,
        message="Inquiries fetched successfully",
        data=inquiries,
        meta={
            "count": len(inquiries),
            "total": total_count,
            "page": filters.page,
            "per_page": filters.per_page,
        },
    )


@quotes_inquiries_router.get(
    "/quotes",
    response_model=APIResponse[List[EnquiryListResponseSchema]],
    status_code=status.HTTP_200_OK,
    description="Returns a paginated list of quotes (is_quote_form=True)",
)
def get_quotes(
    filters: EnquiryFilterSchema = Depends(),
    db: Session = Depends(get_db),
):
    quotes, total_count = retrieve_all_enquiries(filters=filters, db=db, is_quote_form=True)

    return APIResponse(
        success=True,
        message="Quotes fetched successfully",
        data=quotes,
        meta={
            "count": len(quotes),
            "total": total_count,
            "page": filters.page,
            "per_page": filters.per_page,
        },
    )




@quotes_inquiries_router.get(
    "/{enquiry_number}/{enquiry_type}",
    response_model=APIResponse[EnquiryDetailResponseSchema],
    status_code=status.HTTP_200_OK,
    description="Returns a single enquiry details by enquiry_number. Supports joining if enquiry_type='inquiry'",
)
def get_enquiry_by_enquiry_number(
    enquiry_number: str = Path(..., description="The unique enquiry number"),
    enquiry_type: EnquiryType = Path(..., description="Either 'inquiry' or 'quote' to dictate lookup strategy"),
    db: Session = Depends(get_db),
):
    enquiry = retrieve_enquiry_by_enquiry_number(enquiry_number=enquiry_number, enquiry_type=enquiry_type.value, db=db)
    return APIResponse(
        success=True,
        message="Enquiry fetched successfully",
        data=enquiry,
    )


@quotes_inquiries_router.patch(
    "/{enquiry_number}",
    response_model=APIResponse[EnquiryDetailResponseSchema],
    status_code=status.HTTP_200_OK,
    description="Updates an enquiry by enquiry_number",
)
def update_enquiry(
    enquiry_number: str = Path(..., description="The unique enquiry number"),
    enquiry_update: EnquiryUpdateSchema = Body(..., description="The enquiry update payload"),
    db: Session = Depends(get_db),
):
    enquiry = update_enquiry_by_enquiry_number(enquiry_number=enquiry_number, enquiry_update_schema=enquiry_update, db=db)
    return APIResponse(
        success=True,
        message="Enquiry updated successfully",
        data=enquiry,
    )