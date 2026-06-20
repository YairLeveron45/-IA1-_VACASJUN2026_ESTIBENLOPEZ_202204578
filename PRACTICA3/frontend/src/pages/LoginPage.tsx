import axios from "axios";
import { ArrowRight, Eye, EyeOff, LockKeyhole, Mail } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { loginRequest } from "../api/auth";
import { Brand } from "../components/Brand";
import { useAuthStore } from "../store/authStore";

export function LoginPage() {
  const [email, setEmail] = useState("admin@smartinvoice.com");
  const [password, setPassword] = useState("Admin123!");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const setSession = useAuthStore((state) => state.setSession);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const navigate = useNavigate();
  const location = useLocation();

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const session = await loginRequest({ email, password });
      setSession(session);
      const destination =
        (location.state as { from?: { pathname?: string } } | null)?.from
          ?.pathname ?? "/";
      navigate(destination, { replace: true });
    } catch (requestError) {
      if (axios.isAxiosError(requestError)) {
        setError(
          requestError.response?.data?.detail ??
            "No fue posible conectar con SmartInvoice.",
        );
      } else {
        setError("Ocurrió un error inesperado.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-visual">
        <div className="login-visual__mesh" />
        <Brand />
        <div className="login-visual__content">
          <span className="login-kicker">Inteligencia documental</span>
          <h1>
            De factura a información
            <em> sin trabajo repetitivo.</em>
          </h1>
          <p>
            Centraliza documentos, extrae datos con OCR y automatiza procesos
            administrativos desde un solo lugar.
          </p>
        </div>
        <div className="document-preview">
          <div className="document-preview__paper">
            <div className="paper-line paper-line--short" />
            <div className="paper-title" />
            <div className="paper-grid">
              <span />
              <span />
              <span />
              <span />
            </div>
            <div className="scan-beam" />
          </div>
          <div className="data-chip data-chip--one">
            <span>NIT detectado</span>
            <strong>1234567-8</strong>
          </div>
          <div className="data-chip data-chip--two">
            <span>Precisión OCR</span>
            <strong>98.4%</strong>
          </div>
        </div>
        <span className="login-visual__footer">
          Universidad de San Carlos de Guatemala · IA1
        </span>
      </section>

      <section className="login-panel">
        <div className="login-card">
          <div className="login-card__mobile-brand">
            <Brand compact />
          </div>
          <span className="eyebrow">Acceso seguro</span>
          <h2>Bienvenido de vuelta</h2>
          <p className="login-card__intro">
            Ingresa tus credenciales para continuar al panel administrativo.
          </p>

          <form onSubmit={handleSubmit} className="login-form">
            <label>
              Correo electrónico
              <div className="input-wrap">
                <Mail size={18} />
                <input
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="nombre@empresa.com"
                  autoComplete="email"
                  required
                />
              </div>
            </label>

            <label>
              Contraseña
              <div className="input-wrap">
                <LockKeyhole size={18} />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Tu contraseña"
                  autoComplete="current-password"
                  minLength={8}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((value) => !value)}
                  aria-label={
                    showPassword ? "Ocultar contraseña" : "Mostrar contraseña"
                  }
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </label>

            {error && <div className="form-error">{error}</div>}

            <button
              type="submit"
              className="primary-button"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Verificando..." : "Ingresar al sistema"}
              {!isSubmitting && <ArrowRight size={18} />}
            </button>
          </form>

          <div className="demo-access">
            <span>Acceso de desarrollo</span>
            <code>admin@smartinvoice.com</code>
          </div>
        </div>
      </section>
    </main>
  );
}
