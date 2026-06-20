from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import InvalidFileError


class FileStorageService:
    """Guarda facturas de forma segura y controla tipo, tamaño y ruta."""

    allowed_types = {
        ".pdf": {"application/pdf"},
        ".jpg": {"image/jpeg"},
        ".jpeg": {"image/jpeg"},
        ".png": {"image/png"},
    }
    chunk_size = 1024 * 1024

    def __init__(self, upload_directory: str | None = None) -> None:
        self.upload_directory = Path(
            upload_directory or settings.upload_directory
        ).resolve()
        self.upload_directory.mkdir(parents=True, exist_ok=True)

    async def save_invoice(self, upload: UploadFile) -> tuple[str, str, str]:
        """Valida y escribe una factura por bloques para limitar memoria y tamaño."""
        original_name = Path(upload.filename or "").name
        extension = Path(original_name).suffix.lower()
        content_type = (upload.content_type or "").lower()

        if not original_name or extension not in self.allowed_types:
            raise InvalidFileError(
                "Formato no permitido. Utiliza PDF, JPG, JPEG o PNG."
            )
        if content_type not in self.allowed_types[extension]:
            raise InvalidFileError(
                "El tipo del archivo no coincide con su extensión."
            )

        stored_name = f"{uuid4().hex}{extension}"
        destination = (self.upload_directory / stored_name).resolve()
        self._ensure_inside_upload_directory(destination)
        total_size = 0

        try:
            with destination.open("wb") as output:
                while chunk := await upload.read(self.chunk_size):
                    total_size += len(chunk)
                    if total_size > settings.max_upload_size_bytes:
                        raise InvalidFileError(
                            f"El archivo supera el límite de "
                            f"{settings.max_upload_size_mb} MB."
                        )
                    output.write(chunk)
        except Exception:
            # Elimina archivos parciales ante límites excedidos o errores de escritura.
            destination.unlink(missing_ok=True)
            raise
        finally:
            await upload.close()

        if total_size == 0:
            destination.unlink(missing_ok=True)
            raise InvalidFileError("El archivo está vacío.")

        return original_name, str(destination), content_type

    def get_existing_path(self, stored_path: str) -> Path:
        """Devuelve una ruta solo si pertenece al directorio permitido y existe."""
        path = Path(stored_path).resolve()
        self._ensure_inside_upload_directory(path)
        if not path.is_file():
            raise InvalidFileError("El archivo de la factura no está disponible.")
        return path

    def delete(self, stored_path: str) -> None:
        """Elimina un archivo validando antes que la ruta sea segura."""
        path = Path(stored_path).resolve()
        self._ensure_inside_upload_directory(path)
        path.unlink(missing_ok=True)

    def _ensure_inside_upload_directory(self, path: Path) -> None:
        """Bloquea intentos de acceso fuera del directorio de cargas."""
        if path != self.upload_directory and self.upload_directory not in path.parents:
            raise InvalidFileError("Ruta de archivo inválida.")
