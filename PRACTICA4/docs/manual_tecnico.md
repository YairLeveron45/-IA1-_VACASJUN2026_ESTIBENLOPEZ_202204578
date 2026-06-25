# Manual Técnico - RoboMaze

## 1. Introducción

RoboMaze es un sistema de búsqueda de rutas en laberintos que implementa los algoritmos clásicos de inteligencia artificial BFS (Breadth-First Search) y DFS (Depth-First Search). El sistema permite representar laberintos como cuadrículas bidimensionales, definir obstáculos, puntos de inicio y destino, y ejecutar algoritmos de búsqueda para encontrar rutas óptimas.

## 2. Arquitectura del Sistema



### 2.2 Componentes

| Componente | Tecnología | Descripción |
|------------|-----------|-------------|
| Backend | Python 3.14 + FastAPI | API REST para ejecución de algoritmos |
| Frontend | HTML5 + CSS3 + JavaScript | Interfaz gráfica de usuario |
| Servidor | Uvicorn | Servidor ASGI para FastAPI |

### 2.3 Estructura del Proyecto

```
PRACTICA4/
├── backend/
│   └── src/
│       ├── main.py              # Punto de entrada, configuración FastAPI
│       ├── routers/
│       │   └── maze.py          # Controlador REST
│       ├── services/
│       │   ├── bfs.py           # Implementación BFS
│       │   └── dfs.py           # Implementación DFS
│       ├── models/
│       │   ├── maze.py          # Modelo del laberinto
│       │   └── schemas.py       # Esquemas Pydantic
│       └── mazes/
│           └── predefined.py    # 5 laberintos predefinidos
├── frontend/
│   ├── index.html               # Interfaz principal
│   ├── css/
│   │   └── style.css            # Estilos
│   └── js/
│       └── app.js               # Lógica del frontend
└── docs/
    ├── manual_tecnico.md         # Este documento
    └── manual_usuario.md         # Manual de usuario
```

## 3. Algoritmos Implementados

### 3.1 Breadth-First Search (BFS)

**Descripción:** BFS explora el laberinto por niveles, visitando primero todos los nodos vecinos antes de avanzar al siguiente nivel. Utiliza una cola (FIFO) para gestionar la exploración.

**Complejidad:**
- Tiempo: O(V + E) donde V = número de nodos, E = número de aristas
- Espacio: O(V)

**Características:**
- Garantiza encontrar la ruta más corta en número de aristas
- Explora de manera uniforme en todas las direcciones
- Mayor uso de memoria que DFS

**Implementación:**
```python
from collections import deque

def solve(maze):
    queue = deque()
    queue.append((maze.start, [maze.start]))
    visited = {maze.start}

    while queue:
        (row, col), path = queue.popleft()
        if (row, col) == maze.end:
            return path

        for neighbor in maze.get_neighbors(row, col):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []
```

### 3.2 Depth-First Search (DFS)

**Descripción:** DFS explora el laberinto profundizando primero en cada rama antes de retroceder. Utiliza una pila (LIFO) para gestionar la exploración.

**Complejidad:**
- Tiempo: O(V + E)
- Espacio: O(V)

**Características:**
- No garantiza la ruta más corta
- Utiliza menos memoria que BFS
- Puede quedar atrapado en caminos muy profundos

**Implementación:**
```python
def solve(maze):
    stack = [maze.start]
    visited = {maze.start}
    parent = {maze.start: None}

    while stack:
        current = stack.pop()
        if current == maze.end:
            # Reconstruir ruta
            path = []
            while current:
                path.append(current)
                current = parent[current]
            return path[::-1]

        for neighbor in maze.get_neighbors(*current):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)
    return []
```

## 4. API REST

### 4.1 Endpoints

| Método | Endpoint | Body | Respuesta | Descripción |
|--------|----------|------|-----------|-------------|
| POST | `/api/solve/bfs` | `{grid, start, end}` | `{path, explored, nodes_explored, path_length, execution_time_ms, found}` | Ejecuta BFS |
| POST | `/api/solve/dfs` | `{grid, start, end}` | `{path, explored, nodes_explored, path_length, execution_time_ms, found}` | Ejecuta DFS |
| POST | `/api/compare` | `{grid, start, end}` | `{bfs: {...}, dfs: {...}}` | Compara ambos algoritmos |
| GET | `/api/mazes` | - | `[{id, name, grid, start, end, rows, cols}]` | Lista laberintos |
| GET | `/api/mazes/{id}` | - | `{id, name, grid, start, end, rows, cols}` | Obtiene laberinto |
| GET | `/api/health` | - | `{status: "ok"}` | Health check |

### 4.2 Formato de Solicitud

```json
{
  "grid": [[0,0,0],[1,1,0],[0,0,0]],
  "start": [0, 0],
  "end": [2, 2]
}
```

- `grid`: matriz 2D donde 0 = camino libre, 1 = obstáculo
- `start`: coordenada [fila, columna] de inicio
- `end`: coordenada [fila, columna] de destino

### 4.3 Formato de Respuesta

```json
{
  "algorithm": "BFS",
  "path": [[0,0], [0,1], [0,2], [1,2], [2,2]],
  "explored": [[0,0], [0,1], [1,0], [0,2], [1,2], [2,2]],
  "nodes_explored": 6,
  "path_length": 5,
  "execution_time_ms": 0.045,
  "found": true
}
```

## 5. Requerimientos Funcionales

| ID | Descripción |
|----|-------------|
| RF01 | El sistema debe representar laberintos como cuadrículas bidimensionales |
| RF02 | El sistema debe implementar el algoritmo BFS para búsqueda de rutas |
| RF03 | El sistema debe implementar el algoritmo DFS para búsqueda de rutas |
| RF04 | El usuario debe poder definir punto de inicio y destino |
| RF05 | El usuario debe poder colocar obstáculos en el laberinto |
| RF06 | El sistema debe mostrar gráficamente la ruta encontrada |
| RF07 | El sistema debe mostrar la cantidad de nodos explorados |
| RF08 | El sistema debe mostrar el tiempo de ejecución de cada algoritmo |
| RF09 | El sistema debe incluir 5 laberintos predefinidos para pruebas |
| RF10 | El sistema debe poder ejecutar BFS y DFS de forma independiente |
| RF11 | El sistema debe permitir la comparación entre BFS y DFS |
| RF12 | El sistema debe manejar errores cuando no exista ruta válida |

## 6. Requerimientos No Funcionales

| ID | Descripción |
|----|-------------|
| RNF01 | El backend debe desarrollarse exclusivamente en Python |
| RNF02 | La API debe ser RESTful |
| RNF03 | El frontend debe ser una interfaz web interactiva |
| RNF04 | Los algoritmos deben ser implementados manualmente (sin librerías) |
| RNF05 | El sistema debe responder en menos de 1 segundo para laberintos de hasta 10x10 |
| RNF06 | El código debe seguir el patrón MVC con capa de servicios |
| RNF07 | El sistema debe usar control de versiones con Git |

## 7. Diagramas

### 7.1 Diagrama de Arquitectura

![Diagrama de Arquitectura](screenshots/DIAGRAMA%20DE%20ARQUITECTURA.svg)

### 7.2 Diagrama de Flujo BFS

![Diagrama BFS](screenshots/Diagrama%20bfs.svg)

### 7.3 Diagrama de Flujo DFS

![Diagrama DFS](screenshots/Diagrama%20dfs.svg)

