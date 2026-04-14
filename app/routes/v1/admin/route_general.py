import asyncio

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db, SESSIONLOCAL
from app.schemas.general_schema import KPIResponse
from app.schemas.response import APIResponse
from app.services.categories.category_service import fetch_total_categories
from app.services.enquiries.enquiry_service import fetch_active_leads
from app.services.products.product_service import fetch_total_products
from app.services.suppliers.supplier_service import fetch_active_suppliers


general_router = APIRouter()


def _run_with_own_session(func):
    """Run a service function with its own DB session (thread-safe)."""
    db = SESSIONLOCAL()
    try:
        return func(db=db)
    finally:
        db.close()


@general_router.get(
    '/kpis', 
    response_model=APIResponse[KPIResponse],
    status_code=status.HTTP_200_OK,
    description="This endpoint will return the kpi for admin dashboard with total products, active_leads, enquiry_request and total_categories"
)
async def generate_kpis():
    total_products, active_leads, active_suppliers, total_categories = await asyncio.gather(
        asyncio.to_thread(_run_with_own_session, fetch_total_products),
        asyncio.to_thread(_run_with_own_session, fetch_active_leads),
        asyncio.to_thread(_run_with_own_session, fetch_active_suppliers),
        asyncio.to_thread(_run_with_own_session, fetch_total_categories)
    )
    
    return APIResponse(
        success=True,
        message="Kpi fetched sucessfully",
        data= {
            "total_products": total_products,
            "active_leads": active_leads,
            "active_suppliers": active_suppliers,
            "total_categories": total_categories
        }
    )

