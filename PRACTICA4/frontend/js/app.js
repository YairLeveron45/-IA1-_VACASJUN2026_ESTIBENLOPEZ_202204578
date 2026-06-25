/**
 * app.js — RoboMaze Frontend
 * Gestiona la cuadricula, las interacciones del usuario, la comunicacion
 * con la API FastAPI y la animacion de los resultados en pantalla.
 */

// URL base de la API de FastAPI (mismo origen)
const API_URL = '/api';

// Estado global de la aplicacion
let grid = [];       // Matriz 2D (0 = libre, 1 = obstaculo)
let start = null;    // Coordenada [fila, columna] del inicio
let end = null;      // Coordenada [fila, columna] del destino
let mode = 'start';  // Modo de edicion actual
let currentMazeId = null;            // ID del laberinto cargado
let animTimeouts = [];               // IDs de timeouts de animacion activos

// Cancela todas las animaciones pendientes (evita estados inconsistentes)
function clearAnimTimeouts() {
    animTimeouts.forEach(id => clearTimeout(id));
    animTimeouts = [];
}

// Carga la lista de laberintos predefinidos desde la API y llena el select
async function loadPredefinedMazes() {
    try {
        const res = await fetch(`${API_URL}/mazes`);
        const mazes = await res.json();
        const sel = document.getElementById('maze-select');
        sel.innerHTML = '<option value="">— Seleccionar laberinto —</option>';
        mazes.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.id;
            opt.textContent = `${m.name} (${m.rows}x${m.cols})`;
            sel.appendChild(opt);
        });
    } catch (e) {
        console.error('Error loading mazes:', e);
    }
}

// Carga un laberinto predefinido por su ID y actualiza la cuadricula
function loadMaze(mazeId) {
    fetch(`${API_URL}/mazes/${mazeId}`)
        .then(r => r.json())
        .then(m => {
            currentMazeId = mazeId;
            grid = m.grid.map(row => [...row]);
            start = [m.start[0], m.start[1]];
            end = [m.end[0], m.end[1]];
            renderGrid();
            clearResults();
        });
}

// Inicializa una cuadricula vacia con el tamano indicado
function initGrid(rows, cols) {
    grid = Array.from({ length: rows }, () => Array(cols).fill(0));
    start = null;
    end = null;
    renderGrid();
    clearResults();
}

// Renderiza la cuadricula del laberinto en el DOM
function renderGrid() {
    const container = document.getElementById('maze-grid');
    if (!grid.length) return;
    const rows = grid.length;
    const cols = grid[0].length;
    container.style.gridTemplateColumns = `repeat(${cols}, 36px)`;
    container.innerHTML = '';
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = r;
            cell.dataset.col = c;
            updateCellDisplay(cell, r, c);
            cell.addEventListener('click', () => onCellClick(r, c));
            container.appendChild(cell);
        }
    }
    document.getElementById('grid-size').textContent = `${rows} × ${cols}`;
}

// Actualiza la clase CSS de una celda segun su estado actual
function updateCellDisplay(cell, r, c) {
    cell.className = 'cell';
    if (start && r === start[0] && c === start[1]) {
        cell.classList.add('start');
    } else if (end && r === end[0] && c === end[1]) {
        cell.classList.add('end');
    } else if (grid[r][c] === 1) {
        cell.classList.add('obstacle');
    } else {
        cell.classList.add('empty');
    }
}

// Maneja el clic sobre una celda segun el modo de edicion activo
function onCellClick(r, c) {
    clearAnimTimeouts();
    if (mode === 'start') {
        if (start) {
            const [or, oc] = start;
            const prev = document.querySelector(`.cell[data-row="${or}"][data-col="${oc}"]`);
            if (prev) updateCellDisplay(prev, or, oc);
        }
        start = [r, c];
        if (end && r === end[0] && c === end[1]) end = null;
        if (grid[r][c] === 1) grid[r][c] = 0;
    } else if (mode === 'end') {
        if (end) {
            const [or, oc] = end;
            const prev = document.querySelector(`.cell[data-row="${or}"][data-col="${oc}"]`);
            if (prev) updateCellDisplay(prev, or, oc);
        }
        end = [r, c];
        if (start && r === start[0] && c === start[1]) start = null;
        if (grid[r][c] === 1) grid[r][c] = 0;
    } else if (mode === 'obstacle') {
        if ((start && r === start[0] && c === start[1]) || (end && r === end[0] && c === end[1])) return;
        grid[r][c] = grid[r][c] === 1 ? 0 : 1;
    } else if (mode === 'erase') {
        if (start && r === start[0] && c === start[1]) { start = null; }
        else if (end && r === end[0] && c === end[1]) { end = null; }
        else { grid[r][c] = 0; }
    }
    const cell = document.querySelector(`.cell[data-row="${r}"][data-col="${c}"]`);
    if (cell) updateCellDisplay(cell, r, c);
    clearResults();
}

// Valida que el laberinto tenga inicio y destino antes de ejecutar
function validateMaze() {
    if (!start) { alert('Coloca un punto de inicio'); return false; }
    if (!end) { alert('Coloca un punto de destino'); return false; }
    return true;
}

// Ejecuta el algoritmo BFS en el backend
async function solveBFS() {
    if (!validateMaze()) return;
    clearAnimTimeouts();
    clearResults();
    const result = await solve('bfs');
    if (result) displayResult('bfs', result);
}

// Ejecuta el algoritmo DFS en el backend
async function solveDFS() {
    if (!validateMaze()) return;
    clearAnimTimeouts();
    clearResults();
    const result = await solve('dfs');
    if (result) displayResult('dfs', result);
}

// Compara BFS vs DFS ejecutando ambos en el backend simultaneamente
async function compare() {
    if (!validateMaze()) return;
    clearAnimTimeouts();
    clearResults();
    try {
        const res = await fetch(`${API_URL}/compare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grid, start, end })
        });
        const data = await res.json();
        displayResult('bfs', data.bfs);
        displayResult('dfs', data.dfs);
    } catch (e) {
        console.error('Compare error:', e);
    }
}

// Envia una peticion POST a la API para ejecutar un algoritmo
async function solve(algorithm) {
    try {
        const res = await fetch(`${API_URL}/solve/${algorithm}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grid, start, end })
        });
        return await res.json();
    } catch (e) {
        console.error(`${algorithm} error:`, e);
        return null;
    }
}

// Muestra los resultados de un algoritmo en su panel y anima la exploracion
function displayResult(algorithm, data) {
    const prefix = algorithm === 'bfs' ? 'bfs' : 'dfs';
    document.getElementById(`${prefix}-found`).textContent = data.found ? 'Si' : 'No';
    document.getElementById(`${prefix}-path-length`).textContent = data.path_length;
    document.getElementById(`${prefix}-nodes`).textContent = data.nodes_explored;
    document.getElementById(`${prefix}-time`).textContent = `${data.execution_time_ms} ms`;

    const panel = document.getElementById(`${prefix}-result`);
    panel.classList.add('visible');

    animateResult(algorithm, data.explored, data.path);
}

// Anima la exploracion y la ruta encontrada con timeouts progresivos
function animateResult(algorithm, explored, path) {
    const pathClass = algorithm === 'bfs' ? 'path-bfs' : 'path-dfs';
    const pathSet = new Set(path.map(p => `${p[0]},${p[1]}`));

    // Anima las celdas exploradas (gris) que NO forman parte de la ruta final
    explored.forEach(([r, c], i) => {
        const key = `${r},${c}`;
        if (!pathSet.has(key)) {
            const id = setTimeout(() => {
                const cell = document.querySelector(`.cell[data-row="${r}"][data-col="${c}"]`);
                if (cell && !cell.classList.contains('start') && !cell.classList.contains('end')) {
                    cell.className = 'cell explored';
                }
            }, i * 5);
            animTimeouts.push(id);
        }
    });

    // Anima la ruta final encima de la exploracion
    path.forEach(([r, c], i) => {
        const id = setTimeout(() => {
            const cell = document.querySelector(`.cell[data-row="${r}"][data-col="${c}"]`);
            if (cell) {
                if (!cell.classList.contains('start') && !cell.classList.contains('end')) {
                    cell.className = `cell ${pathClass}`;
                }
            }
        }, explored.length * 5 + i * 10);
        animTimeouts.push(id);
    });
}

// Limpia resultados, animaciones y restaura la cuadricula a su estado base
function clearResults() {
    clearAnimTimeouts();
    document.getElementById('bfs-result').classList.remove('visible');
    document.getElementById('dfs-result').classList.remove('visible');

    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        const r = parseInt(cell.dataset.row);
        const c = parseInt(cell.dataset.col);
        updateCellDisplay(cell, r, c);
    });
}

// Reinicia el laberinto: elimina todo el contenido y lo vuelve a pintar
function clearMaze() {
    grid = grid.map(row => row.map(() => 0));
    start = null;
    end = null;
    renderGrid();
    clearResults();
}

// Cambia el modo de edicion activo
function setMode(newMode) {
    mode = newMode;
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`mode-${newMode}`).classList.add('active');
    const labels = {
        start: '<strong>Colocar inicio</strong> (naranja)',
        end: '<strong>Colocar destino</strong> (rojo)',
        obstacle: '<strong>Colocar obstaculos</strong>',
        erase: '<strong>Borrar celdas</strong>'
    };
    document.getElementById('current-mode').innerHTML = labels[newMode] || '';
}

// Inicializacion: carga mazes, crea cuadricula por defecto y enlaza eventos
document.addEventListener('DOMContentLoaded', () => {
    loadPredefinedMazes();
    initGrid(8, 8);
    setMode('start');

    document.getElementById('maze-select').addEventListener('change', (e) => {
        if (e.target.value) loadMaze(parseInt(e.target.value));
    });

    document.getElementById('btn-bfs').addEventListener('click', solveBFS);
    document.getElementById('btn-dfs').addEventListener('click', solveDFS);
    document.getElementById('btn-compare').addEventListener('click', compare);
    document.getElementById('btn-clear').addEventListener('click', clearMaze);

    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', () => setMode(btn.dataset.mode));
    });
});
