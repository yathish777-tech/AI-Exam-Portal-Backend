from __future__ import annotations

import base64
import json

import pytest
from jose import JWTError

from app.core.constants import ACCESS_TOKEN_TYPE, PASSWORD_MAX_LENGTH
from app.core.security import (
    decode_access_token,
    generate_access_token,
    generate_jti,
    generate_otp,
    hash_password,
    verify_otp_hash,
    verify_password,
)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def test_password_hash_verify_and_max_length() -> None:
    password = "correct horse battery staple"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong password", hashed)

    with pytest.raises(ValueError):
        hash_password("a" * (PASSWORD_MAX_LENGTH + 1))


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


def test_access_token_requires_access_type() -> None:
    token = generate_access_token(
        subject="7b2304e3-9b40-4d33-bba7-b53cb41aa553",
        jti=generate_jti(),
        role="CANDIDATE",
        extra_claims={"type": "refresh"},
    )

    payload = decode_access_token(token)

    assert payload["type"] == ACCESS_TOKEN_TYPE


def test_otp_is_six_digits_and_hmac_verified() -> None:
    raw_otp, otp_hash = generate_otp()

    assert raw_otp.isdigit()
    assert len(raw_otp) == 6
    assert raw_otp not in otp_hash
    assert verify_otp_hash(raw_otp, otp_hash)
    assert not verify_otp_hash("000000" if raw_otp != "000000" else "111111", otp_hash)
