from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.admin import Admin
from app.schemas.product_type_schema import (
    ProductTypeFilterSchema,
    ProductTypeResponseSchema,
    CreateProductTypeSchema,
    UpdateProductTypeSchema,
)
from app.schemas.response import APIResponse
from app.services.auth.auth_service import get_current_user
from app.services.product_types.product_type_service import (
    create_product_type_service,
    delete_product_type_service,
    retrieve_all_product_types,
    retrieve_single_product_type,
    update_product_type_service,
)

product_type_router = APIRouter()


@product_type_router.get(
    "/",
    response_model=APIResponse[List[ProductTypeResponseSchema]],
    status_code=status.HTTP_200_OK,
    description="Returns a paginated list of product types with optional search",
)
def get_product_types(
    filters: ProductTypeFilterSchema = Depends(),
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    product_types, total_count = retrieve_all_product_types(filters=filters, db=db)

    return APIResponse(
        success=True,
        message="Product types fetched successfully",
        data=product_types,
        meta={
            "count": len(product_types),
            "total": total_count,
            "page": filters.page,
            "per_page": filters.per_page,
        },
    )


@product_type_router.get(
    "/{product_type_id}",
    response_model=APIResponse[ProductTypeResponseSchema],
    status_code=status.HTTP_200_OK,
    description="Returns a single product type by its ID",
)
def get_product_type(
    product_type_id: int,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    product_type = retrieve_single_product_type(
        product_type_id=product_type_id, db=db
    )

    return APIResponse(
        success=True,
        message="Product type fetched successfully",
        data=product_type,
    )


@product_type_router.post(
    "/",
    response_model=APIResponse[ProductTypeResponseSchema],
    status_code=status.HTTP_201_CREATED,
    description="Creates a new product type",
)
def create_product_type(
    product_type_data: CreateProductTypeSchema,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    response = create_product_type_service(
        product_type_data=product_type_data, db=db
    )

    return APIResponse(
        success=True,
        message="Product type created successfully",
        data=response,
    )


@product_type_router.put(
    "/{product_type_id}",
    response_model=APIResponse[ProductTypeResponseSchema],
    status_code=status.HTTP_200_OK,
    description="Updates an existing product type by its ID",
)
def update_product_type(
    product_type_id: int,
    product_type_data: UpdateProductTypeSchema,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    response = update_product_type_service(
        product_type_id=product_type_id,
        product_type_data=product_type_data,
        db=db,
    )

    return APIResponse(
        success=True,
        message="Product type updated successfully",
        data=response,
    )


@product_type_router.delete(
    "/{product_type_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    description="Soft-deletes a product type by its ID",
)
def delete_product_type(
    product_type_id: int,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    delete_product_type_service(product_type_id=product_type_id, db=db)

    return APIResponse(
        success=True,
        message="Product type deleted successfully",
    )
