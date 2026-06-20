from email import policy
from email.parser import BytesParser

from app.core.config import settings
from app.models.report_model import Report
from app.schemas.email_schema import ReportEmailRequest
from app.services.email_service import EmailService


def test_development_email_is_saved_with_attachment(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "smtp_enabled", False)
    attachment = tmp_path / "report.csv"
    attachment.write_text("ID,Total\n1,112.00\n", encoding="utf-8")
    outbox = tmp_path / "outbox"
    service = EmailService(str(outbox))
    report = Report(
        id=5,
        report_type="invoice_administrative",
        file_format="csv",
        file_path=str(attachment),
    )

    mode = service.send_report(
        report,
        attachment,
        ReportEmailRequest(
            recipient="recipient@example.com",
            subject="Reporte de prueba",
            message="Adjunto el reporte.",
        ),
    )

    messages = list(outbox.glob("*.eml"))
    parsed = BytesParser(policy=policy.default).parsebytes(
        messages[0].read_bytes()
    )
    attachments = list(parsed.iter_attachments())
    html_body = parsed.get_body(preferencelist=("html",))

    assert mode == "outbox"
    assert parsed["To"] == "recipient@example.com"
    assert len(attachments) == 1
    assert attachments[0].get_filename() == "smartinvoice-report-5.csv"
    assert html_body is not None
    assert "Tu reporte está listo" in html_body.get_content()
    assert "smartinvoice-report-5.csv" in html_body.get_content()
