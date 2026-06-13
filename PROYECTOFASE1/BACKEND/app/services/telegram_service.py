import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_diagnosis_message(message: str, chat_id: str | None = None) -> bool:
    from app.services.system_config_service import get_system_config

    config = get_system_config()
    if not config["telegram_enabled"]:
        return False

    target_chat_id = chat_id or config["telegram_chat_id"] or TELEGRAM_CHAT_ID

    if not TELEGRAM_BOT_TOKEN or not target_chat_id:
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": target_chat_id,
        "text": message,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False
