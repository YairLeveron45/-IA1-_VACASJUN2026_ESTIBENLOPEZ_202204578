from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.knowledge import (
    AdminLoginPayload,
    FailurePayload,
    RecommendationPayload,
    RulePayload,
    SymptomPayload,
    SystemConfigPayload,
)
from app.services import knowledge_service
from app.services.admin_auth_service import authenticate_admin, validate_admin_token
from app.services.system_config_service import (
    get_system_config,
    update_system_config,
)


router = APIRouter()
security = HTTPBearer()


def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not validate_admin_token(credentials.credentials):
        raise HTTPException(
            status_code=401,
            detail="Token de administrador invalido.",
        )

    return True


@router.post("/login")
def login_admin(payload: AdminLoginPayload):
    try:
        return authenticate_admin(payload.password)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error


@router.get("/knowledge", dependencies=[Depends(require_admin)])
def read_knowledge_base():
    try:
        return knowledge_service.get_knowledge_base()
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.get("/config", dependencies=[Depends(require_admin)])
def read_system_config():
    return get_system_config()


@router.put("/config", dependencies=[Depends(require_admin)])
def update_config(payload: SystemConfigPayload):
    try:
        return update_system_config(
            telegram_enabled=payload.telegram_enabled,
            telegram_chat_id=payload.telegram_chat_id,
            telegram_message_template=payload.telegram_message_template,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/symptoms", status_code=201, dependencies=[Depends(require_admin)])
def create_symptom(payload: SymptomPayload):
    try:
        return knowledge_service.create_symptom(payload.name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.put("/symptoms/{name}", dependencies=[Depends(require_admin)])
def update_symptom(name: str, payload: SymptomPayload):
    try:
        return knowledge_service.update_symptom(name, payload.name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/symptoms/{name}", dependencies=[Depends(require_admin)])
def delete_symptom(name: str):
    try:
        return knowledge_service.delete_symptom(name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.post("/failures", status_code=201, dependencies=[Depends(require_admin)])
def create_failure(payload: FailurePayload):
    try:
        return knowledge_service.create_failure(payload.name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.put("/failures/{name}", dependencies=[Depends(require_admin)])
def update_failure(name: str, payload: FailurePayload):
    try:
        return knowledge_service.update_failure(name, payload.name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/failures/{name}", dependencies=[Depends(require_admin)])
def delete_failure(name: str):
    try:
        return knowledge_service.delete_failure(name)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.post(
    "/recommendations",
    status_code=201,
    dependencies=[Depends(require_admin)],
)
def create_recommendation(payload: RecommendationPayload):
    try:
        return knowledge_service.create_recommendation(payload.failure, payload.text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.put("/recommendations/{failure}", dependencies=[Depends(require_admin)])
def update_recommendation(failure: str, payload: RecommendationPayload):
    try:
        return knowledge_service.update_recommendation(
            failure,
            payload.failure,
            payload.text,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/recommendations/{failure}", dependencies=[Depends(require_admin)])
def delete_recommendation(failure: str):
    try:
        return knowledge_service.delete_recommendation(failure)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.post("/rules", status_code=201, dependencies=[Depends(require_admin)])
def create_rule(payload: RulePayload):
    try:
        return knowledge_service.create_rule(payload.failure, payload.symptoms)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.put("/rules/{failure}", dependencies=[Depends(require_admin)])
def update_rule(failure: str, payload: RulePayload):
    try:
        return knowledge_service.update_rule(
            failure,
            payload.failure,
            payload.symptoms,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@router.delete("/rules/{failure}", dependencies=[Depends(require_admin)])
def delete_rule(failure: str):
    try:
        return knowledge_service.delete_rule(failure)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
