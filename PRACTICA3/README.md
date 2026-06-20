# SmartInvoice

Sistema para procesamiento automático de facturas mediante Computer Vision, OCR y RPA.

## Documentación

- [Manual de usuario](docs/ManualUsuario.md)
- [Manual técnico](docs/ManualTecnico.md)
- [Estado del backend](docs/EstadoBackend.md)
- [Plan de desarrollo](docs/PlanDesarrollo.md)
- [Enunciado de la práctica](docs/Practica3.md)

## Ejecución rápida

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

## Despliegue en EC2

Utilice `.env.production.example` como plantilla:

```bash
cp .env.production.example .env
nano .env
docker compose up -d --build
```

Reemplace la IP pública, contraseñas, secreto JWT y credenciales SMTP antes de iniciar.
