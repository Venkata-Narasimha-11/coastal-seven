from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Configure passlib CryptContext with bcrypt scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Generate a secure salted bcrypt hash for a plain text password using passlib."""
    return pwd_context.hash(password)


def hash_password(password: str) -> str:
    """Alias for get_password_hash for backward compatibility."""
    return get_password_hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored bcrypt hash using passlib."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[dict] = None,
) -> str:
    """Encode JWT access token with expiry claim and token type using python-jose."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "sub": str(subject),
        "type": "access",
    }
    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Encode JWT refresh token with extended validity using python-jose."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        # Default refresh token expiry: 7 days
        expire = now + timedelta(days=getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7))

    to_encode = {
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "sub": str(subject),
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(
        to_encode,
        getattr(settings, "REFRESH_SECRET_KEY", settings.SECRET_KEY),
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_token(
    token: str,
    secret_key: Optional[str] = None,
    expected_type: Optional[str] = None,
) -> Optional[dict]:
    """Decode and validate a JWT token using python-jose with optional type verification."""
    key = secret_key or settings.SECRET_KEY
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[settings.ALGORITHM],
        )
        if expected_type:
            token_type = payload.get("type")
            if token_type and token_type != expected_type:
                return None
        return payload
    except (JWTError, Exception):
        return None


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    return decode_token(token, secret_key=settings.SECRET_KEY, expected_type="access")


def decode_refresh_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT refresh token."""
    secret = getattr(settings, "REFRESH_SECRET_KEY", settings.SECRET_KEY)
    return decode_token(token, secret_key=secret, expected_type="refresh")

