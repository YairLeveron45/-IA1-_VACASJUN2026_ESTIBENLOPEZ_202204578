from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin_routes import router as admin_router
from app.api.routes import router as api_router
from app.api.telegram_routes import router as telegram_router


app = FastAPI(title="Doctor Byte API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(admin_router, prefix="/api/admin")
app.include_router(telegram_router, prefix="/api/telegram")


@app.get("/")
def read_root():
    return {"message": "Doctor Byte API activa"}
