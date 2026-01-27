from typing import List
from fastapi import APIRouter, Depends,status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.category_response_schema import CategoryResponseSchema
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
)
def get_categories(db: Session = Depends(get_db)):
    
    # (Service layer)
    categories = retrieve_all_categories(db=db)

    # Return using the Wrapper
    # Pydantic automatically converts the 'categories' ORM objects into the 'data' field schema
    return APIResponse(
        success=True,
        message="Categories fetched successfully",
        data=categories,
        meta={"count": len(categories)}
    )
     


@category_router.get("/categories")
def get_subcategories():
    return {"success": "The subcategory list fetched successfully..."}