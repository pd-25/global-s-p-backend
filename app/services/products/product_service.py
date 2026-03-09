import os
import time
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.product import Product
from app.models.product_image import ProductImage
from app.schemas.product_schema import (
    ProductFilterSchema,
    CreateProductSchema,
    UpdateProductSchema,
)
from app.utils.file_utils import save_upload_file
from app.utils.string_utils import generate_slug

logger = logging.getLogger(__name__)

PRODUCT_IMAGE_DIR = "app/static/uploads/products"


def product_model_query(db: Session):
    return db.query(Product).filter(Product.deleted_at == None)

def retrieve_all_products(filters: ProductFilterSchema, db: Session):
    """Retrieve all products with search, pagination, sorting, filters and all relations."""
    try:
        query = product_model_query(db=db)

        # Search filter (search in title)
        if filters.search_string:
            query = query.filter(
                Product.title.ilike(f"%{filters.search_string}%")
            )

        # Filter by country
        if filters.country_id is not None:
            query = query.filter(Product.country_id == filters.country_id)

        # Filter by supplier
        if filters.supplier_id is not None:
            query = query.filter(Product.supplier_id == filters.supplier_id)

        # Filter by product type
        if filters.product_type_id is not None:
            query = query.filter(Product.product_type_id == filters.product_type_id)

        # Filter by category
        if filters.category_id is not None:
            query = query.filter(Product.category_id == filters.category_id)

        # Sorting
        if filters.sort_order == "asc":
            query = query.order_by(asc(Product.id))
        else:
            query = query.order_by(desc(Product.id))

        # Total count before pagination
        total_count = query.count()

        # Pagination + eager load all relations
        offset = (filters.page - 1) * filters.per_page
        products = (
            query
            .options(
                joinedload(Product.country),
                joinedload(Product.supplier),
                joinedload(Product.product_type),
                joinedload(Product.category),
                joinedload(Product.images),
            )
            .offset(offset)
            .limit(filters.per_page)
            .all()
        )

        return products, total_count

    except SQLAlchemyError as e:
        logger.error(f"DB Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not fetch products.",
        )


def create_product_service(product_data: CreateProductSchema, db: Session):
    """Create a new product with multiple images."""
    try:
        # Generate slug from title
        slug = generate_slug(product_data.title)

        # Check if slug already exists, append timestamp if so
        if db.query(Product).filter(Product.slug == slug).first():
            timestamp = int(time.time())
            slug = f"{slug}-{timestamp}"

        new_product = Product(
            slug=slug,
            title=product_data.title,
            description=product_data.description,
            short_desc=product_data.short_desc,
            currency=product_data.currency,
            price=product_data.price,
            price_per_measurement=product_data.price_per_measurement,
            min_order=product_data.min_order,
            country_id=product_data.country_id,
            supplier_id=product_data.supplier_id,
            product_type_id=product_data.product_type_id,
            category_id=product_data.category_id,
        )

        db.add(new_product)
        db.flush()  # Get the product ID before adding images

        # Handle multiple image uploads
        if product_data.images:
            for index, image_file in enumerate(product_data.images):
                image_path = save_upload_file(image_file, PRODUCT_IMAGE_DIR)
                product_image = ProductImage(
                    product_id=new_product.id,
                    image=image_path,
                    is_preview=(index == 0),  # First image is preview by default
                )
                db.add(product_image)

        db.commit()
        db.refresh(new_product)

        return new_product

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not create product.",
        )


def retrieve_single_product(slug: str, db: Session):
    """Retrieve a single product by slug with all relations."""
    product = (
        db.query(Product)
        .options(
            joinedload(Product.country),
            joinedload(Product.supplier),
            joinedload(Product.product_type),
            joinedload(Product.category),
            joinedload(Product.images),
        )
        .filter(
            Product.slug == slug,
            Product.deleted_at == None,
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


def update_product_service(slug: str, product_data: UpdateProductSchema, db: Session):
    """Update an existing product. New images are added alongside existing ones."""
    try:
        existing_product = retrieve_single_product(slug=slug, db=db)

        # Update fields
        existing_product.title = product_data.title
        existing_product.description = product_data.description
        existing_product.short_desc = product_data.short_desc
        existing_product.currency = product_data.currency
        existing_product.price = product_data.price
        existing_product.price_per_measurement = product_data.price_per_measurement
        existing_product.min_order = product_data.min_order
        existing_product.country_id = product_data.country_id
        existing_product.supplier_id = product_data.supplier_id
        existing_product.product_type_id = product_data.product_type_id
        existing_product.category_id = product_data.category_id
        existing_product.updated_at = datetime.now()

        # Handle new image uploads (added alongside existing images)
        if product_data.images:
            for image_file in product_data.images:
                image_path = save_upload_file(image_file, PRODUCT_IMAGE_DIR)
                product_image = ProductImage(
                    product_id=existing_product.id,
                    image=image_path,
                    is_preview=False,
                )
                db.add(product_image)

        db.commit()
        db.refresh(existing_product)

        return existing_product

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not update product.",
        )


def delete_product_service(slug: str, db: Session):
    """Soft delete a product by setting deleted_at timestamp."""
    try:
        existing_product = retrieve_single_product(slug=slug, db=db)

        existing_product.deleted_at = datetime.now()

        db.commit()

        return True

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not delete product.",
        )


def delete_product_image_service(image_id: int, db: Session):
    """Delete a single product image by its ID."""
    try:
        image = db.query(ProductImage).filter(ProductImage.id == image_id).first()

        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product image not found",
            )

        # Delete file from disk
        if image.image:
            try:
                os.remove(image.image)
            except OSError:
                pass

        db.delete(image)
        db.commit()

        return True

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting product image: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not delete product image.",
        )

def fetch_recomended_products(db: Session):
    return product_model_query(db=db).filter(Product.id_recomended == 1).options(
        joinedload(Product.primary_image)
    ).all()