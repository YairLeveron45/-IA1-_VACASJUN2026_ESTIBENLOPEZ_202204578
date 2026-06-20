import csv
from datetime import date
from decimal import Decimal

from app.models.invoice_model import Invoice, InvoiceStatus
from app.schemas.report_schema import ReportFormat
from app.services.report_file_service import ReportFileService


def make_invoice() -> Invoice:
    return Invoice(
        id=1,
        invoice_number="FAC-001",
        invoice_date=date(2026, 6, 18),
        detected_provider_name="Proveedor Ejemplo",
        detected_nit="1234K",
        subtotal=Decimal("100.00"),
        taxes=Decimal("12.00"),
        total=Decimal("112.00"),
        file_name="factura.pdf",
        file_path="/tmp/factura.pdf",
        content_type="application/pdf",
        status=InvoiceStatus.PROCESSED,
    )


def test_generate_csv(tmp_path) -> None:
    service = ReportFileService(str(tmp_path))
    path = service.generate([make_invoice()], ReportFormat.CSV)

    content = path.read_text(encoding="utf-8-sig")
    rows = list(csv.reader(content.splitlines()[1:], delimiter=";"))

    assert content.startswith("sep=;\n")
    assert rows[0] == ["SMARTINVOICE", "Reporte administrativo de facturas"]
    assert rows[4][1] == "Número de factura"
    assert rows[5][-1] == "Procesada"
    assert rows[7][0] == "TOTAL GENERAL"
    assert "FAC-001" in content
    assert "112.00" in content


def test_generate_pdf(tmp_path) -> None:
    service = ReportFileService(str(tmp_path))
    path = service.generate([make_invoice()], ReportFormat.PDF)

    assert path.read_bytes().startswith(b"%PDF")
