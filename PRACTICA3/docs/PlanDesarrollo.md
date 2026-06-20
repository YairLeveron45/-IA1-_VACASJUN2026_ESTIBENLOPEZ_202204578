# Plan de desarrollo - Práctica 3: SmartInvoice

## 1. Objetivo general

Desarrollar una plataforma web llamada **SmartInvoice** que permita cargar facturas en
formato PDF o imagen, procesarlas localmente mediante Computer Vision y OCR, validar y
almacenar la información extraída, generar reportes y ejecutar automatizaciones RPA.

El sistema deberá ejecutarse mediante Docker Compose, estar desplegado en la nube y contar
con una URL pública para su evaluación.

## 2. Tecnologías recomendadas

| Componente | Tecnología |
|---|---|
| Backend y API REST | Python 3.11 y FastAPI |
| Frontend | Jinja2, HTML, CSS, Bootstrap y JavaScript |
| Base de datos | PostgreSQL |
| ORM | SQLAlchemy |
| Migraciones | Alembic |
| Computer Vision | OpenCV |
| OCR | Tesseract OCR |
| Procesamiento de PDF | PyMuPDF |
| Automatización RPA | Playwright |
| Reportes | CSV y PDF |
| Correo electrónico | SMTP |
| Autenticación | JWT o sesiones |
| Contenedores | Docker y Docker Compose |
| Control de versiones | Git y GitHub |

## 3. Arquitectura propuesta

Se utilizará inicialmente un **monolito modular**, porque permite implementar y desplegar
los requisitos obligatorios con menor complejidad.

```text
Usuario
   |
   v
Frontend web
   |
   v
FastAPI / API REST
   |
   +---- Autenticación
   +---- Proveedores
   +---- Facturas
   +---- OCR y Computer Vision
   +---- Validaciones
   +---- Reportes
   +---- RPA
   +---- Correos
   +---- Bitácora
   |
   v
PostgreSQL
```

## 4. Estructura inicial del proyecto

```text
PRACTICA3/
|-- app/
|   |-- api/
|   |-- core/
|   |-- db/
|   |-- models/
|   |-- schemas/
|   |-- services/
|   |   |-- ocr/
|   |   |-- reports/
|   |   |-- rpa/
|   |   `-- email/
|   |-- static/
|   |-- templates/
|   `-- main.py
|-- uploads/
|-- tests/
|-- docs/
|-- scripts/
|-- .env.example
|-- .gitignore
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
`-- README.md
```

## 5. Fases de desarrollo

### Fase 1: Preparación del proyecto

- [ ] Crear la estructura de carpetas.
- [ ] Crear el entorno virtual de Python.
- [ ] Crear `requirements.txt`.
- [ ] Crear `.gitignore`.
- [ ] Crear `.env.example` sin credenciales reales.
- [ ] Crear la aplicación mínima de FastAPI.
- [ ] Agregar un endpoint de prueba o salud: `GET /health`.
- [ ] Crear el `Dockerfile`.
- [ ] Crear `docker-compose.yml` con la aplicación y PostgreSQL.
- [ ] Verificar que el proyecto se levante con `docker compose up`.
- [ ] Crear el primer commit exclusivo de la Práctica 3.

**Criterio de finalización:** FastAPI y PostgreSQL se ejecutan correctamente mediante
Docker Compose, y `GET /health` devuelve una respuesta exitosa.

### Fase 2: Diseño e implementación de la base de datos

Crear como mínimo las siguientes entidades:

#### Usuarios

- Identificador.
- Nombre.
- Correo electrónico.
- Contraseña cifrada.
- Rol.
- Estado.
- Fecha de creación.

#### Proveedores

- Identificador.
- Nombre.
- NIT.
- Correo electrónico.
- Teléfono.
- Dirección.
- Fecha de creación.

#### Facturas

- Identificador.
- Número de factura.
- Fecha de factura.
- Proveedor.
- NIT detectado.
- Subtotal.
- Impuestos.
- Total.
- Ruta o nombre del archivo.
- Tipo de archivo.
- Texto completo obtenido por OCR.
- Estado: `Pendiente`, `Procesado`, `Error` o `Rechazado`.
- Usuario que realizó la carga.
- Fecha de creación y actualización.

#### Bitácora de procesamiento

- Identificador.
- Fecha y hora.
- Usuario responsable.
- Factura o documento procesado.
- Acción realizada.
- Estado del procesamiento.
- Resultado o mensaje.
- Detalle del error, si existe.

#### Reportes

- Identificador.
- Tipo de reporte.
- Formato.
- Ruta del archivo generado.
- Usuario que lo generó.
- Fecha de generación.

Tareas:

- [ ] Crear los modelos con SQLAlchemy.
- [ ] Configurar la conexión a PostgreSQL.
- [ ] Configurar Alembic.
- [ ] Crear y ejecutar la migración inicial.
- [ ] Verificar las relaciones entre las tablas.

**Criterio de finalización:** las tablas se crean mediante migraciones y la aplicación puede
registrar y consultar información.

### Fase 3: Autenticación y usuarios

- [ ] Crear un usuario administrador inicial.
- [ ] Implementar inicio de sesión.
- [ ] Cifrar las contraseñas.
- [ ] Implementar cierre de sesión.
- [ ] Proteger las rutas administrativas.
- [ ] Registrar en la bitácora los accesos importantes.

**Criterio de finalización:** un usuario válido puede iniciar sesión y acceder al panel; un
usuario no autenticado no puede acceder a las funciones protegidas.

### Fase 4: Administración de proveedores

- [ ] Crear proveedor.
- [ ] Listar proveedores.
- [ ] Consultar un proveedor.
- [ ] Editar proveedor.
- [ ] Eliminar o desactivar proveedor.
- [ ] Validar que el NIT no se repita cuando corresponda.
- [ ] Registrar las operaciones en la bitácora.

**Criterio de finalización:** el CRUD de proveedores funciona desde la API REST y desde la
interfaz web.

### Fase 5: Carga y almacenamiento de facturas

- [ ] Crear el formulario para cargar archivos.
- [ ] Aceptar únicamente PDF, JPG, JPEG y PNG.
- [ ] Establecer un tamaño máximo permitido.
- [ ] Generar nombres seguros y únicos para los archivos.
- [ ] Guardar los archivos en una ubicación controlada.
- [ ] Crear el registro de la factura con estado `Pendiente`.
- [ ] Mostrar la lista y el detalle de las facturas cargadas.
- [ ] Registrar la carga en la bitácora.

**Criterio de finalización:** el usuario puede cargar una factura válida, el archivo queda
almacenado y se crea su registro en la base de datos.

### Fase 6: Computer Vision y OCR

Implementar el siguiente flujo:

```text
Cargar archivo
    |
    v
Validar formato
    |
    v
Convertir PDF a imagen, si corresponde
    |
    v
Preprocesar con OpenCV
    |
    v
Ejecutar Tesseract OCR
    |
    v
Extraer campos
    |
    v
Validar resultados
    |
    v
Guardar información y actualizar estado
```

Tareas:

- [ ] Convertir las páginas de un PDF a imágenes.
- [ ] Corregir orientación o inclinación cuando sea necesario.
- [ ] Convertir imágenes a escala de grises.
- [ ] Aplicar reducción de ruido.
- [ ] Aplicar umbralización o mejora de contraste.
- [ ] Ejecutar Tesseract con idioma español.
- [ ] Guardar el texto completo extraído.
- [ ] Crear expresiones regulares y reglas para obtener:
  - [ ] Número de factura.
  - [ ] Fecha.
  - [ ] Nombre del proveedor.
  - [ ] NIT.
  - [ ] Subtotal.
  - [ ] Impuestos.
  - [ ] Total.
- [ ] Probar primero con un formato de factura.
- [ ] Ajustar las reglas para varios diseños de factura.
- [ ] Registrar duración, resultado y errores en la bitácora.

**Criterio de finalización:** el sistema procesa una factura desde su carga hasta la
extracción automática de los siete campos solicitados.

### Fase 7: Validación y corrección manual

- [ ] Verificar que los campos obligatorios estén presentes.
- [ ] Validar el formato de la fecha.
- [ ] Validar que los montos sean numéricos y no negativos.
- [ ] Comprobar que el total sea coherente con subtotal e impuestos.
- [ ] Comparar el proveedor o NIT con los proveedores registrados.
- [ ] Mostrar advertencias cuando exista información dudosa.
- [ ] Crear una pantalla para corregir manualmente los datos extraídos.
- [ ] Guardar los datos únicamente después de validarlos.
- [ ] Marcar la factura como `Procesado`, `Error` o `Rechazado`.

**Criterio de finalización:** los resultados del OCR se validan antes del almacenamiento
definitivo y el usuario puede corregir los datos incorrectos.

### Fase 8: Interfaz web administrativa

Crear como mínimo las siguientes pantallas:

- [ ] Inicio de sesión.
- [ ] Dashboard o página principal.
- [ ] Carga de facturas.
- [ ] Resultado del procesamiento OCR.
- [ ] Corrección y confirmación de datos.
- [ ] Lista y detalle de facturas.
- [ ] CRUD de proveedores.
- [ ] Consulta de la bitácora.
- [ ] Generación y descarga de reportes.
- [ ] Estado de las automatizaciones.

**Criterio de finalización:** todas las funciones obligatorias pueden utilizarse desde un
navegador sin depender directamente de Swagger o de un cliente de API.

### Fase 9: API REST

Endpoints mínimos sugeridos:

```text
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/providers
POST   /api/providers
GET    /api/providers/{id}
PUT    /api/providers/{id}
DELETE /api/providers/{id}
GET    /api/invoices
POST   /api/invoices/upload
GET    /api/invoices/{id}
POST   /api/invoices/{id}/process
PUT    /api/invoices/{id}/validate
GET    /api/logs
POST   /api/reports
GET    /api/reports/{id}/download
POST   /api/rpa/invoices/{id}/execute
POST   /api/reports/{id}/email
```

- [ ] Crear esquemas de entrada y salida.
- [ ] Agregar validaciones.
- [ ] Utilizar códigos HTTP apropiados.
- [ ] Manejar errores de forma uniforme.
- [ ] Documentar los endpoints mediante OpenAPI/Swagger.

**Criterio de finalización:** la API permite administrar los componentes principales y
cuenta con documentación accesible.

### Fase 10: Reportes administrativos

- [ ] Definir filtros por fecha, proveedor y estado.
- [ ] Generar un reporte CSV o Excel.
- [ ] Generar un reporte PDF.
- [ ] Incluir totales y cantidad de facturas.
- [ ] Guardar el registro del reporte generado.
- [ ] Permitir su descarga desde la interfaz.

**Criterio de finalización:** el usuario puede generar y descargar al menos un reporte
administrativo usando la información almacenada.

### Fase 11: Automatización RPA

Se recomienda crear un formulario web simulado dentro del proyecto y utilizar Playwright
para registrar automáticamente los datos de una factura.

- [ ] Crear el formulario o sistema simulado.
- [ ] Crear el script de automatización con Playwright.
- [ ] Iniciar sesión en el sistema simulado, si corresponde.
- [ ] Completar los campos usando los datos de una factura procesada.
- [ ] Enviar el formulario.
- [ ] Capturar el resultado de la automatización.
- [ ] Guardar el resultado en la bitácora.
- [ ] Manejar errores y tiempos de espera.

**Criterio de finalización:** desde SmartInvoice se puede ejecutar una automatización que
registre los datos extraídos en un formulario web y deje evidencia de su resultado.

### Fase 12: Envío de reportes por correo

- [ ] Configurar SMTP mediante variables de entorno.
- [ ] Crear una plantilla para el correo.
- [ ] Adjuntar el reporte generado.
- [ ] Permitir indicar o seleccionar el destinatario.
- [ ] Registrar el envío exitoso o fallido en la bitácora.
- [ ] Evitar almacenar contraseñas reales en Git.

**Criterio de finalización:** el sistema puede enviar un reporte generado a una dirección de
correo y registrar el resultado.

### Fase 13: Docker y despliegue

- [ ] Instalar las dependencias de Tesseract dentro del contenedor.
- [ ] Configurar volúmenes para archivos y datos persistentes.
- [ ] Configurar variables de entorno.
- [ ] Agregar verificaciones de salud.
- [ ] Ejecutar todo el proyecto con Docker Compose.
- [ ] Seleccionar un proveedor de nube.
- [ ] Configurar la base de datos en producción.
- [ ] Desplegar la aplicación.
- [ ] Publicar una URL accesible.
- [ ] Verificar carga, OCR, reportes, RPA y correo en producción.

**Criterio de finalización:** el sistema funciona mediante Docker Compose y está disponible
desde una URL pública.

### Fase 14: Pruebas

- [ ] Reunir al menos 20 facturas de prueba.
- [ ] Incluir distintos formatos y calidades de imagen.
- [ ] Probar PDF, JPG, JPEG y PNG.
- [ ] Probar archivos inválidos.
- [ ] Probar errores del OCR.
- [ ] Probar facturas con campos faltantes.
- [ ] Probar autenticación y permisos.
- [ ] Probar CRUD de proveedores.
- [ ] Probar generación y envío de reportes.
- [ ] Probar la automatización RPA.
- [ ] Probar la ejecución completa mediante Docker Compose.
- [ ] Registrar los resultados y limitaciones conocidas.

**Criterio de finalización:** se procesan correctamente al menos 20 facturas de prueba y se
han documentado los casos que requieren corrección manual.

### Fase 15: Documentación y entrega

- [ ] Completar el `README.md`.
- [ ] Documentar instalación y ejecución.
- [ ] Documentar variables de entorno.
- [ ] Documentar ejecución con Docker Compose.
- [ ] Crear el modelo o diagrama de la base de datos.
- [ ] Crear el diagrama de arquitectura.
- [ ] Documentar la API REST.
- [ ] Documentar el proceso de Computer Vision y OCR.
- [ ] Documentar la automatización RPA.
- [ ] Documentar la generación y envío de reportes.
- [ ] Escribir los requerimientos funcionales.
- [ ] Escribir los requerimientos no funcionales.
- [ ] Documentar el despliegue y la URL pública.
- [ ] Agregar posibles mejoras futuras.
- [ ] Revisar que el repositorio no contenga credenciales.
- [ ] Verificar que el historial de Git muestre avances progresivos.

## 6. Primer MVP

Antes de agregar reportes, correo o RPA, se deberá completar este flujo:

```text
Iniciar sesión
    -> cargar una factura
    -> almacenar el archivo
    -> ejecutar OCR
    -> extraer los siete campos
    -> validar o corregir los datos
    -> guardar la factura
    -> consultar su detalle
    -> revisar la bitácora
```

Este flujo representa el núcleo de SmartInvoice y debe desarrollarse antes de trabajar en
funciones opcionales o detalles visuales.

## 7. Orden de prioridad

### Prioridad alta: requisitos obligatorios

1. Docker Compose, FastAPI y PostgreSQL.
2. Base de datos.
3. Autenticación.
4. CRUD de proveedores.
5. Carga de facturas.
6. Computer Vision y OCR.
7. Extracción y validación de campos.
8. Gestión de facturas.
9. Bitácora.
10. Interfaz web.
11. Reportes.
12. Automatización RPA.
13. Envío de correo.
14. Despliegue público.
15. Documentación y pruebas con 20 facturas.

### Prioridad baja: funciones opcionales

Estas funciones deben implementarse únicamente después de completar y probar todos los
requisitos obligatorios:

- Dashboard con métricas.
- Clasificación automática.
- Procesamiento masivo.
- Detección de duplicados.
- Gráficas.
- Tareas programadas.
- Integraciones externas.
- Colas de procesamiento.

## 8. Plan sugerido por bloques de trabajo

### Bloque 1: Base funcional

- Preparar el proyecto.
- Configurar Docker Compose.
- Configurar PostgreSQL.
- Crear modelos y migraciones.
- Implementar autenticación.

### Bloque 2: Administración

- Implementar CRUD de proveedores.
- Implementar carga de archivos.
- Crear gestión básica de facturas.
- Implementar la bitácora.

### Bloque 3: Inteligencia del sistema

- Implementar preprocesamiento con OpenCV.
- Implementar OCR con Tesseract.
- Extraer los siete campos.
- Validar y permitir correcciones manuales.

### Bloque 4: Automatizaciones

- Generar reportes.
- Implementar RPA.
- Implementar envío de correo.

### Bloque 5: Finalización

- Completar la interfaz.
- Ejecutar pruebas con 20 facturas.
- Corregir errores.
- Desplegar en la nube.
- Completar la documentación.
- Preparar la demostración presencial.

## 9. Demostración final esperada

Durante la evaluación se deberá poder demostrar, sin pasos manuales ocultos:

1. Inicio de sesión.
2. Carga de una factura.
3. Preprocesamiento de la imagen.
4. Ejecución del OCR.
5. Extracción de los campos solicitados.
6. Validación o corrección de la información.
7. Almacenamiento en la base de datos.
8. Consulta de la factura.
9. Consulta de la bitácora.
10. Generación de un reporte.
11. Ejecución de la automatización RPA.
12. Envío del reporte por correo.

## 10. Primera meta de implementación

La primera meta concreta será:

> Levantar FastAPI y PostgreSQL mediante Docker Compose, permitir la carga de una factura
> y almacenarla en la base de datos con estado `Pendiente`.

Cuando esta meta funcione de principio a fin, se continuará con el módulo de Computer
Vision y OCR.
