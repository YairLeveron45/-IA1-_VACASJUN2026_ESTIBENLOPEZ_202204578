import type { User, UserRole } from "./auth";

export interface UserListResponse {
  items: User[];
  total: number;
  page: number;
  page_size: number;
}

export interface UserCreatePayload {
  name: string;
  email: string;
  password: string;
  role: UserRole;
}

export interface UserUpdatePayload {
  name?: string;
  email?: string;
  role?: UserRole;
  is_active?: boolean;
}

export interface PasswordResetPayload {
  new_password: string;
}
