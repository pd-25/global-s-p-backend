from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from app.enums.enums import CategoryOrderBy, SortOrder
from app.models.category import Categories
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.schemas.category_schema import CategoryFilterSchema
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
    query = db.query(Categories)

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
        .offset(offset)
        .limit(filters.per_page)
        .all()
    )

    return categories, total_count