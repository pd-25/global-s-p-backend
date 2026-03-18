
from fastapi import APIRouter

from app.routes.v1.website.route_product import product_router
from app.routes.v1.website.route_category import category_router
from app.routes.v1.website.route_suppliers import supplier_router
from app.routes.v1.website.route_country import country_router
from app.routes.v1.website.route_supplier_type import supplier_type_router
from app.routes.v1.website.route_enquiry import enquiry_router

website_router = APIRouter()

website_router.include_router(product_router, prefix="/products", tags=["Website - Products"])
website_router.include_router(category_router, prefix="/categories", tags=["Website - Categories"])
website_router.include_router(supplier_router, prefix="/suppliers", tags=["Website - Suppliers"])
website_router.include_router(country_router, prefix="/countries", tags=["Website - Countries"])
website_router.include_router(supplier_type_router, prefix="/supplier-types", tags=["Website - Supplier Types"])
website_router.include_router(enquiry_router, prefix="/enquiries", tags=["Website - Enquiries"])
