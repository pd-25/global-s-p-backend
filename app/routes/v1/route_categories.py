from typing import List
from fastapi import APIRouter, Depends, UploadFile,status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.category_schema import CategoryFilterSchema, CategoryResponseSchema, CreateCategorySchema
from app.schemas.response import APIResponse
from app.services.categories.category_service import create_category_service, retrieve_all_categories
from app.utils.file_utils import validate_image_file


category_router = APIRouter()


# @category_router.get("/")
# def get_categories(db: Session= Depends(get_db))-> JSONResponse:
#     print('this')
#     return retrieve_all_categories(db=db)


# @category_router.get(
#     "/",
#     response_model=dict,
#     status_code=status.HTTP_200_OK
# )
# def get_categories(db: Session = Depends(get_db)):
#     categories = retrieve_all_categories(db=db)

#     return {
#         "success": True,
#         "message": "Categories fetched successfully",
#         "data": categories,
#         "meta": {
#             "count": len(categories)
#         }
#     }

@category_router.get(
    "/",
    # This is the magic: It documents that we return our Standard Envelope containing a List of Categories
    response_model=APIResponse[List[CategoryResponseSchema]], 
    status_code=status.HTTP_200_OK,
    description="This endpoints returns list of categories with search functionlity and pagination"
)
def get_categories(filters: CategoryFilterSchema = Depends(), db: Session = Depends(get_db)):
    
    # (Service layer)
    categories, total_count = retrieve_all_categories(filters=filters, db=db)

    # Return using the Wrapper
    # Pydantic automatically converts the 'categories' ORM objects into the 'data' field schema
    return APIResponse(
        success=True,
        message="Categories fetched successfully",
        data=categories,
        meta={
            "count": len(categories),
            "total": total_count,
            "page": filters.page,
            "per_page": filters.per_page,
        }
    )
     


@category_router.post("/", response_model=APIResponse[CategoryResponseSchema], description="This endpoint will create new category")
async def create_category(category_data: CreateCategorySchema = Depends(CreateCategorySchema.as_form), db: Session = Depends(get_db)):
    validate_image_file(category_data.image)
    # Here category_data is already validated
    response = await create_category_service(category_data=category_data, db=db)
    
    return APIResponse(
        success=True, 
        message="Category created successfully",
        data=response
    )