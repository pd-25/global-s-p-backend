from sqlalchemy.orm import relationship

from app.database.base_class import Base
from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text

class EnquirySupplierType(Base):
    __tablename__ = 'enquiry_suppliers_types'

    id = Column(Integer, primary_key=True)
    enquiry_id = Column(Integer, ForeignKey("enquiries.id"), nullable=True)
    supplier_type_id = Column(Integer, ForeignKey("supplier_types.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    
    supplier = relationship("SupplierType", backref="enquiry_suppliers_types")
    enquiry = relationship("Enquiry", back_populates="enquiry_supplier_types")