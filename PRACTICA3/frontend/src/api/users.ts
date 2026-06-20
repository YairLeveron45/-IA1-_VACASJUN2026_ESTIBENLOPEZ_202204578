import { apiClient } from "./client";
import type { User } from "../types/auth";
import type {
  PasswordResetPayload,
  UserCreatePayload,
  UserListResponse,
  UserUpdatePayload,
} from "../types/user";

/** Consulta usuarios con paginación. */
export async function listUsers(
  page = 1,
  pageSize = 20,
): Promise<UserListResponse> {
  const { data } = await apiClient.get<UserListResponse>("/users", {
    params: { page, page_size: pageSize },
  });
  return data;
}

/** Crea una cuenta y asigna su rol inicial. */
export async function createUser(
  payload: UserCreatePayload,
): Promise<User> {
  const { data } = await apiClient.post<User>("/users", payload);
  return data;
}

/** Modifica los datos o el estado de una cuenta. */
export async function updateUser(
  userId: number,
  payload: UserUpdatePayload,
): Promise<User> {
  const { data } = await apiClient.patch<User>(`/users/${userId}`, payload);
  return data;
}

/** Desactiva una cuenta sin borrar su historial. */
export async function deactivateUser(userId: number): Promise<User> {
  const { data } = await apiClient.delete<User>(`/users/${userId}`);
  return data;
}

/** Permite al administrador restablecer una contraseña. */
export async function resetUserPassword(
  userId: number,
  payload: PasswordResetPayload,
): Promise<User> {
  const { data } = await apiClient.patch<User>(
    `/users/${userId}/password`,
    payload,
  );
  return data;
}
