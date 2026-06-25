# Router de FastAPI que expone los endpoints del sistema RoboMaze
from fastapi import APIRouter, HTTPException
from ..models.maze import Maze                       # Modelo del laberinto
from ..models.schemas import SolveRequest, SolveResponse, CompareRequest, CompareResponse, MazeInfo
from ..services import bfs, dfs                      # Algoritmos de busqueda
from ..mazes.predefined import PREDEFINED_MAZES, get_maze_by_id

# Prefijo /api para todos los endpoints
router = APIRouter(prefix="/api", tags=["maze"])

# Endpoint para ejecutar BFS: recibe grid, start, end y devuelve ruta + metricas
@router.post("/solve/bfs", response_model=SolveResponse)
def solve_bfs(req: SolveRequest):
    maze = Maze(req.grid, tuple(req.start), tuple(req.end))
    result = bfs.solve(maze)
    return SolveResponse(algorithm="BFS", **result)

# Endpoint para ejecutar DFS: recibe grid, start, end y devuelve ruta + metricas
@router.post("/solve/dfs", response_model=SolveResponse)
def solve_dfs(req: SolveRequest):
    maze = Maze(req.grid, tuple(req.start), tuple(req.end))
    result = dfs.solve(maze)
    return SolveResponse(algorithm="DFS", **result)

# Endpoint para comparar BFS vs DFS sobre el mismo laberinto
@router.post("/compare", response_model=CompareResponse)
def compare(req: CompareRequest):
    maze = Maze(req.grid, tuple(req.start), tuple(req.end))
    bfs_result = bfs.solve(maze)
    dfs_result = dfs.solve(maze)
    return CompareResponse(
        bfs=SolveResponse(algorithm="BFS", **bfs_result),
        dfs=SolveResponse(algorithm="DFS", **dfs_result)
    )

# Endpoint que lista los 5 laberintos predefinidos
@router.get("/mazes", response_model=list[MazeInfo])
def list_mazes():
    return [
        MazeInfo(
            id=m["id"], name=m["name"], grid=m["grid"],
            start=list(m["start"]), end=list(m["end"]),
            rows=len(m["grid"]), cols=len(m["grid"][0])
        )
        for m in PREDEFINED_MAZES
    ]

# Endpoint que devuelve un laberinto predefinido por su ID
@router.get("/mazes/{maze_id}", response_model=MazeInfo)
def get_maze(maze_id: int):
    maze = get_maze_by_id(maze_id)
    if not maze:
        raise HTTPException(status_code=404, detail="Laberinto no encontrado")
    return MazeInfo(
        id=maze["id"], name=maze["name"], grid=maze["grid"],
        start=list(maze["start"]), end=list(maze["end"]),
        rows=len(maze["grid"]), cols=len(maze["grid"][0])
    )

# Endpoint de health check para verificar que el servidor esta activo
@router.get("/health")
def health():
    return {"status": "ok"}
