import type {
  Invoice,
  InvoiceDetail,
  InvoiceListResponse,
  InvoiceStatus,
  InvoiceStats,
  InvoiceValidationPayload,
  OcrProcessingResponse,
} from "../types/invoice";
import { apiClient } from "./client";

/** Consulta facturas aplicando página, estado y búsqueda. */
export async function listInvoices(
  page = 1,
  status?: InvoiceStatus,
  search?: string,
): Promise<InvoiceListResponse> {
  const { data } = await apiClient.get<InvoiceListResponse>("/invoices", {
    params: {
      page,
      page_size: 20,
      status: status || undefined,
      search: search?.trim() || undefined,
    },
  });
  return data;
}

/** Obtiene todos los datos de una factura. */
export async function getInvoice(id: number): Promise<InvoiceDetail> {
  const { data } = await apiClient.get<InvoiceDetail>(`/invoices/${id}`);
  return data;
}

/** Obtiene los indicadores de facturas para el panel. */
export async function getInvoiceStats(): Promise<InvoiceStats> {
  const { data } = await apiClient.get<InvoiceStats>("/invoices/stats");
  return data;
}

/** Envía una factura como multipart/form-data. */
export async function uploadInvoice(file: File): Promise<Invoice> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await apiClient.post<Invoice>("/invoices/upload", form, {
    headers: { "Content-Type": undefined },
  });
  return data;
}

/** Solicita la ejecución del OCR y la extracción de campos. */
export async function processInvoice(id: number): Promise<OcrProcessingResponse> {
  const { data } = await apiClient.post<OcrProcessingResponse>(
    `/invoices/${id}/process`,
  );
  return data;
}

/** Guarda las correcciones realizadas durante la validación visual. */
export async function validateInvoice(
  id: number,
  payload: InvoiceValidationPayload,
): Promise<InvoiceDetail> {
  const { data } = await apiClient.patch<InvoiceDetail>(
    `/invoices/${id}/validate`,
    payload,
  );
  return data;
}

/** Cambia una factura pendiente a rechazada. */
export async function rejectInvoice(id: number): Promise<Invoice> {
  const { data } = await apiClient.patch<Invoice>(`/invoices/${id}/reject`);
  return data;
}

/** Solicita el borrado lógico de una factura. */
export async function deleteInvoice(id: number): Promise<Invoice> {
  const { data } = await apiClient.delete<Invoice>(`/invoices/${id}`);
  return data;
}

/** Descarga el documento original usando un enlace temporal del navegador. */
export async function downloadInvoice(invoice: Invoice): Promise<void> {
  const data = await getInvoiceFile(invoice.id);
  const url = URL.createObjectURL(data);
  const link = document.createElement("a");
  link.href = url;
  link.download = invoice.file_name;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

/** Obtiene el archivo binario original de una factura. */
export async function getInvoiceFile(id: number): Promise<Blob> {
  const { data } = await apiClient.get<Blob>(`/invoices/${id}/download`, {
    responseType: "blob",
  });
  return data;
}
