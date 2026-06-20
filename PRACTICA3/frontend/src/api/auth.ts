import { apiClient } from "./client";
import type { LoginPayload, LoginResponse, User } from "../types/auth";

/** Inicia sesión y devuelve el token junto con el usuario. */
export async function loginRequest(
  payload: LoginPayload,
): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>("/auth/login", payload);
  return data;
}

/** Recupera el usuario asociado al token almacenado. */
export async function getCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<User>("/auth/me");
  return data;
}
