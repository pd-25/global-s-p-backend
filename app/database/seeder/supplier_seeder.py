import random
from faker import Faker
from slugify import slugify
from sqlalchemy.orm import Session

from app.models.supplier import Supplier
from app.models.supplier_type import SupplierType
from app.models.country import Country

fake = Faker()


class SupplierSeeder:

    def seed(self, db: Session, count: int = 20):
        try:
            # Fetch existing supplier_type and country IDs
            supplier_type_ids = [st.id for st in db.query(SupplierType.id).all()]
            country_ids = [c.id for c in db.query(Country.id).all()]

            if not supplier_type_ids:
                print("⚠️  No supplier types found. Run SupplierTypeSeeder first.")
                return []

            suppliers = []

            for _ in range(count):
                company_name = fake.company()
                slug = slugify(f"{company_name}-{fake.unique.random_int(min=1000, max=99999)}")

                supplier = Supplier(
                    slug=slug,
                    name=company_name,
                    about=fake.paragraph(nb_sentences=3),
                    logo=fake.image_url(),
                    zipcode=fake.zipcode(),
                    city=fake.city(),
                    country_id=random.choice(country_ids) if country_ids else None,
                    address=fake.address(),
                    delivery_area=random.choice(["Local", "National", "International", "Regional"]),
                    founded_year=random.randint(1980, 2024),
                    employee_strength=random.choice([10, 50, 100, 250, 500, 1000, 5000]),
                    supplier_type_id=random.choice(supplier_type_ids),
                    is_verified=random.choice([True, False]),
                    vat_number=fake.bothify(text="??########"),
                    company_site=fake.url(),
                    company_phone_number=fake.phone_number(),
                    company_email=fake.company_email(),
                )
                suppliers.append(supplier)

            db.add_all(suppliers)
            db.commit()

            for s in suppliers:
                db.refresh(s)

            print(f"✅ Seeded {len(suppliers)} suppliers")
            return suppliers

        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding suppliers: {e}")
            raise e

    def run(self, db: Session):
        return self.seed(db=db)
