# RoboMaze

Sistema de búsqueda de rutas en laberintos utilizando los algoritmos BFS (Breadth-First Search) y DFS (Depth-First Search).

## Requisitos

- Python 3.11+
- Navegador web moderno

## Instalación y Ejecución

```bash
# Instalar dependencias
pip install -r backend/requirements.txt

# Iniciar el servidor
cd backend
python -m uvicorn src.main:app --reload
```

Abrir en el navegador: http://localhost:8000

## Estructura del Proyecto

```
PRACTICA4/
├── backend/
│   └── src/
│       ├── main.py          # Punto de entrada FastAPI
│       ├── routers/
│       │   └── maze.py      # Endpoints REST
│       ├── services/
│       │   ├── bfs.py       # Algoritmo BFS
│       │   └── dfs.py       # Algoritmo DFS
│       ├── models/
│       │   ├── maze.py      # Modelo del laberinto
│       │   └── schemas.py   # Esquemas Pydantic
│       └── mazes/
│           └── predefined.py # 5 laberintos predefinidos
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
└── docs/
    └── (documentación)
```

## API REST

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /api/solve/bfs | Ejecuta BFS |
| POST | /api/solve/dfs | Ejecuta DFS |
| POST | /api/compare | Compara BFS vs DFS |
| GET | /api/mazes | Lista laberintos predefinidos |
| GET | /api/mazes/{id} | Obtiene laberinto por ID |
| GET | /api/health | Health check |
