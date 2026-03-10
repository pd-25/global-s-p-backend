from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.supplier_schema import ValuablePartnerSchema
from app.schemas.response import APIResponse
from app.services.suppliers.supplier_service import fetch_valuable_partners

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
