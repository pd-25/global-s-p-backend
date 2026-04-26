from typing import List
from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.admin import Admin
from app.schemas.supplier_schema import (
    SupplierFilterSchema,
    SupplierResponseSchema,
    CreateSupplierSchema,
    UpdateSupplierSchema,
)
from app.schemas.response import APIResponse
from app.services.auth.auth_service import get_current_user
from app.services.suppliers.supplier_service import (
    create_supplier_service,
    delete_supplier_service,
    retrieve_all_suppliers,
    retrieve_single_supplier,
    update_supplier_service,
)
from app.utils.file_utils import validate_image_file, validate_document_file

supplier_router = APIRouter()


@supplier_router.get(
    "/",
    response_model=APIResponse[List[SupplierResponseSchema]],
    status_code=status.HTTP_200_OK,
    description="Returns a paginated list of suppliers with optional search and filters",
)
def get_suppliers(
    filters: SupplierFilterSchema = Depends(),
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    suppliers, total_count = retrieve_all_suppliers(filters=filters, db=db)

    return APIResponse(
        success=True,
        message="Suppliers fetched successfully",
        data=suppliers,
        meta={
            "count": len(suppliers),
            "total": total_count,
            "page": filters.page,
            "per_page": filters.per_page,
        },
    )


@supplier_router.get(
    "/{slug}",
    response_model=APIResponse[SupplierResponseSchema],
    status_code=status.HTTP_200_OK,
    description="Returns a single supplier by its slug",
)
def get_supplier(
    slug: str,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    supplier = retrieve_single_supplier(slug=slug, db=db)

    return APIResponse(
        success=True,
        message="Supplier fetched successfully",
        data=supplier,
    )


@supplier_router.post(
    "/",
    response_model=APIResponse[SupplierResponseSchema],
    status_code=status.HTTP_201_CREATED,
    description="Creates a new supplier",
)
async def create_supplier(
    request: Request,
    current_user: Admin = Depends(get_current_user),
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
    # print("doc_indices------------")
    # print(doc_indices)
    # print("doc_indices--------")         
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

    # print('documents++++++++++++++++++')
    # print(documents)
    # print("documents++++++++++++++++++")
    # return
    response = create_supplier_service(supplier_data=supplier_data, db=db, documents=documents)

    return APIResponse(
        success=True,
        message="Supplier created successfully",
        data=response,
    )


@supplier_router.put(
    "/{slug}",
    response_model=APIResponse[SupplierResponseSchema],
    status_code=status.HTTP_200_OK,
    description="Updates an existing supplier by its slug",
)
async def update_supplier(
    slug: str,
    supplier_data: UpdateSupplierSchema = Depends(UpdateSupplierSchema.as_form),
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    if supplier_data.logo:
        validate_image_file(supplier_data.logo)

    response = update_supplier_service(
        slug=slug, supplier_data=supplier_data, db=db
    )

    return APIResponse(
        success=True,
        message="Supplier updated successfully",
        data=response,
    )


@supplier_router.delete(
    "/{slug}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    description="Soft-deletes a supplier by its slug",
)
def delete_supplier(
    slug: str,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    delete_supplier_service(slug=slug, db=db)

    return APIResponse(
        success=True,
        message="Supplier deleted successfully",
    )