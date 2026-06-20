from pathlib import Path

import cv2
import fitz
import numpy as np

from app.core.exceptions import InvalidFileError


class ImageProcessingService:
    """Convierte documentos y mejora imágenes antes de ejecutar Tesseract."""

    supported_image_extensions = {".jpg", ".jpeg", ".png"}

    def load_document(self, file_path: Path) -> list[np.ndarray]:
        """Carga un PDF o imagen y rechaza formatos o archivos inválidos."""
        extension = file_path.suffix.lower()
        if extension == ".pdf":
            return self._load_pdf(file_path)
        if extension in self.supported_image_extensions:
            image = cv2.imread(str(file_path))
            if image is None:
                raise InvalidFileError("No se pudo leer la imagen.")
            return [image]
        raise InvalidFileError("Formato no compatible con OCR.")

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Corrige inclinación, reduce ruido y aumenta el contraste del texto."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = self._deskew(gray)
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        return cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            15,
        )

    def _load_pdf(self, file_path: Path) -> list[np.ndarray]:
        """Renderiza cada página del PDF como una imagen para OCR."""
        images: list[np.ndarray] = []
        try:
            document = fitz.open(file_path)
            for page in document:
                pixmap = page.get_pixmap(
                    matrix=fitz.Matrix(2.0, 2.0),
                    alpha=False,
                )
                array = np.frombuffer(pixmap.samples, dtype=np.uint8)
                image = array.reshape(pixmap.height, pixmap.width, pixmap.n)
                if pixmap.n == 4:
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
                else:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                images.append(image)
            document.close()
        except (fitz.FileDataError, ValueError) as exc:
            # Normaliza errores de PyMuPDF como un error de archivo controlado.
            raise InvalidFileError("El documento PDF no es válido.") from exc

        if not images:
            raise InvalidFileError("El documento PDF no contiene páginas.")
        return images

    def _deskew(self, gray: np.ndarray) -> np.ndarray:
        """Endereza inclinaciones moderadas sin alterar imágenes poco confiables."""
        inverted = cv2.bitwise_not(gray)
        coordinates = np.column_stack(np.where(inverted > 0))
        if len(coordinates) < 20:
            return gray

        angle = cv2.minAreaRect(coordinates)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        if abs(angle) < 0.2 or abs(angle) > 15:
            return gray

        height, width = gray.shape
        center = (width // 2, height // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(
            gray,
            matrix,
            (width, height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )
