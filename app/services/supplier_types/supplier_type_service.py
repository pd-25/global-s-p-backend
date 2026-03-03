from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.supplier_type import SupplierType
from app.schemas.supplier_type_schema import (
    SupplierTypeFilterSchema,
    CreateSupplierTypeSchema,
    UpdateSupplierTypeSchema,
)

logger = logging.getLogger(__name__)


def retrieve_all_supplier_types(filters: SupplierTypeFilterSchema, db: Session):
    """Retrieve all supplier types with search, pagination and sorting."""
    try:
        query = db.query(SupplierType).filter(SupplierType.deleted_at == None)

        # Search filter
        if filters.search_string:
            query = query.filter(
                SupplierType.name.ilike(f"%{filters.search_string}%")
            )

        # Sorting
        if filters.sort_order == "asc":
            query = query.order_by(asc(SupplierType.id))
        else:
            query = query.order_by(desc(SupplierType.id))

        # Total count before pagination
        total_count = query.count()

        # Pagination
        offset = (filters.page - 1) * filters.per_page
        supplier_types = query.offset(offset).limit(filters.per_page).all()

        return supplier_types, total_count

    except SQLAlchemyError as e:
        logger.error(f"DB Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not fetch supplier types.",
        )


def create_supplier_type_service(supplier_type_data: CreateSupplierTypeSchema, db: Session):
    """Create a new supplier type."""
    try:
        # Check if supplier type with same name already exists
        existing = db.query(SupplierType).filter(
            SupplierType.name == supplier_type_data.name,
            SupplierType.deleted_at == None,
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supplier type with this name already exists.",
            )

        new_supplier_type = SupplierType(
            name=supplier_type_data.name,
        )

        db.add(new_supplier_type)
        db.commit()
        db.refresh(new_supplier_type)

        return new_supplier_type

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating supplier type: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not create supplier type.",
        )


def retrieve_single_supplier_type(supplier_type_id: int, db: Session):
    """Retrieve a single supplier type by ID."""
    supplier_type = db.query(SupplierType).filter(
        SupplierType.id == supplier_type_id,
        SupplierType.deleted_at == None,
    ).first()

    if not supplier_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier type not found",
        )

    return supplier_type


def update_supplier_type_service(
    supplier_type_id: int, supplier_type_data: UpdateSupplierTypeSchema, db: Session
):
    """Update an existing supplier type."""
    try:
        existing_supplier_type = retrieve_single_supplier_type(
            supplier_type_id=supplier_type_id, db=db
        )

        # Check if another supplier type with the same name exists
        duplicate = db.query(SupplierType).filter(
            SupplierType.name == supplier_type_data.name,
            SupplierType.id != supplier_type_id,
            SupplierType.deleted_at == None,
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supplier type with this name already exists.",
            )

        existing_supplier_type.name = supplier_type_data.name
        existing_supplier_type.updated_at = datetime.now()

        db.commit()
        db.refresh(existing_supplier_type)

        return existing_supplier_type

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating supplier type: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not update supplier type.",
        )


def delete_supplier_type_service(supplier_type_id: int, db: Session):
    """Soft delete a supplier type by setting deleted_at timestamp."""
    try:
        existing_supplier_type = retrieve_single_supplier_type(
            supplier_type_id=supplier_type_id, db=db
        )

        existing_supplier_type.deleted_at = datetime.now()

        db.commit()

        return True

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting supplier type: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not delete supplier type.",
        )
