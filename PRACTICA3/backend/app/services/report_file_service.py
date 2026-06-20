import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.config import settings
from app.core.exceptions import InvalidFileError
from app.models.invoice_model import Invoice, InvoiceStatus
from app.schemas.report_schema import ReportFormat


class ReportFileService:
    """Genera archivos CSV/PDF y valida el acceso a reportes guardados."""

    headers = [
        "ID",
        "Número",
        "Fecha",
        "Proveedor",
        "NIT",
        "Subtotal",
        "Impuestos",
        "Total",
        "Estado",
    ]
    navy = colors.HexColor("#151B2E")
    primary = colors.HexColor("#5356D9")
    success = colors.HexColor("#28A57A")
    warning = colors.HexColor("#D79636")
    danger = colors.HexColor("#D95464")
    ink = colors.HexColor("#172033")
    muted = colors.HexColor("#6F788B")
    line = colors.HexColor("#E4E8F0")
    surface = colors.HexColor("#F7F8FB")

    def __init__(self, report_directory: str | None = None) -> None:
        self.report_directory = Path(
            report_directory or settings.report_directory
        ).resolve()
        self.report_directory.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        invoices: list[Invoice],
        file_format: ReportFormat,
    ) -> Path:
        """Crea el reporte solicitado y devuelve su ruta absoluta."""
        path = self.report_directory / f"invoice-report-{uuid4().hex}.{file_format}"
        if file_format == ReportFormat.CSV:
            self._generate_csv(path, invoices)
        else:
            self._generate_pdf(path, invoices)
        return path.resolve()

    def get_existing_path(self, stored_path: str) -> Path:
        """Acepta únicamente archivos existentes dentro del directorio permitido."""
        path = Path(stored_path).resolve()
        if (
            path != self.report_directory
            and self.report_directory not in path.parents
        ):
            raise InvalidFileError("Ruta de reporte inválida.")
        if not path.is_file():
            raise InvalidFileError("El archivo del reporte no está disponible.")
        return path

    def delete(self, path: Path) -> None:
        """Elimina un reporte parcial o que ya no debe conservarse."""
        path.unlink(missing_ok=True)

    def _generate_csv(self, path: Path, invoices: list[Invoice]) -> None:
        """Genera un CSV UTF-8 compatible con la configuración regional de Excel."""
        with path.open("w", newline="", encoding="utf-8-sig") as output:
            writer = csv.writer(
                output,
                delimiter=";",
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\r\n",
            )
            # Excel reconoce esta directiva y abre el archivo en columnas incluso
            # cuando Windows utiliza otro separador regional.
            output.write("sep=;\r\n")
            writer.writerow(["SMARTINVOICE", "Reporte administrativo de facturas"])
            writer.writerow(
                ["Fecha de generación", datetime.now().strftime("%d/%m/%Y %H:%M")]
            )
            writer.writerow(["Facturas incluidas", len(invoices)])
            writer.writerow([])
            writer.writerow(
                [
                    "ID",
                    "Número de factura",
                    "Fecha",
                    "Proveedor",
                    "NIT",
                    "Subtotal (GTQ)",
                    "Impuestos (GTQ)",
                    "Total (GTQ)",
                    "Estado",
                ]
            )
            for invoice in invoices:
                row = self._invoice_row(invoice)
                row[-1] = self._status_label(str(row[-1]))
                writer.writerow(row)
            writer.writerow([])
            writer.writerow(
                [
                    "TOTAL GENERAL",
                    "",
                    "",
                    "",
                    "",
                    self._sum(invoices, "subtotal"),
                    self._sum(invoices, "taxes"),
                    self._sum(invoices, "total"),
                    "",
                ]
            )

    def _generate_pdf(self, path: Path, invoices: list[Invoice]) -> None:
        """Genera un PDF administrativo con resumen, detalle y totales."""
        document = SimpleDocTemplate(
            str(path),
            pagesize=landscape(letter),
            leftMargin=0.42 * inch,
            rightMargin=0.42 * inch,
            topMargin=0.52 * inch,
            bottomMargin=0.52 * inch,
            title="Reporte administrativo de facturas - SmartInvoice",
            author="SmartInvoice",
        )
        styles = self._styles()
        total = self._sum_decimal(invoices, "total")
        subtotal = self._sum_decimal(invoices, "subtotal")
        taxes = self._sum_decimal(invoices, "taxes")
        processed = sum(
            invoice.status == InvoiceStatus.PROCESSED for invoice in invoices
        )
        attention = sum(
            invoice.status in (InvoiceStatus.PENDING, InvoiceStatus.ERROR)
            for invoice in invoices
        )

        story = [
            self._header(styles),
            Spacer(1, 0.2 * inch),
            self._summary_cards(
                styles,
                len(invoices),
                processed,
                attention,
                total,
            ),
            Spacer(1, 0.2 * inch),
            Paragraph("Detalle de facturas", styles["section"]),
            Paragraph(
                "Información consolidada de los documentos incluidos en este reporte.",
                styles["caption"],
            ),
            Spacer(1, 0.1 * inch),
            self._invoice_table(invoices, styles),
            Spacer(1, 0.18 * inch),
            self._totals_table(styles, subtotal, taxes, total),
        ]
        document.build(
            story,
            onFirstPage=self._page_decoration,
            onLaterPages=self._page_decoration,
        )

    def _styles(self) -> dict[str, ParagraphStyle]:
        styles = getSampleStyleSheet()
        return {
            "brand": ParagraphStyle(
                "Brand",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=20,
                leading=23,
                alignment=TA_LEFT,
                textColor=colors.white,
                spaceAfter=2,
            ),
            "brand_subtitle": ParagraphStyle(
                "BrandSubtitle",
                parent=styles["Normal"],
                fontSize=8,
                leading=10,
                textColor=colors.HexColor("#B9C0D2"),
                tracking=1,
            ),
            "meta": ParagraphStyle(
                "Meta",
                parent=styles["Normal"],
                fontSize=8,
                leading=11,
                alignment=TA_RIGHT,
                textColor=colors.white,
            ),
            "section": ParagraphStyle(
                "Section",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=13,
                leading=15,
                textColor=self.ink,
                spaceAfter=2,
            ),
            "caption": ParagraphStyle(
                "Caption",
                parent=styles["Normal"],
                fontSize=7.5,
                leading=10,
                textColor=self.muted,
            ),
            "card_label": ParagraphStyle(
                "CardLabel",
                parent=styles["Normal"],
                fontSize=7,
                leading=9,
                textColor=self.muted,
                uppercase=True,
            ),
            "card_value": ParagraphStyle(
                "CardValue",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=15,
                leading=18,
                textColor=self.ink,
            ),
            "cell": ParagraphStyle(
                "Cell",
                parent=styles["Normal"],
                fontSize=6.7,
                leading=8.2,
                textColor=self.ink,
            ),
            "cell_center": ParagraphStyle(
                "CellCenter",
                parent=styles["Normal"],
                fontSize=6.7,
                leading=8.2,
                alignment=TA_CENTER,
                textColor=self.ink,
            ),
            "cell_right": ParagraphStyle(
                "CellRight",
                parent=styles["Normal"],
                fontSize=6.7,
                leading=8.2,
                alignment=TA_RIGHT,
                textColor=self.ink,
            ),
            "header_cell": ParagraphStyle(
                "HeaderCell",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=6.6,
                leading=8,
                textColor=colors.white,
                alignment=TA_CENTER,
            ),
            "total_label": ParagraphStyle(
                "TotalLabel",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=10,
                textColor=self.ink,
            ),
            "total_value": ParagraphStyle(
                "TotalValue",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=11,
                alignment=TA_RIGHT,
                textColor=self.ink,
            ),
        }

    def _header(self, styles: dict[str, ParagraphStyle]) -> Table:
        generated = datetime.now().strftime("%d/%m/%Y - %H:%M")
        left = [
            Paragraph("SmartInvoice", styles["brand"]),
            Paragraph("DOCUMENT INTELLIGENCE", styles["brand_subtitle"]),
        ]
        right = Paragraph(
            f"<b>Reporte administrativo</b><br/>Generado: {generated}",
            styles["meta"],
        )
        table = Table([[left, right]], colWidths=[6.7 * inch, 3.2 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), self.navy),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 18),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 18),
                    ("TOPPADDING", (0, 0), (-1, -1), 15),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
                    ("ROUNDEDCORNERS", [10]),
                ]
            )
        )
        return table

    def _summary_cards(
        self,
        styles: dict[str, ParagraphStyle],
        count: int,
        processed: int,
        attention: int,
        total: Decimal,
    ) -> Table:
        cards = [
            ("FACTURAS INCLUIDAS", str(count), self.primary),
            ("PROCESADAS", str(processed), self.success),
            ("REQUIEREN ATENCIÓN", str(attention), self.warning),
            ("MONTO CONSOLIDADO", self._currency(total), self.primary),
        ]
        cells = []
        for label, value, accent in cards:
            content = [
                Paragraph(label, styles["card_label"]),
                Spacer(1, 4),
                Paragraph(value, styles["card_value"]),
            ]
            card = Table([[content]], colWidths=[2.25 * inch])
            card.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                        ("BOX", (0, 0), (-1, -1), 0.6, self.line),
                        ("LINEBEFORE", (0, 0), (0, -1), 4, accent),
                        ("LEFTPADDING", (0, 0), (-1, -1), 13),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ]
                )
            )
            cells.append(card)
        wrapper = Table([cells], colWidths=[2.47 * inch] * 4)
        wrapper.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        return wrapper

    def _invoice_table(
        self,
        invoices: list[Invoice],
        styles: dict[str, ParagraphStyle],
    ) -> Table:
        data = [
            [Paragraph(header, styles["header_cell"]) for header in self.headers]
        ]
        for invoice in invoices:
            row = self._invoice_row(invoice)
            data.append(
                [
                    Paragraph(str(row[0]), styles["cell_center"]),
                    Paragraph(str(row[1]), styles["cell"]),
                    Paragraph(str(row[2]), styles["cell_center"]),
                    Paragraph(str(row[3]), styles["cell"]),
                    Paragraph(str(row[4]), styles["cell_center"]),
                    Paragraph(self._currency_text(str(row[5])), styles["cell_right"]),
                    Paragraph(self._currency_text(str(row[6])), styles["cell_right"]),
                    Paragraph(self._currency_text(str(row[7])), styles["cell_right"]),
                    Paragraph(self._status_label(str(row[8])), styles["cell_center"]),
                ]
            )
        if len(data) == 1:
            data.append(
                [
                    "",
                    Paragraph("No hay facturas para los filtros seleccionados.", styles["cell"]),
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                ]
            )

        table = Table(
            data,
            repeatRows=1,
            colWidths=[
                0.35 * inch,
                0.85 * inch,
                0.68 * inch,
                1.7 * inch,
                0.82 * inch,
                0.82 * inch,
                0.82 * inch,
                0.82 * inch,
                0.75 * inch,
            ],
        )
        style = [
            ("BACKGROUND", (0, 0), (-1, 0), self.primary),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.35, self.line),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, 0), 7),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ]
        for row_index in range(1, len(data)):
            if row_index % 2 == 0:
                style.append(
                    ("BACKGROUND", (0, row_index), (-1, row_index), self.surface)
                )
        table.setStyle(TableStyle(style))
        return table

    def _totals_table(
        self,
        styles: dict[str, ParagraphStyle],
        subtotal: Decimal,
        taxes: Decimal,
        total: Decimal,
    ) -> KeepTogether:
        data = [
            [
                Paragraph("Resumen financiero", styles["section"]),
                "",
            ],
            [
                Paragraph("Subtotal acumulado", styles["total_label"]),
                Paragraph(self._currency(subtotal), styles["total_value"]),
            ],
            [
                Paragraph("Impuestos acumulados", styles["total_label"]),
                Paragraph(self._currency(taxes), styles["total_value"]),
            ],
            [
                Paragraph("Total consolidado", styles["total_label"]),
                Paragraph(self._currency(total), styles["total_value"]),
            ],
        ]
        table = Table(data, colWidths=[2.25 * inch, 1.35 * inch], hAlign="RIGHT")
        table.setStyle(
            TableStyle(
                [
                    ("SPAN", (0, 0), (1, 0)),
                    ("BACKGROUND", (0, 0), (-1, 0), self.surface),
                    ("BOX", (0, 0), (-1, -1), 0.6, self.line),
                    ("LINEABOVE", (0, -1), (-1, -1), 1.4, self.primary),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EEEEFF")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        return KeepTogether([table])

    def _page_decoration(self, canvas, document) -> None:
        canvas.saveState()
        width, _ = landscape(letter)
        canvas.setStrokeColor(self.line)
        canvas.line(0.42 * inch, 0.34 * inch, width - 0.42 * inch, 0.34 * inch)
        canvas.setFillColor(self.muted)
        canvas.setFont("Helvetica", 6.5)
        canvas.drawString(
            0.42 * inch,
            0.2 * inch,
            "SmartInvoice - Reporte generado automáticamente",
        )
        page_text = f"Página {document.page}"
        canvas.drawRightString(
            width - 0.42 * inch,
            0.2 * inch,
            page_text,
        )
        canvas.restoreState()

    def _invoice_row(self, invoice: Invoice) -> list[str | int]:
        """Transforma una factura en una fila reutilizable por CSV y PDF."""
        return [
            invoice.id,
            invoice.invoice_number or "-",
            invoice.invoice_date.strftime("%d/%m/%Y")
            if invoice.invoice_date
            else "-",
            invoice.detected_provider_name or "Sin detectar",
            invoice.detected_nit or "-",
            self._money(invoice.subtotal),
            self._money(invoice.taxes),
            self._money(invoice.total),
            invoice.status.value,
        ]

    def _sum_decimal(self, invoices: list[Invoice], field: str) -> Decimal:
        """Suma un campo monetario tratando valores vacíos como cero."""
        return sum(
            (getattr(invoice, field) or Decimal("0") for invoice in invoices),
            Decimal("0"),
        )

    def _sum(self, invoices: list[Invoice], field: str) -> str:
        return self._money(self._sum_decimal(invoices, field))

    def _money(self, value: Decimal | None) -> str:
        return f"{value or Decimal('0'):.2f}"

    def _currency(self, value: Decimal) -> str:
        return f"Q {value:,.2f}"

    def _currency_text(self, value: str) -> str:
        return f"Q {Decimal(value):,.2f}"

    def _status_label(self, value: str) -> str:
        """Traduce el estado interno a una etiqueta para el usuario."""
        return {
            InvoiceStatus.PROCESSED.value: "Procesada",
            InvoiceStatus.PENDING.value: "Pendiente",
            InvoiceStatus.ERROR.value: "Revisar",
            InvoiceStatus.REJECTED.value: "Rechazada",
        }.get(value, value.title())
