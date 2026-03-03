from fastapi import APIRouter
from app.routes.v1.auth_route import auth_router
from app.routes.v1.route_user import user_router
from app.routes.v1.route_categories import category_router
from app.routes.v1.route_country import country_router
from app.routes.v1.route_supplier_type import supplier_type_router
from app.routes.v1.route_product_types import product_type_router
from app.routes.v1.route_supplier import supplier_router
from app.routes.v1.route_product import product_router



api_router = APIRouter()

api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(category_router, prefix="/categories", tags=["categories"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(country_router, prefix="/countries", tags=["country"])
api_router.include_router(supplier_type_router, prefix="/supplier-types", tags=["supplier types"])
api_router.include_router(product_type_router, prefix="/product-types", tags=["product types"])
api_router.include_router(supplier_router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(product_router, prefix="/products", tags=["products"])