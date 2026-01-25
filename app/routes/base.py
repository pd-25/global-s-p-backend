from fastapi import APIRouter
from app.routes.v1.route_user import user_router
from app.routes.v1.route_categories import category_router

api_router = APIRouter()

api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(category_router, prefix="/categories", tags=["categories"])