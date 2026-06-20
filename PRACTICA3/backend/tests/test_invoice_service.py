from datetime import UTC, datetime
from decimal import Decimal
from io import BytesIO
from unittest.mock import AsyncMock

import pytest
from fastapi import UploadFile

from app.core.exceptions import BusinessRuleError
from app.models.invoice_model import Invoice, InvoiceStatus
from app.models.user_model import User, UserRole
from app.schemas.invoice_schema import InvoiceValidationRequest
from app.services.file_storage_service import FileStorageService
from app.services.invoice_service import InvoiceService


def make_user() -> User:
    now = datetime.now(UTC)
    return User(
        id=1,
        name="Operador",
        email="operator@example.com",
        password_hash="hash",
        role=UserRole.OPERATOR,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_upload_creates_pending_invoice_and_log(tmp_path) -> None:
    repository = AsyncMock()
    repository.create_with_log.side_effect = lambda invoice, log: invoice
    service = InvoiceService(
        repository,
        FileStorageService(str(tmp_path)),
    )
    upload = UploadFile(
        filename="factura.png",
        file=BytesIO(b"\x89PNG test"),
        headers={"content-type": "image/png"},
    )

    invoice = await service.upload(upload, make_user())

    assert invoice.status == InvoiceStatus.PENDING
    assert invoice.uploaded_by_id == 1
    repository.create_with_log.assert_awaited_once()


@pytest.mark.asyncio
async def test_processed_invoice_cannot_be_rejected() -> None:
    repository = AsyncMock()
    repository.get_by_id.return_value = Invoice(
        id=1,
        file_name="factura.pdf",
        file_path="/tmp/factura.pdf",
        content_type="application/pdf",
        status=InvoiceStatus.PROCESSED,
    )
    service = InvoiceService(repository)

    with pytest.raises(BusinessRuleError):
        await service.reject(1, make_user())


@pytest.mark.asyncio
async def test_rejected_invoice_cannot_be_processed(tmp_path) -> None:
    repository = AsyncMock()
    repository.get_by_id.return_value = Invoice(
        id=1,
        file_name="factura.pdf",
        file_path=str(tmp_path / "factura.pdf"),
        content_type="application/pdf",
        status=InvoiceStatus.REJECTED,
    )
    service = InvoiceService(
        repository,
        FileStorageService(str(tmp_path)),
    )

    with pytest.raises(BusinessRuleError):
        await service.process(1, make_user())


@pytest.mark.asyncio
async def test_manual_validation_marks_invoice_processed() -> None:
    repository = AsyncMock()
    provider_repository = AsyncMock()
    invoice = Invoice(
        id=1,
        file_name="factura.pdf",
        file_path="/tmp/factura.pdf",
        content_type="application/pdf",
        status=InvoiceStatus.ERROR,
    )
    repository.get_by_id.return_value = invoice
    repository.update_with_logs.side_effect = lambda item, logs: item
    provider_repository.get_by_nit.return_value = None
    service = InvoiceService(
        repository,
        provider_repository=provider_repository,
    )
    data = InvoiceValidationRequest(
        invoice_number="FAC-001",
        invoice_date="2026-06-18",
        provider_name="Proveedor Ejemplo",
        nit="1234K",
        subtotal="100.00",
        taxes="12.00",
        total="112.00",
    )

    result = await service.validate_manually(1, data, make_user())

    assert result.status == InvoiceStatus.PROCESSED
    assert result.invoice_number == "FAC-001"
    assert result.total == Decimal("112.00")
    repository.update_with_logs.assert_awaited_once()


@pytest.mark.asyncio
async def test_manual_validation_creates_and_associates_provider() -> None:
    repository = AsyncMock()
    provider_repository = AsyncMock()
    invoice = Invoice(
        id=1,
        file_name="factura.pdf",
        file_path="/tmp/factura.pdf",
        content_type="application/pdf",
        status=InvoiceStatus.ERROR,
    )
    repository.get_by_id.return_value = invoice
    repository.update_with_logs.side_effect = lambda item, logs: item
    provider_repository.get_by_nit.return_value = None

    async def create_provider(provider):
        provider.id = 8
        return provider

    provider_repository.create_pending.side_effect = create_provider
    service = InvoiceService(
        repository,
        provider_repository=provider_repository,
    )
    data = InvoiceValidationRequest(
        invoice_number="FAC-001",
        invoice_date="2026-06-18",
        provider_name="Proveedor Nuevo",
        nit="9876543-1",
        subtotal="100.00",
        taxes="12.00",
        total="112.00",
        create_provider_if_missing=True,
    )

    result = await service.validate_manually(1, data, make_user())

    assert result.provider_id == 8
    provider_repository.create_pending.assert_awaited_once()
    logs = repository.update_with_logs.call_args.args[1]
    assert [log.action for log in logs] == [
        "invoice_manually_validated",
        "provider_created",
    ]


@pytest.mark.asyncio
async def test_delete_invoice_is_logical_and_removes_file(tmp_path) -> None:
    invoice_path = tmp_path / "factura.pdf"
    invoice_path.write_bytes(b"%PDF-test")
    repository = AsyncMock()
    invoice = Invoice(
        id=1,
        file_name="factura.pdf",
        file_path=str(invoice_path),
        content_type="application/pdf",
        status=InvoiceStatus.PROCESSED,
        is_deleted=False,
    )
    repository.get_by_id.return_value = invoice
    repository.update_with_log.side_effect = lambda item, log: item
    service = InvoiceService(
        repository,
        FileStorageService(str(tmp_path)),
    )

    result = await service.delete(1, make_user())

    assert result.is_deleted is True
    assert not invoice_path.exists()
    repository.update_with_log.assert_awaited_once()
    log = repository.update_with_log.call_args.args[1]
    assert log.action == "invoice_deleted"
