from sqlalchemy import Column, Integer, Text, text, Boolean, DateTime, ForeignKey
from app.database.base_class import Base
from datetime import datetime
class BannerImage(Base):
    __tablename__ = 'banner_images'
    
    id = Column(Integer, primary_key=True)
    image = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, default=datetime.now, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  '))
