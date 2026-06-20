import {
  Activity,
  Bot,
  ChevronDown,
  FileBarChart,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  Settings,
  Truck,
  Users,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  Link,
  NavLink,
  Outlet,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { getCurrentUser } from "../api/auth";
import { Brand } from "../components/Brand";
import { useAuthStore } from "../store/authStore";

const primaryNavigation = [
  { to: "/", label: "Resumen", icon: LayoutDashboard, end: true },
  { to: "/invoices", label: "Facturas", icon: FileText },
  { to: "/rpa", label: "Automatización RPA", icon: Bot },
  { to: "/reports", label: "Reportes", icon: FileBarChart },
  { to: "/logs", label: "Bitácora", icon: Activity },
  { to: "/providers", label: "Proveedores", icon: Truck },
];

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const user = useAuthStore((state) => state.user);
  const setUser = useAuthStore((state) => state.setUser);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    getCurrentUser().then(setUser).catch(() => undefined);

    const handleUnauthorized = () => {
      logout();
      navigate("/login", { replace: true });
    };
    window.addEventListener("smartinvoice:unauthorized", handleUnauthorized);
    return () =>
      window.removeEventListener(
        "smartinvoice:unauthorized",
        handleUnauthorized,
      );
  }, [logout, navigate, setUser]);

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "sidebar--open" : ""}`}>
        <div className="sidebar__top">
          <Brand />
          <button
            className="icon-button sidebar__close"
            onClick={() => setSidebarOpen(false)}
            aria-label="Cerrar navegación"
          >
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar__nav">
          <span className="sidebar__label">Workspace</span>
          {primaryNavigation.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `nav-item ${isActive ? "nav-item--active" : ""}`
              }
            >
              <Icon size={19} />
              <span>{label}</span>
            </NavLink>
          ))}

          {user?.role === "admin" && (
            <>
              <span className="sidebar__label sidebar__label--spaced">
                Administración
              </span>
              <NavLink
                to="/users"
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "nav-item--active" : ""}`
                }
              >
                <Users size={19} />
                <span>Usuarios</span>
              </NavLink>
              <NavLink
                to="/settings"
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "nav-item--active" : ""}`
                }
              >
                <Settings size={19} />
                <span>Configuración</span>
              </NavLink>
            </>
          )}
        </nav>

        <div className="sidebar__footer">
          <div className="user-card">
            <div className="avatar">{user?.name?.charAt(0) ?? "S"}</div>
            <div className="user-card__text">
              <strong>{user?.name ?? "Usuario"}</strong>
              <span>{user?.role === "admin" ? "Administrador" : "Operador"}</span>
            </div>
            <ChevronDown size={16} />
          </div>
          <button className="logout-button" onClick={handleLogout}>
            <LogOut size={17} />
            Cerrar sesión
          </button>
        </div>
      </aside>

      {sidebarOpen && (
        <button
          className="sidebar-backdrop"
          onClick={() => setSidebarOpen(false)}
          aria-label="Cerrar navegación"
        />
      )}

      <main className="app-main">
        <header className="topbar">
          <button
            className="icon-button topbar__menu"
            onClick={() => setSidebarOpen(true)}
            aria-label="Abrir navegación"
          >
            <Menu size={21} />
          </button>
          <div>
            <span className="topbar__eyebrow">SmartInvoice</span>
            <strong>Centro de operaciones</strong>
          </div>
          <div className="topbar__status">
            <span className="status-dot" />
            API conectada
          </div>
        </header>
        <div className="page-container">
          <ProcessGuide pathname={location.pathname} />
          <Outlet />
        </div>
      </main>
    </div>
  );
}

const processSteps = [
  { to: "/invoices", label: "Facturas", detail: "Carga el documento" },
  { to: "/invoices", label: "OCR y validación", detail: "Extrae y revisa datos" },
  { to: "/rpa", label: "RPA", detail: "Registra en el sistema" },
  { to: "/reports", label: "Reporte y correo", detail: "Genera y notifica" },
  { to: "/logs", label: "Bitácora", detail: "Comprueba evidencias" },
];

function ProcessGuide({ pathname }: { pathname: string }) {
  return (
    <section className="process-guide" aria-label="Flujo de SmartInvoice">
      <div className="process-guide__heading">
        <div>
          <span>Flujo recomendado</span>
          <strong>¿Dónde estoy y qué sigue?</strong>
        </div>
        <Link to="/">Ver guía completa</Link>
      </div>
      <div className="process-guide__steps">
        {processSteps.map((step, index) => (
          <Link
            key={`${step.label}-${index}`}
            to={step.to}
            className={pathname === step.to ? "is-active" : ""}
          >
            <i>{index + 1}</i>
            <span>
              <strong>{step.label}</strong>
              <small>{step.detail}</small>
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}
