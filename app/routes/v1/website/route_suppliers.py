from typing import List

from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.supplier_schema import CreateSupplierSchema, SupplierResponseSchema, ValuablePartnerSchema
from app.schemas.response import APIResponse
from app.services.suppliers.supplier_service import create_supplier_service, fetch_valuable_partners
from app.utils.file_utils import validate_image_file, validate_document_file
supplier_router = APIRouter()



@supplier_router.get(
    '/valuable-partners',
    response_model=APIResponse[List[ValuablePartnerSchema]],
    status_code=status.HTTP_200_OK,
    description="This api will list all the valuable partners"
)
def get_valuable_partners(db: Session = Depends(get_db)):
    valuable_partners = fetch_valuable_partners(db=db)
    return APIResponse(
        success=True,
        message="Valuable Partners Fetched Successfully",
        data=valuable_partners,
        meta={},
    )


#create new supplier from frontend
@supplier_router.post(
    '/create',
    response_model=APIResponse[SupplierResponseSchema],
    status_code=status.HTTP_200_OK,
    description="This api will create a new supplier"
)
async def create_supplier(
    request: Request,
    supplier_data: CreateSupplierSchema = Depends(CreateSupplierSchema.as_form), 
    db: Session = Depends(get_db)
):
    if supplier_data.logo:
        validate_image_file(supplier_data.logo)

    form_data = await request.form()
    
    documents = []
    doc_indices = set()
    for key in form_data.keys():
        if key.startswith("documents["):
            try:
                idx = int(key.split("[")[1].split("]")[0])
                doc_indices.add(idx)
            except ValueError:
                pass
                
    if len(doc_indices) > 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Maximum 5 documents can be uploaded per supplier"
        )
        
    for i in doc_indices:
        doc_name = form_data.get(f"documents[{i}][name]")
        doc_file = form_data.get(f"documents[{i}][file]")
        
        if doc_name and doc_file:
            validate_document_file(doc_file)
            documents.append({"name": doc_name, "file": doc_file})

    response = create_supplier_service(supplier_data=supplier_data, db=db, documents=documents)

    return APIResponse(
        success=True,
        message="Supplier created successfully",
        data=response,
    )

