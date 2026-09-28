"""Unit tests for JWT Token generation, decoding, expiration, and types using python-jose."""

from datetime import timedelta
import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    decode_token,
)


class TestJWTTokens:
    """Test suite covering python-jose JWT token operations."""

    def test_access_token_creation_and_decoding(self):
        """create_access_token produces verifiable JWT with subject, roles, and access type."""
        user_id = 101
        roles = ["user", "manager"]
        token = create_access_token(subject=user_id, roles=roles)

        assert isinstance(token, str)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"
        assert payload["roles"] == roles
        assert "exp" in payload
        assert "iat" in payload

    def test_refresh_token_creation_and_decoding(self):
        """create_refresh_token produces verifiable JWT with refresh type and extended expiry."""
        user_id = 202
        token = create_refresh_token(subject=user_id)

        assert isinstance(token, str)
        payload = decode_refresh_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload

    def test_token_type_separation(self):
        """Access token cannot be decoded as refresh token and vice versa."""
        user_id = 303
        access_tok = create_access_token(subject=user_id)
        refresh_tok = create_refresh_token(subject=user_id)

        # Access token decoded expecting 'refresh' type must fail
        assert decode_token(access_tok, expected_type="refresh") is None
        assert decode_refresh_token(access_tok) is None

        # Refresh token decoded expecting 'access' type must fail
        assert decode_token(refresh_tok, expected_type="access") is None
        assert decode_access_token(refresh_tok) is None

    def test_expired_token_handling(self):
        """decode_token returns None when token expiration has passed."""
        user_id = 404
        # Create token that expired 10 minutes ago
        expired_token = create_access_token(
            subject=user_id,
            expires_delta=timedelta(minutes=-10),
        )

        payload = decode_access_token(expired_token)
        assert payload is None

    def test_tampered_token_rejection(self):
        """decode_token rejects tokens whose payload or signature has been modified."""
        valid_token = create_access_token(subject=505)
        # Tamper with the token string
        tampered_token = valid_token[:-4] + "AAAA"

        payload = decode_access_token(tampered_token)
        assert payload is None

    def test_custom_secret_key_rejection(self):
        """Token encoded with wrong secret key is rejected."""
        wrong_token = jwt.encode(
            {"sub": "999", "type": "access"},
            "completely-wrong-secret-key-1234567890",
            algorithm=settings.ALGORITHM,
        )
        payload = decode_access_token(wrong_token)
        assert payload is None
