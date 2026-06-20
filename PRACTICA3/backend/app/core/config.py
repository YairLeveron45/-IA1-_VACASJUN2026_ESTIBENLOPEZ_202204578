from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SmartInvoice API"
    app_env: str = "development"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://frontend:5173"
    )

    jwt_secret_key: str = "development_secret_change_before_deploying"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    upload_directory: str = "/app/uploads"
    report_directory: str = "/app/reports"
    mail_outbox_directory: str = "/app/reports/outbox"
    rpa_output_directory: str = "/app/reports/rpa"
    max_upload_size_mb: int = 10
    tesseract_language: str = "spa"
    rpa_target_url: str = "http://api:8000/api/v1/rpa-simulator/form"
    rpa_browser_executable: str = "/usr/bin/chromium"

    smtp_enabled: bool = False
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "reports@smartinvoice.com"
    smtp_from_name: str = "SmartInvoice"
    smtp_use_tls: bool = True

    initial_admin_name: str = "Administrador"
    initial_admin_email: str = "admin@smartinvoice.com"
    initial_admin_password: str = "Admin123!"

    postgres_db: str = "smartinvoice"
    postgres_user: str = "smartinvoice"
    postgres_password: str = "change_me"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @computed_field
    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
