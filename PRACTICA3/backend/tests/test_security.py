import pytest

from app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing() -> None:
    encoded = hash_password("Secure123!")

    assert encoded != "Secure123!"
    assert verify_password("Secure123!", encoded) is True
    assert verify_password("Incorrect123!", encoded) is False


def test_access_token_round_trip() -> None:
    token = create_access_token("42", {"role": "admin"})
    payload = decode_access_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_invalid_access_token() -> None:
    with pytest.raises(AuthenticationError):
        decode_access_token("not-a-valid-token")
