import type {
  ProcessingLog,
  ProcessingLogFilters,
  ProcessingLogListResponse,
} from "../types/processingLog";
import { apiClient } from "./client";

/** Consulta eventos de auditoría aplicando los filtros activos. */
export async function listProcessingLogs(
  page = 1,
  filters: ProcessingLogFilters = {},
): Promise<ProcessingLogListResponse> {
  const { data } = await apiClient.get<ProcessingLogListResponse>("/logs", {
    params: { page, page_size: 20, ...filters },
  });
  return data;
}

/** Obtiene el detalle completo de un evento. */
export async function getProcessingLog(id: number): Promise<ProcessingLog> {
  const { data } = await apiClient.get<ProcessingLog>(`/logs/${id}`);
  return data;
}
