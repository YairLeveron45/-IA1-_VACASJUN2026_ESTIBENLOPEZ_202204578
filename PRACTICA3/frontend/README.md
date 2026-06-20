# Frontend de SmartInvoice

Aplicación React + Vite + TypeScript.

## Ejecución local

```powershell
npm install
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`.

También puede iniciarse desde la raíz del proyecto:

```powershell
docker compose up -d --build
```

## Estado actual

- Login conectado con FastAPI.
- Sesión JWT persistente.
- Cliente Axios con token automático.
- Manejo global de respuestas 401.
- Rutas privadas.
- Rutas administrativas por rol.
- Layout responsivo.
- Dashboard inicial.
- Navegación preparada para todos los módulos.
