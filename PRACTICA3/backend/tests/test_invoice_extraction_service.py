from decimal import Decimal

from app.services.invoice_extraction_service import InvoiceExtractionService


def test_extract_complete_invoice() -> None:
    service = InvoiceExtractionService()
    text = """
    Proveedor: Distribuidora Ejemplo, S.A.
    NIT: 1234567-8
    No. Factura: FAC-2026-001
    Fecha: 18/06/2026
    Subtotal: Q 100.00
    IVA: Q 12.00
    Total a pagar: Q 112.00
    """

    data, warnings = service.extract(text)

    assert data.invoice_number == "FAC-2026-001"
    assert data.provider_name == "Distribuidora Ejemplo, S.A."
    assert data.nit == "1234567-8"
    assert service.parse_amount(data.total) == Decimal("112.00")
    assert warnings == []


def test_extracts_tax_amount_after_iva_percentage() -> None:
    service = InvoiceExtractionService()
    text = """
    FACTURA FAC-00001
    Proveedor: Manufacturas Mesa y asociados S.L.N.E
    NIT: 6356625-9
    Fecha: 15/06/2025
    Subtotal: Q 6087.34
    IVA 12%: Q 730.48
    TOTAL: Q 6817.82
    """

    data, warnings = service.extract(text)

    assert data.invoice_number == "FAC-00001"
    assert data.taxes == "730.48"
    assert warnings == []


def test_warns_when_amounts_do_not_match() -> None:
    service = InvoiceExtractionService()
    text = """
    Proveedor: Empresa Prueba
    NIT: 1234-5
    Factura No. ABC-123
    Fecha: 18/06/2026
    Subtotal: 100.00
    IVA: 12.00
    Total: 120.00
    """

    _, warnings = service.extract(text)

    assert "El total no coincide con subtotal más impuestos." in warnings


def test_parse_guatemalan_amount_formats() -> None:
    service = InvoiceExtractionService()

    assert service.parse_amount("1,234.56") == Decimal("1234.56")
    assert service.parse_amount("1.234,56") == Decimal("1234.56")
    assert service.parse_amount("Q 250.00") == Decimal("250.00")
    assert service.parse_amount("1.100 €") == Decimal("1100")


def test_extracts_spanish_rental_invoice_with_withholding() -> None:
    service = InvoiceExtractionService()
    text = """
    Factura nº
    1
    2017
    Arrendador
    Nombre
    ALDAITURRIAGA ZUBIMENDI JON
    NIF/CIF
    12345678Z
    Período del alquiler
    Del 1 al 31 de enero de 2017
    SUBTOTAL 1.100 €
    + IVA 21% 231 €
    - IRPF 19% (sobre subtotal) 209 €
    TOTAL a ingresar - 1.122 €
    """

    data, warnings = service.extract(text)

    assert data.invoice_number == "1/2017"
    assert data.invoice_date == "31/01/2017"
    assert data.provider_name == "Aldaiturriaga Zubimendi Jon"
    assert data.nit == "12345678Z"
    assert service.parse_amount(data.subtotal) == Decimal("1100")
    assert service.parse_amount(data.taxes) == Decimal("231")
    assert service.parse_amount(data.total) == Decimal("1122")
    assert warnings == []
