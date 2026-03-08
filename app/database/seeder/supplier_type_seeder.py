from faker import Faker
from sqlalchemy.orm import Session

from app.models.supplier_type import SupplierType

fake = Faker()

# Realistic supplier type names
SUPPLIER_TYPE_NAMES = [
    "Manufacturer",
    "Wholesaler",
    "Distributor",
    "Retailer",
    "Importer",
    "Exporter",
    "Trading Company",
    "Agent",
    "Service Provider",
    "Raw Material Supplier",
]


class SupplierTypeSeeder:

    def seed(self, db: Session, count: int = 10):
        try:
            supplier_types = []

            names_to_use = SUPPLIER_TYPE_NAMES[:count]

            for name in names_to_use:
                supplier_type = SupplierType(name=name)
                supplier_types.append(supplier_type)

            db.add_all(supplier_types)
            db.commit()

            for st in supplier_types:
                db.refresh(st)

            print(f"✅ Seeded {len(supplier_types)} supplier types")
            return supplier_types

        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding supplier types: {e}")
            raise e

    def run(self, db: Session):
        return self.seed(db=db)
