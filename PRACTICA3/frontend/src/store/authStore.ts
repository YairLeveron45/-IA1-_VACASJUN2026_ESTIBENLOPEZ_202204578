import { create } from "zustand";
import type { LoginResponse, User } from "../types/auth";

const TOKEN_KEY = "smartinvoice_token";
const USER_KEY = "smartinvoice_user";

function loadUser(): User | null {
  const value = localStorage.getItem(USER_KEY);
  if (!value) return null;

  try {
    return JSON.parse(value) as User;
  } catch {
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  setSession: (session: LoginResponse) => void;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem(TOKEN_KEY),
  user: loadUser(),
  isAuthenticated: Boolean(localStorage.getItem(TOKEN_KEY)),
  setSession: (session) => {
    localStorage.setItem(TOKEN_KEY, session.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(session.user));
    set({
      token: session.access_token,
      user: session.user,
      isAuthenticated: true,
    });
  },
  setUser: (user) => {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    set({ user });
  },
  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    set({ token: null, user: null, isAuthenticated: false });
  },
}));
