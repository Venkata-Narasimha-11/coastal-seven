"""Unit tests verifying Pydantic V2 validations: Field, field_validator, and model_validator."""

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserUpdate
from app.schemas.product import ProductCreate, ProductUpdate, ProductBase


class TestPydanticV2Validators:
    """Test suite for Pydantic V2 schema validations."""

    def test_user_create_valid(self):
        """Valid UserCreate payload succeeds and normalizes strings."""
        user = UserCreate(
            username="  Test_User_99  ",
            email="  User.Test@Domain.COM  ",
            password="SecurePassword123!",
            confirm_password="SecurePassword123!",
            full_name="Test User",
        )
        # Check field validator normalization
        assert user.username == "test_user_99"
        assert user.email == "user.test@domain.com"
        assert user.full_name == "Test User"

    def test_user_password_mismatch_raises_model_validator_error(self):
        """Model validator rejects mismatched passwords with clear error."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="mismatch_user",
                email="mismatch@domain.com",
                password="Password123!",
                confirm_password="DifferentPassword456!",
            )
        errors = exc_info.value.errors()
        assert any("Password and confirmation password do not match" in e["msg"] for e in errors)

    def test_user_password_weak_raises_field_validator_error(self):
        """Field validator rejects passwords lacking numbers or letters."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="weak_user",
                email="weak@domain.com",
                password="onlylettersnopassword",
                confirm_password="onlylettersnopassword",
            )
        assert any("at least one digit" in e["msg"] for e in exc_info.value.errors())

    def test_user_invalid_username_regex(self):
        """Field pattern rejects illegal characters in username."""
        with pytest.raises(ValidationError):
            UserCreate(
                username="invalid user with spaces!",
                email="valid@domain.com",
                password="Password123!",
                confirm_password="Password123!",
            )

    def test_product_valid_and_normalization(self):
        """Product SKU is normalized to uppercase and prices rounded to 2 decimals."""
        product = ProductCreate(
            title="Gaming Headset",
            sku="  tech-gh01  ",
            price=89.999,
            discount_price=69.501,
            stock_quantity=15,
            category="Electronics",
            owner_id=1,
        )
        assert product.sku == "TECH-GH01"
        assert product.price == 90.00
        assert product.discount_price == 69.50

    def test_product_discount_greater_than_or_equal_to_price_fails(self):
        """Model validator rejects discount price >= base price."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                title="Faulty Pricing Item",
                sku="TECH-FLT01",
                price=50.00,
                discount_price=60.00,
                category="Electronics",
                owner_id=1,
            )
        assert any("must be strictly less than base price" in e["msg"] for e in exc_info.value.errors())

        # Equal price also fails
        with pytest.raises(ValidationError):
            ProductCreate(
                title="Equal Pricing Item",
                sku="TECH-EQL01",
                price=50.00,
                discount_price=50.00,
                category="Electronics",
                owner_id=1,
            )

    def test_product_sku_regex_pattern(self):
        """Field regex enforces standard format (3-10 chars, hyphen, 2-10 chars)."""
        with pytest.raises(ValidationError):
            ProductCreate(
                title="Bad SKU Item",
                sku="INVALID_SKU_WITHOUT_HYPHEN",
                price=10.00,
                category="Books",
                owner_id=1,
            )

    def test_product_update_model_validator(self):
        """ProductUpdate validates discount < price when both are supplied."""
        with pytest.raises(ValidationError) as exc_info:
            ProductUpdate(price=100.0, discount_price=120.0)
        assert any("strictly less than price" in e["msg"] for e in exc_info.value.errors())
