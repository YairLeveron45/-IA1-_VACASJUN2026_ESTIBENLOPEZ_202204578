import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock3,
  Eye,
  Filter,
  Search,
  XCircle,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import {
  getProcessingLog,
  listProcessingLogs,
} from "../api/processingLogs";
import { Modal } from "../components/Modal";
import type {
  ProcessingLog,
  ProcessingLogFilters,
} from "../types/processingLog";

const actionLabels: Record<string, string> = {
  invoice_upload: "Factura cargada",
  invoice_ocr_processed: "OCR procesado",
  invoice_ocr_error: "Error de OCR",
  invoice_manually_validated: "Factura validada",
  invoice_rejected: "Factura rechazada",
  provider_created: "Proveedor creado",
  provider_updated: "Proveedor actualizado",
  provider_deactivated: "Proveedor desactivado",
  user_created: "Usuario creado",
  user_updated: "Usuario actualizado",
  user_deactivated: "Usuario desactivado",
  user_password_reset: "Contraseña restablecida",
  report_generated: "Reporte generado",
  report_emailed: "Reporte enviado",
  report_email_error: "Error al enviar reporte",
  invoice_deleted: "Factura eliminada",
  rpa_invoice_registered: "Automatización ejecutada",
  rpa_invoice_error: "Error de automatización",
};

const actionGroups = [
  {
    label: "Facturas",
    actions: [
      "invoice_upload",
      "invoice_ocr_processed",
      "invoice_ocr_error",
      "invoice_manually_validated",
      "invoice_rejected",
    ],
  },
  {
    label: "Proveedores y usuarios",
    actions: [
      "provider_created",
      "provider_updated",
      "provider_deactivated",
      "user_created",
      "user_updated",
      "user_deactivated",
      "user_password_reset",
    ],
  },
  {
    label: "Reportes y RPA",
    actions: [
      "report_generated",
      "report_emailed",
      "report_email_error",
      "invoice_deleted",
      "rpa_invoice_registered",
      "rpa_invoice_error",
    ],
  },
];

export function ProcessingLogsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [filters, setFilters] = useState<ProcessingLogFilters>({});
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const logsQuery = useQuery({
    queryKey: ["processing-logs", page, filters],
    queryFn: () => listProcessingLogs(page, filters),
  });
  const detailQuery = useQuery({
    queryKey: ["processing-log", selectedId],
    queryFn: () => getProcessingLog(selectedId!),
    enabled: selectedId !== null,
  });

  const shown = useMemo(() => {
    const term = search.trim().toLowerCase();
    const items = logsQuery.data?.items ?? [];
    if (!term) return items;
    return items.filter((log) =>
      [
        String(log.id),
        actionLabels[log.action] ?? log.action,
        log.action,
        log.status,
        log.result,
        log.error_detail,
      ]
        .filter(Boolean)
        .some((value) => value?.toLowerCase().includes(term)),
    );
  }, [logsQuery.data?.items, search]);

  const totalPages = Math.max(
    1,
    Math.ceil((logsQuery.data?.total ?? 0) / 20),
  );
  const activeFilterCount = Object.values(filters).filter(Boolean).length;

  return (
    <div className="management-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Auditoría</span>
          <h1>Bitácora de procesamiento</h1>
          <p>Consulta las acciones, resultados y errores registrados por el sistema.</p>
        </div>
        <button
          className="ghost-button page-filter-button"
          onClick={() => setFiltersOpen(true)}
        >
          <Filter size={17} />
          Filtros
          {activeFilterCount > 0 && <span>{activeFilterCount}</span>}
        </button>
      </section>

      <section className="log-summary-grid">
        <LogSummary
          icon={<Activity size={19} />}
          value={logsQuery.data?.total ?? 0}
          label="Eventos registrados"
          tone="primary"
        />
        <LogSummary
          icon={<CheckCircle2 size={19} />}
          value={
            logsQuery.data?.items.filter((log) =>
              ["success", "processed"].includes(log.status),
            ).length ?? 0
          }
          label="Exitosos en página"
          tone="success"
        />
        <LogSummary
          icon={<AlertTriangle size={19} />}
          value={
            logsQuery.data?.items.filter((log) =>
              ["error", "rejected"].includes(log.status),
            ).length ?? 0
          }
          label="Con incidencias"
          tone="danger"
        />
      </section>

      <section className="management-card">
        <div className="management-toolbar">
          <div className="search-box">
            <Search size={17} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Buscar acción, estado o resultado"
            />
          </div>
          <div className="management-summary">
            <Activity size={17} />
            <span>
              <strong>{logsQuery.data?.total ?? 0}</strong> eventos
            </span>
          </div>
        </div>

        {logsQuery.isLoading ? (
          <Skeleton />
        ) : logsQuery.isError ? (
          <div className="empty-state">
            <XCircle size={30} />
            <strong>No fue posible cargar la bitácora</strong>
            <button onClick={() => logsQuery.refetch()}>Intentar de nuevo</button>
          </div>
        ) : shown.length === 0 ? (
          <div className="empty-state">
            <Activity size={30} />
            <strong>No hay eventos que coincidan</strong>
            <span>Prueba con otros filtros o términos de búsqueda.</span>
          </div>
        ) : (
          <div className="table-scroll">
            <table className="data-table log-table">
              <thead>
                <tr>
                  <th>Evento</th>
                  <th>Resultado</th>
                  <th>Referencia</th>
                  <th>Estado</th>
                  <th>Fecha y hora</th>
                  <th aria-label="Acciones" />
                </tr>
              </thead>
              <tbody>
                {shown.map((log) => (
                  <tr key={log.id}>
                    <td>
                      <div className="log-event">
                        <LogIcon status={log.status} />
                        <div>
                          <strong>{actionLabels[log.action] ?? log.action}</strong>
                          <span>{log.action}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <p className="log-result">{log.result || "Sin resultado"}</p>
                    </td>
                    <td>
                      <div className="log-references">
                        {log.invoice_id && <span>Factura #{log.invoice_id}</span>}
                        {log.user_id && <span>Usuario #{log.user_id}</span>}
                        {!log.invoice_id && !log.user_id && <span>Sistema</span>}
                      </div>
                    </td>
                    <td>
                      <span className={`log-status log-status--${statusTone(log.status)}`}>
                        {statusLabel(log.status)}
                      </span>
                    </td>
                    <td className="table-muted">
                      {formatDateTime(log.created_at)}
                    </td>
                    <td>
                      <div className="table-actions">
                        <button
                          title="Ver detalle del evento"
                          onClick={() => setSelectedId(log.id)}
                        >
                          <Eye size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <footer className="pagination">
          <span>Página {page} de {totalPages}</span>
          <div>
            <button
              disabled={page === 1}
              onClick={() => setPage((value) => value - 1)}
              aria-label="Página anterior"
            >
              <ChevronLeft size={17} />
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((value) => value + 1)}
              aria-label="Página siguiente"
            >
              <ChevronRight size={17} />
            </button>
          </div>
        </footer>
      </section>

      {filtersOpen && (
        <FiltersModal
          filters={filters}
          onClose={() => setFiltersOpen(false)}
          onApply={(nextFilters) => {
            setFilters(nextFilters);
            setPage(1);
            setFiltersOpen(false);
          }}
        />
      )}

      {selectedId !== null && (
        <LogDetailModal
          log={detailQuery.data}
          loading={detailQuery.isLoading}
          onClose={() => setSelectedId(null)}
        />
      )}
    </div>
  );
}

function FiltersModal({
  filters,
  onClose,
  onApply,
}: {
  filters: ProcessingLogFilters;
  onClose: () => void;
  onApply: (filters: ProcessingLogFilters) => void;
}) {
  const [form, setForm] = useState({
    invoice_id: filters.invoice_id?.toString() ?? "",
    user_id: filters.user_id?.toString() ?? "",
    action: filters.action ?? "",
    status: filters.status ?? "",
    date_from: filters.date_from?.slice(0, 10) ?? "",
    date_to: filters.date_to?.slice(0, 10) ?? "",
  });
  const [error, setError] = useState("");

  const submit = () => {
    if (form.date_from && form.date_to && form.date_from > form.date_to) {
      setError("La fecha inicial no puede ser posterior a la fecha final.");
      return;
    }
    onApply({
      invoice_id: form.invoice_id ? Number(form.invoice_id) : undefined,
      user_id: form.user_id ? Number(form.user_id) : undefined,
      action: form.action || undefined,
      status: form.status || undefined,
      date_from: form.date_from
        ? new Date(`${form.date_from}T00:00:00`).toISOString()
        : undefined,
      date_to: form.date_to
        ? new Date(`${form.date_to}T23:59:59`).toISOString()
        : undefined,
    });
  };

  return (
    <Modal
      title="Filtrar bitácora"
      description="Combina criterios para localizar eventos específicos."
      onClose={onClose}
    >
      <div className="entity-form">
        <div className="form-grid">
          <label>
            Acción
            <select
              value={form.action}
              onChange={(event) =>
                setForm((current) => ({ ...current, action: event.target.value }))
              }
            >
              <option value="">Todas las acciones</option>
              {actionGroups.map((group) => (
                <optgroup key={group.label} label={group.label}>
                  {group.actions.map((action) => (
                    <option key={action} value={action}>
                      {actionLabels[action]}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </label>
          <label>
            Estado
            <select
              value={form.status}
              onChange={(event) =>
                setForm((current) => ({ ...current, status: event.target.value }))
              }
            >
              <option value="">Todos los estados</option>
              <option value="success">Exitoso</option>
              <option value="pending">Pendiente</option>
              <option value="processed">Procesado</option>
              <option value="error">Error</option>
              <option value="rejected">Rechazado</option>
            </select>
          </label>
          <label>
            ID de factura
            <input
              type="number"
              min="1"
              value={form.invoice_id}
              onChange={(event) =>
                setForm((current) => ({ ...current, invoice_id: event.target.value }))
              }
            />
          </label>
          <label>
            ID de usuario
            <input
              type="number"
              min="1"
              value={form.user_id}
              onChange={(event) =>
                setForm((current) => ({ ...current, user_id: event.target.value }))
              }
            />
          </label>
          <label>
            Fecha inicial
            <input
              type="date"
              value={form.date_from}
              onChange={(event) =>
                setForm((current) => ({ ...current, date_from: event.target.value }))
              }
            />
          </label>
          <label>
            Fecha final
            <input
              type="date"
              value={form.date_to}
              onChange={(event) =>
                setForm((current) => ({ ...current, date_to: event.target.value }))
              }
            />
          </label>
        </div>
        {error && <div className="form-error">{error}</div>}
        <div className="modal-actions">
          <button
            className="ghost-button"
            onClick={() =>
              onApply({})
            }
          >
            Limpiar filtros
          </button>
          <button className="primary-button modal-primary" onClick={submit}>
            Aplicar filtros
          </button>
        </div>
      </div>
    </Modal>
  );
}

function LogDetailModal({
  log,
  loading,
  onClose,
}: {
  log?: ProcessingLog;
  loading: boolean;
  onClose: () => void;
}) {
  return (
    <Modal
      title="Detalle del evento"
      description="Información técnica registrada para auditoría."
      onClose={onClose}
    >
      {loading || !log ? (
        <div className="modal-loading">Cargando evento...</div>
      ) : (
        <div className="log-detail">
          <div className="log-detail__heading">
            <LogIcon status={log.status} />
            <div>
              <strong>{actionLabels[log.action] ?? log.action}</strong>
              <span>Evento #{log.id} · {formatDateTime(log.created_at)}</span>
            </div>
          </div>
          <div className="invoice-detail__grid">
            <Detail label="Acción técnica" value={log.action} />
            <Detail label="Estado" value={statusLabel(log.status)} />
            <Detail label="Factura" value={log.invoice_id ? `#${log.invoice_id}` : null} />
            <Detail label="Usuario" value={log.user_id ? `#${log.user_id}` : null} />
          </div>
          <section className="log-message">
            <span>Resultado</span>
            <p>{log.result || "No se registró un resultado."}</p>
          </section>
          {log.error_detail && (
            <section className="log-message log-message--error">
              <span>Detalle del error</span>
              <pre>{log.error_detail}</pre>
            </section>
          )}
        </div>
      )}
    </Modal>
  );
}

function Detail({ label, value }: { label: string; value: string | null }) {
  return <div><span>{label}</span><strong>{value || "No aplica"}</strong></div>;
}

function LogSummary({
  icon,
  value,
  label,
  tone,
}: {
  icon: React.ReactNode;
  value: number;
  label: string;
  tone: "primary" | "success" | "danger";
}) {
  return (
    <div className={`invoice-metric log-summary--${tone}`}>
      <span>{icon}</span>
      <div><strong>{value}</strong><small>{label}</small></div>
    </div>
  );
}

function LogIcon({ status }: { status: string }) {
  const tone = statusTone(status);
  return (
    <div className={`log-icon log-icon--${tone}`}>
      {tone === "success" ? (
        <CheckCircle2 size={17} />
      ) : tone === "danger" ? (
        <AlertTriangle size={17} />
      ) : (
        <Clock3 size={17} />
      )}
    </div>
  );
}

function statusTone(status: string): "success" | "danger" | "pending" {
  if (["success", "processed"].includes(status)) return "success";
  if (["error", "rejected"].includes(status)) return "danger";
  return "pending";
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    success: "Exitoso",
    processed: "Procesado",
    pending: "Pendiente",
    error: "Error",
    rejected: "Rechazado",
  };
  return labels[status] ?? status;
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("es-GT", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function Skeleton() {
  return (
    <div className="table-skeleton">
      {Array.from({ length: 5 }).map((_, index) => (
        <div key={index}><i /><i /><i /><i /></div>
      ))}
    </div>
  );
}
