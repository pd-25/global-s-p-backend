from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.hashing import Hasher
from app.core.security import create_access_token
from app.database.session import get_db
from app.models.admin import Admin
from app.services.auth.auth_service import authenticate_user, get_current_user

auth_router = APIRouter()

@auth_router.post('/token')
def login(login_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
     user = authenticate_user(login_data.username, login_data.password, db)
     if not user:
        raise HTTPException(
            detail="Incorrect cradentials",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
     access_token = create_access_token(data={"sub": user.email})
     return {"access_token": access_token, "token_type": "bearer"}
 
@auth_router.get("/me")
def me(db: Session = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    return current_user
@auth_router.post("/logout")
def logout(current_user: Admin = Depends(get_current_user)):
    # In a stateless JWT implementation, logout is primarily handled by the client
    # by deleting the token. We return a success response here.
    return {"success": True, "message": "Successfully logged out"}
