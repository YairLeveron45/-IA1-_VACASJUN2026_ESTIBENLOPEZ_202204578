from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.exceptions import AuthenticationError


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Genera un hash seguro; nunca almacena la contraseña original."""
    return password_hash.hash(password)


def verify_password(password: str, encoded_password: str) -> bool:
    """Compara una contraseña con su hash almacenado."""
    return password_hash.verify(password, encoded_password)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """Crea un JWT firmado con identidad, vencimiento y datos opcionales."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Valida firma, vencimiento y tipo del token de acceso."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except InvalidTokenError as exc:
        # Unifica tokens alterados y vencidos para no revelar detalles sensibles.
        raise AuthenticationError("Token inválido o vencido.") from exc

    if payload.get("type") != "access" or not payload.get("sub"):
        raise AuthenticationError("Token de acceso inválido.")

    return payload
