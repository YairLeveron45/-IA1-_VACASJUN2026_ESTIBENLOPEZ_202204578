export interface HealthResponse {
  status: "ok";
  application: string;
  environment: string;
}

export interface SystemSettings {
  application: string;
  environment: string;
  debug: boolean;
  api_prefix: string;
  access_token_expire_minutes: number;
  max_upload_size_mb: number;
  allowed_invoice_formats: string[];
  tesseract_language: string;
  smtp_enabled: boolean;
  smtp_delivery_mode: "smtp" | "outbox";
  smtp_from_email: string;
  rpa_enabled: boolean;
  rpa_target_url: string;
  database_engine: string;
}
