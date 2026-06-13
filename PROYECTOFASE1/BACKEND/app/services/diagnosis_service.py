from datetime import datetime, timedelta, timezone

from app.schemas.diagnosis import DiagnosisResponse
from app.services.history_service import save_history
from app.services.prolog_service import run_diagnosis
from app.services.system_config_service import get_system_config
from app.services.telegram_service import send_diagnosis_message


def _format_label(value: str) -> str:
    return value.replace("_", " ").title()


def _format_telegram_message(diagnosis: dict) -> str:
    guatemala_timezone = timezone(timedelta(hours=-6))
    generated_at = datetime.now(guatemala_timezone).strftime(
        "%d/%m/%Y %H:%M:%S"
    )
    symptoms = ", ".join(
        _format_label(symptom) for symptom in diagnosis["matched_symptoms"]
    )
    config = get_system_config()

    return config["telegram_message_template"].format(
        fecha=generated_at,
        falla=_format_label(diagnosis["failure"]),
        sintomas=symptoms,
        recomendacion=diagnosis["recommendation"],
    )


def build_diagnosis(
    symptoms: list[str],
    notify_telegram: bool = False,
    chat_id: str | None = None,
) -> DiagnosisResponse:
    diagnosis = run_diagnosis(symptoms)
    telegram_sent = False

    if notify_telegram:
        telegram_sent = send_diagnosis_message(
            _format_telegram_message(diagnosis),
            chat_id,
        )

    response = DiagnosisResponse(
        failure=diagnosis["failure"],
        recommendation=diagnosis["recommendation"],
        matched_symptoms=diagnosis["matched_symptoms"],
        telegram_sent=telegram_sent,
    )

    save_history(response.model_dump())
    return response
