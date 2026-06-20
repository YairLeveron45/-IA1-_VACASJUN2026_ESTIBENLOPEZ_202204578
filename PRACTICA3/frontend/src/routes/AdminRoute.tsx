import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "../store/authStore";

export function AdminRoute() {
  const user = useAuthStore((state) => state.user);
  return user?.role === "admin" ? <Outlet /> : <Navigate to="/" replace />;
}
