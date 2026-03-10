
from fastapi import APIRouter

from app.routes.v1.website.route_product import product_router
from app.routes.v1.website.route_category import category_router
from app.routes.v1.website.route_suppliers import supplier_router

website_router = APIRouter()

website_router.include_router(product_router, prefix="/products", tags=["Website - Products"])
website_router.include_router(category_router, prefix="/categories", tags=["Website - Categories"])
website_router.include_router(supplier_router, prefix="/suppliers", tags=["Website - Suppliers"])