from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.admin import Admin
from app.schemas.country_schema import (
    CountryFilterSchema,
    CountryResponseSchema,
    CreateCountrySchema,
    UpdateCountrySchema,
)
from app.schemas.response import APIResponse
from app.services.auth.auth_service import get_current_user
from app.services.countries.country_service import (
    create_country_service,
    delete_country_service,
    retrieve_all_countries,
    retrieve_single_country,
    update_country_service,
)
from app.utils.file_utils import validate_image_file

country_router = APIRouter()


@country_router.get(
    "/",
    response_model=APIResponse[List[CountryResponseSchema]],
    status_code=status.HTTP_200_OK,
    description="Returns a paginated list of countries with optional search",
)
def get_countries(
    filters: CountryFilterSchema = Depends(),
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    countries, total_count = retrieve_all_countries(filters=filters, db=db)

    return APIResponse(
        success=True,
        message="Countries fetched successfully",
        data=countries,
        meta={
            "count": len(countries),
            "total": total_count,
            "page": filters.page,
            "per_page": filters.per_page,
        },
    )


@country_router.get(
    "/{country_id}",
    response_model=APIResponse[CountryResponseSchema],
    status_code=status.HTTP_200_OK,
    description="Returns a single country by its ID",
)
def get_country(
    country_id: int,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    country = retrieve_single_country(country_id=country_id, db=db)

    return APIResponse(
        success=True,
        message="Country fetched successfully",
        data=country,
    )


@country_router.post(
    "/",
    response_model=APIResponse[CountryResponseSchema],
    status_code=status.HTTP_201_CREATED,
    description="Creates a new country",
)
async def create_country(
    current_user: Admin = Depends(get_current_user),
    country_data: CreateCountrySchema = Depends(CreateCountrySchema.as_form),
    db: Session = Depends(get_db),
):
    if country_data.country_flag:
        validate_image_file(country_data.country_flag)
    response = create_country_service(country_data=country_data, db=db)

    return APIResponse(
        success=True,
        message="Country created successfully",
        data=response,
    )


@country_router.put(
    "/{country_id}",
    response_model=APIResponse[CountryResponseSchema],
    status_code=status.HTTP_200_OK,
    description="Updates an existing country by its ID",
)
async def update_country(
    country_id: int,
    current_user: Admin = Depends(get_current_user),
    country_data: UpdateCountrySchema = Depends(UpdateCountrySchema.as_form),
    db: Session = Depends(get_db),
):
    if country_data.country_flag:
        validate_image_file(country_data.country_flag)
    response = update_country_service(
        country_id=country_id, country_data=country_data, db=db
    )

    return APIResponse(
        success=True,
        message="Country updated successfully",
        data=response,
    )


@country_router.delete(
    "/{country_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    description="Soft-deletes a country by its ID",
)
def delete_country(
    country_id: int,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user),
):
    delete_country_service(country_id=country_id, db=db)

    return APIResponse(
        success=True,
        message="Country deleted successfully",
    )
