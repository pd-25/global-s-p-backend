from database.base_class import Base
from datetime import datetime
from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
class Categories(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    image = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"))
    # Self-referencing relationship
    parent = relationship(
        "Categories",
        remote_side=[id],
        backref="children"
    )
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=False)
    