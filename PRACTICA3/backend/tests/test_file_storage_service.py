from io import BytesIO

import pytest
from fastapi import UploadFile

from app.core.exceptions import InvalidFileError
from app.services.file_storage_service import FileStorageService


@pytest.mark.asyncio
async def test_save_valid_pdf(tmp_path) -> None:
    service = FileStorageService(str(tmp_path))
    upload = UploadFile(
        filename="factura.pdf",
        file=BytesIO(b"%PDF-1.4 test"),
        headers={"content-type": "application/pdf"},
    )

    original_name, stored_path, content_type = await service.save_invoice(upload)

    assert original_name == "factura.pdf"
    assert tmp_path in service.get_existing_path(stored_path).parents
    assert content_type == "application/pdf"


@pytest.mark.asyncio
async def test_reject_unsupported_extension(tmp_path) -> None:
    service = FileStorageService(str(tmp_path))
    upload = UploadFile(
        filename="factura.txt",
        file=BytesIO(b"not an invoice"),
        headers={"content-type": "text/plain"},
    )

    with pytest.raises(InvalidFileError):
        await service.save_invoice(upload)


@pytest.mark.asyncio
async def test_reject_mismatched_content_type(tmp_path) -> None:
    service = FileStorageService(str(tmp_path))
    upload = UploadFile(
        filename="factura.pdf",
        file=BytesIO(b"not a pdf"),
        headers={"content-type": "image/png"},
    )

    with pytest.raises(InvalidFileError):
        await service.save_invoice(upload)
