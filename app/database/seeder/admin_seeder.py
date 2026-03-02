from sqlalchemy.orm import Session

from app.core.hashing import Hasher
from app.models.admin import Admin


class AdminSeeder:
    def seed(self, db: Session):
        # data = {
        #     'name': 'Admin GSE',
        #     'email': 'admin@mail.com',
        #     'password': Hasher.make_hash_password('12345'),
        #     'is_subadmin': 0
        # }
        hasp = Hasher.make_hash_password('12345')
        print("seing-------------")
        print("hasp------------- ", hasp)
        # return
        admin_data = Admin(
            name = 'Admin GSE',
            email = 'admin1@mail.com',
            password = hasp,
            is_subadmin = 0
        )
        db.add(admin_data)
        db.commit()
        db.refresh(admin_data)
        
    def run(self, db: Session):
        self.seed(db=db)