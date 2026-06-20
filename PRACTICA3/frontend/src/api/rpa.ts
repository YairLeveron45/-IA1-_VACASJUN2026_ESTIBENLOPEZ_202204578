import type { RpaExecutionResponse } from "../types/rpa";
import { apiClient } from "./client";

/** Ejecuta el robot sobre una factura validada. */
export async function executeInvoiceRpa(
  invoiceId: number,
): Promise<RpaExecutionResponse> {
  const { data } = await apiClient.post<RpaExecutionResponse>(
    `/rpa/invoices/${invoiceId}/execute`,
  );
  return data;
}
