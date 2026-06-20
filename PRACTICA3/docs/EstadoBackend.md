# Estado del proyecto SmartInvoice

## Resumen

El backend obligatorio de SmartInvoice se encuentra implementado y funcionando mediante
Docker Compose.

Tecnologías utilizadas:

- Python 3.11.
- FastAPI.
- PostgreSQL 17.
- SQLAlchemy asíncrono.
- Alembic.
- JWT y Argon2.
- OpenCV.
- Tesseract OCR 5.5 en español.
- PyMuPDF.
- ReportLab.
- Playwright y Chromium.
- Docker y Docker Compose.

## Arquitectura

Se utiliza una arquitectura MVC adaptada para una API:

```text
Route
  -> Controller
    -> Service
      -> Repository
        -> Model
          -> PostgreSQL
```

Responsabilidades:

- `routes`: endpoints HTTP y dependencias.
- `controllers`: coordinación de solicitudes y respuestas.
- `services`: reglas y procesos de negocio.
- `repositories`: consultas y persistencia.
- `models`: entidades de SQLAlchemy.
- `schemas`: validación con Pydantic.
- `core`: configuración, seguridad y excepciones.
- `db`: conexión y sesiones de PostgreSQL.

## Ejecución

Desde la raíz de `PRACTICA3`:

```powershell
docker compose up -d --build
```

Direcciones locales:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Salud: `http://localhost:8000/api/v1/health`

Los contenedores utilizados son:

- `smartinvoice_api`
- `smartinvoice_db`

## Credenciales de desarrollo

```text
Correo: admin@smartinvoice.com
Contraseña: Admin123!
```

Estas credenciales deben cambiarse antes de desplegar el sistema.

La configuración local se encuentra en `.env`. La plantilla segura para nuevas
instalaciones se encuentra en `.env.example`.

## Módulos implementados

### Salud de la aplicación

```text
GET /api/v1/health
```

Permite comprobar que la API está disponible.

### Autenticación

```text
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

Características:

- Tokens JWT.
- Expiración configurable.
- Contraseñas cifradas mediante Argon2.
- Creación automática del administrador inicial.
- Roles `admin` y `operator`.
- Protección reutilizable de endpoints.

### Usuarios

```text
GET    /api/v1/users
POST   /api/v1/users
GET    /api/v1/users/{id}
PATCH  /api/v1/users/{id}
DELETE /api/v1/users/{id}
PATCH  /api/v1/users/{id}/password
PATCH  /api/v1/users/me/password
```

Características:

- CRUD administrativo.
- Correos únicos.
- Asignación de roles.
- Cambio y restablecimiento de contraseña.
- Desactivación lógica.
- Un administrador no puede desactivarse ni retirar su propio rol.

### Proveedores

```text
GET    /api/v1/providers
POST   /api/v1/providers
GET    /api/v1/providers/{id}
PATCH  /api/v1/providers/{id}
DELETE /api/v1/providers/{id}
```

Características:

- CRUD completo.
- Paginación.
- Normalización del NIT.
- NIT único.
- Validación de correo.
- Desactivación lógica.
- Auditoría automática.

### Facturas

```text
GET   /api/v1/invoices
POST  /api/v1/invoices/upload
GET   /api/v1/invoices/{id}
GET   /api/v1/invoices/{id}/download
PATCH /api/v1/invoices/{id}/reject
```

Características:

- Carga autenticada.
- Archivos PDF, JPG, JPEG y PNG.
- Límite configurable de 10 MB.
- Validación de extensión y tipo MIME.
- Nombres internos aleatorios.
- Asociación con el usuario responsable.
- Estados `pending`, `processed`, `error` y `rejected`.
- Listado paginado y filtros.
- Descarga del archivo original.

### OCR y Computer Vision

```text
POST /api/v1/invoices/{id}/process
```

Flujo:

```text
Documento
  -> conversión a imágenes
  -> escala de grises
  -> corrección de inclinación
  -> reducción de ruido
  -> umbralización
  -> Tesseract OCR
  -> extracción de campos
  -> validación
  -> PostgreSQL
```

Campos extraídos:

- Número de factura.
- Fecha.
- Proveedor.
- NIT.
- Subtotal.
- Impuestos.
- Total.

El texto completo obtenido mediante OCR también se almacena. Si existen campos faltantes o
montos incoherentes, la factura queda en estado `error` para revisión manual.

### Corrección y validación manual

```text
PATCH /api/v1/invoices/{id}/validate
```

Características:

- Corrección de los siete campos.
- Validación de fechas y montos.
- Tolerancia de redondeo de Q0.05.
- Normalización del NIT.
- Asociación automática con un proveedor registrado.
- Cambio de estado a `processed`.
- Auditoría de la corrección.

### Bitácora

```text
GET /api/v1/logs
GET /api/v1/logs/{id}
```

Filtros disponibles:

- Factura.
- Usuario.
- Acción.
- Estado.
- Fecha inicial y final.
- Paginación.

La bitácora es de solo lectura desde la API. Registra operaciones relacionadas con
facturas, OCR, proveedores, usuarios, reportes, correo y RPA.

### Reportes

```text
GET  /api/v1/reports
POST /api/v1/reports
GET  /api/v1/reports/{id}/download
```

Formatos:

- CSV UTF-8.
- PDF horizontal.

Filtros:

- Rango de fechas.
- Proveedor.
- Estado de factura.

Los reportes incluyen subtotales, impuestos, totales y acumulados. Se almacenan en el
volumen `reports` y se registran en PostgreSQL.

### Correo electrónico

```text
POST /api/v1/reports/{id}/email
```

Características:

- Reporte CSV o PDF como adjunto.
- SMTP configurable.
- Soporte para TLS y autenticación.
- Remitente configurable.
- Bitácora de éxito o error.

Actualmente se utiliza el modo de desarrollo:

```text
SMTP_ENABLED=false
```

En este modo, los mensajes se guardan como `.eml` en `reports/outbox` y no se envía un
correo real. Para producción se deben configurar las variables `SMTP_*`.

### Automatización RPA

```text
POST /api/v1/rpa/invoices/{id}/execute
```

Flujo:

```text
Factura procesada
  -> Playwright abre Chromium
  -> completa formulario simulado
  -> envía los siete campos
  -> recibe confirmación
  -> guarda evidencias
  -> registra bitácora
```

Evidencias:

- Captura PNG.
- JSON de ejecución.
- JSON recibido por el sistema simulado.
- Entrada de auditoría.

La factura debe estar en estado `processed`.

## Modelos de base de datos

Se encuentran implementadas las tablas:

- `users`
- `providers`
- `invoices`
- `processing_logs`
- `reports`
- `alembic_version`

Las migraciones se aplican automáticamente al iniciar el contenedor de la API.

## Pruebas realizadas

La última ejecución contiene:

```text
35 pruebas aprobadas
```

También se verificaron manualmente:

- Login y protección mediante JWT.
- Restricciones por rol.
- CRUD de usuarios y proveedores.
- Carga y descarga de facturas.
- OCR de un PDF de 11 páginas.
- Extracción de 19,808 caracteres.
- Corrección manual y asociación por NIT.
- Reportes CSV y PDF.
- Mensaje `.eml` con reporte adjunto.
- Ejecución real de Chromium con Playwright.
- Registro RPA de una factura con captura y evidencias.

Para ejecutar las pruebas:

```powershell
docker compose exec api python -m pytest -q
```

## Archivos y volúmenes

- `uploads/`: documentos cargados.
- `reports/`: reportes generados.
- `reports/outbox/`: correos de desarrollo.
- `reports/rpa/`: evidencias de automatización.
- Volumen `postgres_data`: información persistente de PostgreSQL.

## Estado actual

Los módulos obligatorios principales del backend se encuentran implementados:

- Autenticación.
- Usuarios.
- Proveedores.
- Facturas.
- OCR y Computer Vision.
- Corrección manual.
- Bitácora.
- Reportes.
- Correo.
- RPA.
- Docker Compose.

## Estado del frontend

La primera base del frontend se encuentra implementada con:

- React.
- Vite.
- TypeScript.
- React Router.
- Axios.
- TanStack Query.
- Zustand.

Estructura sugerida:

```text
frontend/
|-- src/
|   |-- api/
|   |-- components/
|   |-- layouts/
|   |-- pages/
|   |-- routes/
|   |-- schemas/
|   |-- store/
|   |-- types/
|   `-- utils/
|-- Dockerfile
`-- package.json
```

Pantallas previstas:

1. Inicio de sesión.
2. Dashboard.
3. Usuarios.
4. Proveedores.
5. Carga y gestión de facturas.
6. Resultado OCR y corrección manual.
7. Bitácora.
8. Reportes.
9. Envío por correo.
10. Ejecución RPA.

Ya se implementó:

- Login conectado con FastAPI.
- Persistencia de la sesión JWT.
- Cliente Axios con token automático.
- Manejo global de respuestas `401`.
- Rutas privadas.
- Rutas administrativas por rol.
- Layout administrativo responsivo.
- Dashboard inicial.
- Navegación para todos los módulos.
- CORS en FastAPI.
- Contenedor de desarrollo para Vite.
- Build de producción con Nginx.

Direcciones:

```text
Frontend: http://localhost:5173
API:      http://localhost:8000
Swagger:  http://localhost:8000/docs
```

El build de producción fue verificado correctamente y el backend conserva sus 35 pruebas
aprobadas.

La siguiente etapa será conectar las páginas funcionales de usuarios, proveedores,
facturas, bitácora, reportes y RPA con sus endpoints existentes.
