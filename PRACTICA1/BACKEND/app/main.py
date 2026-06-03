"""
Punto de entrada del backend.

Este archivo crea la aplicacion FastAPI y registra las rutas
que permiten consultar la logica implementada en Prolog.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router


app = FastAPI(
    title="Ruta Mas Corta Entre Ciudades",
    description="Backend en Python que consulta Prolog para resolver rutas.",
    version="1.0.0",
)

# Permite que el frontend en desarrollo hecho con Vite consuma la API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registramos todos los endpoints definidos en app/api/routes.py.
app.include_router(router)


@app.get("/")
def health_check() -> dict[str, str]:
    """
    Endpoint basico para comprobar que el backend esta corriendo.

    Returns:
        dict[str, str]: mensaje simple de estado.
    """
    return {"message": "Backend activo y listo para consultar Prolog."}
