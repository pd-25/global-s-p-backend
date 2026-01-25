import random
from faker import Faker
from sqlalchemy.orm import Session
from slugify import slugify  # pip install python-slugify

from app.database.session import SessionLocal
from app.database.base_class import Base
from app.database.engine import engine
from app.models.categories import Categories

fake = Faker()


def seed_categories(
    db: Session,
    parent_count: int = 10,
    children_per_parent: int = 5
):
    categories = []

    # ---------- Parent Categories ----------
    parents = []
    for _ in range(parent_count):
        name = fake.unique.word().capitalize()
        parent = Categories(
            name=name,
            slug=slugify(name),
            image=fake.image_url(),
            is_active=True
        )
        parents.append(parent)

    db.add_all(parents)
    db.commit()
    db.refresh(parents[0])

    # ---------- Child Categories ----------
    for parent in parents:
        for _ in range(children_per_parent):
            name = fake.unique.word().capitalize()
            child = Categories(
                name=name,
                slug=slugify(f"{name}-{parent.id}"),
                parent_id=parent.id,
                image=fake.image_url(),
                is_active=True
            )
            categories.append(child)

    db.add_all(categories)
    db.commit()

    print(f"✅ Seeded {len(parents)} parent categories")
    print(f"✅ Seeded {len(categories)} child categories")


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        seed_categories(db)
    finally:
        db.close()


if __name__ == "__main__":
    run()
