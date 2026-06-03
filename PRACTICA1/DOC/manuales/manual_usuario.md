# Manual de Usuario - Ruta Más Corta Entre Ciudades

## Tabla de Contenidos
1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación y Ejecución](#instalación-y-ejecución)
4. [Interfaz de Usuario](#interfaz-de-usuario)
5. [Funcionalidades](#funcionalidades)
6. [Ejemplos de Uso](#ejemplos-de-uso)
7. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

**Ruta Más Corta Entre Ciudades** es una aplicación web que permite calcular automáticamente la ruta más corta entre dos ciudades conectadas por carreteras. El sistema utiliza una base de conocimiento en Prolog para determinar las rutas óptimas y permite gestionar nuevas ciudades y conexiones de forma interactiva.

### Características Principales
- ✅ Búsqueda de ruta más corta entre ciudades
- ✅ Visualización de todas las rutas posibles
- ✅ Gestión de ciudades (crear nuevas ciudades)
- ✅ Gestión de conexiones (agregar nuevas carreteras)
- ✅ Interfaz moderna e intuitiva
- ✅ Estadísticas en tiempo real

---

## Requisitos del Sistema

### Software Necesario
- **Node.js** (v16 o superior)
- **Python** (v3.8 o superior)
- **SWI-Prolog** (última versión)
- **Git** (opcional, para clonar el repositorio)

### Hardware Mínimo
- Procesador: Intel Core i3 o equivalente
- RAM: 2 GB
- Espacio en disco: 500 MB

### Navegadores Compatibles
- Chrome/Chromium (v90+)
- Firefox (v88+)
- Safari (v14+)
- Edge (v90+)

---

## Instalación y Ejecución

### Paso 1: Configurar el Backend

```bash
# Navegar a la carpeta del backend
cd PRACTICA1/BACKEND

# Instalar dependencias de Python
pip install -r requirements.txt

# Ejecutar el servidor (Puerto 8000)
python -m uvicorn app.main:app --reload
```

**Resultado esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Paso 2: Configurar el Frontend

```bash
# En otra terminal, navegar a la carpeta del frontend
cd PRACTICA1/FRONTEND

# Instalar dependencias de Node.js
npm install

# Ejecutar el servidor de desarrollo (Puerto 5173)
npm run dev
```

**Resultado esperado:**
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### Paso 3: Acceder a la Aplicación

1. Abre tu navegador web
2. Ve a `http://localhost:5173`
3. ¡La aplicación está lista para usar!

> **Nota:** Asegúrate de tener los dos servidores (backend en 8000 y frontend en 5173) ejecutándose simultáneamente.

---

## Interfaz de Usuario

### Vista General

**>>> [IMAGEN AQUÍ] Captura de pantalla completa de la aplicación <<<**

*Muestra el header azul, pestañas de búsqueda/gestionar, formularios en el sidebar y panel de resultados*

### Secciones Principales

#### 1. **Header Azul (Encabezado)**
- Título: "Rutas entre ciudades"
- Descripción: "Consulta recorridos, compara distancias y administra ciudades"
- **KPIs en vivo:**
  - Número total de ciudades registradas
  - Número de rutas consultadas

#### 2. **Barra de Pestañas**
- **Buscar**: Acceso a búsquedas de rutas
- **Gestionar**: Acceso para agregar ciudades y conexiones

#### 3. **Panel Izquierdo (Sidebar)**
Contiene los formularios según la pestaña seleccionada:
- Inputs de selección/texto
- Botones de envío
- Descripciones de cada sección

#### 4. **Panel Derecho (Info Panel)**
Muestra:
- Ruta más corta encontrada (si existe)
- Listado de todas las rutas disponibles
- Mensaje vacío si no hay resultados
- Estadísticas en tarjetas

---

## Funcionalidades

### 📍 Pestaña "Buscar"

#### **Ruta Más Corta**

Encuentra automáticamente el camino óptimo entre dos ciudades.

**Pasos:**
1. Haz clic en la pestaña **"Buscar"**
2. En la sección "Ruta más corta", selecciona:
   - **Origen**: Ciudad de salida
   - **Destino**: Ciudad de llegada
3. Haz clic en **"Buscar"**

**Resultado:**
El panel derecho mostrará:
- Las ciudades por las que pasarás (en badges azules)
- La distancia total en kilómetros
- Un ícono de regla junto a la distancia

**>>> [IMAGEN AQUÍ] Pantalla con resultado de ruta más corta <<<**
*Muestra el recorrido: Guatemala → Escuintla → Puerto Barrios con la distancia*

---

#### **Todas las Rutas**

Visualiza todas las rutas posibles entre dos ciudades ordenadas por distancia.

**Pasos:**
1. En la sección "Todas las rutas", selecciona:
   - **Origen**: Ciudad de partida
   - **Destino**: Ciudad final
2. Haz clic en **"Ver rutas"**

**Resultado:**
El panel derecho mostrará:
- Cada ruta en una tarjeta
- Ciudades representadas como badges
- Distancia total de cada ruta en color verde
- Un contador: "Rutas disponibles (X)"

**>>> [IMAGEN AQUÍ] Pantalla con listado de rutas <<<**
*Muestra múltiples rutas con sus distancias y el badge de cada ciudad*

> **Nota:** Si no existe ruta entre las ciudades, verás un mensaje: "Información de rutas - Busca o carga rutas para verlas aquí"

---

### ⚙️ Pestaña "Gestionar"

#### **Agregar Ciudad**

Crea una nueva ciudad en la base de conocimiento.

**Pasos:**
1. Haz clic en la pestaña **"Gestionar"**
2. En la sección "Agregar ciudad", ingresa:
   - **Nombre**: Nombre de la nueva ciudad
3. Haz clic en **"Agregar"**

**Validaciones:**
- El nombre no puede estar vacío
- Se mostrará un mensaje de éxito o error

**Mensajes:**
- ✅ **Éxito (verde):** "Ciudad agregada correctamente"
- ❌ **Error (rojo):** Se mostrará el motivo del error

**>>> [IMAGEN AQUÍ] Pantalla con formulario de agregar ciudad y mensaje de éxito <<<**

---

#### **Agregar Conexión**

Establece una nueva carretera entre dos ciudades.

**Pasos:**
1. En la sección "Agregar conexión", completa:
   - **Origen**: Ciudad de inicio de la carretera
   - **Destino**: Ciudad destino de la carretera
   - **Distancia (km)**: Distancia en kilómetros (número entero)
2. Haz clic en **"Agregar"**

**Validaciones:**
- Las ciudades deben existir
- La distancia debe ser mayor a 0
- No se pueden conectar dos ciudades iguales

**Mensajes:**
- ✅ **Éxito:** "Conexión agregada correctamente"
- ❌ **Error:** Se mostrará el motivo del error

**>>> [IMAGEN AQUÍ] Pantalla con formulario de agregar conexión <<<**

---

## Ejemplos de Uso

### Ejemplo 1: Buscar Ruta Más Corta

**Objetivo:** Encontrar la ruta más corta de Guatemala a Huehuetenango

**Procedimiento:**
1. Abre la aplicación en `http://localhost:5173`
2. Asegúrate de estar en la pestaña **"Buscar"**
3. En "Ruta más corta":
   - Origen: Selecciona "Guatemala"
   - Destino: Selecciona "Huehuetenango"
4. Haz clic en **"Buscar"**

**Resultado Esperado:**
```
Recorrido: Guatemala → Antigua → Chichicastenango → Huehuetenango
Distancia: 180 km en total
```

**>>> [IMAGEN AQUÍ] Resultado del búsqueda de ruta más corta <<<**

---

### Ejemplo 2: Ver Todas las Rutas

**Objetivo:** Ver todas las formas de llegar de Escuintla a Puerto Barrios

**Procedimiento:**
1. En la pestaña **"Buscar"**
2. En "Todas las rutas":
   - Origen: "Escuintla"
   - Destino: "Puerto Barrios"
3. Haz clic en **"Ver rutas"**

**Resultado Esperado:**
Se mostrará un listado de todas las rutas disponibles con sus distancias

**>>> [IMAGEN AQUÍ] Resultado mostrando listado de rutas <<<**

---

### Ejemplo 3: Agregar Nueva Ciudad

**Objetivo:** Agregar la ciudad de "Totonicapán" al sistema

**Procedimiento:**
1. Ve a la pestaña **"Gestionar"**
2. En "Agregar ciudad":
   - Nombre: "Totonicapán"
3. Haz clic en **"Agregar"**

**Resultado Esperado:**
- Mensaje verde: "Ciudad agregada correctamente"
- El KPI de "Ciudades" en el header se incrementa en 1

**>>> [IMAGEN AQUÍ] Mensaje de éxito al agregar ciudad <<<**

---

### Ejemplo 4: Agregar Conexión Entre Ciudades

**Objetivo:** Conectar Totonicapán con Quetzaltenango con una carretera de 45 km

**Procedimiento:**
1. En la pestaña **"Gestionar"**
2. En "Agregar conexión":
   - Origen: "Totonicapán"
   - Destino: "Quetzaltenango"
   - Distancia: 45
3. Haz clic en **"Agregar"**

**Resultado Esperado:**
- Mensaje verde: "Conexión agregada correctamente"
- Ahora la búsqueda de rutas incluye este nuevo tramo

**>>> [IMAGEN AQUÍ] Mensaje de éxito al agregar conexión <<<**

---

## Solución de Problemas

### Problema 1: "No se puede conectar al servidor"

**Síntoma:** Error en la consola del navegador

**Causa Posible:**
- El backend no está ejecutándose en puerto 8000
- El servidor fue cerrado

**Solución:**
```bash
# Verifica que el backend esté corriendo
python -m uvicorn app.main:app --reload
```

---

### Problema 2: "No hay rutas disponibles" entre ciudades

**Síntoma:** Se muestra mensaje vacío al buscar

**Causa Posible:**
- Las ciudades seleccionadas no están conectadas
- Las ciudades no existen

**Solución:**
1. Verifica que ambas ciudades existan
2. Agrega una conexión entre ellas en la pestaña "Gestionar"
3. Intenta nuevamente

---

### Problema 3: Formularios no responden

**Síntoma:** Los botones no funcionan

**Causa Posible:**
- Campo obligatorio vacío
- Datos inválidos

**Solución:**
- Rellena todos los campos requeridos
- Para distancia, usa un número entero positivo
- Verifica que las ciudades existan antes de conectarlas

---

### Problema 4: El frontend no carga

**Síntoma:** Error 404 o página en blanco

**Causa Posible:**
- El servidor de desarrollo no está ejecutándose
- Puerto 5173 no está disponible

**Solución:**
```bash
# Ejecuta el servidor de desarrollo
cd PRACTICA1/FRONTEND
npm run dev
```

---

## Preguntas Frecuentes (FAQ)

**P: ¿Cuántas ciudades puedo agregar?**
R: No hay límite. El sistema puede gestionar cientos de ciudades sin problemas.

**P: ¿Se guarda la información cuando cierro la aplicación?**
R: No. Los datos se almacenan solo en la sesión actual. Para datos persistentes, necesitarías una base de datos.

**P: ¿Puedo agregar rutas en ambas direcciones?**
R: Sí, pero debes agregarlas como dos conexiones separadas (A→B y B→A).

**P: ¿Cuál es la distancia máxima que puedo registrar?**
R: No hay límite. Puedes usar cualquier número positivo.

**P: ¿Qué pasa si agrego una ciudad duplicada?**
R: El sistema la rechazará y mostrará un mensaje de error.

---

## Soporte y Contacto

Si encuentras problemas o tienes sugerencias, contacta al equipo de desarrollo.

**Última actualización:** 3 de junio de 2026

