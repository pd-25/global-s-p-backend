import sys
import os

# Add the project root to sys.path to allow imports from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.database.seeder.categories_seeder import CategoriesSeeder
from app.database.session import get_db

class DatabaseSeeder:
    def run(self):
        print("Starting Database Seeder...")
        # Manually get the session generator and the session object
        db_gen = get_db()
        db = next(db_gen)
        try:
            # Call individual seeders here, passing the db session
            CategoriesSeeder().run(db=db)
            print("✅ Database Seeding Completed Successfully!")
        finally:
            try:
                next(db_gen) 
            except StopIteration:
                pass
            db_gen.close()

if __name__ == "__main__":
    seeder = DatabaseSeeder()
    seeder.run()
