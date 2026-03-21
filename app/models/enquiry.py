from sqlalchemy.orm import relationship

from app.database.base_class import Base
from datetime import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text

class Enquiry(Base):
    __tablename__ = 'enquiries'

    id = Column(Integer, primary_key=True)
    reason_for_contacting = Column(Text, nullable=True)
    request_title = Column(Text, nullable=True)
    delivery_location = Column(Text, nullable=True)
    quantity = Column(String(255), nullable=True)
    request_type = Column(String(255), nullable=True)
    message = Column(Text, nullable=True)
    business_email = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    forward_to_other = Column(Boolean, nullable=True, default=0, server_default="0")
    is_quote_form = Column(Boolean, nullable=True, default=0, server_default="0", comment="submitted from quote form = 1 and join enquery_supplier_types table, submitted from contact supplier button = 0 and use supplier_id colum")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True, comment="submitted from contact supplier button will have this value, submitted from quote form will have null value")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
    
    
    supplier = relationship("Supplier", backref="enquiries")
    product = relationship("Product", backref="enquiries")
    files = relationship("EnquiryFiles", back_populates="enquiry", cascade="all, delete-orphan")
    enquiry_supplier_types = relationship("EnquirySupplierType", back_populates="enquiry", cascade="all, delete-orphan")