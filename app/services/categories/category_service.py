from sqlalchemy.orm import Session
from app.models.category import Categories

def retrieve_all_blogs(db: Session):
    blogs = db.query(Categories).all()
    return blogs
    