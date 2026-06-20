from app.services.system_settings_service import SystemSettingsService


def test_safe_settings_do_not_expose_secrets() -> None:
    data = SystemSettingsService().get_safe_settings().model_dump()

    assert data["database_engine"] == "PostgreSQL"
    assert data["max_upload_size_mb"] > 0
    assert "jwt_secret_key" not in data
    assert "postgres_password" not in data
    assert "smtp_password" not in data
