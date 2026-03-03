from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.hashing import Hasher
from app.database.session import get_db
from app.models.admin import Admin


def authenticate_user(email: str, password: str, db: Session):
    user = get_user_by_email(email=email, db=db)
    print(user)
    if not user:
        return False
    if not Hasher.verify_password(password, user.password):
        return False
    return user

def get_user_by_email(email: str, db: Session):
    user = db.query(Admin).filter(Admin.email==email).first()
    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(token: str= Depends(oauth2_scheme), db: Session=Depends(get_db)):
    credentials_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials, Please login again"
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exceptions
    except JWTError:
        raise credentials_exceptions
    user = get_user_by_email(email=email, db=db)
    if user is None:
        raise credentials_exceptions
    return user