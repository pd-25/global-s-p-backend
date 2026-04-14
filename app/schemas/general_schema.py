from pydantic import BaseModel

class CategorySubCategoryCount(BaseModel):
    total_main_categories: int
    total_sub_categories: int

class KPIResponse(BaseModel):
    total_products: int
    active_leads: int
    active_suppliers: int
    total_categories: CategorySubCategoryCount
    
