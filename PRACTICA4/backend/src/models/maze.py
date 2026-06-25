from typing import List, Tuple

# Clase que representa el laberinto: contiene la cuadricula y las posiciones inicio/destino
class Maze:
    def __init__(self, grid: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]):
        self.grid = grid          # Matriz 2D: 0 = libre, 1 = obstaculo
        self.start = start        # Coordenada (fila, columna) del inicio
        self.end = end            # Coordenada (fila, columna) del destino
        self.rows = len(grid)     # Numero de filas
        self.cols = len(grid[0]) if grid else 0  # Numero de columnas

    # Verifica si una celda esta dentro del laberinto y no es un obstaculo
    def is_valid(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols and self.grid[row][col] == 0

    # Obtiene los vecinos validos (arriba, abajo, izquierda, derecha) de una celda
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        return [(r, c) for dr, dc in directions
                if self.is_valid(r := row + dr, c := col + dc)]
