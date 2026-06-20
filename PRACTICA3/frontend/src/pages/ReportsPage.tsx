import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Download,
  FileBarChart,
  FileSpreadsheet,
  Mail,
  Plus,
  Search,
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useMemo, useState } from "react";
import { listProviders } from "../api/providers";
import {
  downloadReport,
  emailReport,
  generateReport,
  listReports,
} from "../api/reports";
import { Modal } from "../components/Modal";
import type { InvoiceStatus } from "../types/invoice";
import type {
  Report,
  ReportCreatePayload,
  ReportEmailPayload,
  ReportFormat,
} from "../types/report";
import { getApiErrorMessage } from "../utils/apiError";

export function ReportsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [generateOpen, setGenerateOpen] = useState(false);
  const [emailTarget, setEmailTarget] = useState<Report | null>(null);
  const [feedback, setFeedback] = useState<{
    tone: "success" | "error";
    message: string;
  } | null>(null);
  const queryClient = useQueryClient();

  const reportsQuery = useQuery({
    queryKey: ["reports", page],
    queryFn: () => listReports(page),
  });

  const shown = useMemo(() => {
    const items = reportsQuery.data?.items ?? [];
    const term = search.trim().toLowerCase();
    if (!term) return items;
    return items.filter((report) =>
      [`reporte ${report.id}`, report.file_format, report.report_type].some(
        (value) => value.toLowerCase().includes(term),
      ),
    );
  }, [reportsQuery.data?.items, search]);

  const refresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ["reports"] });
  };

  const download = async (report: Report) => {
    try {
      await downloadReport(report);
    } catch (error) {
      setFeedback({ tone: "error", message: getApiErrorMessage(error) });
    }
  };

  const totalPages = Math.max(
    1,
    Math.ceil((reportsQuery.data?.total ?? 0) / 20),
  );

  return (
    <div className="management-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Analítica</span>
          <h1>Reportes administrativos</h1>
          <p>Genera, descarga y comparte reportes consolidados de facturas.</p>
        </div>
        <button
          className="primary-button page-action"
          onClick={() => setGenerateOpen(true)}
        >
          <Plus size={18} /> Generar reporte
        </button>
      </section>

      {feedback && (
        <div className={`inline-alert inline-alert--${feedback.tone}`}>
          {feedback.message}
          <button onClick={() => setFeedback(null)}>Cerrar</button>
        </div>
      )}

      <section className="report-summary-grid">
        <Summary
          icon={<FileBarChart size={19} />}
          value={reportsQuery.data?.total ?? 0}
          label="Reportes generados"
        />
        <Summary
          icon={<FileSpreadsheet size={19} />}
          value={
            reportsQuery.data?.items.filter(
              (report) => report.file_format === "csv",
            ).length ?? 0
          }
          label="Archivos CSV en página"
        />
        <Summary
          icon={<CalendarDays size={19} />}
          value={
            reportsQuery.data?.items.filter(
              (report) =>
                new Date(report.created_at).toDateString() ===
                new Date().toDateString(),
            ).length ?? 0
          }
          label="Generados hoy"
        />
      </section>

      <section className="management-card">
        <div className="management-toolbar">
          <div className="search-box">
            <Search size={17} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Buscar por número o formato"
            />
          </div>
          <div className="management-summary">
            <FileBarChart size={17} />
            <span>
              <strong>{reportsQuery.data?.total ?? 0}</strong> reportes
            </span>
          </div>
        </div>

        {reportsQuery.isLoading ? (
          <Skeleton />
        ) : reportsQuery.isError ? (
          <div className="empty-state">
            <FileBarChart size={30} />
            <strong>No fue posible cargar los reportes</strong>
            <button onClick={() => reportsQuery.refetch()}>
              Intentar de nuevo
            </button>
          </div>
        ) : shown.length === 0 ? (
          <div className="empty-state">
            <FileBarChart size={30} />
            <strong>No hay reportes generados</strong>
            <span>Genera un archivo CSV o PDF para comenzar.</span>
          </div>
        ) : (
          <div className="table-scroll">
            <table className="data-table report-table">
              <thead>
                <tr>
                  <th>Reporte</th>
                  <th>Tipo</th>
                  <th>Formato</th>
                  <th>Generado</th>
                  <th aria-label="Acciones" />
                </tr>
              </thead>
              <tbody>
                {shown.map((report) => (
                  <tr key={report.id}>
                    <td>
                      <div className="table-user">
                        <div className={`report-file report-file--${report.file_format}`}>
                          {report.file_format === "csv" ? (
                            <FileSpreadsheet size={17} />
                          ) : (
                            <FileBarChart size={17} />
                          )}
                        </div>
                        <div>
                          <strong>Reporte #{report.id}</strong>
                          <span>
                            smartinvoice-report-{report.id}.
                            {report.file_format}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td className="table-muted">Facturas administrativas</td>
                    <td>
                      <span className={`format-badge format-badge--${report.file_format}`}>
                        {report.file_format.toUpperCase()}
                      </span>
                    </td>
                    <td className="table-muted">
                      {new Intl.DateTimeFormat("es-GT", {
                        dateStyle: "medium",
                        timeStyle: "short",
                      }).format(new Date(report.created_at))}
                    </td>
                    <td>
                      <div className="table-actions">
                        <button
                          title="Descargar reporte"
                          onClick={() => download(report)}
                        >
                          <Download size={16} />
                        </button>
                        <button
                          title="Enviar por correo"
                          onClick={() => setEmailTarget(report)}
                        >
                          <Mail size={16} />
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
          <span>
            Página {page} de {totalPages}
          </span>
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

      {generateOpen && (
        <GenerateReportModal
          onClose={() => setGenerateOpen(false)}
          onSuccess={async (message) => {
            await refresh();
            setGenerateOpen(false);
            setFeedback({ tone: "success", message });
          }}
        />
      )}

      {emailTarget && (
        <EmailReportModal
          report={emailTarget}
          onClose={() => setEmailTarget(null)}
          onSuccess={(message) => {
            setEmailTarget(null);
            setFeedback({ tone: "success", message });
          }}
        />
      )}
    </div>
  );
}

function Summary({
  icon,
  value,
  label,
}: {
  icon: React.ReactNode;
  value: number;
  label: string;
}) {
  return (
    <div className="invoice-metric">
      <span>{icon}</span>
      <div>
        <strong>{value}</strong>
        <small>{label}</small>
      </div>
    </div>
  );
}

function GenerateReportModal({
  onClose,
  onSuccess,
}: {
  onClose: () => void;
  onSuccess: (message: string) => void;
}) {
  const [form, setForm] = useState<ReportCreatePayload>({
    file_format: "pdf",
    date_from: null,
    date_to: null,
    provider_id: null,
    status: null,
  });
  const [error, setError] = useState("");
  const providersQuery = useQuery({
    queryKey: ["providers", "report-options"],
    queryFn: () => listProviders(1, 100),
  });

  const mutation = useMutation({
    mutationFn: generateReport,
    onSuccess: (result) =>
      onSuccess(
        result.automatic_email_sent
          ? `Reporte ${result.report.file_format.toUpperCase()} generado con ${result.invoice_count} factura(s) y enviado automáticamente a ${result.automatic_email_recipient}.`
          : `Reporte generado, pero no fue posible enviarlo automáticamente a ${result.automatic_email_recipient}. Puedes reenviarlo desde el botón de correo.`,
      ),
    onError: (requestError) => setError(getApiErrorMessage(requestError)),
  });

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    if (form.date_from && form.date_to && form.date_from > form.date_to) {
      setError("La fecha inicial no puede ser posterior a la fecha final.");
      return;
    }
    mutation.mutate(form);
  };

  return (
    <Modal
      title="Generar reporte"
      description="Selecciona el formato y los filtros que deseas aplicar."
      onClose={onClose}
    >
      <form className="entity-form" onSubmit={submit}>
        <div className="report-format-picker">
          {(["pdf", "csv"] as ReportFormat[]).map((format) => (
            <label
              key={format}
              className={form.file_format === format ? "is-selected" : ""}
            >
              <input
                type="radio"
                name="format"
                value={format}
                checked={form.file_format === format}
                onChange={() =>
                  setForm((current) => ({
                    ...current,
                    file_format: format,
                  }))
                }
              />
              {format === "pdf" ? (
                <FileBarChart size={22} />
              ) : (
                <FileSpreadsheet size={22} />
              )}
              <span>
                <strong>{format.toUpperCase()}</strong>
                <small>
                  {format === "pdf"
                    ? "Documento listo para compartir"
                    : "Datos para hojas de cálculo"}
                </small>
              </span>
            </label>
          ))}
        </div>
        <div className="form-grid">
          <label>
            Fecha inicial
            <input
              type="date"
              value={form.date_from ?? ""}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  date_from: event.target.value || null,
                }))
              }
            />
          </label>
          <label>
            Fecha final
            <input
              type="date"
              value={form.date_to ?? ""}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  date_to: event.target.value || null,
                }))
              }
            />
          </label>
          <label>
            Proveedor
            <select
              value={form.provider_id ?? ""}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  provider_id: event.target.value
                    ? Number(event.target.value)
                    : null,
                }))
              }
            >
              <option value="">Todos los proveedores</option>
              {providersQuery.data?.items
                .filter((provider) => provider.is_active)
                .map((provider) => (
                  <option key={provider.id} value={provider.id}>
                    {provider.name} — {provider.nit}
                  </option>
                ))}
            </select>
          </label>
          <label>
            Estado
            <select
              value={form.status ?? ""}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  status:
                    (event.target.value as InvoiceStatus) || null,
                }))
              }
            >
              <option value="">Todos los estados</option>
              <option value="pending">Pendientes</option>
              <option value="processed">Procesadas</option>
              <option value="error">Con observaciones</option>
              <option value="rejected">Rechazadas</option>
            </select>
          </label>
        </div>
        {error && <div className="form-error">{error}</div>}
        <div className="modal-actions">
          <button type="button" className="ghost-button" onClick={onClose}>
            Cancelar
          </button>
          <button
            className="primary-button modal-primary"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Generando..." : "Generar reporte"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function EmailReportModal({
  report,
  onClose,
  onSuccess,
}: {
  report: Report;
  onClose: () => void;
  onSuccess: (message: string) => void;
}) {
  const [form, setForm] = useState<ReportEmailPayload>({
    recipient: "",
    subject: "Reporte de facturas - SmartInvoice",
    message: "Adjunto se encuentra el reporte solicitado desde SmartInvoice.",
  });
  const [error, setError] = useState("");
  const mutation = useMutation({
    mutationFn: () => emailReport(report.id, form),
    onSuccess: (result) =>
      onSuccess(
        result.delivery_mode === "smtp"
          ? `Reporte enviado a ${result.recipient}.`
          : `Correo preparado para ${result.recipient} en la bandeja local.`,
      ),
    onError: (requestError) => setError(getApiErrorMessage(requestError)),
  });

  return (
    <Modal
      title="Enviar reporte por correo"
      description={`Adjuntará el reporte #${report.id} en formato ${report.file_format.toUpperCase()}.`}
      onClose={onClose}
    >
      <form
        className="entity-form"
        onSubmit={(event) => {
          event.preventDefault();
          setError("");
          mutation.mutate();
        }}
      >
        <label>
          Destinatario
          <input
            type="email"
            value={form.recipient}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                recipient: event.target.value,
              }))
            }
            required
          />
        </label>
        <label>
          Asunto
          <input
            value={form.subject}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                subject: event.target.value,
              }))
            }
            minLength={3}
            maxLength={180}
            required
          />
        </label>
        <label>
          Mensaje
          <textarea
            value={form.message}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                message: event.target.value,
              }))
            }
            minLength={3}
            maxLength={2000}
            rows={5}
            required
          />
        </label>
        {error && <div className="form-error">{error}</div>}
        <div className="modal-actions">
          <button type="button" className="ghost-button" onClick={onClose}>
            Cancelar
          </button>
          <button
            className="primary-button modal-primary"
            disabled={mutation.isPending}
          >
            <Mail size={15} />
            {mutation.isPending ? "Enviando..." : "Enviar reporte"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function Skeleton() {
  return (
    <div className="table-skeleton">
      {Array.from({ length: 5 }).map((_, index) => (
        <div key={index}>
          <i />
          <i />
          <i />
          <i />
        </div>
      ))}
    </div>
  );
}
