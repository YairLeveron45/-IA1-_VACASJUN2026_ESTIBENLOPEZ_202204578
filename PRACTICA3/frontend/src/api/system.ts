import type { HealthResponse, SystemSettings } from "../types/system";
import { apiClient } from "./client";

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get<HealthResponse>("/health");
  return data;
}

export async function getSystemSettings(): Promise<SystemSettings> {
  const { data } = await apiClient.get<SystemSettings>("/settings");
  return data;
}
