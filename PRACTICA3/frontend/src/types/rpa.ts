export interface RpaExecutionResponse {
  success: boolean;
  invoice_id: number;
  target_url: string;
  confirmation: string;
  evidence_file: string;
  executed_at: string;
}
