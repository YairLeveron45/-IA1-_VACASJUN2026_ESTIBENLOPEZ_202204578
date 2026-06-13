# SmartBot

SmartBot es un sistema de atencion automatizada para consultas frecuentes mediante Telegram. Permite administrar preguntas, respuestas, categorias y configuracion del bot desde un panel web, mientras una API REST en Python consulta la base de datos SQLite para responder mensajes enviados desde el chat o grupo autorizado.

El proyecto integra un backend con FastAPI, un frontend administrativo con React + Vite, un bot de Telegram y ejecucion completa mediante Docker Compose.

## Estructura

```txt
backend/   API REST FastAPI y bot de Telegram
frontend/  Panel administrativo React + Vite
database/  Base de datos SQLite local
Documentacion/  Manual tecnico, manual de usuario y capturas
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
