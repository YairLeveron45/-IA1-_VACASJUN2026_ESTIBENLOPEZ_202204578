# Backend de SmartInvoice

La documentación completa de arquitectura, base de datos, endpoints, OCR, RPA, correo,
Docker y despliegue se encuentra en el
[Manual técnico](../docs/ManualTecnico.md).

El backend utiliza FastAPI con una organización inspirada en MVC:

- `models/`: modelos y entidades persistentes.
- `controllers/`: coordinación de solicitudes y respuestas.
- `services/`: reglas de negocio.
- `schemas/`: validación y representación de datos de entrada y salida.
- `routes/`: definición de endpoints.
- `db/`: conexión, sesiones y base de SQLAlchemy.
- `core/`: configuración y utilidades compartidas.

## Ejecución local

Desde la raíz de `PRACTICA3`:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

La API estará disponible en:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Salud: `http://localhost:8000/api/v1/health`

## Autenticación

Al iniciar el proyecto se crea el administrador definido en `.env` si todavía no existe.

```text
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

El inicio de sesión devuelve un token JWT. Para acceder a las rutas protegidas se debe
enviar:

```text
Authorization: Bearer <token>
```

Las rutas de proveedores requieren autenticación.

## Usuarios

Las operaciones administrativas requieren un token con rol `admin`:

```text
GET    /api/v1/users
POST   /api/v1/users
GET    /api/v1/users/{id}
PATCH  /api/v1/users/{id}
DELETE /api/v1/users/{id}
PATCH  /api/v1/users/{id}/password
PATCH  /api/v1/users/me/password
```

La eliminación es lógica. Un administrador no puede desactivar su propia cuenta ni retirar
su propio rol de administrador.

## Facturas

Las rutas de facturas requieren autenticación:

```text
GET   /api/v1/invoices
POST  /api/v1/invoices/upload
GET   /api/v1/invoices/{id}
GET   /api/v1/invoices/{id}/download
PATCH /api/v1/invoices/{id}/reject
DELETE /api/v1/invoices/{id}
```

El listado permite consultar por estado, proveedor y texto. La búsqueda incluye archivo,
número de factura, proveedor detectado y NIT. La eliminación es lógica: retira la factura
de las consultas, elimina el archivo almacenado y conserva la bitácora histórica.

Se aceptan archivos PDF, JPG, JPEG y PNG de hasta 10 MB. Los archivos reciben un nombre
interno aleatorio, se almacenan fuera de las rutas públicas y se registran inicialmente con
estado `pending`. La carga y el rechazo generan entradas en la bitácora.

El procesamiento OCR se ejecuta con:

```text
POST /api/v1/invoices/{id}/process
```

El módulo convierte PDF a imágenes, aplica escala de grises, corrección ligera de
inclinación, reducción de ruido y umbralización. Después utiliza Tesseract en español para
extraer texto y detectar número de factura, fecha, proveedor, NIT, subtotal, impuestos y
total. Si faltan campos o los montos no coinciden, la factura queda en estado `error` para
revisión manual.

La corrección y validación manual se realiza con:

```text
PATCH /api/v1/invoices/{id}/validate
```

Se deben enviar los siete campos requeridos. El backend valida los montos, normaliza el
NIT, busca un proveedor registrado con ese NIT y marca la factura como `processed` cuando
los datos son coherentes.

Durante la validación, el usuario puede registrar el proveedor detectado si el NIT todavía
no existe. La creación, asociación con la factura y entradas de bitácora se guardan en una
misma transacción. Si el proveedor ya existe, se asocia automáticamente sin duplicarlo.

## Bitácora

La bitácora es de solo lectura desde la API:

```text
GET /api/v1/logs
GET /api/v1/logs/{id}
```

El listado admite filtros por `invoice_id`, `user_id`, `action`, `status`, `date_from` y
`date_to`, además de paginación. Se registran acciones de facturas, proveedores, usuarios
y cambios de contraseña.

## Reportes

Los reportes administrativos se generan en CSV o PDF:

```text
GET  /api/v1/reports
POST /api/v1/reports
GET  /api/v1/reports/{id}/download
```

Se pueden filtrar por rango de fechas, proveedor y estado de factura. El reporte incluye
subtotal, impuestos, total y una fila de acumulados. Los archivos se almacenan en el
volumen `reports` y cada generación queda registrada en la bitácora.

## Correo electrónico

Un reporte existente puede enviarse mediante:

```text
POST /api/v1/reports/{id}/email
```

En producción se utiliza SMTP con las variables `SMTP_*`. Mientras `SMTP_ENABLED=false`,
los mensajes se guardan como archivos `.eml` en `reports/outbox`; este modo permite probar
destinatario, contenido y adjunto sin enviar correos reales. Cada intento queda registrado
en la bitácora.

## Automatización RPA

La automatización registra una factura procesada en un formulario web simulado:

```text
POST /api/v1/rpa/invoices/{id}/execute
```

Playwright abre Chromium, completa los siete campos, envía el formulario y guarda una
captura PNG, una evidencia JSON y el registro recibido por el sistema simulado. La factura
debe estar en estado `processed` y cada ejecución queda registrada en la bitácora.

## Proveedores

El primer módulo funcional implementa un CRUD con eliminación lógica:

```text
GET    /api/v1/providers
POST   /api/v1/providers
GET    /api/v1/providers/{id}
PATCH  /api/v1/providers/{id}
DELETE /api/v1/providers/{id}
```

El NIT se normaliza automáticamente y no puede repetirse. El endpoint `DELETE` conserva
el registro y cambia `is_active` a `false`.

## Migraciones

Las migraciones se aplican automáticamente al iniciar el contenedor de la API. También
pueden ejecutarse manualmente:

```powershell
docker compose exec api alembic upgrade head
```

## Pruebas

```powershell
Set-Location backend
python -m pytest
```
