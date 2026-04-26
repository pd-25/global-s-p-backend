from datetime import datetime
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey, text
from sqlalchemy.orm import relationship


class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    about = Column(Text, nullable=True)
    busines_doc = Column(Text, nullable=True)
    logo = Column(Text, nullable=True)
    zipcode = Column(String(20), nullable=True)
    city = Column(String(255), nullable=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=True)
    address = Column(Text, nullable=True)
    address_two = Column(Text, nullable=True)
    delivery_area = Column(String(255), nullable=True)
    founded_year = Column(Integer, nullable=True)
    employee_strength = Column(String(255), nullable=True)
    supplier_type_id = Column(Integer, ForeignKey("supplier_types.id"), nullable=True)
    business_sector = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    is_accept_terms = Column(Boolean, default=True)
    vat_number = Column(String(100), nullable=True)
    company_site = Column(String(255), nullable=True)
    company_phone_number = Column(String(50), nullable=True)
    company_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  '))
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    country = relationship("Country", backref="suppliers")
    supplier_type = relationship("SupplierType", backref="suppliers")
    documents = relationship("SupplierDocument", back_populates="supplier", cascade="all, delete-orphan")
