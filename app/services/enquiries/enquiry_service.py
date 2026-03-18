import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.enquiry import Enquiry
from app.models.enquiry_files import EnquiryFiles
from app.models.product import Product
from app.models.supplier import Supplier
from app.schemas.enquiry_schema import CreateEnquirySchema
from app.utils.file_utils import save_upload_file

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
            reason_for_contacting=enquiry_data.reason_for_contacting,
            request_title=enquiry_data.request_title,
            delivery_location=enquiry_data.delivery_location,
            quantity=enquiry_data.quantity,
            request_type=enquiry_data.request_type,
            message=enquiry_data.message,
            business_email=enquiry_data.business_email,
            company_name=enquiry_data.company_name,
            forward_to_other=enquiry_data.forward_to_other,
            supplier_id=enquiry_data.supplier_id,
            product_id=enquiry_data.product_id,
        )
        
        db.add(new_enquiry)
        db.flush()
        
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
