import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./layouts/AppLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { InvoicesPage } from "./pages/InvoicesPage";
import { LoginPage } from "./pages/LoginPage";
import { ProcessingLogsPage } from "./pages/ProcessingLogsPage";
import { ProvidersPage } from "./pages/ProvidersPage";
import { ReportsPage } from "./pages/ReportsPage";
import { RpaPage } from "./pages/RpaPage";
import { SettingsPage } from "./pages/SettingsPage";
import { UsersPage } from "./pages/UsersPage";
import { AdminRoute } from "./routes/AdminRoute";
import { ProtectedRoute } from "./routes/ProtectedRoute";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="invoices" element={<InvoicesPage />} />
          <Route path="providers" element={<ProvidersPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="logs" element={<ProcessingLogsPage />} />
          <Route path="rpa" element={<RpaPage />} />
          <Route element={<AdminRoute />}>
            <Route path="users" element={<UsersPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
