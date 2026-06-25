# Definicion de los 5 laberintos predefinidos del sistema
# 0 = celda libre, 1 = obstaculo
from typing import List, Tuple, Dict

PREDEFINED_MAZES: List[Dict] = [
    # Laberinto Simple: 5x5, camino despejado en forma de "S"
    {
        "id": 1,
        "name": "Laberinto Simple",
        "grid": [
            [0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1],
            [0, 0, 0, 0, 0]
        ],
        "start": (0, 0),
        "end": (4, 4)
    },
    # Laberinto Espiral: 7x7, pasillo que da vueltas alrededor de un nucleo
    {
        "id": 2,
        "name": "Laberinto Espiral",
        "grid": [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 1, 1, 1, 0, 1, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0]
        ],
        "start": (0, 0),
        "end": (6, 6)
    },
    # Laberinto Obstaculos: 8x8, multiples barreras verticales
    {
        "id": 3,
        "name": "Laberinto Obstaculos",
        "grid": [
            [0, 0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 1, 0],
            [1, 1, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ],
        "start": (0, 0),
        "end": (7, 7)
    },
    # Laberinto Puente: 7x9, pasillos horizontales separados por muros
    {
        "id": 4,
        "name": "Laberinto Puente",
        "grid": [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]
        ],
        "start": (0, 0),
        "end": (6, 8)
    },
    # Laberinto Complejo: 10x10, camino largo y sinuoso con muchas bifurcaciones
    {
        "id": 5,
        "name": "Laberinto Complejo",
        "grid": [
            [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 1, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 1, 1, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 1, 1, 1, 1, 0, 0, 0]
        ],
        "start": (0, 0),
        "end": (9, 9)
    }
]

# Busca un laberinto por su ID, retorna None si no existe
def get_maze_by_id(maze_id: int) -> Dict:
    for maze in PREDEFINED_MAZES:
        if maze["id"] == maze_id:
            return maze
    return None
