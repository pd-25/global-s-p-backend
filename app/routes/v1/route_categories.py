from typing import List
from fastapi import APIRouter, Depends,status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.category_schema import CategoryFilterSchema, CategoryResponseSchema, CreateCategorySchema
from app.schemas.response import APIResponse
from app.services.categories.category_service import retrieve_all_categories


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
     


@category_router.post("/", description="This endpoint will create new category")
def create_category(category_data: CreateCategorySchema = Depends(CreateCategorySchema.as_form)):
    # Here category_data is already validated
    return {
        "success": True, 
        "message": "Category created successfully",
        "data": {
            "name": category_data.name, 
            "description": category_data.description,
            "filename": category_data.image.filename
        }
    }