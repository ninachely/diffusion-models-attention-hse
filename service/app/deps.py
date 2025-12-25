from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user or not user.get("username"):
        raise HTTPException(status_code=401, detail="invalid token")
    return user

def require_admin(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    return user
