from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from app.models.report_model import Report
from app.models.user_model import User, UserRole
from app.schemas.report_schema import ReportCreate, ReportFormat
from app.services.report_service import ReportService


def make_user() -> User:
    return User(
        id=7,
        name="Operador",
        email="operator@example.com",
        password_hash="hash",
        role=UserRole.OPERATOR,
        is_active=True,
    )


def make_saved_report(path: Path) -> Report:
    return Report(
        id=12,
        report_type="invoice_administrative",
        file_format="pdf",
        file_path=str(path),
        generated_by_id=7,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_generate_sends_report_automatically(tmp_path) -> None:
    report_path = tmp_path / "report.pdf"
    report_path.write_bytes(b"%PDF-test")
    repository = AsyncMock()
    repository.get_invoices.return_value = []
    repository.create_with_log.return_value = make_saved_report(report_path)
    files = Mock()
    files.generate.return_value = report_path
    email = Mock()
    email.automatic_recipient.return_value = "operator@example.com"
    email.send_report.return_value = "smtp"
    service = ReportService(repository, files, email)

    response = await service.generate(
        ReportCreate(file_format=ReportFormat.PDF),
        make_user(),
    )

    assert response.automatic_email_sent is True
    assert response.automatic_email_recipient == "operator@example.com"
    assert response.automatic_email_delivery_mode == "smtp"
    email.send_report.assert_called_once()
    repository.create_log.assert_awaited_once()
    assert repository.create_log.call_args.args[0].action == "report_emailed"


@pytest.mark.asyncio
async def test_generate_keeps_report_when_automatic_email_fails(
    tmp_path,
) -> None:
    report_path = tmp_path / "report.pdf"
    report_path.write_bytes(b"%PDF-test")
    repository = AsyncMock()
    repository.get_invoices.return_value = []
    repository.create_with_log.return_value = make_saved_report(report_path)
    files = Mock()
    files.generate.return_value = report_path
    email = Mock()
    email.automatic_recipient.return_value = "operator@example.com"
    email.send_report.side_effect = RuntimeError("SMTP unavailable")
    service = ReportService(repository, files, email)

    response = await service.generate(
        ReportCreate(file_format=ReportFormat.PDF),
        make_user(),
    )

    assert response.report.id == 12
    assert response.automatic_email_sent is False
    assert response.automatic_email_error == "SMTP unavailable"
    repository.create_log.assert_awaited_once()
    assert (
        repository.create_log.call_args.args[0].action
        == "report_email_error"
    )
