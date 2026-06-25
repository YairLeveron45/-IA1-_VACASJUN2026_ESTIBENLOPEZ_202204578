# Implementacion manual del algoritmo BFS (Breadth-First Search)
# Usa una cola FIFO para explorar el laberinto por niveles
import time
from collections import deque
from typing import List, Tuple
from ..models.maze import Maze

def solve(maze: Maze) -> dict:
    # Inicia el cronometro para medir el tiempo de ejecucion
    start_time = time.perf_counter()

    # Cola FIFO: guarda tuplas de (coordenada_actual, ruta_hasta_esa_coordenada)
    queue = deque()
    queue.append((maze.start, [maze.start]))
    # Conjunto de celdas visitadas para evitar ciclos
    visited = {maze.start}
    # Lista que preserva el orden en que se exploraron las celdas
    explored_order = []

    # Mientras haya nodos pendientes en la cola
    while queue:
        # Extrae el primer nodo de la cola (FIFO)
        (row, col), path = queue.popleft()
        explored_order.append((row, col))

        # Si llegamos al destino, devolvemos la ruta y metricas
        if (row, col) == maze.end:
            elapsed = (time.perf_counter() - start_time) * 1000
            return {
                "path": path,
                "explored": explored_order,
                "nodes_explored": len(visited),
                "path_length": len(path),
                "execution_time_ms": round(elapsed, 3),
                "found": True
            }

        # Expande todos los vecinos validos no visitados
        for nr, nc in maze.get_neighbors(row, col):
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(nr, nc)]))

    # Si la cola se vacia sin encontrar el destino, no hay ruta
    elapsed = (time.perf_counter() - start_time) * 1000
    return {
        "path": [],
        "explored": explored_order,
        "nodes_explored": len(visited),
        "path_length": 0,
        "execution_time_ms": round(elapsed, 3),
        "found": False
    }
