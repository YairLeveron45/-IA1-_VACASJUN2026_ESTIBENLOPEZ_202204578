import smtplib
from html import escape
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.core.exceptions import BusinessRuleError
from app.models.report_model import Report
from app.schemas.email_schema import ReportEmailRequest


class EmailService:
    """Construye y entrega reportes por SMTP o a una bandeja local."""

    def __init__(self, outbox_directory: str | None = None) -> None:
        self.outbox_directory = Path(
            outbox_directory or settings.mail_outbox_directory
        ).resolve()
        self.outbox_directory.mkdir(parents=True, exist_ok=True)

    def send_report(
        self,
        report: Report,
        attachment: Path,
        data: ReportEmailRequest,
    ) -> str:
        """Envía el reporte y devuelve el canal usado: smtp u outbox."""
        username = self._smtp_username()
        from_email = settings.smtp_from_email.strip() or username
        message = self._build_message(
            report,
            attachment,
            data,
            from_email,
        )
        if not settings.smtp_enabled:
            self._save_to_outbox(message)
            return "outbox"

        if not settings.smtp_host or not from_email:
            raise BusinessRuleError("La configuración SMTP está incompleta.")

        try:
            with smtplib.SMTP(
                settings.smtp_host,
                settings.smtp_port,
                timeout=30,
            ) as smtp:
                if settings.smtp_use_tls:
                    smtp.starttls()
                if username:
                    smtp.login(
                        username,
                        "".join(settings.smtp_password.split()),
                    )
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException) as exc:
            # Convierte errores de red/autenticación en un mensaje controlado.
            raise BusinessRuleError(
                "No fue posible enviar el correo mediante SMTP."
            ) from exc
        return "smtp"

    def automatic_recipient(self, fallback: str) -> str:
        """Elige la cuenta SMTP o utiliza el correo del usuario como respaldo."""
        if settings.smtp_enabled:
            username = self._smtp_username()
            if username:
                return username
        return fallback

    def _build_message(
        self,
        report: Report,
        attachment: Path,
        data: ReportEmailRequest,
        from_email: str,
    ) -> EmailMessage:
        """Crea el correo HTML y adjunta el archivo del reporte."""
        message = EmailMessage()
        message["From"] = formataddr(
            (settings.smtp_from_name, from_email)
        )
        message["To"] = str(data.recipient)
        message["Subject"] = data.subject
        message.set_content(data.message)
        message.add_alternative(
            self._html_content(report, data),
            subtype="html",
        )

        maintype, subtype = (
            ("text", "csv")
            if report.file_format == "csv"
            else ("application", "pdf")
        )
        message.add_attachment(
            attachment.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=f"smartinvoice-report-{report.id}.{report.file_format}",
        )
        return message

    def _html_content(
        self,
        report: Report,
        data: ReportEmailRequest,
    ) -> str:
        """Genera el cuerpo HTML escapando el contenido escrito por el usuario."""
        file_format = report.file_format.upper()
        report_id = report.id or "nuevo"
        safe_message = escape(data.message).replace("\n", "<br>")
        return f"""\
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(data.subject)}</title>
</head>
<body style="margin:0;padding:0;background:#f4f6fa;color:#172033;font-family:Arial,sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f6fa;padding:28px 14px;">
    <tr>
      <td align="center">
        <table role="presentation" width="620" cellspacing="0" cellpadding="0" style="width:100%;max-width:620px;background:#ffffff;border:1px solid #e4e8f0;border-radius:18px;overflow:hidden;">
          <tr>
            <td style="padding:28px 32px;background:#151b2e;color:#ffffff;">
              <div style="font-size:23px;font-weight:700;letter-spacing:-0.5px;">SmartInvoice</div>
              <div style="margin-top:4px;color:#aeb6c9;font-size:10px;letter-spacing:1.4px;">DOCUMENT INTELLIGENCE</div>
            </td>
          </tr>
          <tr>
            <td style="padding:32px;">
              <div style="display:inline-block;padding:7px 11px;border-radius:999px;background:#ecf8f3;color:#287c61;font-size:11px;font-weight:700;">
                REPORTE GENERADO
              </div>
              <h1 style="margin:18px 0 10px;font-size:26px;line-height:1.2;color:#172033;">Tu reporte está listo</h1>
              <p style="margin:0;color:#6f788b;font-size:14px;line-height:1.65;">{safe_message}</p>

              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin:26px 0;border:1px solid #e4e8f0;border-radius:12px;background:#f8f9fc;">
                <tr>
                  <td style="padding:18px;">
                    <div style="color:#5356d9;font-size:10px;font-weight:700;letter-spacing:1px;">ARCHIVO ADJUNTO</div>
                    <div style="margin-top:8px;font-size:15px;font-weight:700;color:#172033;">smartinvoice-report-{report_id}.{report.file_format}</div>
                    <div style="margin-top:4px;color:#7d8699;font-size:12px;">Formato {file_format} · Reporte administrativo #{report_id}</div>
                  </td>
                  <td width="72" align="center" style="padding:18px;">
                    <div style="width:46px;height:46px;line-height:46px;border-radius:12px;background:#5356d9;color:#ffffff;font-size:12px;font-weight:700;text-align:center;">{file_format}</div>
                  </td>
                </tr>
              </table>

              <div style="padding:15px 17px;border-left:4px solid #5356d9;border-radius:8px;background:#f1f1ff;color:#4f5870;font-size:12px;line-height:1.55;">
                El archivo contiene los datos consolidados de las facturas procesadas. Revisa el adjunto y conserva este correo como evidencia del proceso automático.
              </div>
            </td>
          </tr>
          <tr>
            <td style="padding:18px 32px;border-top:1px solid #e4e8f0;background:#fafbfc;color:#8a93a5;font-size:11px;line-height:1.5;">
              Mensaje enviado automáticamente por SmartInvoice.<br>
              Procesamiento de facturas con OCR, Computer Vision y RPA.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    @staticmethod
    def _smtp_username() -> str:
        """Normaliza nombres de usuario Gmail que no incluyen dominio."""
        username = settings.smtp_username.strip()
        if (
            username
            and "@" not in username
            and settings.smtp_host.lower() == "smtp.gmail.com"
        ):
            return f"{username}@gmail.com"
        return username

    def _save_to_outbox(self, message: EmailMessage) -> Path:
        """Guarda el correo como EML cuando SMTP está deshabilitado."""
        path = self.outbox_directory / f"email-{uuid4().hex}.eml"
        path.write_bytes(message.as_bytes())
        return path
