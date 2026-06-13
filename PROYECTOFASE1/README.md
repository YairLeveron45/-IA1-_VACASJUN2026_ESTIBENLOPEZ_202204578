# PROYECTOFASE1 - Doctor Byte

Estructura base del proyecto para la Fase 1.

Doctor Byte es un sistema experto para diagnosticar fallas comunes en computadoras
utilizando Prolog como motor de inferencia, un backend en Python, una interfaz web
y una integracion con Telegram para notificaciones.

## Estructura general

- `PROLOG/`: base de conocimiento, hechos y reglas.
- `BACKEND/`: API y servicios para consultar Prolog, guardar historial y enviar mensajes.
- `FRONTEND/`: interfaz web para seleccionar sintomas y ver diagnosticos.
- `DOC/`: documentacion tecnica, manuales, casos de prueba y evidencias.

## Ejecucion con Docker Compose

Levanta backend, frontend y SWI-Prolog dentro del contenedor del backend:

```bash
docker compose up --build
```

URLs principales:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Documentacion API: `http://localhost:8000/docs`

Variables opcionales para la demo:

```env
ADMIN_PASSWORD=admin123
ADMIN_ACCESS_TOKEN=doctor-byte-admin-token
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```
