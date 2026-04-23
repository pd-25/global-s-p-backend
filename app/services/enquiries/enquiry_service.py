from app.schemas.enquiry_schema import EnquiryUpdateSchema
from app.enums.enums import EnquiryStatus
from app.utils.string_utils import generate_enquiry_number
import logging
from typing import Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc, asc
from datetime import timedelta
from fastapi import HTTPException, status

from app.models.enquiry import Enquiry
from app.models.enquiry_files import EnquiryFiles
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.product_image import ProductImage
from app.schemas.enquiry_schema import CreateEnquirySchema, EnquiryFilterSchema
from app.utils.s3_utils import upload_file_to_s3
from app.models.enquiry_supplier_types import EnquirySupplierType
import json
from sqlalchemy import select, and_

logger = logging.getLogger(__name__)

S3_ENQUIRY_FOLDER = "enquiries"

def create_enquiry_service(enquiry_data: CreateEnquirySchema, db: Session):
    try:
        # Validate supplier_id if provided
        if enquiry_data.supplier_id:
            supplier = db.query(Supplier).filter(Supplier.id == enquiry_data.supplier_id).first()
            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supplier not found."
                )

        # Validate product_id if provided
        if enquiry_data.product_id:
            product = db.query(Product).filter(Product.id == enquiry_data.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found."
                )

        new_enquiry = Enquiry(
            name=enquiry_data.name or None,
            email=enquiry_data.email or None,
            phone=enquiry_data.phone or None,
            status=enquiry_data.status or EnquiryStatus.pending,
            enquiry_number=generate_enquiry_number(),
            reason_for_contacting=enquiry_data.reason_for_contacting or None,
            request_title=enquiry_data.request_title or None,
            delivery_location=enquiry_data.delivery_location or None,
            quantity=enquiry_data.quantity or None,
            request_type=enquiry_data.request_type or None,
            message=enquiry_data.message or None,
            business_email=enquiry_data.business_email or None,
            company_name=enquiry_data.company_name or None,
            forward_to_other=enquiry_data.forward_to_other or None,
            supplier_id=enquiry_data.supplier_id or None,
            product_id=enquiry_data.product_id or None,
        )
        
        if enquiry_data.supplier_type_ids:
            new_enquiry.is_quote_form = True
        
        db.add(new_enquiry)
        db.flush()
        
        if enquiry_data.supplier_type_ids:
            try:
                # Parse JSON array if it comes as a stringified list
                parsed_ids = json.loads(enquiry_data.supplier_type_ids)
                if not isinstance(parsed_ids, list):
                    parsed_ids = [parsed_ids]
            except Exception:
                # Fallback to comma-separated string
                parsed_ids = [int(s) for s in str(enquiry_data.supplier_type_ids).split(",") if str(s).strip().isdigit()]
            
            for s_id in parsed_ids:
                supplier_enquiry = EnquirySupplierType(
                    enquiry_id=new_enquiry.id,
                    supplier_type_id=int(s_id)
                )
                db.add(supplier_enquiry)

        
        if enquiry_data.files:
            for index, file in enumerate(enquiry_data.files):
                if file.filename:  # skip empty file elements if explicitly parsed
                    file_path = upload_file_to_s3(file, S3_ENQUIRY_FOLDER)
                    enquiry_file = EnquiryFiles(
                        enquiry_id=new_enquiry.id,
                        file=file_path,
                        is_preview=(index == 0)
                    )
                    db.add(enquiry_file)
        
        db.commit()
        db.refresh(new_enquiry)
        
        return new_enquiry
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating enquiry: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not create enquiry."
        )

def fetch_product_supplier_data_service(db: Session, slug: str, req_type: str):
    try:
        result: dict[str, Any] = {"product": None, "supplier": None}
        # print("req_type", req_type)
        # print("slug", slug)
        # return
        if req_type == "product":
            product = db.query(Product).options(joinedload(Product.supplier).joinedload(Supplier.supplier_type)).filter(Product.slug == slug, Product.deleted_at == None).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
            
            # Get preview image
            preview_image = db.query(ProductImage).filter(
                ProductImage.product_id == product.id,
                ProductImage.is_preview == True
            ).first()
            
            if not preview_image:
                preview_image = db.query(ProductImage).filter(
                    ProductImage.product_id == product.id
                ).first()

            result["product"] = {
                "id": product.id,
                "title": product.title,
                "slug": product.slug,
                "preview_image": preview_image.image if preview_image else None
            }
            
            if product.supplier:
                result["supplier"] = product.supplier

        elif req_type == "supplier":
            supplier = db.query(Supplier).options(joinedload(Supplier.supplier_type)).filter(Supplier.slug == slug, Supplier.deleted_at == None).first()
            if not supplier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supplier not found"
                )
            result["supplier"] = supplier
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid type. Must be 'product' or 'supplier'."
            )
            
        return result

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching product/supplier data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not fetch product/supplier data."
        )
        
def fetch_active_leads(db: Session):
    # print('2222222222222')
    return db.query(Enquiry).count()

def retrieve_all_enquiries(filters: EnquiryFilterSchema, db: Session, is_quote_form: bool = False):
    from sqlalchemy import select, and_

    if is_quote_form:
        query = db.query(
            Enquiry.id,
            Enquiry.enquiry_number,
            Enquiry.name,
            Enquiry.email,
            Enquiry.phone,
            Enquiry.status,
            Enquiry.created_at,
            Enquiry.updated_at
        ).filter(
            Enquiry.is_quote_form == is_quote_form
        )
    else:
        query = db.query(
            Enquiry.id,
            Enquiry.enquiry_number,
            Enquiry.name,
            Enquiry.email,
            Enquiry.phone,
            Enquiry.status,
            Enquiry.created_at,
            Enquiry.updated_at,
            Product.title.label("product_name"),
            Product.slug.label("product_slug"),
            ProductImage.image.label("product_image")
        ).outerjoin(
            Product, Enquiry.product_id == Product.id
        ).outerjoin(
            ProductImage, and_(ProductImage.product_id == Product.id, ProductImage.is_preview == True)
        ).filter(
            Enquiry.is_quote_form == is_quote_form
        )
    
    if filters.search_string:
        search = f"%{filters.search_string}%"
        query = query.filter(
            or_(
                Enquiry.enquiry_number.ilike(search),
                Enquiry.name.ilike(search),
                Enquiry.email.ilike(search),
                Enquiry.phone.ilike(search),
                Enquiry.request_title.ilike(search),
                Enquiry.message.ilike(search),
                Enquiry.business_email.ilike(search),
                Enquiry.company_name.ilike(search)
            )
        )
        
    if filters.start_date:
        query = query.filter(Enquiry.created_at >= filters.start_date)
    if filters.end_date:
        query = query.filter(Enquiry.created_at < filters.end_date + timedelta(days=1))
        
    if filters.sort_order == "asc":
        query = query.order_by(asc(Enquiry.created_at))
    else:
        query = query.order_by(desc(Enquiry.created_at))
        
    total_count = query.count()
    
    offset = (filters.page - 1) * filters.per_page
    query = query.offset(offset).limit(filters.per_page)
    
    enquiries = query.all()
    
    result_list = [
        {
            "id": row.id,
            "enquiry_number": row.enquiry_number,
            "name": row.name,
            "email": row.email,
            "phone": row.phone,
            "status": row.status,
            "product_name": getattr(row, 'product_name', None),
            "product_slug": getattr(row, 'product_slug', None),
            "product_image": getattr(row, 'product_image', None),
            "created_at": row.created_at,
            "updated_at": row.updated_at
        }
        for row in enquiries
    ]
        
    return result_list, total_count


def retrieve_enquiry_by_enquiry_number(enquiry_number: str, enquiry_type: str, db: Session):

    query = db.query(
            Enquiry.id,
            Enquiry.enquiry_number,
            Enquiry.name,
            Enquiry.email,
            Enquiry.phone,
            Enquiry.status,
            Enquiry.reason_for_contacting,
            Enquiry.request_title,
            Enquiry.delivery_location,
            Enquiry.quantity,
            Enquiry.request_type,
            Enquiry.message,
            Enquiry.business_email,
            Enquiry.company_name,
            Enquiry.forward_to_other,
            Enquiry.supplier_id,
            Enquiry.product_id,
            Enquiry.created_at,
            Enquiry.updated_at,
        )

    if enquiry_type == "inquiry":
        query = query.add_columns(
            Product.title.label("product_name"),
            Product.slug.label("product_slug"),
            ProductImage.image.label("product_image"),
            Supplier.name.label("supplier_name"),
            Supplier.slug.label("supplier_slug")
        )
        query = query.outerjoin(
            Product, Enquiry.product_id == Product.id
        ).outerjoin(
            ProductImage, and_(ProductImage.product_id == Product.id, ProductImage.is_preview == True)
        ).outerjoin(
            Supplier, Enquiry.supplier_id == Supplier.id
        )
    query = query.filter(
        Enquiry.enquiry_number == enquiry_number
    )
    # print('--------------------------------')
    # print(query.statement.compile(compile_kwargs={"literal_binds": True}))
    # print('--------------------------------')
    query = query.filter(
        Enquiry.enquiry_number == enquiry_number
    ).first()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enquiry not found"
        )
    return query

    # return {
    #     "id": query.id,
    #     "enquiry_number": query.enquiry_number,
    #     "name": getattr(query, 'name', None),
    #     "email": getattr(query, 'email', None),
    #     "phone": getattr(query, 'phone', None),
    #     "status": getattr(query, 'status', None),
    #     "reason_for_contacting": getattr(query, 'reason_for_contacting', None),
    #     "request_title": getattr(query, 'request_title', None),
    #     "delivery_location": getattr(query, 'delivery_location', None),
    #     "quantity": getattr(query, 'quantity', None),
    #     "request_type": getattr(query, 'request_type', None),
    #     "message": getattr(query, 'message', None),
    #     "business_email": getattr(query, 'business_email', None),
    #     "company_name": getattr(query, 'company_name', None),
    #     "forward_to_other": getattr(query, 'forward_to_other', None),
    #     "supplier_id": getattr(query, 'supplier_id', None),
    #     "product_id": getattr(query, 'product_id', None),
    #     "product_name": getattr(query, 'product_name', None),
    #     "product_slug": getattr(query, 'product_slug', None),
    #     "product_image": getattr(query, 'product_image', None),
    #     "supplier_name": getattr(query, 'supplier_name', None),
    #     "supplier_slug": getattr(query, 'supplier_slug', None),
    #     "created_at": getattr(query, 'created_at', None),
    #     "updated_at": getattr(query, 'updated_at', None)
    # }


def update_enquiry_by_enquiry_number(enquiry_number: str, db: Session, enquiry_update_schema: EnquiryUpdateSchema):
    try:
        query = db.query(Enquiry).filter(
            Enquiry.enquiry_number == enquiry_number
        ).first()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enquiry not found"
            )
        
        update_data = enquiry_update_schema.model_dump(exclude_unset=True) if hasattr(enquiry_update_schema, 'model_dump') else enquiry_update_schema.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(query, key, value)
        
        db.commit()
        db.refresh(query)
        return query
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating enquiry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Could not update enquiry."
        )
        
