from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db


category_router = APIRouter()


@category_router.get("/")
def get_categories(db: Session= Depends(get_db)):
    print('this')
    blogs = retrieve_all_blogs(db=db)
    return blogs
    return {"success": "The category list fetched successfully..."}


@category_router.get("/categories")
def get_subcategories():
    return {"success": "The subcategory list fetched successfully..."}