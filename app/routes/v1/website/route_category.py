from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.category_schema import CategoryWiseSubcategoriesSchema
from app.schemas.response import APIResponse
from app.services.categories.category_service import fetch_category_wise_subcategories

category_router = APIRouter()



@category_router.get(
    '/category-wise-subcategories',
    response_model=APIResponse[List[CategoryWiseSubcategoriesSchema]],
    status_code=status.HTTP_200_OK,
    description="This api will list all the category wise subcategories"
)
def get_category_wise_subcategories(db: Session = Depends(get_db)):
    category_wise_subcategories = fetch_category_wise_subcategories(db=db)
    return APIResponse(
        success=True,
        message="Category Wise Subcategories Fetched Successfully",
        data=category_wise_subcategories,
        meta={},
    )


