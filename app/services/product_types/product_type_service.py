from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.product_type import ProductType
from app.schemas.product_type_schema import (
    ProductTypeFilterSchema,
    CreateProductTypeSchema,
    UpdateProductTypeSchema,
)

logger = logging.getLogger(__name__)


def retrieve_all_product_types(filters: ProductTypeFilterSchema, db: Session):
    """Retrieve all product types with search, pagination and sorting."""
    try:
        query = db.query(ProductType).filter(ProductType.deleted_at == None)

        # Search filter
        if filters.search_string:
            query = query.filter(
                ProductType.name.ilike(f"%{filters.search_string}%")
            )

        # Sorting
        if filters.sort_order == "asc":
            query = query.order_by(asc(ProductType.id))
        else:
            query = query.order_by(desc(ProductType.id))

        # Total count before pagination
        total_count = query.count()

        # Pagination
        offset = (filters.page - 1) * filters.per_page
        product_types = query.offset(offset).limit(filters.per_page).all()

        return product_types, total_count

    except SQLAlchemyError as e:
        logger.error(f"DB Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not fetch product types.",
        )


def create_product_type_service(product_type_data: CreateProductTypeSchema, db: Session):
    """Create a new product type."""
    try:
        # Check if product type with same name already exists
        existing = db.query(ProductType).filter(
            ProductType.name == product_type_data.name,
            ProductType.deleted_at == None,
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product type with this name already exists.",
            )

        new_product_type = ProductType(
            name=product_type_data.name,
        )

        db.add(new_product_type)
        db.commit()
        db.refresh(new_product_type)

        return new_product_type

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating product type: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not create product type.",
        )


def retrieve_single_product_type(product_type_id: int, db: Session):
    """Retrieve a single product type by ID."""
    product_type = db.query(ProductType).filter(
        ProductType.id == product_type_id,
        ProductType.deleted_at == None,
    ).first()

    if not product_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product type not found",
        )

    return product_type


def update_product_type_service(
    product_type_id: int, product_type_data: UpdateProductTypeSchema, db: Session
):
    """Update an existing product type."""
    try:
        existing_product_type = retrieve_single_product_type(
            product_type_id=product_type_id, db=db
        )

        # Check if another product type with the same name exists
        duplicate = db.query(ProductType).filter(
            ProductType.name == product_type_data.name,
            ProductType.id != product_type_id,
            ProductType.deleted_at == None,
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product type with this name already exists.",
            )

        existing_product_type.name = product_type_data.name
        existing_product_type.updated_at = datetime.now()

        db.commit()
        db.refresh(existing_product_type)

        return existing_product_type

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating product type: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not update product type.",
        )


def delete_product_type_service(product_type_id: int, db: Session):
    """Soft delete a product type by setting deleted_at timestamp."""
    try:
        existing_product_type = retrieve_single_product_type(
            product_type_id=product_type_id, db=db
        )

        existing_product_type.deleted_at = datetime.now()

        db.commit()

        return True

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting product type: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not delete product type.",
        )
