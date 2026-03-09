from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.admin import Admin
from app.schemas.supplier_type_schema import (
    SupplierTypeFilterSchema,
    SupplierTypeResponseSchema,
    CreateSupplierTypeSchema,
    UpdateSupplierTypeSchema,
)
from app.schemas.response import APIResponse
from app.services.auth.auth_service import get_current_user
from app.services.supplier_types.supplier_type_service import (
    create_supplier_type_service,
    delete_supplier_type_service,
    retrieve_all_supplier_types,
    retrieve_single_supplier_type,
    update_supplier_type_service,
)

supplier_type_router = APIRouter()


@supplier_type_router.get(
    "/",
    response_model=APIResponse[List[SupplierTypeResponseSchema]],
    status_code=status.HTTP_200_OK,
    description="Returns a paginated list of supplier types with optional search",
)
def get_supplier_types(
    filters: SupplierTypeFilterSchema = Depends(),
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    supplier_types, total_count = retrieve_all_supplier_types(filters=filters, db=db)

    return APIResponse(
        success=True,
        message="Supplier types fetched successfully",
        data=supplier_types,
        meta={
            "count": len(supplier_types),
            "total": total_count,
            "page": filters.page,
            "per_page": filters.per_page,
        },
    )


@supplier_type_router.get(
    "/{supplier_type_id}",
    response_model=APIResponse[SupplierTypeResponseSchema],
    status_code=status.HTTP_200_OK,
    description="Returns a single supplier type by its ID",
)
def get_supplier_type(
    supplier_type_id: int,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    supplier_type = retrieve_single_supplier_type(
        supplier_type_id=supplier_type_id, db=db
    )

    return APIResponse(
        success=True,
        message="Supplier type fetched successfully",
        data=supplier_type,
    )


@supplier_type_router.post(
    "/",
    response_model=APIResponse[SupplierTypeResponseSchema],
    status_code=status.HTTP_201_CREATED,
    description="Creates a new supplier type",
)
def create_supplier_type(
    supplier_type_data: CreateSupplierTypeSchema,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    response = create_supplier_type_service(
        supplier_type_data=supplier_type_data, db=db
    )

    return APIResponse(
        success=True,
        message="Supplier type created successfully",
        data=response,
    )


@supplier_type_router.put(
    "/{supplier_type_id}",
    response_model=APIResponse[SupplierTypeResponseSchema],
    status_code=status.HTTP_200_OK,
    description="Updates an existing supplier type by its ID",
)
def update_supplier_type(
    supplier_type_id: int,
    supplier_type_data: UpdateSupplierTypeSchema,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    response = update_supplier_type_service(
        supplier_type_id=supplier_type_id,
        supplier_type_data=supplier_type_data,
        db=db,
    )

    return APIResponse(
        success=True,
        message="Supplier type updated successfully",
        data=response,
    )


@supplier_type_router.delete(
    "/{supplier_type_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    description="Soft-deletes a supplier type by its ID",
)
def delete_supplier_type(
    supplier_type_id: int,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    delete_supplier_type_service(supplier_type_id=supplier_type_id, db=db)

    return APIResponse(
        success=True,
        message="Supplier type deleted successfully",
    )
