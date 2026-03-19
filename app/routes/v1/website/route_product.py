from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.product_schema import ProductDetailsResponse, ProductFilterSchema, ProductListingSchema, RecommendedProductSchema, ProductResponseSchema
from app.schemas.response import APIResponse
from app.services.products.product_service import fetch_recomended_products, fetch_website_products, retrieve_single_product

product_router = APIRouter()


@product_router.get(
    '/recomended-products',
    response_model=APIResponse[List[RecommendedProductSchema]],
    status_code=status.HTTP_200_OK,
    description="This api will list all the recommended products"
)
def get_recomended_products(db: Session = Depends(get_db)):
    recomended_products = fetch_recomended_products(db=db)
    return APIResponse(
        success=True,
        message="Recommended Products Fetched Successfully",
        data=recomended_products,
        meta={},
    )

@product_router.get(
    '/',
    response_model=APIResponse[List[ProductListingSchema]],
    status_code=status.HTTP_200_OK,
    description="Public product listing page — supports search, country & supplier-type filtering, and pagination",
)
def get_products(filters: ProductFilterSchema = Depends(), db: Session = Depends(get_db)):
    products, total_count, total_pages = fetch_website_products(filters=filters, db=db)
    return APIResponse(
        success=True,
        message="Products Fetched Successfully",
        data=products,
        meta={
            "page": filters.page,
            "per_page": filters.per_page,
            "total_count": total_count,
            "total_pages": total_pages,
        },
    )
    
@product_router.get(
    '/product/{slug}',
    response_model=APIResponse[ProductDetailsResponse],
    status_code=status.HTTP_200_OK,
    description="Fetch single product details by slug",
)
def get_product_detail(slug: str, db: Session = Depends(get_db)):
    product = retrieve_single_product(slug=slug, db=db)
    return APIResponse(
        success=True,
        message="Product details fetched successfully",
        data=product,
    )


@product_router.get(
    '/{category_slug}',
    response_model=APIResponse[List[ProductListingSchema]],
    status_code=status.HTTP_200_OK,
    description="Public product listing page — supports search, country & supplier-type filtering, and pagination",
)
def get_products(category_slug: str, filters: ProductFilterSchema = Depends(), db: Session = Depends(get_db)):
    products, total_count, total_pages = fetch_website_products(filters=filters, db=db, category_slug=category_slug)
    return APIResponse(
        success=True,
        message="Products Fetched Successfully",
        data=products,
        meta={
            "page": filters.page,
            "per_page": filters.per_page,
            "total_count": total_count,
            "total_pages": total_pages,
        },
    )
