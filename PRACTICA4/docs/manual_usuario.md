# Manual de Usuario - RoboMaze

RoboMaze es una aplicación web para construir laberintos y resolverlos con los algoritmos de búsqueda BFS (Breadth-First Search) y DFS (Depth-First Search). El sistema permite cargar laberintos predefinidos, editar celdas manualmente, ejecutar cada algoritmo y comparar sus resultados.

![Pantalla principal de RoboMaze](screenshots/pantalla_principal.png)

## 1. Requisitos

- Python 3.11 o superior.
- Navegador web moderno, por ejemplo Chrome, Edge o Firefox.
- Conexión local al puerto `8000`.

## 2. Instalación y Ejecución

Desde la carpeta principal del proyecto, ejecutar:

```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.src.main:app --reload
```

Luego abrir el navegador en:

- Aplicación web: `http://localhost:8000`
- Documentación interactiva de la API: `http://localhost:8000/docs`
- Estado del servidor: `http://localhost:8000/api/health`

## 3. Pantalla Principal

La interfaz está organizada en tres áreas:

1. Panel lateral: permite seleccionar laberintos, elegir el modo de edición y ejecutar algoritmos.
2. Área del laberinto: muestra la cuadrícula editable.
3. Panel de resultados: presenta las métricas obtenidas por BFS y DFS.

## 4. Seleccionar un Laberinto Predefinido

1. Abrir el selector del panel **Laberintos**.
2. Elegir uno de los laberintos disponibles.
3. El laberinto se carga automáticamente en la cuadrícula.

Laberintos incluidos:

| ID | Nombre | Tamaño |
|----|--------|--------|
| 1 | Laberinto Simple | 5x5 |
| 2 | Laberinto Espiral | 7x7 |
| 3 | Laberinto Obstáculos | 8x8 |
| 4 | Laberinto Puente | 7x9 |
| 5 | Laberinto Complejo | 10x10 |

## 5. Editar el Laberinto

En el panel **Edición** se selecciona el tipo de celda que se desea colocar. Después de elegir un modo, hacer clic sobre una celda del laberinto.

| Modo | Función | Color visual |
|------|---------|--------------|
| Inicio | Coloca el punto inicial del robot | Naranja |
| Destino | Coloca la meta del recorrido | Rojo |
| Obstáculo | Agrega o quita paredes | Negro |
| Borrar | Limpia la celda seleccionada | Vacío |

Notas de uso:

- Solo puede existir un punto de inicio y un punto de destino.
- Si se coloca inicio o destino sobre un obstáculo, la celda se limpia automáticamente.
- No se puede colocar un obstáculo encima del inicio o del destino.
- El botón **Limpiar** reinicia el laberinto actual y elimina inicio, destino, obstáculos y resultados.

## 6. Ejecutar Algoritmos

Antes de ejecutar un algoritmo, el laberinto debe tener inicio y destino.

| Botón | Acción |
|-------|--------|
| BFS | Ejecuta Breadth-First Search. Suele encontrar rutas más cortas en laberintos sin pesos. |
| DFS | Ejecuta Depth-First Search. Explora en profundidad y puede encontrar una ruta válida distinta. |
| Comparar BFS vs DFS | Ejecuta ambos algoritmos sobre el mismo laberinto y muestra sus métricas lado a lado. |

## 7. Interpretar Resultados

Después de ejecutar un algoritmo, el panel **Resultados** muestra:

| Métrica | Descripción |
|---------|-------------|
| Ruta encontrada | Indica si existe un camino entre inicio y destino. |
| Longitud | Cantidad de celdas que forman la ruta encontrada. |
| Nodos explorados | Número de celdas visitadas durante la búsqueda. |
| Tiempo | Tiempo de ejecución del algoritmo en milisegundos. |

Colores de la cuadrícula:

| Color | Significado |
|-------|-------------|
| Naranja | Inicio |
| Rojo | Destino |
| Negro | Obstáculo |
| Gris | Celda explorada |
| Verde | Ruta encontrada por BFS |
| Morado | Ruta encontrada por DFS |
| Amarillo | Celda compartida por BFS y DFS |

## 8. Ejemplos de Uso

### 8.1 Ejecutar BFS en el Laberinto Simple

1. Seleccionar **Laberinto Simple (5x5)**.
2. Presionar **BFS**.
3. Revisar la ruta marcada en verde y las métricas del panel inferior.

![Ejecución de BFS en Laberinto Simple](screenshots/laberinto_simple_bfs.png)

### 8.2 Comparar BFS y DFS en el Laberinto Complejo

1. Seleccionar **Laberinto Complejo (10x10)**.
2. Presionar **Comparar BFS vs DFS**.
3. Comparar longitud, nodos explorados y tiempo de ejecución.

![Comparación de BFS y DFS](screenshots/comparacion_complejo.png)

### 8.3 Consultar Laberintos desde la API

El endpoint `GET /api/mazes` devuelve la lista de laberintos predefinidos.

![Respuesta del endpoint de laberintos](screenshots/api_mazes.png)

### 8.4 Ejecutar BFS desde la API

El endpoint `POST /api/solve/bfs` recibe una cuadrícula, una posición de inicio y una posición de destino. La respuesta incluye la ruta, las celdas exploradas y las métricas de ejecución.

![Respuesta del endpoint BFS](screenshots/api_bfs.png)

## 9. Solución de Problemas

| Problema | Posible causa | Solución |
|----------|---------------|----------|
| No carga la aplicación | El servidor no está iniciado | Ejecutar `python -m uvicorn backend.src.main:app --reload` |
| Error de conexión | El puerto `8000` está ocupado o el servidor se detuvo | Cerrar el proceso anterior o reiniciar el servidor |
| No se ejecuta el algoritmo | Falta inicio o destino | Colocar ambas celdas antes de ejecutar |
| No encuentra ruta | Los obstáculos bloquean el camino | Quitar obstáculos o cambiar inicio/destino |
| Los cambios no se ven | Caché del navegador | Recargar con `Ctrl+F5` |

