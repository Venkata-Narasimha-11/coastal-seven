"""Unit tests for Password Security using passlib + bcrypt."""

import pytest
from pydantic import ValidationError

from app.core.security import get_password_hash, hash_password, verify_password
from app.schemas.auth import UserRegister


class TestPasswordSecurity:
    """Test suite covering passlib + bcrypt hashing and verification."""

    def test_bcrypt_hash_generation(self):
        """get_password_hash produces a valid bcrypt hash string."""
        raw_password = "SecurePassword123!"
        hashed = get_password_hash(raw_password)

        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
        assert len(hashed) >= 59

    def test_password_verification_success(self):
        """verify_password returns True for matching credentials."""
        password = "MySecretPassword2026!"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """verify_password returns False for non-matching credentials."""
        password = "CorrectPassword123!"
        hashed = get_password_hash(password)

        assert verify_password("WrongPassword123!", hashed) is False
        assert verify_password("", hashed) is False

    def test_unique_salts_for_identical_passwords(self):
        """Salts are unique per hash even for identical plain-text passwords."""
        password = "IdenticalPassword999!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_alias_hash_password(self):
        """hash_password acts as an alias for get_password_hash."""
        password = "AliasPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_password_strength_validator(self):
        """UserRegister schema rejects weak passwords without letters or digits."""
        # Missing digits
        with pytest.raises(ValidationError) as exc1:
            UserRegister(
                username="testuser",
                email="test@example.com",
                password="OnlyLetters!",
                confirm_password="OnlyLetters!",
            )
        assert "at least one digit" in str(exc1.value)

        # Missing letters
        with pytest.raises(ValidationError) as exc2:
            UserRegister(
                username="testuser",
                email="test@example.com",
                password="1234567890!",
                confirm_password="1234567890!",
            )
        assert "at least one letter" in str(exc2.value)

    def test_password_confirmation_match_validator(self):
        """UserRegister schema rejects mismatching password and confirm_password."""
        with pytest.raises(ValidationError) as exc:
            UserRegister(
                username="testuser",
                email="test@example.com",
                password="ValidPass123!",
                confirm_password="DifferentPass123!",
            )
        assert "do not match" in str(exc.value)
