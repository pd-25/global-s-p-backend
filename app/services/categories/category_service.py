from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.category import Categories
from sqlalchemy.exc import SQLAlchemyError
import logging
logger = logging.getLogger(__name__)
        

def retrieve_all_categories(db: Session):
    try:
        
        return db.query(Categories).all()
    except SQLAlchemyError as e:
        logger.error(f"DB Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not fetch categories."
        )