import json
import os
from pathlib import Path


CONFIG_FILE = Path(__file__).resolve().parents[1] / "data" / "system_config.json"

DEFAULT_MESSAGE_TEMPLATE = """🩺 DOCTOR BYTE - DIAGNOSTICO
--------------------------------
📅 Fecha y hora: {fecha}

⚠️ Falla detectada:
{falla}

🧩 Sintomas evaluados:
{sintomas}

🛠️ Recomendacion:
{recomendacion}

✅ Diagnostico generado correctamente por el sistema experto Doctor Byte."""

DEFAULT_CONFIG = {
    "telegram_enabled": True,
    "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID") or "",
    "telegram_message_template": DEFAULT_MESSAGE_TEMPLATE,
}


def get_system_config() -> dict:
    if not CONFIG_FILE.exists():
        save_system_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    content = CONFIG_FILE.read_text(encoding="utf-8").strip()
    if not content:
        save_system_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    stored_config = json.loads(content)
    return {**DEFAULT_CONFIG, **stored_config}


def save_system_config(config: dict) -> dict:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return config


def update_system_config(
    telegram_enabled: bool,
    telegram_chat_id: str,
    telegram_message_template: str,
) -> dict:
    template = telegram_message_template.strip()
    if not template:
        raise ValueError("La plantilla del mensaje no puede estar vacia.")

    required_tokens = ["{fecha}", "{falla}", "{sintomas}", "{recomendacion}"]
    missing_tokens = [token for token in required_tokens if token not in template]
    if missing_tokens:
        raise ValueError(
            "La plantilla debe incluir: " + ", ".join(missing_tokens)
        )

    return save_system_config(
        {
            "telegram_enabled": telegram_enabled,
            "telegram_chat_id": telegram_chat_id.strip(),
            "telegram_message_template": template,
        }
    )
