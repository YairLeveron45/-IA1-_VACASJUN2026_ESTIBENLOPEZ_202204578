import {
  ArrowUpRight,
  Bot,
  CheckCircle2,
  ChevronRight,
  Clock3,
  FileText,
  Mail,
  ScanLine,
  TrendingUp,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getInvoiceStats } from "../api/invoices";
import { listProcessingLogs } from "../api/processingLogs";
import { getHealth } from "../api/system";
import { useAuthStore } from "../store/authStore";

const actionLabels: Record<string, string> = {
  invoice_upload: "Factura cargada",
  invoice_ocr_processed: "OCR completado",
  invoice_manually_validated: "Factura validada",
  invoice_rejected: "Factura rechazada",
  provider_created: "Proveedor creado",
  user_created: "Usuario creado",
  report_generated: "Reporte generado",
  report_emailed: "Reporte enviado",
  invoice_deleted: "Factura eliminada",
  rpa_invoice_registered: "Registro RPA completado",
  rpa_invoice_error: "Error en automatización",
};

export function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const dashboardQuery = useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => {
      const [invoices, rpa, logs, health] =
        await Promise.all([
          getInvoiceStats(),
          listProcessingLogs(1, { action: "rpa_invoice_registered" }),
          listProcessingLogs(1),
          getHealth(),
        ]);
      return { invoices, rpa, logs, health };
    },
    refetchInterval: 60_000,
  });

  const data = dashboardQuery.data;
  const attention =
    (data?.invoices.pending ?? 0) + (data?.invoices.error ?? 0);
  const ocrBase =
    (data?.invoices.processed ?? 0) + (data?.invoices.error ?? 0);
  const ocrRate = ocrBase
    ? Math.round(((data?.invoices.processed ?? 0) / ocrBase) * 100)
    : 0;
  const metrics = [
    {
      label: "Facturas procesadas",
      value: data?.invoices.processed ?? 0,
      helper: `${data?.invoices.total ?? 0} documentos totales`,
      icon: FileText,
      tone: "indigo",
    },
    {
      label: "Pendientes de revisión",
      value: attention,
      helper: "Pendientes y con observaciones",
      icon: Clock3,
      tone: "amber",
    },
    {
      label: "Éxito de extracción",
      value: `${ocrRate}%`,
      helper: "Procesadas frente a observaciones",
      icon: ScanLine,
      tone: "green",
    },
    {
      label: "Automatizaciones",
      value: data?.rpa.total ?? 0,
      helper: "Registros RPA exitosos",
      icon: Bot,
      tone: "cyan",
    },
  ];

  const statusBars = [
    {
      label: "Procesadas",
      value: data?.invoices.processed ?? 0,
      tone: "processed",
    },
    {
      label: "Pendientes",
      value: data?.invoices.pending ?? 0,
      tone: "pending",
    },
    {
      label: "Observaciones",
      value: data?.invoices.error ?? 0,
      tone: "error",
    },
  ];
  const maxBar = Math.max(1, ...statusBars.map((item) => item.value));
  const nextStep =
    (data?.invoices.total ?? 0) === 0
      ? {
          title: "Carga tu primera factura",
          description:
            "Empieza con un PDF o una imagen. Después podrás ejecutar OCR.",
          to: "/invoices",
          action: "Ir a cargar factura",
          step: 1,
        }
      : (data?.invoices.pending ?? 0) > 0
        ? {
            title: "Procesa las facturas pendientes",
            description:
              "Ejecuta OCR para extraer número, fecha, proveedor, NIT y montos.",
            to: "/invoices",
            action: "Procesar pendientes",
            step: 2,
          }
        : (data?.invoices.error ?? 0) > 0
          ? {
              title: "Revisa los datos con observaciones",
              description:
                "Corrige los campos detectados y valida los totales.",
              to: "/invoices",
              action: "Revisar facturas",
              step: 2,
            }
          : (data?.invoices.processed ?? 0) > (data?.rpa.total ?? 0)
            ? {
                title: "Registra las facturas mediante RPA",
                description:
                  "El robot copiará los datos al sistema contable simulado.",
                to: "/rpa",
                action: "Ejecutar RPA",
                step: 3,
              }
            : {
                title: "Genera el reporte final",
                description:
                  "Consolida los resultados y envíalos automáticamente por correo.",
                to: "/reports",
                action: "Generar reporte",
                step: 4,
              };

  return (
    <div className="dashboard">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Resumen operativo</span>
          <h1>Buenos días, {user?.name?.split(" ")[0] ?? "Administrador"}.</h1>
          <p>Esta es la actividad actual de SmartInvoice.</p>
        </div>
        <Link className="secondary-button dashboard-link" to="/logs">
          Ver actividad <ArrowUpRight size={17} />
        </Link>
      </section>

      <section className="workflow-overview">
        <div className="workflow-overview__intro">
          <span className="eyebrow">Guía paso a paso</span>
          <h2>De una factura al reporte final</h2>
          <p>Sigue este orden. Cada resultado quedará registrado en la bitácora.</p>
        </div>
        <div className="workflow-overview__steps">
          {[
            ["1", "Cargar", "Sube PDF o imagen", FileText],
            ["2", "Procesar", "OCR y validación", ScanLine],
            ["3", "Registrar", "Automatización RPA", Bot],
            ["4", "Informar", "Reporte y correo", Mail],
            ["5", "Comprobar", "Revisa la bitácora", CheckCircle2],
          ].map(([number, title, description, Icon]) => (
            <div key={String(number)}>
              <span>{String(number)}</span>
              <Icon size={19} />
              <strong>{String(title)}</strong>
              <small>{String(description)}</small>
            </div>
          ))}
        </div>
      </section>

      <section className="next-step-card">
        <div className="next-step-card__number">{nextStep.step}</div>
        <div>
          <span>Siguiente acción recomendada</span>
          <h2>{nextStep.title}</h2>
          <p>{nextStep.description}</p>
        </div>
        <Link to={nextStep.to}>
          {nextStep.action} <ChevronRight size={17} />
        </Link>
      </section>

      <section className="metric-grid">
        {metrics.map(({ label, value, helper, icon: Icon, tone }) => (
          <article className="metric-card" key={label}>
            <div className={`metric-card__icon metric-card__icon--${tone}`}>
              <Icon size={21} />
            </div>
            <span>{label}</span>
            <strong>{dashboardQuery.isLoading ? "—" : value}</strong>
            <small>{helper}</small>
          </article>
        ))}
      </section>

      <section className="dashboard-grid">
        <article className="content-card content-card--wide">
          <div className="content-card__header">
            <div>
              <span className="eyebrow">Rendimiento</span>
              <h2>Estado de facturas</h2>
            </div>
            <span className="period-chip">Datos actuales</span>
          </div>
          <div className="status-chart">
            {statusBars.map((item) => (
              <div key={item.label}>
                <header>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </header>
                <div>
                  <i
                    className={`status-chart__bar status-chart__bar--${item.tone}`}
                    style={{ width: `${(item.value / maxBar) * 100}%` }}
                  />
                </div>
              </div>
            ))}
            {data?.invoices.total === 0 && (
              <div className="dashboard-empty">
                <TrendingUp size={24} />
                Carga facturas para comenzar a visualizar el rendimiento.
              </div>
            )}
          </div>
        </article>

        <article className="content-card">
          <div className="content-card__header">
            <div>
              <span className="eyebrow">Actividad</span>
              <h2>Eventos recientes</h2>
            </div>
          </div>
          <div className="dashboard-activity">
            {data?.logs.items.slice(0, 5).map((log) => (
              <div key={log.id}>
                <span
                  className={
                    log.status === "error"
                      ? "activity-dot activity-dot--error"
                      : "activity-dot"
                  }
                />
                <div>
                  <strong>{actionLabels[log.action] ?? log.action}</strong>
                  <small>{log.result || "Evento registrado"}</small>
                </div>
                <time>
                  {new Intl.DateTimeFormat("es-GT", {
                    hour: "2-digit",
                    minute: "2-digit",
                  }).format(new Date(log.created_at))}
                </time>
              </div>
            ))}
            {!data?.logs.items.length && (
              <div className="dashboard-empty">Aún no hay actividad registrada.</div>
            )}
          </div>
        </article>
      </section>
    </div>
  );
}
