from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.constants import RoleName
from app.schemas.auth import LoginRequest, SignupRequest, VerifyOTPRequest


def test_signup_normalizes_email_and_restricts_role() -> None:
    request = SignupRequest(
        email="  USER@Example.COM ",
        password="candidate passphrase",
    )

    assert request.email == "user@example.com"
    assert request.role == RoleName.CANDIDATE

    with pytest.raises(ValidationError):
        SignupRequest(
            email="admin@example.com",
            password="candidate passphrase",
            role=RoleName.ADMIN,
        )


def test_auth_schemas_forbid_mass_assignment() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(
            email="user@example.com",
            password="candidate passphrase",
            is_admin=True,
        )


def test_otp_schema_requires_six_digits() -> None:
    assert VerifyOTPRequest(email="u@example.com", otp="123456").otp == "123456"

    with pytest.raises(ValidationError):
        VerifyOTPRequest(email="u@example.com", otp="12345a")
