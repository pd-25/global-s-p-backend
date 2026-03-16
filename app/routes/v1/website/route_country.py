from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.country_schema import CountryResponseSchema
from app.schemas.response import APIResponse
from app.services.countries.country_service import fetch_countries_website

country_router = APIRouter()



@country_router.get(
    '/',
    response_model=APIResponse[List[CountryResponseSchema]],
    status_code=status.HTTP_200_OK,
    description="This api will list all the countries"
)
def get_countries(db: Session = Depends(get_db)):
    countries = fetch_countries_website(db=db)
    return APIResponse(
        success=True,
        message="Valuable Partners Fetched Successfully",
        data=countries,
        meta={},
    )
