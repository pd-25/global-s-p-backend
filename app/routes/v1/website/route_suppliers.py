from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.supplier_schema import CreateSupplierSchema, SupplierResponseSchema, ValuablePartnerSchema
from app.schemas.response import APIResponse
from app.services.suppliers.supplier_service import create_supplier_service, fetch_valuable_partners
from app.utils.file_utils import validate_image_file
supplier_router = APIRouter()



@supplier_router.get(
    '/valuable-partners',
    response_model=APIResponse[List[ValuablePartnerSchema]],
    status_code=status.HTTP_200_OK,
    description="This api will list all the valuable partners"
)
def get_valuable_partners(db: Session = Depends(get_db)):
    valuable_partners = fetch_valuable_partners(db=db)
    return APIResponse(
        success=True,
        message="Valuable Partners Fetched Successfully",
        data=valuable_partners,
        meta={},
    )


#create new supplier from frontend
@supplier_router.post(
    '/create',
    response_model=APIResponse[SupplierResponseSchema],
    status_code=status.HTTP_200_OK,
    description="This api will create a new supplier"
)
def create_supplier(supplier_data: CreateSupplierSchema = Depends(CreateSupplierSchema.as_form), db: Session = Depends(get_db)):
    if supplier_data.logo:
        validate_image_file(supplier_data.logo)

    response = create_supplier_service(supplier_data=supplier_data, db=db)

    return APIResponse(
        success=True,
        message="Supplier created successfully",
        data=response,
    )

