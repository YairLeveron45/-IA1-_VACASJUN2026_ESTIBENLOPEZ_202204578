import type {
  EmailSendResponse,
  Report,
  ReportCreatePayload,
  ReportEmailPayload,
  ReportGenerationResponse,
  ReportListResponse,
} from "../types/report";
import { apiClient } from "./client";

/** Consulta los reportes administrativos generados. */
export async function listReports(page = 1): Promise<ReportListResponse> {
  const { data } = await apiClient.get<ReportListResponse>("/reports", {
    params: { page, page_size: 20 },
  });
  return data;
}

/** Genera un reporte utilizando formato y filtros seleccionados. */
export async function generateReport(
  payload: ReportCreatePayload,
): Promise<ReportGenerationResponse> {
  const { data } = await apiClient.post<ReportGenerationResponse>(
    "/reports",
    payload,
  );
  return data;
}

/** Solicita el envío manual de un reporte por correo. */
export async function emailReport(
  reportId: number,
  payload: ReportEmailPayload,
): Promise<EmailSendResponse> {
  const { data } = await apiClient.post<EmailSendResponse>(
    `/reports/${reportId}/email`,
    payload,
  );
  return data;
}

/** Descarga el reporte y libera después la URL temporal. */
export async function downloadReport(report: Report): Promise<void> {
  const { data } = await apiClient.get<Blob>(
    `/reports/${report.id}/download`,
    { responseType: "blob" },
  );
  const url = URL.createObjectURL(data);
  const link = document.createElement("a");
  const generatedDate = new Date(report.created_at).toISOString().slice(0, 10);
  link.href = url;
  link.download =
    `smartinvoice-facturas-${generatedDate}-reporte-${report.id}.` +
    report.file_format;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
