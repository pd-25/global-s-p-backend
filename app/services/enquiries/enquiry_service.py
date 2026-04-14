import logging
from typing import Any
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.enquiry import Enquiry
from app.models.enquiry_files import EnquiryFiles
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.product_image import ProductImage
from app.schemas.enquiry_schema import CreateEnquirySchema
from app.utils.file_utils import save_upload_file
from app.models.enquiry_supplier_types import EnquirySupplierType
import json

logger = logging.getLogger(__name__)

ENQUIRY_FILE_DIR = "app/static/uploads/enquiries"

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
                    file_path = save_upload_file(file, ENQUIRY_FILE_DIR)
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
