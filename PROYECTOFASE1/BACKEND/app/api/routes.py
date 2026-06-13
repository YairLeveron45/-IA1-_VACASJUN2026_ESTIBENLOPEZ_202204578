from fastapi import APIRouter, HTTPException

from app.schemas.diagnosis import DiagnosisRequest, SymptomSuggestionRequest
from app.services.diagnosis_service import build_diagnosis
from app.services.history_service import load_history
from app.services.knowledge_service import get_symptom_suggestions, get_symptoms


router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/symptoms")
def list_symptoms():
    return {"items": get_symptoms()}


@router.post("/symptom-suggestions")
def suggest_related_symptoms(payload: SymptomSuggestionRequest):
    try:
        return get_symptom_suggestions(payload.symptoms)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/diagnose")
def diagnose(payload: DiagnosisRequest):
    if not payload.symptoms:
        raise HTTPException(
            status_code=400,
            detail="Debes enviar al menos un sintoma para generar un diagnostico.",
        )

    try:
        diagnosis = build_diagnosis(
            symptoms=payload.symptoms,
            notify_telegram=payload.notify_telegram,
            chat_id=payload.chat_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return diagnosis.model_dump()


@router.get("/history")
def get_history():
    return {"items": load_history()}
