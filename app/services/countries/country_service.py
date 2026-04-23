from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.country import Country
from app.schemas.country_schema import CountryFilterSchema, CreateCountrySchema, UpdateCountrySchema
from app.utils.s3_utils import upload_file_to_s3, delete_file_from_s3

S3_COUNTRY_FOLDER = "countries"

logger = logging.getLogger(__name__)

def fetch_countries_website(db: Session):
    return db.query(Country).filter(Country.deleted_at == None).all()

def retrieve_all_countries(filters: CountryFilterSchema, db: Session):
    """Retrieve all countries with search, pagination and sorting."""
    try:
        query = db.query(Country).filter(Country.deleted_at == None)

        # Search filter
        if filters.search_string:
            query = query.filter(
                Country.name.ilike(f"%{filters.search_string}%")
            )

        # Sorting
        if filters.sort_order == "asc":
            query = query.order_by(asc(Country.id))
        else:
            query = query.order_by(desc(Country.id))

        # Total count before pagination
        total_count = query.count()

        # Pagination
        offset = (filters.page - 1) * filters.per_page
        countries = query.offset(offset).limit(filters.per_page).all()

        return countries, total_count

    except SQLAlchemyError as e:
        logger.error(f"DB Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not fetch countries."
        )


def create_country_service(country_data: CreateCountrySchema, db: Session):
    """Create a new country."""
    try:
        # Check if country with same name already exists
        existing = db.query(Country).filter(
            Country.name == country_data.name,
            Country.deleted_at == None
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Country with this name already exists."
            )
        image_path = upload_file_to_s3(country_data.country_flag, S3_COUNTRY_FOLDER)

        new_country = Country(
            name=country_data.name,
            country_flag = image_path
        )

        db.add(new_country)
        db.commit()
        db.refresh(new_country)

        return new_country

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating country: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not create country."
        )


def retrieve_single_country(country_id: int, db: Session):
    """Retrieve a single country by ID."""
    country = db.query(Country).filter(
        Country.id == country_id,
        Country.deleted_at == None
    ).first()

    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )

    return country


def update_country_service(country_id: int, country_data: UpdateCountrySchema, db: Session):
    """Update an existing country."""
    try:
        existing_country = retrieve_single_country(country_id=country_id, db=db)

        # Check if another country with the same name exists
        duplicate = db.query(Country).filter(
            Country.name == country_data.name,
            Country.id != country_id,
            Country.deleted_at == None
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Country with this name already exists."
            )

        existing_country.name = country_data.name
        existing_country.updated_at = datetime.now()
        # Handle image update if a new image is provided
        if country_data.country_flag:
            # Delete old country_flag from S3
            if existing_country.country_flag:
                delete_file_from_s3(existing_country.country_flag)
            
            # Upload new image to S3
            image_url = upload_file_to_s3(country_data.country_flag, S3_COUNTRY_FOLDER)
            existing_country.country_flag = image_url

        db.commit()
        db.refresh(existing_country)

        return existing_country

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating country: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not update country."
        )


def delete_country_service(country_id: int, db: Session):
    """Soft delete a country by setting deleted_at timestamp."""
    try:
        existing_country = retrieve_single_country(country_id=country_id, db=db)

        existing_country.deleted_at = datetime.now()

        db.commit()

        return True

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting country: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not delete country."
        )
