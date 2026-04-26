from datetime import datetime
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, Text, ForeignKey, text
from sqlalchemy.orm import relationship


class SupplierDocument(Base):
    __tablename__ = 'supplier_documents'

    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    name = Column(Text, nullable=False)
    document = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, server_default="1")
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  '))
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    supplier = relationship("Supplier", back_populates="documents")
