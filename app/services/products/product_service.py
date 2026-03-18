import os
import time
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session, joinedload, load_only, selectinload
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.models.category import Categories
from app.models.country import Country
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.supplier import Supplier
from app.models.supplier_type import SupplierType
from app.schemas.product_schema import (
    AdminProductFilterSchema,
    ProductFilterSchema,
    CreateProductSchema,
    UpdateProductSchema,
)
from app.utils.file_utils import save_upload_file
from app.utils.string_utils import generate_slug

logger = logging.getLogger(__name__)

PRODUCT_IMAGE_DIR = "app/static/uploads/products"


def product_model_query(db: Session):
    return db.query(Product).filter(Product.deleted_at == None).distinct()

def retrieve_all_products(filters: AdminProductFilterSchema, db: Session):
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


# def fetch_website_products(category_slug: str, filters: ProductFilterSchema, db: Session):
#     """Fetch paginated products for the public website listing page.

#     Supports:
#     - Full-text search on product title
#     - Filter by country_code (ISO code, e.g. "BD", "US") — exact, case-insensitive
#     - Filter by supplier_type_slug (e.g. "raw-material") — slug converted to name match
#     - Pagination (page + per_page)
#     Returns: (products list, total_count, total_pages)
#     """
#     try:
#         query = product_model_query(db=db)

#         # Filter by category slug
#         if category_slug:
#             query = query.join(Categories, Product.category_id == Categories.id).filter(
#                 Categories.slug.ilike(category_slug)
#             )

#         # Full-text search on product title
#         if filters.search_string:
#             query = query.filter(
#                 Product.title.ilike(f"%{filters.search_string}%")
#             )

#         # Filter by ISO country code — exact match (e.g. "BD")
#         if filters.country_code:
#             query = query.join(Country, Product.country_id == Country.id).filter(
#                 Country.country_code.ilike(filters.country_code)
#             )

#         # Filter by supplier_type slug — convert "raw-material" → "raw material"
#         # and match against SupplierType.name (no slug column exists on supplier_types)
#         if filters.supplier_type_slug:
#             name_from_slug = filters.supplier_type_slug.replace("-", " ")
#             query = (
#                 query
#                 .join(Supplier, Product.supplier_id == Supplier.id)
#                 .join(SupplierType, Supplier.supplier_type_id == SupplierType.id)
#                 .filter(SupplierType.name.ilike(name_from_slug))
#             )

#         # Sort newest first by default
#         query = query.order_by(desc(Product.id))

#         # Total count before pagination
#         total_count = query.count()
#         total_pages = (total_count + filters.per_page - 1) // filters.per_page

#         # Pagination + select ONLY the columns needed by ProductListingSchema
#         # products  : id, slug, title  (+ FK cols kept for relationship resolution)
#         # images    : image
#         # countries : country_flag
#         # suppliers : name
#         offset = (filters.page - 1) * filters.per_page
#         products = (
#             query
#             .options(
#                 load_only(
#                     Product.id,
#                     Product.slug,
#                     Product.title,
#                     Product.country_id,
#                     Product.supplier_id,
#                 ),
#                 joinedload(Product.primary_image).load_only(
#                     ProductImage.image,
#                 ),
#                 joinedload(Product.country).load_only(
#                     Country.country_flag,
#                 ),
#                 joinedload(Product.supplier).load_only(
#                     Supplier.name,
#                 ),
#             )
#             .offset(offset)
#             .limit(filters.per_page)
#             .all()
#         )

#         return products, total_count, total_pages

#     except SQLAlchemyError as e:
#         logger.error(f"DB Error in fetch_website_products: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Internal Server Error: Could not fetch products.",
#         )

from sqlalchemy import or_, desc # Make sure 'or_' is imported
from sqlalchemy.orm import load_only, joinedload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

def fetch_website_products(filters: ProductFilterSchema, db: Session, category_slug: str = None):
    """Fetch paginated products for the public website listing page.

    Supports:
    - Full-text search on product title
    - Filter by country_code (ISO code, e.g. "BD", "US") — exact, case-insensitive
    - Filter by supplier_type_slug (e.g. "raw-material") — slug converted to name match
    - Pagination (page + per_page)
    Returns: (products list, total_count, total_pages)
    """
    try:
        query = product_model_query(db=db)

        # -----------------------------------------------------------------
        # UPDATED: Filter by category slug (Main category + Subcategories)
        # -----------------------------------------------------------------
        # if category_slug:
        #     # Subquery to find the ID of the target category based on the slug
        #     target_cat_query = db.query(Categories.id).filter(Categories.slug.ilike(category_slug))
            
        #     # Join and filter for exact match OR if the category's parent is the target
        #     query = query.join(Categories, Product.category_id == Categories.id).filter(
        #         or_(
        #             Categories.slug.ilike(category_slug),
        #             Categories.parent_id.in_(target_cat_query)
        #         )
        #     )
        if category_slug:
            # 2. It's also best practice to use .scalar_subquery() for single-value subqueries
            target_cat_query = db.query(Categories.id).filter(Categories.slug.ilike(category_slug)).scalar_subquery()
            
            query = query.join(Categories, Product.category_id == Categories.id).filter(
                or_(
                    Categories.slug.ilike(category_slug),
                    Categories.parent_id == target_cat_query # Using == with scalar_subquery is cleaner
                )
            )

        # Full-text search on product title
        if filters.search_string:
            query = query.filter(
                Product.title.ilike(f"%{filters.search_string}%")
            )

        # Filter by ISO country code — exact match (e.g. "BD")
        if filters.country_code:
            country_codes = [c.strip() for c in filters.country_code.split(",") if c.strip()]
            if country_codes:
                query = query.join(Country, Product.country_id == Country.id).filter(
                    or_(*[Country.country_code.ilike(c) for c in country_codes])
                )

        # Filter by supplier/supplier_type
        if getattr(filters, 'supplier_type_slug', None) or getattr(filters, 'supplier_slug', None):
            query = query.join(Supplier, Product.supplier_id == Supplier.id)

            if getattr(filters, 'supplier_type_slug', None):
                supplier_types = [s.strip().replace("-", " ") for s in filters.supplier_type_slug.split(",") if s.strip()]
                if supplier_types:
                    query = (
                        query
                        .join(SupplierType, Supplier.supplier_type_id == SupplierType.id)
                        .filter(or_(*[SupplierType.name.ilike(s) for s in supplier_types]))
                    )

            if getattr(filters, 'supplier_slug', None):
                supplier_slugs = [s.strip() for s in filters.supplier_slug.split(",") if s.strip()]
                if supplier_slugs:
                    query = query.filter(or_(*[Supplier.slug.ilike(s) for s in supplier_slugs]))

        # Filter by price
        if getattr(filters, 'min_price', None) is not None:
            query = query.filter(Product.price >= filters.min_price)

        if getattr(filters, 'max_price', None) is not None:
            query = query.filter(Product.price <= filters.max_price)

        # Sort newest first by default
        query = query.order_by(desc(Product.id))

        # Total count before pagination
        total_count = query.count()
        
        # Prevent division by zero if per_page is somehow 0, though schema usually handles this
        total_pages = (total_count + filters.per_page - 1) // filters.per_page if filters.per_page else 0

        # Pagination
        # query = query.options(
        #         load_only(
        #             Product.id,
        #             Product.slug,
        #             Product.title,
        #             Product.country_id,
        #             Product.supplier_id,
        #         ),
        #         joinedload(Product.primary_image).load_only(
        #             ProductImage.image,
        #         ),
        #         joinedload(Product.country).load_only(
        #             Country.country_flag,
        #         ),
        #         joinedload(Product.supplier).load_only(
        #             Supplier.name,
        #         ),
        #     ).offset(offset).limit(filters.per_page)
        # print("+++++++++++++++++++++++++++++++++++++++++")
        # sql = query.statement.compile(
        #     compile_kwargs={"literal_binds": True}
        # )

        # print(sql)
        # print("+++++++++++++++++++++++++++++++++++++++++")
        
        # return
        offset = (filters.page - 1) * filters.per_page
        products = (
            query
            .options(
                load_only(
                    Product.id,
                    Product.slug,
                    Product.title,
                    Product.country_id,
                    Product.supplier_id,
                ),
                # ---------------------------------------------------------
                # CHANGED: Use selectinload for the image relationship
                # ---------------------------------------------------------
                selectinload(Product.primary_image).load_only(
                    ProductImage.image,
                ),
                # joinedload is perfectly safe here because the foreign keys 
                # are on the Product table itself (Many-to-One). No fan-out!
                joinedload(Product.country).load_only(
                    Country.country_flag,
                ),
                joinedload(Product.supplier).load_only(
                    Supplier.name,
                ),
            )
            .offset(offset)
            .limit(filters.per_page)
            .all()
        )

        return products, total_count, total_pages

    except SQLAlchemyError as e:
        logger.error(f"DB Error in fetch_website_products: {str(e)}")
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
        joinedload(Product.primary_image),
        joinedload(Product.country),
    ).all()
