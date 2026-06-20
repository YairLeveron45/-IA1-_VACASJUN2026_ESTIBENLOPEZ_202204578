export type InvoiceStatus = "pending" | "processed" | "error" | "rejected";

export interface Invoice {
  id: number;
  invoice_number: string | null;
  invoice_date: string | null;
  provider_id: number | null;
  detected_provider_name: string | null;
  detected_nit: string | null;
  subtotal: string | null;
  taxes: string | null;
  total: string | null;
  file_name: string;
  content_type: string;
  status: InvoiceStatus;
  uploaded_by_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface InvoiceDetail extends Invoice {
  ocr_text: string | null;
}

export interface InvoiceListResponse {
  items: Invoice[];
  total: number;
  page: number;
  page_size: number;
}

export interface InvoiceStats {
  total: number;
  pending: number;
  processed: number;
  error: number;
  rejected: number;
}

export interface InvoiceValidationPayload {
  invoice_number: string;
  invoice_date: string;
  provider_name: string;
  nit: string;
  subtotal: number;
  taxes: number;
  total: number;
  create_provider_if_missing: boolean;
}

export interface OcrProcessingResponse {
  invoice: InvoiceDetail;
  warnings: string[];
  pages_processed: number;
}
