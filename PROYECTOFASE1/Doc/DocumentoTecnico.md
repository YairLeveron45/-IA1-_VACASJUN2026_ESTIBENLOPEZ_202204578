# Documento Tecnico

# Doctor Byte - Sistema Experto para Diagnostico de Fallas

## 1. Introduccion

Doctor Byte es un sistema experto desarrollado para diagnosticar fallas comunes en computadoras. La solucion utiliza una base de conocimiento implementada en Prolog, un backend en Python con FastAPI, una interfaz web construida con React y una integracion con Telegram para enviar notificaciones del diagnostico generado.

El sistema permite que un usuario seleccione sintomas desde la interfaz web, reciba una falla probable y obtenga una recomendacion tecnica. Tambien incluye una vista administrativa protegida por login para gestionar sintomas, fallas, recomendaciones y reglas directamente sobre los archivos Prolog.

---

## 2. Objetivos

### Objetivo general

Desarrollar un sistema experto funcional que diagnostique fallas de computadoras mediante reglas de inferencia en Prolog, integrado con una API REST, una interfaz web y notificaciones por Telegram.

### Objetivos especificos

- Implementar una base de conocimiento en SWI-Prolog.
- Crear hechos para sintomas, fallas y recomendaciones.
- Implementar reglas de inferencia para asociar sintomas con fallas.
- Usar listas, unificacion, recursividad y corte en Prolog.
- Conectar Python con Prolog mediante PySwip.
- Desarrollar endpoints REST con FastAPI.
- Crear una interfaz web amigable con React y Vite.
- Implementar historial de diagnosticos en formato JSON.
- Agregar una vista de administracion con CRUD de conocimiento.
- Integrar envio de diagnosticos mediante Telegram Bot API.
- Facilitar la ejecucion del proyecto mediante Docker Compose.

---

## 3. Tecnologias utilizadas

| Tecnologia | Uso dentro del proyecto |
| --- | --- |
| SWI-Prolog | Motor experto y base de conocimiento |
| Prolog | Hechos, reglas, listas, inferencia y corte |
| Python | Lenguaje del backend |
| FastAPI | Construccion de la API REST |
| PySwip | Conexion entre Python y SWI-Prolog |
| React | Interfaz web |
| Vite | Servidor y empaquetador del frontend |
| CSS | Estilos visuales de la aplicacion |
| JSON | Almacenamiento del historial de diagnosticos |
| Telegram Bot API | Envio de notificaciones |
| Docker Compose | Ejecucion del frontend y backend en contenedores |

---

## 4. Arquitectura general

El proyecto esta dividido en cuatro capas principales:

- Frontend: interfaz web para diagnostico y administracion.
- Backend: API REST y servicios de aplicacion.
- Motor experto Prolog: base de conocimiento e inferencia.
- Servicios externos: Telegram Bot API.

### Diagrama de Arquitectura

![Manual de usuario Guía breve que explique cómo ejecutar y utilizar el sistema.

](<img/Diagrama de arquictura.png>)
### Docker Compose

El proyecto se puede ejecutar con Docker Compose. La configuracion contiene:

- Contenedor frontend: ejecuta React con Vite.
- Contenedor backend: ejecuta Python, FastAPI, PySwip y SWI-Prolog.
- Volumen `PROLOG`: permite leer y escribir los archivos `.pl`.
- Volumen `BACKEND/app/data`: conserva el historial JSON.

SWI-Prolog no esta en un contenedor separado. Esta instalado dentro del contenedor del backend, ya que PySwip necesita comunicarse con SWI-Prolog desde Python.

---

## 5. Estructura del proyecto

```txt
PROYECTOFASE1/
├── BACKEND/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py
│   │   │   ├── admin_routes.py
│   │   │   └── telegram_routes.py
│   │   ├── schemas/
│   │   │   ├── diagnosis.py
│   │   │   └── knowledge.py
│   │   ├── services/
│   │   │   ├── admin_auth_service.py
│   │   │   ├── diagnosis_service.py
│   │   │   ├── history_service.py
│   │   │   ├── knowledge_service.py
│   │   │   ├── prolog_service.py
│   │   │   └── telegram_service.py
│   │   ├── data/
│   │   │   └── diagnosis_history.json
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── FRONTEND/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AdminLogin.jsx
│   │   │   ├── AdminPanel.jsx
│   │   │   ├── DiagnosisResult.jsx
│   │   │   ├── HistoryPanel.jsx
│   │   │   ├── SymptomSelector.jsx
│   │   │   └── TelegramForm.jsx
│   │   ├── styles/
│   │   │   └── styles.css
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   └── package.json
│
├── PROLOG/
│   ├── sintomas.pl
│   ├── fallas.pl
│   ├── recomendaciones.pl
│   └── doctor_byte.pl
│
├── Doc/
│   ├── DocumentoTecnico.md
│   └── manual_usuario.md
│
├── docker-compose.yml
└── README.md
```

---

## 6. Modulos principales

### 6.1 Frontend

El frontend esta desarrollado con React y Vite. Contiene dos vistas principales:

### Vista Diagnostico

Permite al usuario:

- Ver sintomas cargados desde el backend.
- Seleccionar sintomas.
- Ver sugerencias de sintomas relacionados marcadas como `match`.
- Generar un diagnostico.
- Ver la falla detectada.
- Ver la recomendacion.
- Activar el envio del diagnostico por Telegram.
- Consultar el historial de diagnosticos.

### Vista Admin

Permite al administrador:

- Iniciar sesion con contraseña.
- Ver resumen de sintomas, fallas, recomendaciones y reglas.
- Gestionar sintomas con CRUD.
- Gestionar fallas con CRUD.
- Gestionar recomendaciones con CRUD.
- Gestionar reglas con CRUD.

La vista Admin usa un menu interno:

```txt
Resumen | Sintomas | Fallas | Recomendaciones | Reglas
```

En reglas, las fallas y sintomas se seleccionan desde listas existentes para evitar escribir valores invalidos.

---

## 7. Backend

El backend esta construido con FastAPI y organiza la logica en rutas, esquemas y servicios.

### Rutas principales

| Endpoint | Metodo | Descripcion |
| --- | --- | --- |
| `/api/health` | GET | Verifica que la API este activa |
| `/api/symptoms` | GET | Lista sintomas desde Prolog |
| `/api/symptom-suggestions` | POST | Sugiere sintomas relacionados segun reglas |
| `/api/diagnose` | POST | Genera un diagnostico consultando Prolog |
| `/api/history` | GET | Devuelve historial de diagnosticos |
| `/api/admin/login` | POST | Autentica al administrador |
| `/api/admin/knowledge` | GET | Devuelve sintomas, fallas, recomendaciones y reglas |
| `/api/admin/symptoms` | POST | Crea sintomas |
| `/api/admin/symptoms/{name}` | PUT/DELETE | Edita o elimina sintomas |
| `/api/admin/failures` | POST | Crea fallas |
| `/api/admin/failures/{name}` | PUT/DELETE | Edita o elimina fallas |
| `/api/admin/recommendations` | POST | Crea recomendaciones |
| `/api/admin/recommendations/{failure}` | PUT/DELETE | Edita o elimina recomendaciones |
| `/api/admin/rules` | POST | Crea reglas |
| `/api/admin/rules/{failure}` | PUT/DELETE | Edita o elimina reglas |
| `/api/telegram/send` | POST | Envia mensaje manual por Telegram |

### Servicios principales

| Servicio | Funcion |
| --- | --- |
| `prolog_service.py` | Consulta el motor Prolog mediante PySwip |
| `knowledge_service.py` | Lee y escribe archivos Prolog para el Admin |
| `diagnosis_service.py` | Coordina diagnostico, historial y Telegram |
| `history_service.py` | Guarda y lee `diagnosis_history.json` |
| `telegram_service.py` | Envia mensajes mediante Telegram Bot API |
| `admin_auth_service.py` | Valida login y token de administrador |

---

## 8. Base de conocimiento Prolog

La base de conocimiento se encuentra en la carpeta `PROLOG/`.

### Archivos

| Archivo | Contenido |
| --- | --- |
| `sintomas.pl` | Hechos `sintoma(...)` |
| `fallas.pl` | Hechos `falla(...)` |
| `recomendaciones.pl` | Hechos `recomendacion(Falla, Texto)` |
| `doctor_byte.pl` | Carga archivos, define reglas e inferencia |

### Hechos

Ejemplo de sintomas:

```prolog
sintoma(no_enciende).
sintoma(pantalla_negra).
sintoma(pitidos_al_arrancar).
```

Ejemplo de fallas:

```prolog
falla(fallo_memoria_ram).
falla(disco_duro_danado).
```

Ejemplo de recomendacion:

```prolog
recomendacion(
    fallo_memoria_ram,
    'Limpiar y reinstalar la memoria RAM, y probar cada modulo por separado.'
).
```

### Reglas de inferencia

Las reglas asocian una falla con una lista de sintomas necesarios:

```prolog
regla_diagnostico(
    fallo_memoria_ram,
    [pitidos_al_arrancar, congelamientos_frecuentes]
).
```

### Uso de listas

El proyecto usa listas para representar sintomas seleccionados y sintomas clave de cada regla:

```prolog
presenta(SintomasSeleccionados, Sintoma) :-
    member(Sintoma, SintomasSeleccionados).

presenta_todos(_, []).
presenta_todos(SintomasSeleccionados, [Sintoma | Resto]) :-
    presenta(SintomasSeleccionados, Sintoma),
    presenta_todos(SintomasSeleccionados, Resto).
```

### Uso de corte

El corte evita que Prolog siga buscando mas diagnosticos despues de encontrar la primera regla valida:

```prolog
diagnosticar(SintomasSeleccionados, Falla) :-
    regla_diagnostico(Falla, SintomasClave),
    presenta_todos(SintomasSeleccionados, SintomasClave),
    !.
```

---

## 9. Flujo de diagnostico

1. El usuario entra a la vista Diagnostico.
2. El frontend solicita sintomas al backend mediante `/api/symptoms`.
3. El usuario selecciona uno o mas sintomas.
4. El frontend consulta `/api/symptom-suggestions` para resaltar sintomas relacionados.
5. El usuario genera el diagnostico.
6. El frontend envia los sintomas a `/api/diagnose`.
7. El backend valida la entrada.
8. Python consulta Prolog mediante PySwip.
9. Prolog evalua las reglas de inferencia.
10. El backend devuelve falla, recomendacion y sintomas utilizados.
11. El diagnostico se guarda en `diagnosis_history.json`.
12. Si el usuario activo Telegram, se envia la notificacion.

---

## 10. Flujo administrativo

1. El administrador entra a la vista Admin.
2. Ingresa la contraseña.
3. El frontend llama a `/api/admin/login`.
4. El backend devuelve un token.
5. El token se usa en los endpoints protegidos con:

```txt
Authorization: Bearer <token>
```

6. El administrador puede crear, leer, editar y eliminar:

- Sintomas.
- Fallas.
- Recomendaciones.
- Reglas.

7. Cada cambio se escribe en los archivos Prolog correspondientes.
8. El backend recarga el servicio Prolog para usar los cambios recientes.

---

## 11. Integracion con Telegram

El sistema usa Telegram Bot API para enviar los resultados del diagnostico. Las credenciales se cargan desde variables de entorno:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

El token y el chat ID no deben escribirse directamente en el codigo fuente.

El mensaje enviado incluye:

- Nombre del sistema.
- Fecha y hora.
- Falla detectada.
- Sintomas evaluados.
- Recomendacion.

Ejemplo de formato:

```txt
DOCTOR BYTE - DIAGNOSTICO
--------------------------------
Fecha y hora: 13/06/2026 23:42:10

Falla detectada:
Fallo Memoria Ram

Sintomas evaluados:
Pitidos Al Arrancar, Congelamientos Frecuentes

Recomendacion:
Limpiar y reinstalar la memoria RAM.
```

En Telegram el mensaje se envia con emojis para mejorar la lectura visual.

---

## 12. Almacenamiento

El proyecto no utiliza una base de datos adicional. Esto es importante porque la logica de conocimiento vive en Prolog.

El almacenamiento local se usa para:

- Historial de diagnosticos: `BACKEND/app/data/diagnosis_history.json`.
- Archivos de conocimiento: `PROLOG/*.pl`.

El historial JSON guarda informacion como:

- Fecha y hora.
- Falla detectada.
- Recomendacion.
- Sintomas utilizados.
- Estado de envio a Telegram.

---

## 13. Seguridad basica

La vista Admin esta protegida por un login simple. El backend usa:

```env
ADMIN_PASSWORD=admin123
ADMIN_ACCESS_TOKEN=doctor-byte-admin-token
```

Los endpoints de administracion requieren token Bearer. Esta seguridad es suficiente para una demostracion local academica, aunque en produccion se recomendaria implementar autenticacion mas robusta.

---

## 14. Ejecucion del proyecto

### Con Docker Compose

Desde la raiz del proyecto:

```bash
docker compose up --build
```

URLs:

```txt
Frontend: http://localhost:5173
Backend: http://localhost:8000
Documentacion API: http://localhost:8000/docs
```

Para detener:

```bash
docker compose down
```

### Sin Docker

Backend:

```bash
cd BACKEND
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd FRONTEND
npm install
npm run dev
```

Tambien es necesario tener SWI-Prolog instalado en el sistema si se ejecuta sin Docker.

---

## 15. Pruebas

El backend incluye pruebas con `pytest`.

Comando:

```bash
cd BACKEND
python -m pytest
```

Las pruebas verifican:

- Lectura de la base Prolog.
- Endpoints de administracion.
- Login de admin.
- CRUD sobre sintomas, fallas, recomendaciones y reglas.
- Sugerencias de sintomas.
- Formato del mensaje de Telegram.

---

## 16. Conclusiones

- Se implemento un sistema experto funcional usando Prolog.
- El backend se conecta con Prolog mediante PySwip.
- La base de conocimiento permanece en archivos `.pl`.
- La interfaz permite diagnostico normal y administracion del conocimiento.
- El sistema permite modificar sintomas, fallas, recomendaciones y reglas desde la vista Admin.
- Se implemento historial de diagnosticos en JSON.
- Se integro Telegram para enviar diagnosticos con fecha, hora y formato legible.
- Docker Compose facilita la ejecucion del proyecto durante la demostracion.
