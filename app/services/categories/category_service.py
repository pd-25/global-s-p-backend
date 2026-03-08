import os
from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session, joinedload
from app.enums.enums import CategoryOrderBy, SortOrder
from app.models.category import Categories
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.schemas.category_schema import CategoryFilterSchema, CategoryResponseSchema, CreateCategorySchema, UpdateCategorySchema
logger = logging.getLogger(__name__)
        

def retrieve_all_categories(filters: CategoryFilterSchema, db: Session):
    try:    
        return fetch_categories(filters=filters, db=db)
    except SQLAlchemyError as e:
        logger.error(f"DB Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not fetch categories."
        )
        
def fetch_categories(filters: CategoryFilterSchema, db: Session):
    query = db.query(Categories).filter(Categories.parent_id == None)
    #  Categories.is_active==1

    # 🔍 Search filter
    if filters.search_string:
        query = query.filter(
            Categories.name.ilike(f"%{filters.search_string}%")
        )
    
    # Safe column mapping
    order_column_map = {
        CategoryOrderBy.id: Categories.id,
        CategoryOrderBy.created_at: Categories.created_at,
    }

    order_column = order_column_map[filters.order_by_column]

    if filters.sort_order == SortOrder.asc:
        query = query.order_by(asc(order_column))
    else:
        query = query.order_by(desc(order_column))

    #Total count before pagination
    total_count = query.count()

    #Pagination
    offset = (filters.page - 1) * filters.per_page

    categories = (
        query
        .options(joinedload(Categories.children))
        .offset(offset)
        .limit(filters.per_page)
        .all()
    )

    return categories, total_count

from app.utils.file_utils import save_upload_file
from app.utils.string_utils import generate_slug
import time


async def create_category_service(category_data: CreateCategorySchema, db: Session):
    try:
        slug = generate_slug(category_data.name)
        
        # Check if slug already exists
        if db.query(Categories).filter(Categories.slug == slug).first():
             timestamp = int(time.time())
             slug = f"{slug}-{timestamp}"
            
        image_path = save_upload_file(category_data.image, "app/static/uploads/categories")
        
        # Remove 'app/' from the path to store relative path if needed, 
        # or keep as is depending on how it's served. 
        # Usually static files are served from the root of static dir.
        # Let's clean up the path to be relative to static or just the filename if serving setup handles it.
        # For now, I'll store the relative path from project root as returned.
        
        new_category = Categories(
            name=category_data.name,
            description=category_data.description,
            slug=slug,
            image=image_path,
            parent_id=category_data.parent_id
        )
        
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        
        return new_category
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not create category."
        )

async def update_single_category(slug: str, category_data: UpdateCategorySchema, db: Session):
    try:
        # retrieve_single_category is a synchronous helper, so do not await it
        existing_category = retrieve_single_category(slug=slug, db=db)
        if not existing_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        print(existing_category)
        # Update fields
        existing_category.name = category_data.name
        existing_category.description = category_data.description
        existing_category.parent_id = category_data.parent_id
        
        # Handle image update if a new image is provided
        if category_data.image:
            # Delete old image
            if existing_category.image:
                try:
                    os.remove(existing_category.image)
                except OSError:
                    pass  # Ignore if file doesn't exist
            
            # Save new image
            image_path = save_upload_file(category_data.image, "app/static/uploads/categories")
            existing_category.image = image_path
        
        db.commit()
        db.refresh(existing_category)
        
        return existing_category
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating category: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not update category."
        )
        
def retrieve_single_category(slug: str, db: Session):
    category = db.query(Categories).filter(Categories.slug == slug).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category
