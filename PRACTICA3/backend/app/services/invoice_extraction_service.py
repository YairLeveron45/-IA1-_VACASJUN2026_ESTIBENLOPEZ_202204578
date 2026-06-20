import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from app.schemas.ocr_schema import ExtractedInvoiceData


class InvoiceExtractionService:
    """Detecta y valida campos administrativos dentro del texto OCR."""

    date_formats = (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d/%m/%y",
        "%d-%m-%y",
    )
    spanish_months = {
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "setiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12,
    }

    def extract(
        self,
        text: str,
    ) -> tuple[ExtractedInvoiceData, list[str]]:
        """Extrae los siete campos requeridos y devuelve advertencias."""
        normalized = self._normalize_text(text)
        lines = [line.strip() for line in normalized.splitlines() if line.strip()]

        data = ExtractedInvoiceData(
            invoice_number=self._extract_invoice_number(normalized),
            invoice_date=self._extract_invoice_date(normalized),
            provider_name=self._extract_provider(normalized, lines),
            nit=self._extract_tax_id(normalized),
            subtotal=self._extract_amount(
                normalized,
                ("subtotal", "sub total"),
            ),
            taxes=self._extract_amount(
                normalized,
                ("iva", "impuesto", "impuestos"),
            ),
            total=self._extract_total(normalized),
        )
        return data, self.validate(data, normalized)

    def validate(
        self,
        data: ExtractedInvoiceData,
        source_text: str = "",
    ) -> list[str]:
        """Comprueba campos faltantes, fecha y coherencia de los montos."""
        warnings = []
        labels = {
            "invoice_number": "número de factura",
            "invoice_date": "fecha",
            "provider_name": "proveedor",
            "nit": "NIT",
            "subtotal": "subtotal",
            "taxes": "impuestos",
            "total": "total",
        }
        for field, label in labels.items():
            if not getattr(data, field):
                warnings.append(f"No se pudo detectar: {label}.")

        parsed_date = self.parse_date(data.invoice_date)
        if data.invoice_date and parsed_date is None:
            warnings.append("La fecha detectada no tiene un formato válido.")

        subtotal = self.parse_amount(data.subtotal)
        taxes = self.parse_amount(data.taxes)
        total = self.parse_amount(data.total)
        if all(value is not None for value in (subtotal, taxes, total)):
            difference = abs((subtotal + taxes) - total)
            withholding = self._extract_withholding(source_text)
            matches_withholding = (
                withholding is not None
                and abs((subtotal + taxes - withholding) - total)
                <= Decimal("0.05")
            )
            if difference > Decimal("0.05") and not matches_withholding:
                warnings.append(
                    "El total no coincide con subtotal más impuestos."
                )
        return warnings

    def parse_date(self, value: str | None) -> date | None:
        """Convierte fechas numéricas o escritas en español."""
        if not value:
            return None
        for date_format in self.date_formats:
            try:
                return datetime.strptime(value, date_format).date()
            except ValueError:
                continue

        natural_date = re.fullmatch(
            r"(\d{1,2})\s+de\s+([a-z]+)\s+de\s+(\d{4})",
            self._normalize_text(value).strip(),
        )
        if natural_date:
            day, month_name, year = natural_date.groups()
            month = self.spanish_months.get(month_name)
            if month:
                try:
                    return date(int(year), month, int(day))
                except ValueError:
                    return None
        return None

    def parse_amount(self, value: str | None) -> Decimal | None:
        """Normaliza separadores decimales y devuelve un monto seguro."""
        if not value:
            return None
        cleaned = re.sub(r"[^\d,.-]", "", value)
        if "," in cleaned and "." in cleaned:
            if cleaned.rfind(".") > cleaned.rfind(","):
                cleaned = cleaned.replace(",", "")
            else:
                cleaned = cleaned.replace(".", "").replace(",", ".")
        elif "," in cleaned:
            parts = cleaned.split(",")
            cleaned = "".join(parts) if len(parts[-1]) == 3 else ".".join(parts)
        elif "." in cleaned:
            parts = cleaned.split(".")
            if len(parts) > 1 and len(parts[-1]) == 3:
                cleaned = "".join(parts)
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            # Un valor no numérico se considera ausente para la validación.
            return None

    def _normalize_text(self, text: str) -> str:
        """Simplifica mayúsculas, acentos y saltos para facilitar búsquedas."""
        text = unicodedata.normalize("NFKD", text)
        text = "".join(
            character
            for character in text
            if not unicodedata.combining(character)
        )
        return text.lower().replace("\r", "")

    def _match_value(
        self,
        text: str,
        patterns: tuple[str, ...],
    ) -> str | None:
        """Devuelve el primer valor que coincida con los patrones indicados."""
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip().upper()
        return None

    def _extract_invoice_number(self, text: str) -> str | None:
        """Busca el número de factura en formatos comunes."""
        compact = re.sub(r"\s+", " ", text)
        split_number = re.search(
            r"factura\s*n(?:o|º|°)?\.?\s*[:#-]?\s*"
            r"(\d{1,8})\s*(?:[/.-]\s*)?((?:19|20)\d{2})\b",
            compact,
        )
        if split_number:
            return f"{split_number.group(1)}/{split_number.group(2)}"

        return self._match_value(
            compact,
            (
                r"(?:numero|no\.?|num\.?|nro\.?)\s*(?:de\s*)?"
                r"factura\s*[:#-]?\s*([a-z0-9][a-z0-9/-]{1,})",
                r"factura\s*(?:no\.?|num\.?|nro\.?|#|nº)?\s*[:#-]?\s*"
                r"([a-z0-9][a-z0-9/-]{1,})",
            ),
        )

    def _extract_invoice_date(self, text: str) -> str | None:
        """Busca una fecha explícita o el cierre de un período facturado."""
        compact = re.sub(r"\s+", " ", text)
        explicit = self._match_value(
            compact,
            (
                r"(?:fecha(?:\s+de\s+emision)?)\s*[:#-]?\s*"
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(\d{4}-\d{1,2}-\d{1,2})",
            ),
        )
        if explicit:
            return explicit

        period = re.search(
            r"del\s+\d{1,2}\s+al\s+(\d{1,2})\s+de\s+("
            + "|".join(self.spanish_months)
            + r")\s+de\s+(\d{4})",
            compact,
        )
        if period:
            day, month_name, year = period.groups()
            return (
                f"{int(day):02d}/"
                f"{self.spanish_months[month_name]:02d}/{year}"
            )
        return None

    def _extract_tax_id(self, text: str) -> str | None:
        """Extrae NIT, NIF o CIF del emisor."""
        compact = re.sub(r"\s+", " ", text)
        return self._match_value(
            compact,
            (
                r"\bn\.?i\.?t\.?\s*[:#-]?\s*([0-9a-z-]{5,20})",
                r"\b(?:nif\s*/\s*cif|nif|cif)\s*[:#-]?\s*"
                r"([0-9a-z-]{5,20})",
            ),
        )

    def _extract_provider(
        self,
        text: str,
        lines: list[str],
    ) -> str | None:
        """Identifica el proveedor mediante etiquetas o encabezados."""
        compact = re.sub(r"\s+", " ", text)
        landlord = re.search(
            r"arrendador\s+nombre\s+(.{3,100}?)\s+"
            r"(?:nif\s*/\s*cif|nif|cif|direccion)",
            compact,
        )
        if landlord:
            return landlord.group(1).strip(" _-").title()

        for line in lines[:20]:
            match = re.search(
                r"(?:proveedor|razon social|emisor)\s*[:#-]\s*(.{3,80})",
                line,
            )
            if match:
                return match.group(1).strip().title()

        ignored = (
            "factura",
            "nit",
            "fecha",
            "pagina",
            "subtotal",
            "total",
        )
        for line in lines[:8]:
            if (
                3 <= len(line) <= 80
                and any(character.isalpha() for character in line)
                and not any(word in line for word in ignored)
            ):
                return line.title()
        return None

    def _extract_amount(
        self,
        text: str,
        labels: tuple[str, ...],
    ) -> str | None:
        """Extrae el último monto de la línea asociada a una etiqueta."""
        label_pattern = "|".join(re.escape(label) for label in labels)
        line_match = re.search(
            rf"^.*?\b(?:{label_pattern})\b(.*)$",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        if not line_match:
            return None

        remainder = re.sub(
            r"\d+(?:[.,]\d+)?\s*%",
            "",
            line_match.group(1),
        )
        amounts = re.findall(r"-?\d[\d.,]*\d|-?\d", remainder)
        return amounts[-1] if amounts else None

    def _extract_total(self, text: str) -> str | None:
        """Obtiene el último total encontrado para evitar subtotales previos."""
        matches = re.findall(
            r"(?:total(?:\s+a\s+pagar|\s+a\s+ingresar)?|monto\s+total)"
            r"[!:\s.-]*(?:q|€|\$)?\s*(-?\d[\d.,]*\d|\d)\s*(?:€|q|\$)?",
            text,
            flags=re.IGNORECASE,
        )
        return matches[-1] if matches else None

    def _extract_withholding(self, text: str) -> Decimal | None:
        """Detecta retenciones para validar correctamente el total final."""
        if not text:
            return None
        candidate_lines = [
            line
            for line in text.splitlines()
            if "irpf" in line or "retencion" in line
        ]
        candidate_lines.sort(key=lambda line: "irpf" not in line)

        for line in candidate_lines:
            without_percentages = re.sub(
                r"\d+(?:[.,]\d+)?\s*%",
                "",
                line,
            )
            amounts = re.findall(
                r"(?:q|€|\$)?\s*(\d[\d.,]*\d|\d)\s*(?:€|q|\$)?",
                without_percentages,
            )
            if amounts:
                return self.parse_amount(amounts[-1])
        return None
