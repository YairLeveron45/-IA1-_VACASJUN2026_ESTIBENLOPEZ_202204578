export interface Provider {
  id: number;
  name: string;
  nit: string;
  email: string | null;
  phone: string | null;
  address: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProviderListResponse {
  items: Provider[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProviderPayload {
  name: string;
  nit: string;
  email: string | null;
  phone: string | null;
  address: string | null;
}

export interface ProviderUpdatePayload extends Partial<ProviderPayload> {
  is_active?: boolean;
}
