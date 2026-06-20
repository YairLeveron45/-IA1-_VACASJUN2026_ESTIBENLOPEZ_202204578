import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.core.config import settings


class RpaSimulatorService:
    """Persiste los datos enviados al formulario contable simulado."""

    def __init__(self) -> None:
        self.output_directory = Path(settings.rpa_output_directory).resolve()
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def save_submission(self, fields: dict[str, str]) -> str:
        """Guarda el formulario en JSON y devuelve su identificador."""
        registration_id = uuid4().hex
        path = self.output_directory / f"submission-{registration_id}.json"
        path.write_text(
            json.dumps(
                {
                    "registration_id": registration_id,
                    "received_at": datetime.now(UTC).isoformat(),
                    "fields": fields,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return registration_id

    def get_submission(self, registration_id: str) -> dict | None:
        """Recupera un registro por ID o devuelve None si no existe."""
        if (
            len(registration_id) != 32
            or any(character not in "0123456789abcdef" for character in registration_id)
        ):
            return None
        path = self.output_directory / f"submission-{registration_id}.json"
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
