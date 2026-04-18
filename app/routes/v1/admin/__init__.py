from fastapi import APIRouter, Depends
from app.routes.v1.admin.auth_route import auth_router
from app.routes.v1.admin.route_user import user_router
from app.routes.v1.admin.route_categories import category_router
from app.routes.v1.admin.route_country import country_router
from app.routes.v1.admin.route_supplier_type import supplier_type_router
from app.routes.v1.admin.route_product_types import product_type_router
from app.routes.v1.admin.route_supplier import supplier_router
from app.routes.v1.admin.route_product import product_router
from app.routes.v1.admin.route_general import general_router
from app.services.auth.auth_service import get_current_user
from app.routes.v1.admin.route_quotes_inquiries import quotes_inquiries_router

admin_router = APIRouter()


admin_router.include_router(auth_router, prefix="/auth", tags=["Admin - Auth"])
admin_router.include_router(user_router, prefix="/users", tags=["Admin - Users"])
admin_router.include_router(general_router, prefix="/general", tags=["Admin - General"], dependencies=[Depends(get_current_user)])
admin_router.include_router(category_router, prefix="/categories", tags=["Admin - Categories"])
admin_router.include_router(country_router, prefix="/countries", tags=["Admin - country"])
admin_router.include_router(supplier_type_router, prefix="/supplier-types", tags=["Admin - supplier types"])
admin_router.include_router(product_type_router, prefix="/product-types", tags=["Admin - product types"])
admin_router.include_router(supplier_router, prefix="/suppliers", tags=["Admin - suppliers"])
admin_router.include_router(product_router, prefix="/products", tags=["Admin - products"])
admin_router.include_router(quotes_inquiries_router, prefix="/quotes-inquiries", tags=["Admin - quotes inquiries"], dependencies=[Depends(get_current_user)])
