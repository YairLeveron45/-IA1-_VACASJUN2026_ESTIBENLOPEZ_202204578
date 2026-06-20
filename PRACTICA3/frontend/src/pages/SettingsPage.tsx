import {
  Bot,
  CheckCircle2,
  Clock3,
  Database,
  FileUp,
  KeyRound,
  Mail,
  RefreshCw,
  ScanLine,
  Server,
  ShieldCheck,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { getHealth, getSystemSettings } from "../api/system";

export function SettingsPage() {
  const settingsQuery = useQuery({
    queryKey: ["system-settings"],
    queryFn: getSystemSettings,
  });
  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 30_000,
  });
  const settings = settingsQuery.data;

  return (
    <div className="management-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Sistema</span>
          <h1>Configuración</h1>
          <p>Consulta los parámetros operativos seguros de la plataforma.</p>
        </div>
        <button
          className="ghost-button page-filter-button"
          onClick={() => {
            settingsQuery.refetch();
            healthQuery.refetch();
          }}
        >
          <RefreshCw size={16} /> Actualizar
        </button>
      </section>

      <section className="settings-health">
        <div>
          <span className="settings-health__icon">
            <Server size={23} />
          </span>
          <div>
            <small>Estado de la plataforma</small>
            <h2>
              {healthQuery.data?.status === "ok"
                ? "Todos los servicios están operativos"
                : "Comprobando servicios"}
            </h2>
            <p>
              {healthQuery.data?.application ?? "SmartInvoice API"} ·{" "}
              {healthQuery.data?.environment ?? settings?.environment}
            </p>
          </div>
        </div>
        <span className="settings-health__badge">
          <CheckCircle2 size={15} /> En línea
        </span>
      </section>

      {settingsQuery.isError ? (
        <div className="inline-alert inline-alert--error">
          No fue posible cargar la configuración.
          <button onClick={() => settingsQuery.refetch()}>Reintentar</button>
        </div>
      ) : (
        <section className="settings-grid">
          <SettingsCard
            icon={<FileUp size={20} />}
            title="Carga de documentos"
            description="Restricciones aplicadas a las facturas."
            rows={[
              ["Tamaño máximo", `${settings?.max_upload_size_mb ?? "—"} MB`],
              [
                "Formatos permitidos",
                settings?.allowed_invoice_formats.join(", ") ?? "—",
              ],
              ["Ruta API", settings?.api_prefix ?? "—"],
            ]}
          />
          <SettingsCard
            icon={<ScanLine size={20} />}
            title="Reconocimiento OCR"
            description="Motor utilizado para extraer datos."
            rows={[
              ["Motor", "Tesseract OCR"],
              ["Idioma", settings?.tesseract_language.toUpperCase() ?? "—"],
              ["Validación manual", "Habilitada"],
            ]}
          />
          <SettingsCard
            icon={<Mail size={20} />}
            title="Correo y reportes"
            description="Canal actual para entregar reportes."
            rows={[
              [
                "Modo de entrega",
                settings?.smtp_delivery_mode === "smtp"
                  ? "Servidor SMTP"
                  : "Bandeja local",
              ],
              ["Remitente", settings?.smtp_from_email ?? "—"],
              ["Formatos", "CSV y PDF"],
            ]}
          />
          <SettingsCard
            icon={<Bot size={20} />}
            title="Automatización RPA"
            description="Registro en el sistema contable simulado."
            rows={[
              ["Estado", settings?.rpa_enabled ? "Habilitada" : "Deshabilitada"],
              ["Navegador", "Chromium / Playwright"],
              ["Evidencia", "JSON y captura PNG"],
            ]}
          />
          <SettingsCard
            icon={<ShieldCheck size={20} />}
            title="Seguridad"
            description="Autenticación y control de acceso."
            rows={[
              ["Autenticación", "JWT Bearer"],
              [
                "Duración de sesión",
                `${settings?.access_token_expire_minutes ?? "—"} minutos`,
              ],
              ["Roles", "Administrador y operador"],
            ]}
          />
          <SettingsCard
            icon={<Database size={20} />}
            title="Infraestructura"
            description="Servicios principales de persistencia."
            rows={[
              ["Base de datos", settings?.database_engine ?? "PostgreSQL"],
              ["Entorno", settings?.environment ?? "—"],
              ["Modo debug", settings?.debug ? "Activo" : "Desactivado"],
            ]}
          />
        </section>
      )}

      <section className="settings-note">
        <KeyRound size={19} />
        <div>
          <strong>Configuración protegida</strong>
          <p>
            Las contraseñas, llaves JWT y credenciales SMTP nunca se envían al
            frontend. Los cambios sensibles se administran mediante variables
            de entorno y requieren reiniciar la API.
          </p>
        </div>
        <Clock3 size={18} />
      </section>
    </div>
  );
}

function SettingsCard({
  icon,
  title,
  description,
  rows,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  rows: string[][];
}) {
  return (
    <article className="settings-card">
      <header>
        <span>{icon}</span>
        <div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
      </header>
      <dl>
        {rows.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </article>
  );
}
