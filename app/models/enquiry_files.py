from datetime import datetime
from app.database.base_class import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, Text, ForeignKey, text
from sqlalchemy.orm import relationship


class EnquiryFiles(Base):
    __tablename__ = 'enquiry_files'

    id = Column(Integer, primary_key=True)
    enquiry_id = Column(Integer, ForeignKey("enquiries.id"), nullable=False)
    file = Column(Text, nullable=False)
    is_preview = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  '))

    # Relationships
    enquiry = relationship("Enquiry", back_populates="files")
