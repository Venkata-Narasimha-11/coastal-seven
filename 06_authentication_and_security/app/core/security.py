"""Security module implementing passlib + bcrypt password hashing and python-jose JWT authentication."""

from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ------------------------------------------------------------------------------
# 1. PASSWORD SECURITY: Passlib + Bcrypt CryptContext
# ------------------------------------------------------------------------------
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def get_password_hash(password: str) -> str:
    """Generate a secure, salted bcrypt hash for a plain text password using passlib."""
    return pwd_context.hash(password)


def hash_password(password: str) -> str:
    """Alias for get_password_hash for API consistency."""
    return get_password_hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a stored bcrypt hash using passlib."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


# ------------------------------------------------------------------------------
# 2. JWT AUTHENTICATION: Python-Jose Access & Refresh Token Management
# ------------------------------------------------------------------------------
def create_access_token(
    subject: Union[str, Any],
    roles: Optional[List[str]] = None,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict] = None,
) -> str:
    """
    Encode a signed JWT access token using python-jose.
    Includes subject (user ID), expiration, issued-at, token type, and roles.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: dict = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
        "roles": roles or ["user"],
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Encode a signed JWT refresh token using python-jose with extended validity.
    Designated strictly for token refresh exchanges (token type: "refresh").
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_token(
    token: str,
    secret_key: Optional[str] = None,
    expected_type: Optional[str] = None,
) -> Optional[dict]:
    """
    Decode and validate signature, expiration, and token type using python-jose.
    Returns payload dictionary or None if invalid or expired.
    """
    key = secret_key or settings.SECRET_KEY
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[settings.ALGORITHM],
        )
        if expected_type:
            token_type = payload.get("type")
            if token_type != expected_type:
                return None
        return payload
    except (JWTError, Exception):
        return None


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    return decode_token(
        token,
        secret_key=settings.SECRET_KEY,
        expected_type="access",
    )


def decode_refresh_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT refresh token."""
    return decode_token(
        token,
        secret_key=settings.REFRESH_SECRET_KEY,
        expected_type="refresh",
    )
