import hashlib
import os
import secrets
from datetime import datetime, timedelta

from fastapi import Depends, Header, HTTPException
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import AdminUser


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
TOKEN_TTL = timedelta(hours=8)
_tokens: dict[str, tuple[int, datetime]] = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def issue_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    _tokens[hashlib.sha256(token.encode()).hexdigest()] = (user_id, datetime.utcnow() + TOKEN_TTL)
    return token


def get_current_admin(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> AdminUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    digest = hashlib.sha256(authorization[7:].encode()).hexdigest()
    record = _tokens.get(digest)
    if not record or record[1] <= datetime.utcnow():
        _tokens.pop(digest, None)
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    user = db.get(AdminUser, record[0])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    return user


def get_optional_admin(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> AdminUser | None:
    if not authorization:
        return None
    try:
        return get_current_admin(authorization, db)
    except HTTPException:
        return None


def ensure_admin(db: Session):
    if db.scalar(select(AdminUser).limit(1)):
        return
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    if not username or not password:
        raise RuntimeError("ADMIN_USERNAME and ADMIN_PASSWORD are required to create the first administrator")
    db.add(AdminUser(username=username, password_hash=hash_password(password)))
    db.commit()
