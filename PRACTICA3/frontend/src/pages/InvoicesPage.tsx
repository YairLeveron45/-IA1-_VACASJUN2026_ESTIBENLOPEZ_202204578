import {
  Bot,
  ChevronLeft,
  ChevronRight,
  Download,
  Eye,
  FileCheck2,
  FileText,
  LoaderCircle,
  Play,
  Plus,
  Search,
  Trash2,
  UploadCloud,
  XCircle,
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  type DragEvent,
  type FormEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";
import { lookupProvider } from "../api/providers";
import {
  downloadInvoice,
  deleteInvoice,
  getInvoice,
  getInvoiceFile,
  listInvoices,
  processInvoice,
  rejectInvoice,
  uploadInvoice,
  validateInvoice,
} from "../api/invoices";
import { Modal } from "../components/Modal";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import type {
  Invoice,
  InvoiceDetail,
  InvoiceStatus,
  InvoiceValidationPayload,
} from "../types/invoice";
import { getApiErrorMessage } from "../utils/apiError";

const labels: Record<InvoiceStatus, string> = {
  pending: "Pendiente",
  processed: "Procesada",
  error: "Revisar",
  rejected: "Rechazada",
};

export function InvoicesPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState<"" | InvoiceStatus>("");
  const [search, setSearch] = useState("");
  const [uploadOpen, setUploadOpen] = useState(false);
  const [detailId, setDetailId] = useState<number | null>(null);
  const [validation, setValidation] = useState<InvoiceDetail | null>(null);
  const [rejectTarget, setRejectTarget] = useState<Invoice | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Invoice | null>(null);
  const [feedback, setFeedback] = useState<{
    tone: "success" | "error";
    message: string;
  } | null>(null);
  const debouncedSearch = useDebouncedValue(search);
  const queryClient = useQueryClient();

  const invoicesQuery = useQuery({
    queryKey: ["invoices", page, status, debouncedSearch],
    queryFn: () =>
      listInvoices(page, status || undefined, debouncedSearch),
    placeholderData: (previousData) => previousData,
  });
  const detailQuery = useQuery({
    queryKey: ["invoice", detailId],
    queryFn: () => getInvoice(detailId!),
    enabled: detailId !== null,
  });

  const refresh = async () => {
    await queryClient.invalidateQueries({ queryKey: ["invoices"] });
    await queryClient.invalidateQueries({ queryKey: ["invoice"] });
  };

  const processMutation = useMutation({
    mutationFn: processInvoice,
    onSuccess: async (result) => {
      await refresh();
      if (result.warnings.length) {
        setValidation(result.invoice);
        setFeedback({
          tone: "error",
          message: `OCR completado con ${result.warnings.length} observación(es). Revisa los datos.`,
        });
      } else {
        setFeedback({
          tone: "success",
          message: `OCR completado en ${result.pages_processed} página(s).`,
        });
      }
    },
    onError: (error) =>
      setFeedback({ tone: "error", message: getApiErrorMessage(error) }),
  });

  const rejectMutation = useMutation({
    mutationFn: rejectInvoice,
    onSuccess: async () => {
      await refresh();
      setRejectTarget(null);
      setDetailId(null);
      setFeedback({ tone: "success", message: "Factura rechazada." });
    },
    onError: (error) =>
      setFeedback({ tone: "error", message: getApiErrorMessage(error) }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteInvoice,
    onSuccess: async () => {
      await refresh();
      setDeleteTarget(null);
      setDetailId(null);
      setFeedback({ tone: "success", message: "Factura eliminada." });
    },
    onError: (error) =>
      setFeedback({ tone: "error", message: getApiErrorMessage(error) }),
  });

  const shown = useMemo(() => {
    const items = invoicesQuery.data?.items ?? [];
    return items;
  }, [invoicesQuery.data?.items]);

  const totalPages = Math.max(
    1,
    Math.ceil((invoicesQuery.data?.total ?? 0) / 20),
  );

  const download = async (invoice: Invoice) => {
    try {
      await downloadInvoice(invoice);
    } catch (error) {
      setFeedback({ tone: "error", message: getApiErrorMessage(error) });
    }
  };

  const review = async (invoice: Invoice) => {
    try {
      setValidation(await getInvoice(invoice.id));
      setDetailId(null);
    } catch (error) {
      setFeedback({ tone: "error", message: getApiErrorMessage(error) });
    }
  };

  return (
    <div className="management-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Documentos</span>
          <h1>Gestión de facturas</h1>
          <p>Carga documentos, extrae sus datos con OCR y valida resultados.</p>
        </div>
        <button className="primary-button page-action" onClick={() => setUploadOpen(true)}>
          <Plus size={18} /> Cargar factura
        </button>
      </section>

      {feedback && (
        <div className={`inline-alert inline-alert--${feedback.tone}`}>
          {feedback.message}
          <button onClick={() => setFeedback(null)}>Cerrar</button>
        </div>
      )}

      <section className="invoice-metrics">
        <Metric label="Facturas" value={invoicesQuery.data?.total ?? 0} />
        <Metric
          label="Procesadas en página"
          value={
            invoicesQuery.data?.items.filter((item) => item.status === "processed")
              .length ?? 0
          }
        />
        <Metric
          label="Por revisar"
          value={
            invoicesQuery.data?.items.filter((item) =>
              ["pending", "error"].includes(item.status),
            ).length ?? 0
          }
        />
      </section>

      <section className="management-card">
        <div className="management-toolbar invoice-toolbar">
          <div className="search-box">
            <Search size={17} />
            <input
              value={search}
              onChange={(event) => {
                setSearch(event.target.value);
                setPage(1);
              }}
              placeholder="Buscar archivo, número, proveedor o NIT"
            />
          </div>
          <select
            className="filter-select"
            value={status}
            onChange={(event) => {
              setStatus(event.target.value as "" | InvoiceStatus);
              setPage(1);
            }}
          >
            <option value="">Todos los estados</option>
            <option value="pending">Pendientes</option>
            <option value="processed">Procesadas</option>
            <option value="error">Con observaciones</option>
            <option value="rejected">Rechazadas</option>
          </select>
        </div>

        {invoicesQuery.isLoading ? (
          <Skeleton />
        ) : invoicesQuery.isError ? (
          <div className="empty-state">
            <XCircle size={30} />
            <strong>No fue posible cargar las facturas</strong>
            <button onClick={() => invoicesQuery.refetch()}>Intentar de nuevo</button>
          </div>
        ) : shown.length === 0 ? (
          <div className="empty-state">
            <FileText size={30} />
            <strong>No hay facturas para mostrar</strong>
            <span>Carga un documento PDF, JPG, JPEG o PNG.</span>
          </div>
        ) : (
          <div className="table-scroll">
            <table className="data-table invoice-table">
              <thead>
                <tr>
                  <th>Documento</th>
                  <th>Proveedor</th>
                  <th>Fecha</th>
                  <th>Total</th>
                  <th>Estado</th>
                  <th aria-label="Acciones" />
                </tr>
              </thead>
              <tbody>
                {shown.map((invoice) => (
                  <tr key={invoice.id}>
                    <td>
                      <div className="table-user">
                        <div className="table-avatar"><FileText size={16} /></div>
                        <div>
                          <strong>{invoice.invoice_number || invoice.file_name}</strong>
                          <span>{invoice.invoice_number ? invoice.file_name : `Factura #${invoice.id}`}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="provider-contact">
                        <strong>{invoice.detected_provider_name || "Sin detectar"}</strong>
                        <span>{invoice.detected_nit || "NIT pendiente"}</span>
                      </div>
                    </td>
                    <td className="table-muted">{invoice.invoice_date || "Pendiente"}</td>
                    <td className="invoice-total">{money(invoice.total)}</td>
                    <td>
                      <span className={`invoice-status invoice-status--${invoice.status}`}>
                        {labels[invoice.status]}
                      </span>
                    </td>
                    <td>
                      <div className="invoice-row-actions">
                        {invoice.status === "pending" && (
                          <button
                            className="invoice-next-action"
                            disabled={processMutation.isPending}
                            onClick={() => processMutation.mutate(invoice.id)}
                          >
                            <Play size={15} /> Procesar OCR
                          </button>
                        )}
                        {invoice.status === "error" && (
                          <button
                            className="invoice-next-action"
                            onClick={() => review(invoice)}
                          >
                            <FileCheck2 size={15} /> Visualizar y validar
                          </button>
                        )}
                        {invoice.status === "processed" && (
                          <button
                            className="invoice-next-action invoice-next-action--success"
                            onClick={() => navigate("/rpa")}
                          >
                            <Bot size={15} /> Continuar a RPA
                          </button>
                        )}
                        <div className="table-actions">
                        <button title="Ver detalle" onClick={() => setDetailId(invoice.id)}>
                          <Eye size={16} />
                        </button>
                        <button
                          title="Procesar OCR"
                          disabled={invoice.status === "rejected" || processMutation.isPending}
                          onClick={() => processMutation.mutate(invoice.id)}
                        >
                          {processMutation.isPending &&
                          processMutation.variables === invoice.id ? (
                            <LoaderCircle className="spin" size={16} />
                          ) : <Play size={16} />}
                        </button>
                        <button title="Descargar archivo" onClick={() => download(invoice)}>
                          <Download size={16} />
                        </button>
                        <button
                          title="Eliminar factura"
                          onClick={() => setDeleteTarget(invoice)}
                        >
                          <Trash2 size={16} />
                        </button>
                        </div>
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
            <button disabled={page === 1} onClick={() => setPage((value) => value - 1)}>
              <ChevronLeft size={17} />
            </button>
            <button disabled={page >= totalPages} onClick={() => setPage((value) => value + 1)}>
              <ChevronRight size={17} />
            </button>
          </div>
        </footer>
      </section>

      {uploadOpen && (
        <UploadModal
          onClose={() => setUploadOpen(false)}
          onSuccess={async () => {
            await refresh();
            setUploadOpen(false);
            setFeedback({ tone: "success", message: "Factura cargada. Ya puedes procesarla." });
          }}
        />
      )}

      {detailId !== null && (
        <DetailModal
          invoice={detailQuery.data}
          loading={detailQuery.isLoading}
          processing={processMutation.isPending}
          onClose={() => setDetailId(null)}
          onDownload={() => detailQuery.data && download(detailQuery.data)}
          onProcess={() => processMutation.mutate(detailId)}
          onReview={() => detailQuery.data && review(detailQuery.data)}
          onReject={() => detailQuery.data && setRejectTarget(detailQuery.data)}
          onDelete={() => detailQuery.data && setDeleteTarget(detailQuery.data)}
        />
      )}

      {validation && (
        <ValidationModal
          invoice={validation}
          onClose={() => setValidation(null)}
          onSuccess={async () => {
            await refresh();
            setValidation(null);
            setFeedback({ tone: "success", message: "Factura validada correctamente." });
          }}
        />
      )}

      {rejectTarget && (
        <Modal
          title="Rechazar factura"
          description="El documento ya no podrá procesarse ni validarse."
          width="small"
          onClose={() => setRejectTarget(null)}
        >
          <div className="confirm-content">
            <p>¿Deseas rechazar <strong>{rejectTarget.file_name}</strong>?</p>
            <div className="modal-actions">
              <button className="ghost-button" onClick={() => setRejectTarget(null)}>Cancelar</button>
              <button
                className="danger-button"
                disabled={rejectMutation.isPending}
                onClick={() => rejectMutation.mutate(rejectTarget.id)}
              >
                {rejectMutation.isPending ? "Rechazando..." : "Rechazar"}
              </button>
            </div>
          </div>
        </Modal>
      )}

      {deleteTarget && (
        <Modal
          title="Eliminar factura"
          description="Se retirará de las consultas y se eliminará su archivo. La bitácora se conservará."
          width="small"
          onClose={() => setDeleteTarget(null)}
        >
          <div className="confirm-content">
            <p>¿Deseas eliminar <strong>{deleteTarget.file_name}</strong>?</p>
            <div className="modal-actions">
              <button className="ghost-button" onClick={() => setDeleteTarget(null)}>
                Cancelar
              </button>
              <button
                className="danger-button"
                disabled={deleteMutation.isPending}
                onClick={() => deleteMutation.mutate(deleteTarget.id)}
              >
                {deleteMutation.isPending ? "Eliminando..." : "Eliminar"}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="invoice-metric">
      <span><FileCheck2 size={18} /></span>
      <div><strong>{value}</strong><small>{label}</small></div>
    </div>
  );
}

function UploadModal({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const mutation = useMutation({
    mutationFn: uploadInvoice,
    onSuccess,
    onError: (requestError) => setError(getApiErrorMessage(requestError)),
  });

  const choose = (candidate?: File) => {
    if (!candidate) return;
    if (candidate.size > 10 * 1024 * 1024) {
      setError("El archivo supera el límite de 10 MB.");
      return;
    }
    setError("");
    setFile(candidate);
  };

  const drop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    choose(event.dataTransfer.files[0]);
  };

  return (
    <Modal title="Cargar factura" description="PDF, JPG, JPEG o PNG. Máximo 10 MB." onClose={onClose}>
      <form
        className="entity-form"
        onSubmit={(event) => {
          event.preventDefault();
          if (!file) return setError("Selecciona un archivo.");
          mutation.mutate(file);
        }}
      >
        <input
          ref={inputRef}
          className="visually-hidden"
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={(event) => choose(event.target.files?.[0])}
        />
        <div
          className="upload-dropzone"
          onDragOver={(event) => event.preventDefault()}
          onDrop={drop}
          onClick={() => inputRef.current?.click()}
        >
          <UploadCloud size={34} />
          <strong>{file?.name || "Arrastra una factura o selecciónala"}</strong>
          <span>{file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "Haz clic para explorar"}</span>
        </div>
        {error && <div className="form-error">{error}</div>}
        <div className="modal-actions">
          <button type="button" className="ghost-button" onClick={onClose}>Cancelar</button>
          <button className="primary-button modal-primary" disabled={mutation.isPending}>
            {mutation.isPending ? "Cargando..." : "Cargar factura"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function DetailModal({
  invoice,
  loading,
  processing,
  onClose,
  onDownload,
  onProcess,
  onReview,
  onReject,
  onDelete,
}: {
  invoice?: InvoiceDetail;
  loading: boolean;
  processing: boolean;
  onClose: () => void;
  onDownload: () => void;
  onProcess: () => void;
  onReview: () => void;
  onReject: () => void;
  onDelete: () => void;
}) {
  return (
    <Modal
      title="Detalle de factura"
      description="Datos extraídos del documento."
      onClose={onClose}
    >
      {loading || !invoice ? (
        <div className="modal-loading"><LoaderCircle className="spin" /> Cargando...</div>
      ) : (
        <div className="invoice-detail">
          <div className="invoice-detail__file">
            <FileText size={22} />
            <div><strong>{invoice.file_name}</strong><span>{labels[invoice.status]}</span></div>
          </div>
          <div className="invoice-detail__grid">
            <Item label="Número" value={invoice.invoice_number} />
            <Item label="Fecha" value={invoice.invoice_date} />
            <Item label="Proveedor" value={invoice.detected_provider_name} />
            <Item label="NIT" value={invoice.detected_nit} />
            <Item label="Subtotal" value={money(invoice.subtotal)} />
            <Item label="Impuestos" value={money(invoice.taxes)} />
            <Item label="Total" value={money(invoice.total)} />
          </div>
          {invoice.ocr_text && (
            <details className="ocr-text"><summary>Ver texto OCR</summary><pre>{invoice.ocr_text}</pre></details>
          )}
          <div className="invoice-detail__actions">
            <button className="ghost-button" onClick={onDownload}><Download size={15} /> Descargar</button>
            {invoice.status !== "rejected" && (
              <>
                <button className="ghost-button" disabled={processing} onClick={onProcess}>
                  <Play size={15} /> {processing ? "Procesando..." : "Procesar OCR"}
                </button>
                <button className="primary-button modal-primary" onClick={onReview}>
                  <FileCheck2 size={15} /> Visualizar y validar
                </button>
              </>
            )}
            {!["processed", "rejected"].includes(invoice.status) && (
              <button className="danger-button" onClick={onReject}>Rechazar</button>
            )}
            <button className="danger-button" onClick={onDelete}>
              <Trash2 size={15} /> Eliminar
            </button>
          </div>
        </div>
      )}
    </Modal>
  );
}

function InvoicePreview({ invoice }: { invoice: InvoiceDetail }) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewError, setPreviewError] = useState("");

  useEffect(() => {
    let active = true;
    let objectUrl: string | null = null;
    setPreviewUrl(null);
    setPreviewError("");

    getInvoiceFile(invoice.id)
      .then((blob) => {
        if (!active) return;
        objectUrl = URL.createObjectURL(blob);
        setPreviewUrl(objectUrl);
      })
      .catch((error) => {
        if (active) setPreviewError(getApiErrorMessage(error));
      });

    return () => {
      active = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [invoice.id]);

  return (
    <div className="invoice-preview">
      <div className="invoice-comparison__heading">
        <span>Documento original</span>
        <strong>Vista previa</strong>
      </div>
      <div className="invoice-preview__frame">
        {previewError ? (
          <div className="invoice-preview__state">
            <XCircle size={24} />
            <span>{previewError}</span>
          </div>
        ) : !previewUrl ? (
          <div className="invoice-preview__state">
            <LoaderCircle className="spin" size={24} />
            <span>Cargando documento...</span>
          </div>
        ) : invoice.content_type === "application/pdf" ? (
          <iframe
            src={`${previewUrl}#toolbar=0&navpanes=0`}
            title={`Vista previa de ${invoice.file_name}`}
          />
        ) : (
          <img src={previewUrl} alt={`Vista previa de ${invoice.file_name}`} />
        )}
      </div>
    </div>
  );
}

function Item({ label, value }: { label: string; value: string | null }) {
  return <div><span>{label}</span><strong>{value || "No detectado"}</strong></div>;
}

function ValidationModal({
  invoice,
  onClose,
  onSuccess,
}: {
  invoice: InvoiceDetail;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [form, setForm] = useState<InvoiceValidationPayload>({
    invoice_number: invoice.invoice_number ?? "",
    invoice_date: invoice.invoice_date ?? "",
    provider_name: invoice.detected_provider_name ?? "",
    nit: invoice.detected_nit ?? "",
    subtotal: Number(invoice.subtotal ?? 0),
    taxes: Number(invoice.taxes ?? 0),
    total: Number(invoice.total ?? 0),
    create_provider_if_missing: true,
  });
  const [error, setError] = useState("");
  const normalizedNit = form.nit.trim().toUpperCase().replace(/\s/g, "");
  const debouncedNit = useDebouncedValue(normalizedNit);
  const providerQuery = useQuery({
    queryKey: ["provider-lookup", debouncedNit],
    queryFn: () => lookupProvider(debouncedNit),
    enabled: debouncedNit.length >= 2,
    retry: false,
  });
  const mutation = useMutation({
    mutationFn: () => validateInvoice(invoice.id, form),
    onSuccess,
    onError: (requestError) => setError(getApiErrorMessage(requestError)),
  });

  const text = (field: keyof InvoiceValidationPayload, value: string) =>
    setForm((current) => ({ ...current, [field]: value }));
  const amount = (field: "subtotal" | "taxes" | "total", value: string) =>
    setForm((current) => ({ ...current, [field]: Number(value) }));

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    if (Math.abs(form.subtotal + form.taxes - form.total) > 0.05) {
      return setError("El total debe coincidir con subtotal más impuestos.");
    }
    mutation.mutate();
  };

  return (
    <Modal
      title="Visualizar y validar factura"
      description="Compara el documento original y corrige los datos antes de aprobarlo."
      width="large"
      onClose={onClose}
    >
      <div className="validation-comparison">
        <InvoicePreview invoice={invoice} />
        <form className="entity-form validation-form" onSubmit={submit}>
          <div className="invoice-comparison__heading">
            <span>Resultado OCR</span>
            <strong>Datos para validar</strong>
          </div>
          <div className="form-grid">
            <label>Número de factura<input value={form.invoice_number} onChange={(e) => text("invoice_number", e.target.value)} required /></label>
            <label>Fecha<input type="date" value={form.invoice_date} onChange={(e) => text("invoice_date", e.target.value)} required /></label>
            <label>Proveedor<input value={form.provider_name} onChange={(e) => text("provider_name", e.target.value)} required /></label>
            <label>NIT<input value={form.nit} onChange={(e) => text("nit", e.target.value)} required /></label>
            <label>Subtotal<input type="number" min="0" step="0.01" value={form.subtotal} onChange={(e) => amount("subtotal", e.target.value)} required /></label>
            <label>Impuestos<input type="number" min="0" step="0.01" value={form.taxes} onChange={(e) => amount("taxes", e.target.value)} required /></label>
            <label className="form-field--full">Total<input type="number" min="0" step="0.01" value={form.total} onChange={(e) => amount("total", e.target.value)} required /></label>
          </div>
          <div
            className={`provider-association ${
              providerQuery.data ? "provider-association--found" : ""
            }`}
          >
            {providerQuery.isFetching ? (
              <div className="provider-association__status">
                <LoaderCircle className="spin" size={18} />
                <span>Buscando proveedor por NIT...</span>
              </div>
            ) : providerQuery.data ? (
              <div className="provider-association__status">
                <FileCheck2 size={18} />
                <span>
                  <strong>Proveedor existente</strong>
                  Se asociará con {providerQuery.data.name}.
                </span>
              </div>
            ) : (
              <label className="provider-create-option">
                <input
                  type="checkbox"
                  checked={form.create_provider_if_missing}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      create_provider_if_missing: event.target.checked,
                    }))
                  }
                />
                <span>
                  <strong>Registrar proveedor detectado</strong>
                  Crear “{form.provider_name || "Proveedor"}” con NIT{" "}
                  {form.nit || "pendiente"} y asociarlo a esta factura.
                </span>
              </label>
            )}
          </div>
          {error && <div className="form-error">{error}</div>}
          <div className="modal-actions">
            <button type="button" className="ghost-button" onClick={onClose}>Cancelar</button>
            <button className="primary-button modal-primary" disabled={mutation.isPending}>
              {mutation.isPending ? "Validando..." : "Validar factura"}
            </button>
          </div>
        </form>
      </div>
    </Modal>
  );
}

function Skeleton() {
  return <div className="table-skeleton">{Array.from({ length: 5 }).map((_, i) => <div key={i}><i /><i /><i /><i /></div>)}</div>;
}

function money(value: string | null): string {
  if (value === null) return "Pendiente";
  return new Intl.NumberFormat("es-GT", { style: "currency", currency: "GTQ" }).format(Number(value));
}
