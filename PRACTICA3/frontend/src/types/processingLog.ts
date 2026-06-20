export interface ProcessingLog {
  id: number;
  invoice_id: number | null;
  user_id: number | null;
  action: string;
  status: string;
  result: string | null;
  error_detail: string | null;
  created_at: string;
}

export interface ProcessingLogListResponse {
  items: ProcessingLog[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProcessingLogFilters {
  invoice_id?: number;
  user_id?: number;
  action?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
}
