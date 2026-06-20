from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import ResourceNotFoundError
from app.models.processing_log_model import ProcessingLog
from app.services.processing_log_service import ProcessingLogService


@pytest.mark.asyncio
async def test_list_logs_calculates_offset() -> None:
    repository = AsyncMock()
    repository.list.return_value = ([], 0)
    service = ProcessingLogService(repository)

    await service.list(
        page=3,
        page_size=10,
        invoice_id=None,
        user_id=None,
        action=None,
        status=None,
        date_from=None,
        date_to=None,
    )

    repository.list.assert_awaited_once_with(
        offset=20,
        limit=10,
        invoice_id=None,
        user_id=None,
        action=None,
        status=None,
        date_from=None,
        date_to=None,
    )


@pytest.mark.asyncio
async def test_get_missing_log() -> None:
    repository = AsyncMock()
    repository.get_by_id.return_value = None
    service = ProcessingLogService(repository)

    with pytest.raises(ResourceNotFoundError):
        await service.get(999)


@pytest.mark.asyncio
async def test_record_log() -> None:
    repository = AsyncMock()
    now = datetime.now(UTC)
    repository.create.side_effect = lambda log: ProcessingLog(
        id=1,
        action=log.action,
        status=log.status,
        user_id=log.user_id,
        result=log.result,
        created_at=now,
        updated_at=now,
    )
    service = ProcessingLogService(repository)

    log = await service.record(
        action="provider_created",
        status="success",
        user_id=1,
        result="Proveedor creado.",
    )

    assert log.action == "provider_created"
    assert log.user_id == 1
    repository.create.assert_awaited_once()
