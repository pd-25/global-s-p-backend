import os
import time
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.supplier import Supplier
from app.schemas.supplier_schema import (
    SupplierFilterSchema,
    CreateSupplierSchema,
    UpdateSupplierSchema,
)
from app.utils.file_utils import save_upload_file
from app.utils.string_utils import generate_slug

logger = logging.getLogger(__name__)

SUPPLIER_LOGO_DIR = "app/static/uploads/suppliers"


def retrieve_all_suppliers(filters: SupplierFilterSchema, db: Session):
    """Retrieve all suppliers with search, pagination, sorting and filters."""
    try:
        query = db.query(Supplier).filter(Supplier.deleted_at == None)

        # Search filter (search in name and city)
        if filters.search_string:
            query = query.filter(
                Supplier.name.ilike(f"%{filters.search_string}%")
            )

        # Filter by country
        if filters.country_id is not None:
            query = query.filter(Supplier.country_id == filters.country_id)

        # Filter by supplier type
        if filters.supplier_type_id is not None:
            query = query.filter(Supplier.supplier_type_id == filters.supplier_type_id)

        # Filter by verification status
        if filters.is_verified is not None:
            query = query.filter(Supplier.is_verified == filters.is_verified)

        # Sorting
        if filters.sort_order == "asc":
            query = query.order_by(asc(Supplier.id))
        else:
            query = query.order_by(desc(Supplier.id))

        # Total count before pagination
        total_count = query.count()

        # Pagination
        offset = (filters.page - 1) * filters.per_page
        suppliers = query.offset(offset).limit(filters.per_page).all()

        return suppliers, total_count

    except SQLAlchemyError as e:
        logger.error(f"DB Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not fetch suppliers.",
        )


def create_supplier_service(supplier_data: CreateSupplierSchema, db: Session):
    """Create a new supplier."""
    try:
        # Generate slug from name
        slug = generate_slug(supplier_data.name)

        # Check if slug already exists, append timestamp if so
        if db.query(Supplier).filter(Supplier.slug == slug).first():
            timestamp = int(time.time())
            slug = f"{slug}-{timestamp}"

        # Handle logo upload
        logo_path = None
        if supplier_data.logo:
            logo_path = save_upload_file(supplier_data.logo, SUPPLIER_LOGO_DIR)

        new_supplier = Supplier(
            slug=slug,
            name=supplier_data.name,
            about=supplier_data.about,
            logo=logo_path,
            zipcode=supplier_data.zipcode,
            city=supplier_data.city,
            country_id=supplier_data.country_id,
            address=supplier_data.address,
            delivery_area=supplier_data.delivery_area,
            founded_year=supplier_data.founded_year,
            employee_strength=supplier_data.employee_strength,
            supplier_type_id=supplier_data.supplier_type_id,
            is_verified=supplier_data.is_verified,
            vat_number=supplier_data.vat_number,
            company_site=supplier_data.company_site,
            company_phone_number=supplier_data.company_phone_number,
            company_email=supplier_data.company_email,
        )

        db.add(new_supplier)
        db.commit()
        db.refresh(new_supplier)

        return new_supplier

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating supplier: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not create supplier.",
        )


def retrieve_single_supplier(slug: str, db: Session):
    """Retrieve a single supplier by slug."""
    supplier = db.query(Supplier).filter(
        Supplier.slug == slug,
        Supplier.deleted_at == None,
    ).first()

    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )

    return supplier


def update_supplier_service(slug: str, supplier_data: UpdateSupplierSchema, db: Session):
    """Update an existing supplier."""
    try:
        existing_supplier = retrieve_single_supplier(slug=slug, db=db)

        # Update fields
        existing_supplier.name = supplier_data.name
        existing_supplier.about = supplier_data.about
        existing_supplier.zipcode = supplier_data.zipcode
        existing_supplier.city = supplier_data.city
        existing_supplier.country_id = supplier_data.country_id
        existing_supplier.address = supplier_data.address
        existing_supplier.delivery_area = supplier_data.delivery_area
        existing_supplier.founded_year = supplier_data.founded_year
        existing_supplier.employee_strength = supplier_data.employee_strength
        existing_supplier.supplier_type_id = supplier_data.supplier_type_id
        existing_supplier.is_verified = supplier_data.is_verified
        existing_supplier.vat_number = supplier_data.vat_number
        existing_supplier.company_site = supplier_data.company_site
        existing_supplier.company_phone_number = supplier_data.company_phone_number
        existing_supplier.company_email = supplier_data.company_email
        existing_supplier.updated_at = datetime.now()

        # Handle logo update if a new logo is provided
        if supplier_data.logo:
            # Delete old logo
            if existing_supplier.logo:
                try:
                    os.remove(existing_supplier.logo)
                except OSError:
                    pass  # Ignore if file doesn't exist

            # Save new logo
            logo_path = save_upload_file(supplier_data.logo, SUPPLIER_LOGO_DIR)
            existing_supplier.logo = logo_path

        db.commit()
        db.refresh(existing_supplier)

        return existing_supplier

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating supplier: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not update supplier.",
        )


def delete_supplier_service(slug: str, db: Session):
    """Soft delete a supplier by setting deleted_at timestamp."""
    try:
        existing_supplier = retrieve_single_supplier(slug=slug, db=db)

        existing_supplier.deleted_at = datetime.now()

        db.commit()

        return True

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting supplier: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not delete supplier.",
        )


def fetch_valuable_partners(db: Session):
    """Fetch all suppliers — only id, name, and logo."""
    return (
        db.query(
            Supplier.id,
            Supplier.name,
            Supplier.logo)
        .filter(Supplier.deleted_at.is_(None))
        .all()
    )
