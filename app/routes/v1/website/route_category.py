from app.schemas.category_schema import CategoryResponseSchema
from app.services.categories.category_service import retrieve_single_category
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.category_schema import CategoryWiseSubcategoriesFilterSchema, CategoryWiseSubcategoriesSchema
from app.schemas.response import APIResponse
from app.services.categories.category_service import fetch_category_wise_subcategories, fetch_category_wise_subcategories_by_slug

category_router = APIRouter()



@category_router.get(
    '/category-wise-subcategories',
    response_model=APIResponse[List[CategoryWiseSubcategoriesSchema]],
    status_code=status.HTTP_200_OK,
    description="This api will list all the category wise subcategories"
)
def get_category_wise_subcategories(filters: CategoryWiseSubcategoriesFilterSchema = Depends(), db: Session = Depends(get_db)):
    category_wise_subcategories = fetch_category_wise_subcategories(db=db, filters=filters)
    return APIResponse(
        success=True,
        message="Category Wise Subcategories Fetched Successfully",
        data=category_wise_subcategories,
        meta={},
    )
  
@category_router.get(
    '/category-wise-subcategories/{slug}',
    response_model=APIResponse[CategoryResponseSchema],
    status_code=status.HTTP_200_OK,
    description="This will return particular category with more details and with it's child subcategories"
)  
def get_single_category_wise_subcategories(slug: str, db: Session = Depends(get_db)):
    single_category_wise_subcategories = retrieve_single_category(slug=slug, db=db)
    return APIResponse(
        success=True,
        message="Single Category Wise Subcategories Fetched Successfully",
        data=single_category_wise_subcategories,
        meta={},
    )


