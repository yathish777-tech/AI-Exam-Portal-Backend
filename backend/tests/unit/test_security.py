from __future__ import annotations

import base64
import json
from datetime import datetime, timedelta, timezone

import pytest
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.core.constants import ACCESS_TOKEN_TYPE, PASSWORD_MAX_LENGTH, REFRESH_TOKEN_TYPE
from app.core.security import (
    decode_access_token,
    generate_access_token,
    generate_jti,
    generate_otp,
    generate_refresh_token,
    hash_password,
    verify_hash,
    verify_otp_hash,
    verify_password,
)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _settings_kwargs(**overrides: object) -> dict:
    data: dict = {
        "environment": "development",
        "database_url": "postgresql+asyncpg://user:password@localhost/test",
        "jwt_secret_key": "x" * 64,
        "jwt_algorithm": "HS256",
        "otp_hash_secret": "y" * 64,
        "frontend_url": "http://localhost:3000",
    }
    data.update(overrides)
    return data


def _sign_test_token(payload: dict) -> str:
    settings = get_settings()
    assert settings.jwt_secret_key is not None
    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def _valid_payload(**overrides: object) -> dict:
    now = datetime.now(timezone.utc)
    payload: dict = {
        "sub": "7b2304e3-9b40-4d33-bba7-b53cb41aa553",
        "jti": generate_jti(),
        "type": ACCESS_TOKEN_TYPE,
        "role": "CANDIDATE",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=15)).timestamp()),
    }
    payload.update(overrides)
    return payload


def test_password_hash_verify_and_max_length() -> None:
    password = "correct horse battery staple"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong password", hashed)

    with pytest.raises(ValueError):
        hash_password("a" * (PASSWORD_MAX_LENGTH + 1))


def test_settings_rejects_insecure_production_jwt_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(
            **_settings_kwargs(
                environment="production",
                jwt_secret_key="dev_" + "x" * 64,
            )
        )


def test_settings_requires_asymmetric_key_pair() -> None:
    with pytest.raises(ValidationError):
        Settings(
            **_settings_kwargs(
                jwt_algorithm="RS256",
                jwt_secret_key=None,
                jwt_private_key="",
                jwt_public_key="",
            )
        )


def test_access_token_rejects_alg_none() -> None:
    header = _b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    payload = _b64url(
        json.dumps(
            {
                "sub": "7b2304e3-9b40-4d33-bba7-b53cb41aa553",
                "jti": generate_jti(),
                "type": ACCESS_TOKEN_TYPE,
                "exp": 4102444800,
            }
        ).encode()
    )

    with pytest.raises(JWTError):
        decode_access_token(f"{header}.{payload}.")


def test_access_token_preserves_reserved_claims() -> None:
    token = generate_access_token(
        subject="7b2304e3-9b40-4d33-bba7-b53cb41aa553",
        jti=generate_jti(),
        role="CANDIDATE",
        extra_claims={"type": "refresh"},
    )

    payload = decode_access_token(token)

    assert payload["type"] == ACCESS_TOKEN_TYPE


def test_access_token_rejects_wrong_token_type() -> None:
    token = _sign_test_token(_valid_payload(type=REFRESH_TOKEN_TYPE))

    with pytest.raises(JWTError):
        decode_access_token(token)


def test_access_token_rejects_missing_required_claims() -> None:
    for claim in ("sub", "jti", "iat", "exp"):
        payload = _valid_payload()
        del payload[claim]
        token = _sign_test_token(payload)

        with pytest.raises(JWTError):
            decode_access_token(token)


def test_access_token_rejects_expired_token() -> None:
    now = datetime.now(timezone.utc)
    token = _sign_test_token(
        _valid_payload(
            iat=int((now - timedelta(minutes=30)).timestamp()),
            exp=int((now - timedelta(minutes=1)).timestamp()),
        )
    )

    with pytest.raises(JWTError):
        decode_access_token(token)


def test_access_token_rejects_malformed_token() -> None:
    with pytest.raises(JWTError):
        decode_access_token("this-is-not-a-jwt")


def test_access_token_rejects_invalid_signature() -> None:
    token = generate_access_token(
        subject="7b2304e3-9b40-4d33-bba7-b53cb41aa553",
        jti=generate_jti(),
        role="CANDIDATE",
    )
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")

    with pytest.raises(JWTError):
        decode_access_token(tampered)


def test_otp_is_six_digits_and_hmac_verified() -> None:
    raw_otp, otp_hash = generate_otp()

    assert raw_otp.isdigit()
    assert len(raw_otp) == 6
    assert raw_otp not in otp_hash
    assert verify_otp_hash(raw_otp, otp_hash)
    assert not verify_otp_hash("000000" if raw_otp != "000000" else "111111", otp_hash)


def test_refresh_token_is_random_and_only_hash_matches() -> None:
    raw_refresh, refresh_hash = generate_refresh_token()

    assert raw_refresh not in refresh_hash
    assert verify_hash(raw_refresh, refresh_hash)
    assert not verify_hash(raw_refresh + "x", refresh_hash)
