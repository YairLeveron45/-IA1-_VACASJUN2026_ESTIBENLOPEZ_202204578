from fastapi import APIRouter, HTTPException

from app.schemas.diagnosis import TelegramMessageRequest
from app.services.telegram_service import send_diagnosis_message


router = APIRouter()


@router.post("/send")
def send_telegram_message(payload: TelegramMessageRequest):
    sent = send_diagnosis_message(payload.message, payload.chat_id)
    if not sent:
        raise HTTPException(
            status_code=501,
            detail="La integracion con Telegram aun no esta configurada.",
        )

    return {"message": "Mensaje enviado correctamente"}
