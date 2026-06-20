from app.core.config import settings
from app.schemas.system_settings_schema import SystemSettingsResponse


class SystemSettingsService:
    def get_safe_settings(self) -> SystemSettingsResponse:
        return SystemSettingsResponse(
            application=settings.app_name,
            environment=settings.app_env,
            debug=settings.app_debug,
            api_prefix=settings.api_v1_prefix,
            access_token_expire_minutes=settings.access_token_expire_minutes,
            max_upload_size_mb=settings.max_upload_size_mb,
            allowed_invoice_formats=["PDF", "JPG", "JPEG", "PNG"],
            tesseract_language=settings.tesseract_language,
            smtp_enabled=settings.smtp_enabled,
            smtp_delivery_mode="smtp" if settings.smtp_enabled else "outbox",
            smtp_from_email=settings.smtp_from_email,
            rpa_enabled=bool(
                settings.rpa_target_url and settings.rpa_browser_executable
            ),
            rpa_target_url=settings.rpa_target_url,
            database_engine="PostgreSQL",
        )
