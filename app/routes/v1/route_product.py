from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.admin import Admin
from app.schemas.product_schema import (
    ProductFilterSchema,
    ProductResponseSchema,
    CreateProductSchema,
    UpdateProductSchema,
)
from app.schemas.response import APIResponse
from app.services.auth.auth_service import get_current_user
from app.services.products.product_service import (
    create_product_service,
    delete_product_service,
    delete_product_image_service,
    retrieve_all_products,
    retrieve_single_product,
    update_product_service,
)
from app.utils.file_utils import validate_image_file

product_router = APIRouter()


@product_router.get(
    "/",
    response_model=APIResponse[List[ProductResponseSchema]],
    status_code=status.HTTP_200_OK,
    description="Returns a paginated list of products with all relations (country, supplier, product_type, category, images)",
)
def get_products(
    filters: ProductFilterSchema = Depends(),
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    products, total_count = retrieve_all_products(filters=filters, db=db)

    return APIResponse(
        success=True,
        message="Products fetched successfully",
        data=products,
        meta={
            "count": len(products),
            "total": total_count,
            "page": filters.page,
            "per_page": filters.per_page,
        },
    )


@product_router.get(
    "/{slug}",
    response_model=APIResponse[ProductResponseSchema],
    status_code=status.HTTP_200_OK,
    description="Returns a single product with all its relations by slug",
)
def get_product(
    slug: str,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    product = retrieve_single_product(slug=slug, db=db)

    return APIResponse(
        success=True,
        message="Product fetched successfully",
        data=product,
    )


@product_router.post(
    "/",
    response_model=APIResponse[ProductResponseSchema],
    status_code=status.HTTP_201_CREATED,
    description="Creates a new product with multiple image uploads",
)
async def create_product(
    current_user: Admin = Depends(get_current_user),
    product_data: CreateProductSchema = Depends(CreateProductSchema.as_form),
    db: Session = Depends(get_db),
):
    # Validate each uploaded image
    if product_data.images:
        for image in product_data.images:
            validate_image_file(image)

    response = create_product_service(product_data=product_data, db=db)

    return APIResponse(
        success=True,
        message="Product created successfully",
        data=response,
    )


@product_router.put(
    "/{slug}",
    response_model=APIResponse[ProductResponseSchema],
    status_code=status.HTTP_200_OK,
    description="Updates a product by slug. New images are added alongside existing ones.",
)
async def update_product(
    slug: str,
    current_user: Admin = Depends(get_current_user),
    product_data: UpdateProductSchema = Depends(UpdateProductSchema.as_form),
    db: Session = Depends(get_db),
):
    # Validate each uploaded image
    if product_data.images:
        for image in product_data.images:
            validate_image_file(image)

    response = update_product_service(
        slug=slug, product_data=product_data, db=db
    )

    return APIResponse(
        success=True,
        message="Product updated successfully",
        data=response,
    )


@product_router.delete(
    "/{slug}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    description="Soft-deletes a product by its slug",
)
def delete_product(
    slug: str,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    delete_product_service(slug=slug, db=db)

    return APIResponse(
        success=True,
        message="Product deleted successfully",
    )


@product_router.delete(
    "/image/{image_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    description="Deletes a single product image by its ID",
)
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    delete_product_image_service(image_id=image_id, db=db)

    return APIResponse(
        success=True,
        message="Product image deleted successfully",
    )