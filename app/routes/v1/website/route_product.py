from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.product_schema import (
    ProductDetailsResponse,
    ProductFilterSchema,
    ProductListingSchema,
    ProductResponseSchema,
    RecommendedProductSchema,
    ProductBySupplierSchema,
    SupplierProductsFilterSchema,
    TrendingProductSchema,
    SimilarProductSchema,
    SimilarProductsFilterSchema,
    TrendingProductsFilterSchema,
)
from app.schemas.response import APIResponse
from app.services.products.product_service import (
    fetch_recomended_products,
    fetch_website_products,
    fetch_products_by_supplier,
    retrieve_single_product,
    fetch_trending_products,
    fetch_similar_products,
)

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
    '/trending-products',
    response_model=APIResponse[List[TrendingProductSchema]],
    status_code=status.HTTP_200_OK,
    description="Fetch paginated trending products list with filters",
)
def get_trending_products(
    filters: TrendingProductsFilterSchema = Depends(),
    db: Session = Depends(get_db),
):
    trending_products, total_count, total_pages = fetch_trending_products(
        db=db, 
        filters=filters
    )
    return APIResponse(
        success=True,
        message="Trending products fetched successfully",
        data=trending_products,
        meta={
            "page": filters.page,
            "per_page": filters.perPage,
            "total_count": total_count,
            "total_pages": total_pages,
        },
    )


@product_router.get(
    '/similer-products',
    response_model=APIResponse[List[SimilarProductSchema]],
    status_code=status.HTTP_200_OK,
    description="Fetch paginated random similar products list",
)
def get_similar_products(
    filters: SimilarProductsFilterSchema = Depends(),
    db: Session = Depends(get_db),
):
    products, total_count, total_pages = fetch_similar_products(
        page=filters.page,
        per_page=filters.perPage,
        db=db,
    )
    return APIResponse(
        success=True,
        message="Similar products fetched successfully",
        data=products,
        meta={
            "page": filters.page,
            "per_page": filters.perPage,
            "total_count": total_count,
            "total_pages": total_pages,
        },
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
    '/products-by-supplier/{supplier_slug}',
    response_model=APIResponse[List[ProductBySupplierSchema]],
    status_code=status.HTTP_200_OK,
    description="Fetch paginated product cards for a specific supplier by their slug",
)
def get_products_by_supplier(
    supplier_slug: str,
    filters: SupplierProductsFilterSchema = Depends(),
    db: Session = Depends(get_db),
):
    products, total_count, total_pages = fetch_products_by_supplier(
        supplier_slug=supplier_slug,
        page=filters.page,
        per_page=filters.per_page,
        db=db,
    )
    return APIResponse(
        success=True,
        message="Products fetched successfully",
        data=products,
        meta={
            "page": filters.page,
            "per_page": filters.per_page,
            "total_count": total_count,
            "total_pages": total_pages,
        },
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
