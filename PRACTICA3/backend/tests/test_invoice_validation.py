from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.invoice_schema import InvoiceValidationRequest


def make_payload(**changes) -> dict:
    payload = {
        "invoice_number": "FAC-001",
        "invoice_date": date(2026, 6, 18),
        "provider_name": "Proveedor Ejemplo",
        "nit": "1234 K",
        "subtotal": Decimal("100.00"),
        "taxes": Decimal("12.00"),
        "total": Decimal("112.00"),
    }
    payload.update(changes)
    return payload


def test_validation_normalizes_nit() -> None:
    data = InvoiceValidationRequest(**make_payload())

    assert data.nit == "1234K"


def test_validation_rejects_inconsistent_total() -> None:
    with pytest.raises(ValidationError):
        InvoiceValidationRequest(
            **make_payload(total=Decimal("120.00"))
        )


def test_validation_accepts_small_rounding_difference() -> None:
    data = InvoiceValidationRequest(
        **make_payload(total=Decimal("112.04"))
    )

    assert data.total == Decimal("112.04")
