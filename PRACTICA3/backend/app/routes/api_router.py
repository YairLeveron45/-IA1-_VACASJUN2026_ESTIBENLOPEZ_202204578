from fastapi import APIRouter

from app.routes.auth_routes import router as auth_router
from app.routes.health_routes import router as health_router
from app.routes.invoice_routes import router as invoice_router
from app.routes.processing_log_routes import router as processing_log_router
from app.routes.provider_routes import router as provider_router
from app.routes.report_routes import router as report_router
from app.routes.rpa_routes import router as rpa_router
from app.routes.rpa_simulator_routes import router as rpa_simulator_router
from app.routes.system_settings_routes import router as system_settings_router
from app.routes.user_routes import router as user_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(provider_router)
api_router.include_router(invoice_router)
api_router.include_router(processing_log_router)
api_router.include_router(report_router)
api_router.include_router(rpa_router)
api_router.include_router(rpa_simulator_router)
api_router.include_router(system_settings_router)
