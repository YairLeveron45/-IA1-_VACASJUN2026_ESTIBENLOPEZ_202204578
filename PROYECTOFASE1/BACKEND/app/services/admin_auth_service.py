import os

from dotenv import load_dotenv


load_dotenv()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_ACCESS_TOKEN = os.getenv("ADMIN_ACCESS_TOKEN", "doctor-byte-admin-token")


def authenticate_admin(password: str) -> dict:
    if password != ADMIN_PASSWORD:
        raise ValueError("Credenciales de administrador invalidas.")

    return {
        "access_token": ADMIN_ACCESS_TOKEN,
        "token_type": "bearer",
    }


def validate_admin_token(token: str) -> bool:
    return token == ADMIN_ACCESS_TOKEN
