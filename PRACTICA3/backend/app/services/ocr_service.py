from pathlib import Path

import fitz
import pytesseract

from app.core.config import settings
from app.services.image_processing_service import ImageProcessingService


class OcrService:
    """Extrae texto nativo de PDF o aplica OCR sobre imágenes procesadas."""

    def __init__(
        self,
        image_processor: ImageProcessingService | None = None,
    ) -> None:
        self.image_processor = image_processor or ImageProcessingService()

    def extract_text(self, file_path: Path) -> tuple[str, int]:
        """Obtiene el texto y la cantidad de páginas procesadas."""
        if file_path.suffix.lower() == ".pdf":
            native_text = self._extract_native_pdf_text(file_path)
            if native_text is not None:
                return native_text

        pages = self.image_processor.load_document(file_path)
        extracted_pages = []

        for page_number, image in enumerate(pages, start=1):
            processed = self.image_processor.preprocess(image)
            text = pytesseract.image_to_string(
                processed,
                lang=settings.tesseract_language,
                config="--oem 3 --psm 6",
            )
            extracted_pages.append(
                f"--- Página {page_number} ---\n{text.strip()}"
            )

        return "\n\n".join(extracted_pages).strip(), len(pages)

    def _extract_native_pdf_text(
        self,
        file_path: Path,
    ) -> tuple[str, int] | None:
        """Usa texto embebido cuando es suficiente; los escaneos pasan a OCR."""
        try:
            document = fitz.open(file_path)
            pages = [
                page.get_text("text", sort=True).strip()
                for page in document
            ]
            page_count = document.page_count
            document.close()
        except (fitz.FileDataError, ValueError):
            # Un PDF sin texto legible se procesa después como imagen.
            return None

        useful_characters = sum(
            character.isalnum()
            for page in pages
            for character in page
        )
        if page_count == 0 or useful_characters < 80:
            return None

        extracted = [
            f"--- Página {number} ---\n{text}"
            for number, text in enumerate(pages, start=1)
        ]
        return "\n\n".join(extracted).strip(), page_count
