from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.supplier_type_schema import (
    SupplierTypeResponseSchema,
)
from app.schemas.response import APIResponse
from app.services.supplier_types.supplier_type_service import (
    fetch_website_supplier_types
)

supplier_type_router = APIRouter()


@supplier_type_router.get(
    "/",
    response_model=APIResponse[List[SupplierTypeResponseSchema]],
    status_code=status.HTTP_200_OK,
    description="Returns a list of all supplier types",
)
def get_supplier_types(
    db: Session = Depends(get_db)
):
    supplier_types= fetch_website_supplier_types(db=db)

    return APIResponse(
        success=True,
        message="Supplier types fetched successfully",
        data=supplier_types,
        meta={},
    )
