
from fastapi import APIRouter

from app.routes.v1.website.route_product import product_router

website_router = APIRouter()

website_router.include_router(product_router, prefix="/products", tags=["Website - Products"])