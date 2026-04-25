import os
import json
from sqlalchemy.orm import Session
from app.models.country import Country

class CountrySeeder:

    def seed(self, db: Session):
        try:
            json_file_path = os.path.join(
                os.path.dirname(__file__), 
                "raw_data/country_data.json"
            )

            if not os.path.exists(json_file_path):
                print(f"❌ JSON file not found at: {json_file_path}")
                return

            with open(json_file_path, 'r') as file:
                country_data = json.load(file)

            # ✅ Fetch existing country codes in ONE query
            existing_codes = {
                code.lower() for (code,) in db.query(Country.country_code).all()
            }
            # print('existing_codes', existing_codes)
            # return

            countries_to_add = []

            for single_country in country_data:
                code = single_country['code']

                # ✅ Skip if already exists
                if code.lower() in existing_codes:
                    continue

                country = Country(
                    name=single_country['name'],
                    country_code=code,
                    country_flag="https://cdn.pixabay.com/photo/2015/11/12/16/03/flag-1040555_640.png"
                )
                countries_to_add.append(country)

            if countries_to_add:
                db.add_all(countries_to_add)
                db.commit()

            print(f"✅ Added: {len(countries_to_add)} countries")
            print(f"⏭️ Skipped: {len(country_data) - len(countries_to_add)} countries")

        except Exception as e:
            db.rollback()
            print(f'❌ Error occurred: {e}')
            raise e

    def run(self, db: Session):
        return self.seed(db=db)