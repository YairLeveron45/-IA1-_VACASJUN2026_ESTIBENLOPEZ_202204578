# Implementacion manual del algoritmo DFS (Depth-First Search)
# Usa una pila LIFO para explorar el laberinto en profundidad
import time
from typing import List, Tuple
from ..models.maze import Maze

def solve(maze: Maze) -> dict:
    # Inicia el cronometro para medir el tiempo de ejecucion
    start_time = time.perf_counter()

    # Conjunto de celdas visitadas para evitar ciclos
    visited = set()
    # Lista que preserva el orden en que se exploraron las celdas
    explored_order = []
    # Diccionario para reconstruir la ruta (cada nodo guarda su predecesor)
    parent = {}

    # Pila LIFO (lista de Python): apila el nodo inicial
    stack = [maze.start]
    visited.add(maze.start)
    parent[maze.start] = None

    # Mientras haya nodos pendientes en la pila
    while stack:
        # Extrae el ultimo nodo agregado (LIFO)
        current = stack.pop()
        explored_order.append(current)

        # Si llegamos al destino, reconstruye la ruta desde parent
        if current == maze.end:
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            path.reverse()  # Invierte porque se construyo del destino al inicio
            elapsed = (time.perf_counter() - start_time) * 1000
            return {
                "path": path,
                "explored": explored_order,
                "nodes_explored": len(visited),
                "path_length": len(path),
                "execution_time_ms": round(elapsed, 3),
                "found": True
            }

        # Expande los vecinos validos no visitados
        for nr, nc in maze.get_neighbors(*current):
            neighbor = (nr, nc)
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current  # Registra quien descubrio este nodo
                stack.append(neighbor)

    # Si la pila se vacia sin encontrar el destino, no hay ruta
    elapsed = (time.perf_counter() - start_time) * 1000
    return {
        "path": [],
        "explored": explored_order,
        "nodes_explored": len(visited),
        "path_length": 0,
        "execution_time_ms": round(elapsed, 3),
        "found": False
    }
