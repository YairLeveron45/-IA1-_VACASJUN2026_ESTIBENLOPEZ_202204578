import type { InvoiceStatus } from "./invoice";

export type ReportFormat = "csv" | "pdf";

export interface Report {
  id: number;
  report_type: string;
  file_format: ReportFormat;
  generated_by_id: number | null;
  created_at: string;
}

export interface ReportListResponse {
  items: Report[];
  total: number;
  page: number;
  page_size: number;
}

export interface ReportCreatePayload {
  file_format: ReportFormat;
  date_from: string | null;
  date_to: string | null;
  provider_id: number | null;
  status: InvoiceStatus | null;
}

export interface ReportGenerationResponse {
  report: Report;
  invoice_count: number;
  automatic_email_sent: boolean;
  automatic_email_recipient: string;
  automatic_email_delivery_mode: "outbox" | "smtp" | null;
  automatic_email_error: string | null;
}

export interface ReportEmailPayload {
  recipient: string;
  subject: string;
  message: string;
}

export interface EmailSendResponse {
  sent: boolean;
  delivery_mode: "outbox" | "smtp";
  recipient: string;
  report_id: number;
}
