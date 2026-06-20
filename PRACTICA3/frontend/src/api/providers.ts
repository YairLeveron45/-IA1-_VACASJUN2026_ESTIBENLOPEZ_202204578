import type {
  Provider,
  ProviderListResponse,
  ProviderPayload,
  ProviderUpdatePayload,
} from "../types/provider";
import { apiClient } from "./client";

/** Consulta proveedores con paginación. */
export async function listProviders(
  page = 1,
  pageSize = 20,
): Promise<ProviderListResponse> {
  const { data } = await apiClient.get<ProviderListResponse>("/providers", {
    params: { page, page_size: pageSize },
  });
  return data;
}

/** Busca un proveedor por NIT para evitar duplicados. */
export async function lookupProvider(nit: string): Promise<Provider | null> {
  const { data } = await apiClient.get<Provider | null>("/providers/lookup", {
    params: { nit },
  });
  return data;
}

/** Crea un proveedor con los datos del formulario. */
export async function createProvider(
  payload: ProviderPayload,
): Promise<Provider> {
  const { data } = await apiClient.post<Provider>("/providers", payload);
  return data;
}

/** Actualiza únicamente los campos modificados. */
export async function updateProvider(
  providerId: number,
  payload: ProviderUpdatePayload,
): Promise<Provider> {
  const { data } = await apiClient.patch<Provider>(
    `/providers/${providerId}`,
    payload,
  );
  return data;
}

/** Desactiva un proveedor conservando su historial. */
export async function deactivateProvider(
  providerId: number,
): Promise<Provider> {
  const { data } = await apiClient.delete<Provider>(
    `/providers/${providerId}`,
  );
  return data;
}
