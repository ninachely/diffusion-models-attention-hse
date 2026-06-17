from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from .config import settings

def authenticate_admin(username: str, password: str):
    if username == settings.ADMIN_USER and password == settings.ADMIN_PASS:
        return {"username": username, "role": "admin"}
    return None

def create_access_token(sub: str, role: str, minutes: int):
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {"sub": sub, "role": role, "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        sub = payload.get("sub")
        role = payload.get("role")
        if not sub or not role:
            return None
        return {"username": sub, "role": role}
    except JWTError:
        return None
