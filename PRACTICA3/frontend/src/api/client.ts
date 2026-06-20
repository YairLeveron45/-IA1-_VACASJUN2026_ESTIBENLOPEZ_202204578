import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "/api/v1";

export const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30_000,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("smartinvoice_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      error.response?.status === 401 &&
      !error.config?.url?.includes("/auth/login")
    ) {
      localStorage.removeItem("smartinvoice_token");
      localStorage.removeItem("smartinvoice_user");
      window.dispatchEvent(new Event("smartinvoice:unauthorized"));
    }
    return Promise.reject(error);
  },
);
