# Manual Técnico - Ruta Más Corta Entre Ciudades

## Tabla de Contenidos
1. [Introducción Arquitectónica](#introducción-arquitectónica)
2. [Arquitectura General](#arquitectura-general)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Tecnologías Utilizadas](#tecnologías-utilizadas)
5. [Componentes Clave](#componentes-clave)
6. [Flujo de Datos](#flujo-de-datos)
7. [Base de Conocimiento Prolog](#base-de-conocimiento-prolog)
8. [API REST](#api-rest)
9. [Frontend React](#frontend-react)
10. [Mejoras Futuras](#mejoras-futuras)

---

## Introducción Arquitectónica

Este proyecto implementa un **sistema híbrido de resolución de problemas** que combina:

- **Backend Python (FastAPI)**: Actúa como servidor REST y orquestador
- **Motor Lógico (Prolog/SWI-Prolog)**: Maneja la lógica de búsqueda de rutas
- **Frontend React (Vite)**: Interfaz interactiva para el usuario

### Patrón Arquitectónico: **Arquitectura de Capas Lógicas**

```
┌─────────────────────────────────────┐
│         Frontend (React/Vite)       │
│  - Interfaz de usuario              │
│  - Manejo de estado                 │
│  - Comunicación HTTP                │
└────────────────┬────────────────────┘
                 │ HTTP REST
                 ▼
┌─────────────────────────────────────┐
│      Backend (Python/FastAPI)       │
│  - Rutas API                        │
│  - Lógica de negocio                │
│  - Comunicación con Prolog          │
└────────────────┬────────────────────┘
                 │ Consultas Prolog
                 ▼
┌─────────────────────────────────────┐
│      Motor Lógico (SWI-Prolog)      │
│  - Base de conocimiento             │
│  - Algoritmos de búsqueda           │
│  - Inferencia lógica                │
└─────────────────────────────────────┘
```

---

## Arquitectura General

### Vista de Componentes

**>>> [DIAGRAMA AQUÍ] Diagrama de arquitectura con las tres capas <<<**

### Principios de Diseño

1. **Separación de Responsabilidades**: Cada capa tiene un propósito específico
2. **Independencia Tecnológica**: Cambios en una capa no afectan otras
3. **Escalabilidad**: Fácil agregar nuevas funcionalidades
4. **Mantenibilidad**: Código organizado y modular

---

## Estructura del Proyecto

```
PRACTICA1/
├── BACKEND/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # Punto de entrada de FastAPI
│   │   ├── api/
│   │   │   └── routes.py           # Definición de endpoints
│   │   ├── core/                   # Configuración
│   │   ├── schemas/
│   │   │   └── route.py            # Modelos de datos
│   │   └── services/
│   │       └── prolog_service.py   # Lógica de Prolog
│   ├── requirements.txt            # Dependencias Python
│   └── tests/                      # Pruebas unitarias
│
├── FRONTEND/
│   ├── src/
│   │   ├── App.jsx                 # Componente principal
│   │   ├── api.js                  # Cliente HTTP
│   │   ├── main.jsx                # Punto de entrada
│   │   ├── styles.css              # Estilos globales
│   │   └── components/             # Componentes reutilizables
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── PROLOG/
│   └── rutas.pl                    # Base de conocimiento
│
└── DOC/
    ├── practica1.md
    └── manuales/
        ├── manual_usuario.md
        └── manual_tecnico.md
```

---

## Tecnologías Utilizadas

### Backend
| Tecnología | Versión | Propósito |
|-----------|---------|----------|
| Python | 3.8+ | Lenguaje principal |
| FastAPI | 0.95+ | Framework web moderno |
| PySwip | 0.2+ | Comunicación Python-Prolog |
| Uvicorn | 0.20+ | Servidor ASGI |
| Pydantic | 1.10+ | Validación de datos |

### Frontend
| Tecnología | Versión | Propósito |
|-----------|---------|----------|
| React | 18+ | Librería de UI |
| Vite | 4+ | Bundler y servidor dev |
| JavaScript | ES2020+ | Lógica del cliente |
| CSS3 | - | Estilos y diseño |

### Motor Lógico
| Tecnología | Versión | Propósito |
|-----------|---------|----------|
| SWI-Prolog | 8.0+ | Motor de inferencia lógica |

---

## Componentes Clave

### 1. Backend (Python/FastAPI)

#### Estructura de Carpetas

```
backend/app/
├── main.py                    # Aplicación FastAPI
├── api/
│   └── routes.py             # Definición de endpoints REST
├── core/
│   └── config.py             # Variables de configuración
├── schemas/
│   └── route.py              # Modelos Pydantic para validación
└── services/
    └── prolog_service.py     # Servicio de integración Prolog
```

#### main.py - Punto de Entrada

```python
app = FastAPI(
    title="Ruta Mas Corta Entre Ciudades",
    description="Backend en Python que consulta Prolog"
)

# CORS habilitado para desarrollo
app.add_middleware(CORSMiddleware, allow_origins=[...])
app.include_router(router)
```

#### routes.py - Definición de Endpoints

```python
@router.get("/cities")                    # Obtiene todas las ciudades
@router.post("/best-route")               # Busca ruta más corta
@router.post("/routes")                   # Obtiene todas las rutas
@router.post("/cities")                   # Agrega nueva ciudad
@router.post("/connections")              # Agrega nueva conexión
```

#### prolog_service.py - Servicio de Prolog

**Responsabilidades:**
- Inicializar consulta Prolog
- Ejecutar consultas a la base de conocimiento
- Procesar resultados de Prolog
- Convertir datos para el frontend

**Métodos principales:**
```python
get_cities()              # Retorna lista de ciudades
get_best_route()          # Encuentra ruta óptima
get_all_routes()          # Encuentra todas las rutas
add_city()                # Agrega ciudad a Prolog
add_connection()          # Agrega conexión a Prolog
```

### 2. Frontend (React/Vite)

#### Estructura

```
frontend/src/
├── App.jsx               # Componente raíz
├── api.js               # Cliente HTTP (axios)
├── styles.css           # Estilos globales
└── main.jsx             # Punto de entrada React
```

#### App.jsx - Componente Principal

**Responsabilidades:**
- Gestionar estado de la aplicación (React Hooks)
- Renderizar interfaz
- Manejar eventos de usuario
- Comunicarse con el backend

**Estado Clave:**
```javascript
cities                    // Lista de ciudades
bestRoute                 // Ruta más corta encontrada
allRoutes                 // Todas las rutas encontradas
activeTab                 // Tab activa (search/manage)
statusMessage             // Mensajes de estado
```

**SVG Icons:**
```javascript
IconRoute, IconCity, IconNetwork, IconDistance
IconSettings, IconMap, IconSearch, IconPlus, etc.
```

#### api.js - Cliente HTTP

```javascript
// Endpoints disponibles
fetchCities()             // GET /cities
fetchBestRoute(payload)   // POST /best-route
fetchAllRoutes(payload)   // POST /routes
createCity(payload)       // POST /cities
createConnection(payload) // POST /connections
```

#### styles.css - Diseño Responsivo

**Diseño Facebook:**
- Header azul (#1877f2)
- Fondo gris claro (#f0f2f5)
- Cards blancas con sombras sutiles
- Tipografía system-font

**Breakpoints:**
- Desktop: 1024px+
- Tablet: 860px - 1024px
- Mobile: < 860px

### 3. Motor Lógico (Prolog)

#### rutas.pl - Base de Conocimiento

```prolog
% ===== HECHOS: Ciudades =====
ciudad(guatemala).
ciudad(escuintla).
ciudad(huehuetenango).
... (más ciudades)

% ===== HECHOS: Conexiones =====
conexion(guatemala, escuintla, 65).
conexion(escuintla, puerto_barrios, 120).
... (más conexiones)

% ===== REGLAS: Búsqueda =====
ruta(Origen, Destino, Ruta) :- ...
ruta_mas_corta(Origen, Destino, Ruta, Distancia) :- ...
distancia_total(Ruta, Distancia) :- ...
```

**Características:**
- Sin ciclos (evita repetir ciudades)
- Búsqueda exhaustiva de rutas
- Cálculo automático de distancias
- Base conocimiento expandible

---

## Flujo de Datos

### Flujo 1: Búsqueda de Ruta Más Corta

```
Usuario selecciona ciudades
         ↓
Frontend valida datos
         ↓
HTTP POST /best-route {origin, destination}
         ↓
Backend recibe solicitud
         ↓
PrologService.get_best_route()
         ↓
Prolog ejecuta consulta: ruta_mas_corta(...)
         ↓
Prolog retorna resultado
         ↓
Backend procesa y valida
         ↓
HTTP 200 + {route: [...], distance: N}
         ↓
Frontend recibe respuesta
         ↓
Renderiza ruta en panel derecho
```

**>>> [DIAGRAMA AQUÍ] Flujo de datos con secuencia de llamadas <<<**

---

### Flujo 2: Agregar Nueva Conexión

```
Usuario completa formulario (origen, destino, distancia)
         ↓
Frontend valida: ciudades existen, distancia > 0
         ↓
HTTP POST /connections {origin, destination, distance}
         ↓
Backend valida conexión
         ↓
PrologService.add_connection()
         ↓
Genera cláusula Prolog: conexion(A, B, D)
         ↓
Agrega dinámicamente a Prolog
         ↓
HTTP 200 + {message: "Conexión agregada"}
         ↓
Frontend muestra mensaje verde
         ↓
KPI de rutas se actualiza
```

---

## Base de Conocimiento Prolog

### Estructura de rutas.pl

#### 1. Hechos Base

```prolog
% Definición de ciudades
ciudad(guatemala).
ciudad(escuintla).
ciudad(puerto_barrios).
% ... más ciudades

% Definición de conexiones directas
% Formato: conexion(Origen, Destino, Distancia)
conexion(guatemala, escuintla, 65).
conexion(escuintla, puerto_barrios, 120).
conexion(guatemala, antigua, 45).
% ... más conexiones
```

#### 2. Reglas de Búsqueda

```prolog
% Encuentra una ruta entre dos ciudades (sin ciclos)
ruta(Origen, Destino, [Origen, Destino]) :-
    conexion(Origen, Destino, _).
    
ruta(Origen, Destino, [Origen|Ruta]) :-
    conexion(Origen, Intermedia, _),
    ruta(Intermedia, Destino, Ruta),
    \+ member(Origen, Ruta).

% Calcula distancia total de una ruta
distancia_total([], 0).
distancia_total([A, B|Resto], Total) :-
    conexion(A, B, D),
    distancia_total([B|Resto], SubTotal),
    Total is D + SubTotal.

% Encuentra la ruta más corta
ruta_mas_corta(Origen, Destino, MejorRuta, MejorDistancia) :-
    findall(Dist-Ruta, 
            (ruta(Origen, Destino, Ruta), distancia_total(Ruta, Dist)), 
            Soluciones),
    min_member(MejorDistancia-MejorRuta, Soluciones).
```

### Características Implementadas

✅ **Búsqueda de rutas**: Encuentra todos los caminos posibles
✅ **Evita ciclos**: Una ciudad no se repite en una ruta
✅ **Cálculo de distancias**: Suma automática de distancias
✅ **Ruta óptima**: Selecciona la de menor distancia
✅ **Escalable**: Fácil agregar ciudades y conexiones

---

## API REST

### Especificación de Endpoints

#### GET /cities
**Propósito:** Obtener lista de todas las ciudades

```http
GET http://127.0.0.1:8000/cities
```

**Response (200 OK):**
```json
["guatemala", "escuintla", "puerto_barrios", "antigua", ...]
```

---

#### POST /best-route
**Propósito:** Encontrar la ruta más corta

```http
POST http://127.0.0.1:8000/best-route
Content-Type: application/json

{
  "origin": "guatemala",
  "destination": "puerto_barrios"
}
```

**Response (200 OK):**
```json
{
  "route": ["guatemala", "escuintla", "puerto_barrios"],
  "distance": 185
}
```

**Response (404 Not Found):**
```json
{
  "detail": "No se encontró ruta entre las ciudades"
}
```

---

#### POST /routes
**Propósito:** Obtener todas las rutas posibles

```http
POST http://127.0.0.1:8000/routes
Content-Type: application/json

{
  "origin": "guatemala",
  "destination": "puerto_barrios"
}
```

**Response (200 OK):**
```json
[
  {
    "route": ["guatemala", "escuintla", "puerto_barrios"],
    "distance": 185
  },
  {
    "route": ["guatemala", "antigua", "escuintla", "puerto_barrios"],
    "distance": 230
  }
]
```

---

#### POST /cities
**Propósito:** Agregar una nueva ciudad

```http
POST http://127.0.0.1:8000/cities
Content-Type: application/json

{
  "name": "totonicapán"
}
```

**Response (200 OK):**
```json
{
  "message": "Ciudad agregada correctamente"
}
```

---

#### POST /connections
**Propósito:** Agregar una nueva conexión entre ciudades

```http
POST http://127.0.0.1:8000/connections
Content-Type: application/json

{
  "origin": "totonicapán",
  "destination": "quetzaltenango",
  "distance": 45
}
```

**Response (200 OK):**
```json
{
  "message": "Conexión agregada correctamente"
}
```

---

## Frontend React

### Estado Global (Hooks)

```javascript
// Estados principales
const [cities, setCities] = useState([]);
const [bestRoute, setBestRoute] = useState(null);
const [allRoutes, setAllRoutes] = useState([]);
const [activeTab, setActiveTab] = useState("search");
const [statusMessage, setStatusMessage] = useState("");
const [errorMessage, setErrorMessage] = useState("");
```

### Componentes

#### App.jsx
- Componente principal que orquesta todo
- Maneja estado global
- Renderiza UI

#### FieldInput
Componente reutilizable para inputs:
```javascript
<FieldInput 
  name="origin" 
  value={form.origin}
  onChange={handleChange}
  cities={citiesList}  // Para mostrar select
  type="text"
/>
```

#### SVG Icons
Componentes de iconos SVG reutilizables:
- IconRoute (rutas)
- IconCity (ciudades)
- IconNetwork (red de ciudades)
- IconDistance (distancia)
- IconSettings (configuración)
- IconMap (mapa)

### Diseño (CSS)

**Paleta de Colores:**
- Primario: #1877f2 (azul Facebook)
- Secundario: #31a24c (verde)
- Fondo: #f0f2f5 (gris claro)
- Texto: #050505 (negro oscuro)

**Componentes Clave:**
- `.hero`: Header azul con KPIs
- `.card`: Tarjetas de formulario
- `.panel-section`: Secciones de resultados
- `.result`: Resultado de ruta
- `.route-item`: Item de ruta en lista

---

## Mejoras Futuras

### Corto Plazo (1-2 semanas)
- [ ] Persistencia de datos (SQLite/PostgreSQL)
- [ ] Autenticación de usuarios
- [ ] Historial de búsquedas
- [ ] Exportar rutas a PDF
- [ ] Dark mode

### Mediano Plazo (1-2 meses)
- [ ] Visualización en mapa (Google Maps API)
- [ ] Múltiples criterios de búsqueda (tiempo, peaje, etc.)
- [ ] Recomendaciones inteligentes
- [ ] API de terceros (Mapbox)
- [ ] Caché de resultados

### Largo Plazo (3+ meses)
- [ ] Aplicación móvil (React Native)
- [ ] Machine Learning para predicción de rutas
- [ ] Integración con sistemas de tráfico real
- [ ] Optimización de flotas de transporte
- [ ] Microservicios distribuidos

---

## Optimizaciones Realizadas

### Performance
✅ Lazy loading en frontend
✅ Compresión de assets con Vite
✅ Caché de ciudades en el cliente
✅ Validación en cliente antes de enviar

### Seguridad
✅ CORS configurado para desarrollo
✅ Validación de entrada con Pydantic
✅ Manejo de excepciones en backend
✅ Sanitización de datos de usuario

### Mantenibilidad
✅ Código modular y bien documentado
✅ Separación clara de responsabilidades
✅ Nombres descriptivos en variables
✅ Comments explicativos en secciones críticas

---

## Configuración de Desarrollo

### Variables de Entorno Recomendadas

```bash
# Backend
PROLOG_PATH=/path/to/swipl
DEBUG=True
LOG_LEVEL=INFO

# Frontend
VITE_API_URL=http://127.0.0.1:8000
```

### Debugging

**Backend:**
```bash
# Ver logs detallados
python -m uvicorn app.main:app --reload --log-level debug

# Usar debugger Python
import pdb; pdb.set_trace()
```

**Frontend:**
```bash
# Abrir DevTools (F12)
# Console para ver logs
console.log("Debug:", variable)

# React DevTools extension
```

---

## Conclusión

La arquitectura implementada proporciona:
- ✅ Separación clara entre capas
- ✅ Escalabilidad para futuras mejoras
- ✅ Mantenibilidad a largo plazo
- ✅ Flexibilidad tecnológica

El sistema combina eficientemente Prolog (lógica) con Python/React (presentación) para crear una solución robusta y modular.

---

**Última actualización:** 3 de junio de 2026
**Autor:** Estiben López
**Versionado:** 1.0.0

