import re
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from argon2.exceptions import InvalidHashError

from tradegod.auth.exceptions import InvalidToken, TokenExpired
from tradegod.auth.security import (
    ALGORITHM,
    AccessTokenPayload,
    decode_access_token,
    generate_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from tradegod.core.settings import get_settings

URL_SAFE_PATTERN = re.compile(r"[A-Za-z0-9_-]+")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "raw_password",
    [
        "correct horse battery staple",
        "x" * 10_240,  # 10KB password
    ],
)
async def test_hash_password_returns_argon2_hash(raw_password: str) -> None:
    hashed = await hash_password(raw_password)
    assert hashed.startswith("$argon2")
    assert hashed != raw_password


@pytest.mark.asyncio
async def test_verify_password_match() -> None:
    hashed = await hash_password("hunter2")
    assert await verify_password("hunter2", hashed) is True


@pytest.mark.asyncio
async def test_verify_password_mismatch_returns_false() -> None:
    hashed = await hash_password("hunter2")
    assert await verify_password("wrong-password", hashed) is False


@pytest.mark.asyncio
async def test_verify_password_corrupted_hash_raises() -> None:
    with pytest.raises(InvalidHashError):
        _ = await verify_password("anything", "not-an-argon2-hash")


def test_generate_refresh_token_non_empty_string() -> None:
    token = generate_refresh_token()
    assert isinstance(token, str)
    assert len(token) > 0


def test_generate_refresh_token_unique_per_call() -> None:
    assert generate_refresh_token() != generate_refresh_token()


def test_generate_refresh_token_url_safe_charset() -> None:
    token = generate_refresh_token()
    assert URL_SAFE_PATTERN.fullmatch(token) is not None


def test_hash_refresh_token_deterministic() -> None:
    token = "some-refresh-token"
    assert hash_refresh_token(token) == hash_refresh_token(token)


def test_hash_refresh_token_distinct_inputs_distinct_outputs() -> None:
    assert hash_refresh_token("token-a") != hash_refresh_token("token-b")


def test_generate_access_token_payload_shape() -> None:
    token = generate_access_token(user_id=42)
    payload = jwt.decode(
        token,
        get_settings().jwt_secret.get_secret_value(),
        algorithms=[ALGORITHM],
    )
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert "iat" in payload
    assert payload["exp"] == payload["iat"] + get_settings().access_token_expire_minutes * 60


def test_decode_access_token_round_trip() -> None:
    token = generate_access_token(user_id=7)
    payload: AccessTokenPayload = decode_access_token(token)
    assert payload["sub"] == "7"
    assert payload["type"] == "access"


def _make_token(
    *,
    secret: str | None = None,
    type_claim: str | None = "access",
    exp_offset_minutes: int = 5,
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, str | int] = {
        "sub": "1",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_offset_minutes)).timestamp()),
    }
    if type_claim is not None:
        payload["type"] = type_claim
    return jwt.encode(
        payload,
        secret if secret is not None else get_settings().jwt_secret.get_secret_value(),
        algorithm=ALGORITHM,
    )


@pytest.mark.parametrize(
    ("token_factory", "expected_exc"),
    [
        (lambda: _make_token(exp_offset_minutes=-60), TokenExpired),
        (lambda: _make_token(secret="a-different-secret-than-the-real-one"), InvalidToken),
        (lambda: "not.a.real.jwt", InvalidToken),
        (lambda: _make_token(type_claim="refresh"), InvalidToken),
        (lambda: _make_token(type_claim=None), InvalidToken),
    ],
    ids=["expired", "bad_signature", "malformed", "wrong_type", "missing_type"],
)
def test_decode_access_token_failure_modes(token_factory, expected_exc) -> None:  # pyright: ignore[reportMissingParameterType, reportUnknownParameterType]
    with pytest.raises(expected_exc):
        _ = decode_access_token(token_factory())
