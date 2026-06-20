import {
  Bot,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock3,
  ExternalLink,
  FileCheck2,
  History,
  Play,
  RefreshCw,
  Search,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { listInvoices } from "../api/invoices";
import { listProcessingLogs } from "../api/processingLogs";
import { executeInvoiceRpa } from "../api/rpa";
import { Modal } from "../components/Modal";
import type { Invoice } from "../types/invoice";
import type { ProcessingLog } from "../types/processingLog";
import type { RpaExecutionResponse } from "../types/rpa";
import { getApiErrorMessage } from "../utils/apiError";

export function RpaPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [confirmTarget, setConfirmTarget] = useState<Invoice | null>(null);
  const [result, setResult] = useState<RpaExecutionResponse | null>(null);
  const [detailLog, setDetailLog] = useState<ProcessingLog | null>(null);
  const [feedback, setFeedback] = useState<{
    tone: "success" | "error";
    message: string;
  } | null>(null);
  const queryClient = useQueryClient();

  const invoicesQuery = useQuery({
    queryKey: ["rpa-invoices", page],
    queryFn: () => listInvoices(page, "processed"),
  });
  const successLogs = useQuery({
    queryKey: ["rpa-logs", "success"],
    queryFn: () =>
      listProcessingLogs(1, { action: "rpa_invoice_registered" }),
  });
  const errorLogs = useQuery({
    queryKey: ["rpa-logs", "error"],
    queryFn: () => listProcessingLogs(1, { action: "rpa_invoice_error" }),
  });

  const history = useMemo(
    () =>
      [
        ...(successLogs.data?.items ?? []),
        ...(errorLogs.data?.items ?? []),
      ]
        .sort(
          (a, b) =>
            new Date(b.created_at).getTime() -
            new Date(a.created_at).getTime(),
        )
        .slice(0, 20),
    [errorLogs.data?.items, successLogs.data?.items],
  );

  const shown = useMemo(() => {
    const term = search.trim().toLowerCase();
    const invoices = invoicesQuery.data?.items ?? [];
    if (!term) return invoices;
    return invoices.filter((invoice) =>
      [
        invoice.invoice_number,
        invoice.file_name,
        invoice.detected_provider_name,
        invoice.detected_nit,
      ]
        .filter(Boolean)
        .some((value) => value?.toLowerCase().includes(term)),
    );
  }, [invoicesQuery.data?.items, search]);

  const mutation = useMutation({
    mutationFn: executeInvoiceRpa,
    onSuccess: async (execution) => {
      await queryClient.invalidateQueries({ queryKey: ["rpa-logs"] });
      setConfirmTarget(null);
      setResult(execution);
      setFeedback({
        tone: "success",
        message: "La factura fue registrada mediante RPA.",
      });
    },
    onError: (error) => {
      setConfirmTarget(null);
      setFeedback({ tone: "error", message: getApiErrorMessage(error) });
      queryClient.invalidateQueries({ queryKey: ["rpa-logs"] });
    },
  });

  const totalPages = Math.max(
    1,
    Math.ceil((invoicesQuery.data?.total ?? 0) / 20),
  );

  return (
    <div className="management-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Automatización</span>
          <h1>Ejecuciones RPA</h1>
          <p>Registra facturas procesadas en el sistema contable simulado.</p>
        </div>
        <button
          className="ghost-button page-filter-button"
          onClick={() => {
            invoicesQuery.refetch();
            successLogs.refetch();
            errorLogs.refetch();
          }}
        >
          <RefreshCw size={16} /> Actualizar
        </button>
      </section>

      {feedback && (
        <div className={`inline-alert inline-alert--${feedback.tone}`}>
          {feedback.message}
          <button onClick={() => setFeedback(null)}>Cerrar</button>
        </div>
      )}

      <section className="rpa-hero">
        <div className="rpa-hero__icon"><Bot size={28} /></div>
        <div>
          <span>Proceso automatizado</span>
          <h2>Del documento validado al registro contable</h2>
          <p>
            El robot abre el formulario web, completa los datos, confirma el
            registro y almacena evidencia JSON y una captura de pantalla.
          </p>
        </div>
        <div className="rpa-flow" aria-label="Flujo RPA">
          <span><FileCheck2 size={16} /> Factura</span>
          <i>→</i>
          <span><Bot size={16} /> Robot</span>
          <i>→</i>
          <span><ShieldCheck size={16} /> Evidencia</span>
        </div>
      </section>

      <section className="rpa-grid">
        <div className="management-card rpa-invoices">
          <div className="section-title">
            <div>
              <span>Facturas elegibles</span>
              <h2>Listas para automatizar</h2>
            </div>
            <strong>{invoicesQuery.data?.total ?? 0}</strong>
          </div>
          <div className="rpa-search">
            <Search size={16} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Buscar factura o proveedor"
            />
          </div>

          {invoicesQuery.isLoading ? (
            <div className="rpa-empty">Cargando facturas...</div>
          ) : invoicesQuery.isError ? (
            <div className="rpa-empty">
              <XCircle size={25} />
              No fue posible cargar las facturas.
            </div>
          ) : shown.length === 0 ? (
            <div className="rpa-empty">
              <FileCheck2 size={27} />
              <strong>No hay facturas procesadas</strong>
              <span>Valida una factura para habilitar su ejecución RPA.</span>
            </div>
          ) : (
            <div className="rpa-invoice-list">
              {shown.map((invoice) => (
                <article key={invoice.id} className="rpa-invoice-card">
                  <div className="rpa-invoice-card__icon">
                    <FileCheck2 size={18} />
                  </div>
                  <div className="rpa-invoice-card__body">
                    <strong>
                      {invoice.invoice_number || `Factura #${invoice.id}`}
                    </strong>
                    <span>
                      {invoice.detected_provider_name || "Sin proveedor"} ·{" "}
                      {money(invoice.total)}
                    </span>
                  </div>
                  <button
                    className="rpa-run-button"
                    onClick={() => setConfirmTarget(invoice)}
                    disabled={mutation.isPending}
                  >
                    <Play size={15} /> Ejecutar
                  </button>
                </article>
              ))}
            </div>
          )}

          <footer className="pagination">
            <span>Página {page} de {totalPages}</span>
            <div>
              <button
                disabled={page === 1}
                onClick={() => setPage((value) => value - 1)}
              >
                <ChevronLeft size={17} />
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((value) => value + 1)}
              >
                <ChevronRight size={17} />
              </button>
            </div>
          </footer>
        </div>

        <div className="management-card rpa-history">
          <div className="section-title">
            <div>
              <span>Auditoría</span>
              <h2>Historial reciente</h2>
            </div>
            <History size={19} />
          </div>
          {successLogs.isLoading || errorLogs.isLoading ? (
            <div className="rpa-empty">Cargando ejecuciones...</div>
          ) : history.length === 0 ? (
            <div className="rpa-empty">
              <Clock3 size={27} />
              <strong>Aún no hay ejecuciones</strong>
              <span>Los resultados aparecerán aquí.</span>
            </div>
          ) : (
            <div className="rpa-timeline">
              {history.map((log) => (
                <button key={log.id} onClick={() => setDetailLog(log)}>
                  <span
                    className={`rpa-timeline__dot ${
                      log.status === "success"
                        ? "rpa-timeline__dot--success"
                        : "rpa-timeline__dot--error"
                    }`}
                  />
                  <div>
                    <strong>
                      {log.status === "success"
                        ? "Registro completado"
                        : "Ejecución fallida"}
                    </strong>
                    <span>
                      Factura #{log.invoice_id ?? "—"} ·{" "}
                      {formatDateTime(log.created_at)}
                    </span>
                    <p>{log.result}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </section>

      {confirmTarget && (
        <Modal
          title="Ejecutar automatización"
          description="El robot registrará los datos en el sistema contable simulado."
          width="small"
          onClose={() => setConfirmTarget(null)}
        >
          <div className="confirm-content">
            <div className="rpa-confirm">
              <Bot size={24} />
              <div>
                <strong>
                  {confirmTarget.invoice_number ||
                    `Factura #${confirmTarget.id}`}
                </strong>
                <span>{confirmTarget.detected_provider_name}</span>
              </div>
            </div>
            <p>
              Se abrirá un navegador automatizado y se guardará evidencia de la
              operación.
            </p>
            <div className="modal-actions">
              <button
                className="ghost-button"
                onClick={() => setConfirmTarget(null)}
              >
                Cancelar
              </button>
              <button
                className="primary-button modal-primary"
                disabled={mutation.isPending}
                onClick={() => mutation.mutate(confirmTarget.id)}
              >
                {mutation.isPending ? "Ejecutando robot..." : "Ejecutar RPA"}
              </button>
            </div>
          </div>
        </Modal>
      )}

      {result && (
        <Modal
          title="Automatización completada"
          description="La factura fue registrada y la evidencia quedó almacenada."
          onClose={() => setResult(null)}
        >
          <div className="rpa-result">
            <CheckCircle2 size={36} />
            <h3>Registro confirmado</h3>
            <p>{result.confirmation}</p>
            <div className="invoice-detail__grid">
              <Detail label="Factura" value={`#${result.invoice_id}`} />
              <Detail
                label="Ejecutado"
                value={formatDateTime(result.executed_at)}
              />
              <Detail
                label="Destino"
                value={browserTargetUrl(result.target_url)}
              />
              <Detail label="Evidencia" value={fileName(result.evidence_file)} />
            </div>
            <a
              href={browserTargetUrl(result.target_url)}
              target="_blank"
              rel="noreferrer"
              className="rpa-target-link"
            >
              <ExternalLink size={15} /> Ver sistema simulado
            </a>
          </div>
        </Modal>
      )}

      {detailLog && (
        <Modal
          title="Detalle de ejecución"
          description={`Evento de auditoría #${detailLog.id}`}
          width="small"
          onClose={() => setDetailLog(null)}
        >
          <div className="log-detail">
            <div className="rpa-confirm">
              {detailLog.status === "success" ? (
                <CheckCircle2 size={24} />
              ) : (
                <XCircle size={24} />
              )}
              <div>
                <strong>
                  {detailLog.status === "success"
                    ? "Registro completado"
                    : "Ejecución fallida"}
                </strong>
                <span>{formatDateTime(detailLog.created_at)}</span>
              </div>
            </div>
            <div className="log-message">
              <span>Resultado</span>
              <p>{detailLog.result || "Sin resultado."}</p>
            </div>
            {detailLog.error_detail && (
              <div className="log-message log-message--error">
                <span>Error</span>
                <pre>{detailLog.error_detail}</pre>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return <div><span>{label}</span><strong>{value}</strong></div>;
}

function money(value: string | null): string {
  if (value === null) return "Sin total";
  return new Intl.NumberFormat("es-GT", {
    style: "currency",
    currency: "GTQ",
  }).format(Number(value));
}

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("es-GT", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function fileName(path: string): string {
  return path.split(/[\\/]/).pop() ?? path;
}

function browserTargetUrl(target: string): string {
  try {
    const internalUrl = new URL(target, window.location.origin);
    if (internalUrl.hostname === "api") {
      // "api" solo existe dentro de Docker. El navegador debe usar Nginx,
      // que publica la misma ruta /api/v1 desde el dominio actual.
      return new URL(
        `${internalUrl.pathname}${internalUrl.search}${internalUrl.hash}`,
        window.location.origin,
      ).toString();
    }
    return internalUrl.toString();
  } catch {
    return target;
  }
}
