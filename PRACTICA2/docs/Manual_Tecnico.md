# Manual Tecnico - SmartBot

## Arquitectura

SmartBot utiliza una arquitectura cliente-servidor basada en API REST, con frontend y backend separados.

```txt
Frontend React + Vite -> API REST FastAPI -> SQLite
Bot de Telegram ------> API REST FastAPI -> SQLite
```

## Tecnologias

- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- React
- Vite
- python-telegram-bot
- Docker Compose

## Modelo de datos

Entidades principales:

- `admin_users`: usuarios administradores.
- `categories`: categorias de preguntas.
- `faqs`: preguntas frecuentes y respuestas.
- `settings`: configuracion del sistema.
- `query_logs`: registro de consultas realizadas.
  - Guarda fecha y hora, usuario de Telegram, consulta, respuesta y categoria asociada cuando existe.

## Endpoints principales

- `GET /health`: verifica el estado del servicio.
- `POST /api/auth/login`: autentica al administrador.
- `GET /api/admin-users`: lista usuarios administradores autenticados.
- `POST /api/admin-users`: registra un nuevo usuario administrador usando JWT.
- `GET /api/dashboard`: devuelve estadisticas del panel.
- `GET /api/categories`: lista categorias.
- `POST /api/categories`: crea categoria.
- `PUT /api/categories/{category_id}`: actualiza categoria.
- `DELETE /api/categories/{category_id}`: elimina categoria.
- `GET /api/faqs`: lista preguntas.
- `POST /api/faqs`: crea pregunta.
- `PUT /api/faqs/{faq_id}`: actualiza pregunta.
- `DELETE /api/faqs/{faq_id}`: elimina pregunta.
- `GET /api/settings`: obtiene configuracion del sistema.
- `PUT /api/settings`: actualiza configuracion del sistema.
- `POST /api/bot/query`: recibe una consulta y devuelve una respuesta.

## Requerimientos funcionales

- El sistema permite iniciar sesion en el panel administrativo.
- El sistema permite registrar nuevos usuarios administradores desde una sesion autenticada.
- El administrador puede gestionar preguntas y respuestas.
- El administrador puede gestionar categorias.
- El bot consulta la API para responder mensajes de Telegram.
- El sistema registra consultas realizadas por usuarios.
- El panel muestra estadisticas de consultas frecuentes, usuarios y categorias mas consultadas.

## Requerimientos no funcionales

- Seguridad: el panel administrativo esta protegido con autenticacion.
- Mantenibilidad: el codigo esta separado en modelos, rutas, autenticacion y bot.
- Usabilidad: el panel web permite gestionar informacion sin modificar codigo.
- Portabilidad: el proyecto puede ejecutarse con Docker Compose.
