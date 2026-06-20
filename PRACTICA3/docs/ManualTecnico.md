# Manual Técnico - SmartInvoice

## 1. Información general

| Campo | Descripción |
|---|---|
| Proyecto | SmartInvoice |
| Curso | Inteligencia Artificial 1 |
| Práctica | Práctica 3 |
| Backend | Python 3.11 y FastAPI |
| Frontend | React 19, TypeScript y Vite |
| Base de datos | PostgreSQL 17 |
| OCR | Tesseract OCR |
| Computer Vision | OpenCV |
| RPA | Playwright y Chromium |
| Contenedores | Docker y Docker Compose |

SmartInvoice es una aplicación web que automatiza el procesamiento administrativo de
facturas. El sistema recibe documentos PDF o imágenes, mejora visualmente el documento,
extrae su contenido mediante OCR, identifica campos relevantes, permite validar la
información, registra los datos mediante RPA en un sistema web simulado, genera reportes y
notifica los resultados por correo electrónico.

## 2. Objetivos técnicos

- Implementar una API REST utilizando Python.
- Procesar facturas localmente mediante Computer Vision y OCR.
- Persistir usuarios, proveedores, facturas, reportes y bitácoras.
- Aplicar autenticación JWT y control de acceso por roles.
- Automatizar el registro de facturas mediante Playwright.
- Generar reportes administrativos PDF y CSV.
- Enviar reportes automáticamente por SMTP.
- Ejecutar todos los componentes mediante Docker Compose.

## 3. Tecnologías utilizadas

### 3.1 Backend

- Python 3.11.
- FastAPI.
- Uvicorn.
- Pydantic.
- SQLAlchemy asíncrono.
- Asyncpg.
- Alembic.
- PyJWT.
- Argon2 mediante `pwdlib`.

### 3.2 Inteligencia artificial y automatización

- OpenCV para preprocesamiento de imágenes.
- Tesseract OCR para reconocimiento de texto.
- PyMuPDF para lectura y conversión de documentos PDF.
- Expresiones regulares y reglas de negocio para extracción de campos.
- Playwright y Chromium para automatización RPA.

La extracción no depende de servicios externos de inteligencia artificial generativa. El
documento se procesa localmente dentro de la solución.

### 3.3 Frontend

- React 19.
- TypeScript.
- Vite.
- React Router.
- TanStack Query.
- Axios.
- Zustand.
- Lucide React.

### 3.4 Infraestructura

- PostgreSQL 17.
- Docker.
- Docker Compose.
- Nginx para el build de producción del frontend.
- SMTP para el envío de correo.

## 4. Arquitectura del sistema

SmartInvoice utiliza una arquitectura por capas inspirada en MVC y en el patrón Repository.
Cada capa tiene una responsabilidad específica.

![alt text](<assets/Diagrama de Arquietctura.png>)

### 4.1 Responsabilidades de las capas

| Capa | Responsabilidad |
|---|---|
| Routes | Define los endpoints, dependencias y parámetros HTTP. |
| Controllers | Traduce errores de negocio a respuestas HTTP. |
| Services | Implementa reglas de negocio, OCR, RPA, correo y reportes. |
| Repositories | Ejecuta consultas y operaciones de persistencia. |
| Models | Representa las tablas mediante SQLAlchemy. |
| Schemas | Valida las solicitudes y respuestas mediante Pydantic. |
| Core | Contiene configuración, seguridad y excepciones compartidas. |
| DB | Configura el motor, las sesiones y las migraciones. |

### 4.2 Justificación de la arquitectura

La separación por capas permite:

- Evitar lógica de negocio dentro de los endpoints.
- Sustituir repositorios o servicios durante las pruebas.
- Mantener aislados OCR, RPA, correo y almacenamiento.
- Centralizar la validación mediante Pydantic.
- Facilitar el crecimiento y mantenimiento del proyecto.
- Realizar pruebas unitarias con dependencias simuladas.



En desarrollo, los servicios se ejecutan mediante `docker-compose.yml`. La API espera a
que PostgreSQL se encuentre saludable, aplica las migraciones y crea el administrador
inicial antes de iniciar Uvicorn.

## 6. Flujo funcional

![alt text](<assets/Diagrama de flujo.png>)

## 7. Estructura del proyecto

```text
PRACTICA3/
|-- backend/
|   |-- alembic/
|   |   `-- versions/
|   |-- app/
|   |   |-- controllers/
|   |   |-- core/
|   |   |-- db/
|   |   |-- models/
|   |   |-- repositories/
|   |   |-- routes/
|   |   |-- schemas/
|   |   |-- scripts/
|   |   `-- services/
|   |-- tests/
|   |-- Dockerfile
|   |-- alembic.ini
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- api/
|   |   |-- components/
|   |   |-- hooks/
|   |   |-- layouts/
|   |   |-- pages/
|   |   |-- routes/
|   |   |-- store/
|   |   |-- styles/
|   |   `-- types/
|   |-- Dockerfile
|   |-- nginx.conf
|   `-- package.json
|-- docs/
|-- reports/
|-- uploads/
|-- .env.example
|-- .gitignore
`-- docker-compose.yml
```

## 8. Modelo de datos

![alt text](<assets/Diagrama ER.png>)

### 8.1 Tablas

#### Users

Almacena las cuentas del sistema. Los roles disponibles son `admin` y `operator`. Las
contraseñas nunca se almacenan en texto plano.

#### Providers

Almacena la información comercial y tributaria de los proveedores. El NIT es único. La
eliminación es lógica mediante `is_active`.

#### Invoices

Almacena el documento, los resultados OCR, la relación con el proveedor, el usuario
responsable y su estado.

Estados:

- `pending`: cargada, pendiente de OCR.
- `processed`: información validada.
- `error`: OCR completado con observaciones.
- `rejected`: documento rechazado.

La eliminación se realiza lógicamente mediante `is_deleted`, pero el archivo físico se
retira del almacenamiento.

#### Processing logs

Registra fecha, usuario, factura, acción, estado, resultado y detalle de error.

#### Reports

Almacena los reportes generados, formato, ruta, filtros y usuario responsable.

## 9. Seguridad

### 9.1 Autenticación

La autenticación utiliza JWT Bearer. Después del inicio de sesión, el frontend envía:

```http
Authorization: Bearer <token>
```

El token contiene el identificador y rol del usuario y tiene una expiración configurable.

### 9.2 Contraseñas

Las contraseñas se procesan con Argon2. La base de datos únicamente almacena
`password_hash`.

### 9.3 Roles

- `admin`: administra usuarios y configuración.
- `operator`: utiliza facturas, proveedores, reportes, RPA y bitácora.

### 9.4 Archivos

- Se validan extensión y tipo MIME.
- Se aceptan PDF, JPG, JPEG y PNG.
- El tamaño máximo es configurable.
- Los nombres físicos son UUID.
- Las rutas se validan para evitar acceso fuera del directorio permitido.

### 9.5 Secretos

Los secretos se almacenan en `.env`, archivo excluido por `.gitignore`. La plantilla
`.env.example` no contiene credenciales reales.

Nunca deben publicarse:

- `SMTP_PASSWORD`.
- `JWT_SECRET_KEY`.
- `POSTGRES_PASSWORD`.
- `INITIAL_ADMIN_PASSWORD`.

## 10. Procesamiento OCR y Computer Vision

### 10.1 Flujo

1. Se comprueba si el PDF contiene texto nativo suficiente.
2. Si no contiene texto, se convierte cada página a imagen.
3. Se convierte la imagen a escala de grises.
4. Se corrige una inclinación moderada.
5. Se reduce el ruido.
6. Se aplica umbralización adaptativa.
7. Tesseract OCR extrae el texto en español.
8. El texto se normaliza.
9. Se extraen los campos mediante reglas y expresiones regulares.
10. Se aplican validaciones automáticas.

### 10.2 Campos extraídos

- Número de factura.
- Fecha.
- Nombre del proveedor.
- NIT.
- Subtotal.
- Impuestos.
- Total.

### 10.3 Validaciones

- Existencia de los siete campos requeridos.
- Conversión válida de fecha.
- Conversión de montos con formatos locales.
- Verificación de `subtotal + impuestos = total`.
- Tolerancia de redondeo de Q0.05.
- Compatibilidad con retenciones en documentos aplicables.
- Asociación del proveedor mediante NIT.

Si el NIT no existe, el usuario puede registrar el proveedor detectado durante la
validación. La creación del proveedor, asociación de factura y bitácora se confirman en una
misma transacción.

## 11. Automatización RPA

La automatización utiliza Playwright con Chromium en modo headless.

### 11.1 Proceso

1. Comprueba que la factura tenga estado `processed`.
2. Abre el formulario web simulado.
3. Completa número, fecha, proveedor, NIT y montos.
4. Presiona el botón de registro.
5. Espera la confirmación.
6. Guarda una captura PNG.
7. Guarda evidencia JSON.
8. Registra éxito o error en la bitácora.

### 11.2 Evidencias

Las evidencias se almacenan en:

```text
reports/rpa/
```

Archivos generados:

- `rpa-<uuid>.png`: captura del resultado.
- `rpa-<uuid>.json`: datos enviados y confirmación.
- `submission-<uuid>.json`: datos recibidos por el sistema simulado.

## 12. Reportes y correo

### 12.1 Reportes

Se generan reportes:

- PDF administrativo mediante ReportLab.
- CSV UTF-8.

Los reportes incluyen:

- Fecha de generación.
- Cantidad de facturas.
- Facturas procesadas y con observaciones.
- Tabla de detalle.
- Subtotal acumulado.
- Impuestos acumulados.
- Total consolidado.

### 12.2 Correo

El correo utiliza SMTP con TLS. Contiene:

- Versión de texto.
- Plantilla HTML.
- Reporte PDF o CSV adjunto.
- Remitente y destinatario configurables.

Al generar un reporte, el sistema intenta enviarlo automáticamente. Si el correo falla, el
reporte permanece almacenado y el error queda registrado.

En modo de desarrollo, `SMTP_ENABLED=false` guarda los mensajes `.eml` en
`reports/outbox` sin enviarlos.

## 13. API REST

Prefijo general:

```text
/api/v1
```

La documentación Swagger está disponible en:

```text
http://localhost:8000/docs
```

### 13.1 Autenticación

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/auth/login` | Inicia sesión. |
| GET | `/auth/me` | Obtiene el usuario autenticado. |

### 13.2 Usuarios

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/users` | Lista usuarios. |
| POST | `/users` | Crea un usuario. |
| GET | `/users/{id}` | Consulta un usuario. |
| PATCH | `/users/{id}` | Actualiza un usuario. |
| DELETE | `/users/{id}` | Desactiva un usuario. |
| PATCH | `/users/{id}/password` | Restablece contraseña. |
| PATCH | `/users/me/password` | Cambia contraseña propia. |

### 13.3 Proveedores

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/providers` | Lista proveedores. |
| GET | `/providers/lookup?nit=` | Busca por NIT. |
| POST | `/providers` | Crea un proveedor. |
| GET | `/providers/{id}` | Consulta un proveedor. |
| PATCH | `/providers/{id}` | Actualiza un proveedor. |
| DELETE | `/providers/{id}` | Desactiva un proveedor. |

### 13.4 Facturas

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/invoices` | Lista y filtra facturas. |
| GET | `/invoices/stats` | Obtiene estadísticas. |
| POST | `/invoices/upload` | Carga una factura. |
| GET | `/invoices/{id}` | Consulta detalle. |
| GET | `/invoices/{id}/download` | Descarga documento. |
| POST | `/invoices/{id}/process` | Ejecuta OCR. |
| PATCH | `/invoices/{id}/validate` | Valida y corrige datos. |
| PATCH | `/invoices/{id}/reject` | Rechaza una factura. |
| DELETE | `/invoices/{id}` | Elimina lógicamente. |

### 13.5 Bitácora

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/logs` | Lista y filtra eventos. |
| GET | `/logs/{id}` | Consulta un evento. |

### 13.6 Reportes

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/reports` | Lista reportes. |
| POST | `/reports` | Genera reporte y envía correo. |
| GET | `/reports/{id}/download` | Descarga reporte. |
| POST | `/reports/{id}/email` | Reenvía un reporte. |

### 13.7 RPA

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/rpa/invoices/{id}/execute` | Ejecuta RPA. |
| GET | `/rpa-simulator/form` | Formulario simulado. |
| GET | `/rpa-simulator/result/{id}` | Resultado persistente. |

## 14. Manejo de errores

El proyecto utiliza excepciones de aplicación para separar errores técnicos y reglas de
negocio.

| Error | Código HTTP típico |
|---|---|
| Autenticación inválida | 401 |
| Acceso sin permisos | 403 |
| Recurso inexistente | 404 |
| Conflicto o duplicado | 409 |
| Archivo o regla inválida | 400 |
| Error SMTP o automatización externa | 502 |

Los errores de OCR, correo y RPA se registran en la bitácora con `error_detail`.

## 15. Variables de entorno

Crear `.env` a partir de la plantilla:

```powershell
Copy-Item .env.example .env
```

Variables principales:

| Variable | Función |
|---|---|
| `JWT_SECRET_KEY` | Firma de tokens JWT. |
| `CORS_ORIGINS` | Orígenes autorizados. |
| `UPLOAD_DIRECTORY` | Directorio de facturas. |
| `REPORT_DIRECTORY` | Directorio de reportes. |
| `MAX_UPLOAD_SIZE_MB` | Tamaño máximo. |
| `TESSERACT_LANGUAGE` | Idioma OCR. |
| `RPA_TARGET_URL` | Formulario que utiliza el robot. |
| `SMTP_ENABLED` | Activa correo real. |
| `SMTP_HOST` | Servidor SMTP. |
| `SMTP_USERNAME` | Usuario SMTP. |
| `SMTP_PASSWORD` | Contraseña de aplicación. |
| `POSTGRES_*` | Configuración PostgreSQL. |
| `INITIAL_ADMIN_*` | Administrador inicial. |

## 16. Instalación y ejecución

### 16.1 Requisitos

- Docker Desktop o Docker Engine.
- Docker Compose.
- Git.
- Navegador moderno.

### 16.2 Ejecución con Docker

Desde `PRACTICA3`:

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

Servicios:

| Servicio | URL |
|---|---|
| Frontend | `http://localhost:5173` |
| API | `http://localhost:8000` |
| Swagger | `http://localhost:8000/docs` |
| Salud | `http://localhost:8000/api/v1/health` |
| PostgreSQL | `localhost:5432` |

Comprobar contenedores:

```powershell
docker compose ps
```

Consultar logs:

```powershell
docker compose logs -f api
docker compose logs -f frontend
```

Detener:

```powershell
docker compose down
```

Detener y eliminar datos de PostgreSQL:

```powershell
docker compose down -v
```

Este último comando elimina los datos persistentes y debe utilizarse con precaución.

## 17. Migraciones

Las migraciones se ejecutan automáticamente al iniciar la API.

Ejecución manual:

```powershell
docker compose exec api alembic upgrade head
```

Migraciones actuales:

- Creación de tablas iniciales.
- Filtros de reportes.
- Eliminación lógica de facturas.

## 18. Pruebas

Ejecutar pruebas:

```powershell
Set-Location backend
python -m pytest -q
```

El proyecto dispone de pruebas para:

- Seguridad y autenticación.
- Usuarios.
- Proveedores.
- Facturas.
- Validación y extracción.
- Almacenamiento.
- Reportes.
- Correo.
- RPA simulado.
- Bitácora.

Estado verificado:

```text
42 pruebas aprobadas
```

Compilar frontend:

```powershell
Set-Location frontend
npm install
npm run build
```

## 19. Despliegue en AWS

La arquitectura objetivo utiliza servicios administrados de AWS para publicar SmartInvoice
con una URL HTTPS, conservar los datos y mantener aisladas las credenciales.

### 19.1 Servicios utilizados

| Servicio AWS | Uso en SmartInvoice |
|---|---|
| Route 53 | Dominio público y resolución DNS. |
| Certificate Manager | Certificado TLS para HTTPS. |
| Application Load Balancer | Distribución de solicitudes entre frontend y API. |
| ECR | Registro privado de imágenes Docker. |
| ECS con Fargate | Ejecución de los contenedores sin administrar servidores. |
| RDS PostgreSQL | Base de datos administrada. |
| EFS | Persistencia de cargas, reportes y evidencias RPA. |
| Secrets Manager | Almacenamiento seguro de contraseñas y secretos. |
| CloudWatch | Registros, métricas y diagnóstico. |
| SES o SMTP Gmail | Envío automático de reportes. |
| S3 | Respaldo opcional de documentos y reportes. |

### 19.2 Pasos de despliegue

1. Publicar el código fuente en GitHub.
2. Crear los repositorios del frontend y la API en Amazon ECR.
3. Construir y publicar las imágenes Docker.
4. Crear una VPC con subredes públicas y privadas.
5. Crear PostgreSQL en Amazon RDS y restringir su acceso al servicio de la API.
6. Crear un sistema de archivos EFS y montar las rutas `/app/uploads` y `/app/reports`.
7. Registrar en Secrets Manager las variables `POSTGRES_*`, `JWT_SECRET_KEY` y
   `SMTP_*`.
8. Crear las definiciones de tareas y servicios de ECS Fargate.
9. Configurar el Application Load Balancer para dirigir `/api/v1/*` a FastAPI y el resto
   de las rutas al frontend.
10. Configurar `VITE_API_URL`, `CORS_ORIGINS` y `RPA_TARGET_URL` con las direcciones de
    producción.
11. Asociar el dominio de Route 53 y el certificado de Certificate Manager.
12. Configurar CloudWatch y comprobar OCR, RPA, reportes, correo y bitácora.

### 19.3 Variables principales de producción

```text
APP_ENV=production
APP_DEBUG=false
POSTGRES_HOST=<endpoint-privado-de-rds>
UPLOAD_DIRECTORY=/app/uploads
REPORT_DIRECTORY=/app/reports
RPA_OUTPUT_DIRECTORY=/app/reports/rpa
RPA_TARGET_URL=http://<servicio-api>:8000/api/v1/rpa-simulator/form
VITE_API_URL=https://<dominio>/api/v1
CORS_ORIGINS=https://<dominio>
SMTP_ENABLED=true
```

Los secretos reales no deben almacenarse en este archivo ni en GitHub. Deben inyectarse
en la tarea de ECS desde AWS Secrets Manager.

URL pública de producción:

```text
PENDIENTE_DE_CONFIGURAR
```

La URL debe reemplazarse después de completar el despliegue y verificarla desde una red
externa.

## 20. Bitácora y trazabilidad

Acciones principales:

- `invoice_upload`
- `invoice_ocr_processed`
- `invoice_ocr_error`
- `invoice_manually_validated`
- `invoice_rejected`
- `invoice_deleted`
- `provider_created`
- `provider_updated`
- `provider_deactivated`
- `report_generated`
- `report_emailed`
- `report_email_error`
- `rpa_invoice_registered`
- `rpa_invoice_error`

La bitácora permite filtrar por factura, usuario, acción, estado y rango de fechas.

## 21. Decisiones técnicas

### OCR local

Se eligió Tesseract para cumplir con la restricción de procesar las facturas localmente y no
delegar la extracción completa a un servicio generativo externo.

### PostgreSQL

Se eligió PostgreSQL por integridad referencial, transacciones, soporte asíncrono y
compatibilidad con Docker.

### Eliminación lógica

Usuarios, proveedores y facturas utilizan desactivación o eliminación lógica para conservar
trazabilidad.

### RPA con sistema simulado

Playwright interactúa con un formulario real servido por la API. Esto permite demostrar
navegación, llenado, envío y evidencia sin depender de un sistema empresarial externo.

### Correo automático con recuperación ante fallos

El reporte se almacena antes del envío. Si SMTP falla, el archivo no se pierde y el usuario
puede reenviarlo manualmente.

## 22. Limitaciones y mejoras futuras

- Implementar procesamiento masivo.
- Detectar facturas duplicadas.
- Ejecutar OCR y RPA mediante colas en segundo plano.
- Agregar programación automática de tareas.
- Incorporar almacenamiento de objetos en producción.
- Añadir recuperación de contraseña por correo.
- Implementar métricas y monitoreo centralizado.
- Agregar pruebas end-to-end del navegador.

## 23. Comandos útiles

```powershell
# Construir e iniciar
docker compose up -d --build

# Estado
docker compose ps

# Logs
docker compose logs -f api

# Pruebas
docker compose exec api python -m pytest -q

# Migraciones
docker compose exec api alembic upgrade head

# Reiniciar un servicio
docker compose restart api
docker compose restart frontend

# Detener
docker compose down
```

## 24. Conclusión

SmartInvoice implementa un flujo completo de automatización de facturas utilizando Python,
FastAPI, PostgreSQL, OpenCV, Tesseract OCR, Playwright, reportes y correo electrónico. La
arquitectura por capas separa las responsabilidades y permite mantener trazabilidad mediante
bitácoras, evidencias RPA y reportes administrativos.
