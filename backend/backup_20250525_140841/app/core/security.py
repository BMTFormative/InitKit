from datetime import datetime, timedelta, timezone
from typing import Any
import uuid
import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(
    data: Any,
    expires_delta: timedelta | None = None
) -> str:
    # Handle different types of data
    if hasattr(data, "copy"):
        # It's a dictionary-like object
        to_encode = data.copy()
    elif isinstance(data, uuid.UUID):
        # It's a UUID, convert to string and create a dict
        to_encode = {"sub": str(data)}
    else:
        # For other types, convert to string and create a dict
        to_encode = {"sub": str(data)}
    
    # Set expiration
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
