from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from ..auth import authenticate_admin, create_access_token
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_admin(form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="bad credentials")
    token = create_access_token(user["username"], user["role"], settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {"access_token": token, "token_type": "bearer"}
