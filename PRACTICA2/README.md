# SmartBot

Sistema de respuestas automatizadas con bot de Telegram, backend FastAPI, frontend React + Vite y base de datos SQLite.

## Estructura

```txt
backend/   API REST FastAPI y bot de Telegram
frontend/  Panel administrativo React + Vite
database/  Base de datos SQLite local
docs/      Manual tecnico y manual de usuario
```

## Credenciales del panel

```txt
Usuario: IA1-User
Contrasena: IA1-password@_new
```

## Ejecucion con Docker Compose

Levantar backend, frontend y bot:

```bash
docker compose up --build
```

Panel administrativo:

```txt
http://localhost:5173
```

API REST:

```txt
http://localhost:8000/docs
```

## Bot de Telegram

Crea un archivo `.env` en la raiz del proyecto:

```env
TELEGRAM_BOT_TOKEN=token_de_botfather
TELEGRAM_CHAT_ID=1305253706
```

El backend toma `TELEGRAM_CHAT_ID` como configuracion inicial del panel administrativo.

Si cambiaste el token, recrea los contenedores:

```bash
docker compose up --build
```

## Ejecucion local sin Docker

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```
