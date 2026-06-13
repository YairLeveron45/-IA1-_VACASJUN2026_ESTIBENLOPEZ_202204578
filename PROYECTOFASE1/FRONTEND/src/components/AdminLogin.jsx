import { useState } from "react";

import { loginAdmin } from "../api";

function AdminLogin({ onLogin }) {
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await loginAdmin(password);
      onLogin(response.access_token);
      setPassword("");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel admin-login-panel">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">Acceso administrador</h2>
          <p className="panel-subtitle">
            Ingresa la contrasena para gestionar la base de conocimiento.
          </p>
        </div>
      </div>

      {error ? <p className="alert alert-error">{error}</p> : null}

      <form className="admin-login-form" onSubmit={handleSubmit}>
        <label className="field-group">
          <span className="field-label">Contrasena</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="admin123"
            autoComplete="current-password"
          />
        </label>

        <button
          className="primary-button"
          type="submit"
          disabled={loading || password.trim().length === 0}
        >
          {loading ? "Validando..." : "Entrar al admin"}
        </button>
      </form>
    </section>
  );
}

export default AdminLogin;
