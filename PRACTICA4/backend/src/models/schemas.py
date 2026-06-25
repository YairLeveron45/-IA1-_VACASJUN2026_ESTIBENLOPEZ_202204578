# Esquemas Pydantic para validar y documentar las peticiones/respuestas de la API
from pydantic import BaseModel
from typing import List, Tuple, Optional

# Peticion para resolver un laberinto con un solo algoritmo
class SolveRequest(BaseModel):
    grid: List[List[int]]     # Matriz 2D del laberinto
    start: Tuple[int, int]    # Coordenada de inicio (fila, columna)
    end: Tuple[int, int]      # Coordenada de destino (fila, columna)

# Respuesta de un algoritmo: incluye ruta, exploracion, metricas de rendimiento
class SolveResponse(BaseModel):
    algorithm: str                          # Nombre del algoritmo (BFS o DFS)
    path: List[Tuple[int, int]]            # Lista de celdas que forman la ruta solucion
    explored: List[Tuple[int, int]]        # Lista de celdas visitadas durante la busqueda
    nodes_explored: int                     # Cantidad total de nodos explorados
    path_length: int                        # Longitud de la ruta encontrada
    execution_time_ms: float                # Tiempo de ejecucion en milisegundos
    found: bool                             # Indica si se encontro una ruta al destino

# Informacion de un laberinto predefinido
class MazeInfo(BaseModel):
    id: int                   # Identificador unico
    name: str                 # Nombre descriptivo
    grid: List[List[int]]     # Matriz del laberinto
    start: List[int]          # Coordenada de inicio
    end: List[int]            # Coordenada de destino
    rows: int                 # Cantidad de filas
    cols: int                 # Cantidad de columnas

# Peticion para comparar ambos algoritmos sobre el mismo laberinto
class CompareRequest(BaseModel):
    grid: List[List[int]]
    start: Tuple[int, int]
    end: Tuple[int, int]

# Respuesta de la comparacion: contiene el resultado de BFS y DFS lado a lado
class CompareResponse(BaseModel):
    bfs: SolveResponse   # Resultado de BFS
    dfs: SolveResponse   # Resultado de DFS
