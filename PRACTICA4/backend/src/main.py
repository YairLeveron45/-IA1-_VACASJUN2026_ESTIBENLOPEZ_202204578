# Importaciones principales de FastAPI y utilerias
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from .routers import maze

# Creacion de la aplicacion FastAPI con metadatos
app = FastAPI(
    title="RoboMaze API",
    description="API de busqueda de rutas en laberintos usando BFS y DFS",
    version="1.0.0"
)

# Configuracion de CORS para permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de las rutas de la API (prefijadas con /api)
app.include_router(maze.router)

# Determinacion de la ruta a la carpeta frontend relativa al backend
_base = Path(__file__).resolve().parent.parent
frontend_dir = _base / "frontend" if (_base / "frontend").exists() else _base.parent / "frontend"

# Ruta raiz: sirve el index.html del frontend
@app.get("/")
def serve_index():
    return FileResponse(frontend_dir / "index.html")

# Ruta para archivos CSS del frontend
@app.get("/css/{file:path}")
def serve_css(file: str):
    return FileResponse(frontend_dir / "css" / file)

# Ruta para archivos JavaScript del frontend
@app.get("/js/{file:path}")
def serve_js(file: str):
    return FileResponse(frontend_dir / "js" / file)

# Punto de entrada para ejecucion directa del servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
