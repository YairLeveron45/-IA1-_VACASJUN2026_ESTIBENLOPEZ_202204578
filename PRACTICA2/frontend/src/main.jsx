import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { apiRequest, clearToken, getToken, setToken } from "./api";
import "./styles.css";

const emptyFaq = { question: "", answer: "", category_id: "", active: true };
const emptyCategory = { name: "", description: "" };
const emptyAdmin = { username: "", password: "" };

function Icon({ name }) {
  const icons = {
    home: (
      <>
        <path d="M3 10.5 12 3l9 7.5" />
        <path d="M5 9.5V21h14V9.5" />
        <path d="M9 21v-7h6v7" />
      </>
    ),
    message: (
      <>
        <path d="M21 11.5a8.4 8.4 0 0 1-8.8 8.3 9.3 9.3 0 0 1-3.9-.8L3 20l1.1-4.5A8.2 8.2 0 0 1 3 11.5C3 6.8 7 3 12 3s9 3.8 9 8.5Z" />
        <path d="M8 10h8" />
        <path d="M8 14h5" />
      </>
    ),
    folder: (
      <>
        <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" />
        <path d="M3 10h18" />
      </>
    ),
    users: (
      <>
        <path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2" />
        <path d="M9.5 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z" />
        <path d="M22 21v-2a4 4 0 0 0-3-3.8" />
        <path d="M16 3.2a4 4 0 0 1 0 7.6" />
      </>
    ),
    settings: (
      <>
        <path d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Z" />
        <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.3a2 2 0 1 1-4 0V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1A2 2 0 1 1 4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.6-1H2.7a2 2 0 1 1 0-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7A2 2 0 1 1 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3h.1a1.7 1.7 0 0 0 .9-1.6v-.3a2 2 0 1 1 4 0V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1A2 2 0 1 1 19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9v.1A1.7 1.7 0 0 0 21 10h.3a2 2 0 1 1 0 4H21a1.7 1.7 0 0 0-1.6 1Z" />
      </>
    ),
    logout: (
      <>
        <path d="M10 17l5-5-5-5" />
        <path d="M15 12H3" />
        <path d="M21 3v18" />
      </>
    ),
    chart: (
      <>
        <path d="M4 19V5" />
        <path d="M4 19h17" />
        <path d="M8 16v-5" />
        <path d="M13 16V8" />
        <path d="M18 16v-3" />
      </>
    ),
    spark: (
      <>
        <path d="M13 2 5 13h6l-1 9 8-12h-6Z" />
      </>
    ),
    bot: (
      <>
        <path d="M12 6V3" />
        <rect x="5" y="7" width="14" height="12" rx="3" />
        <path d="M9 12h.01" />
        <path d="M15 12h.01" />
        <path d="M9 16h6" />
      </>
    ),
  };

  return (
    <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">
      {icons[name]}
    </svg>
  );
}

function App() {
  const [token, updateToken] = useState(getToken());
  const [view, setView] = useState("dashboard");

  if (!token) {
    return <Login onLogin={(newToken) => { setToken(newToken); updateToken(newToken); }} />;
  }

  return (
    <>
      <header className="topbar">
        <strong><span className="brand-mark"><Icon name="bot" /></span>SmartBot</strong>
        <nav>
          <button className={view === "dashboard" ? "active" : ""} onClick={() => setView("dashboard")}><Icon name="home" />Inicio</button>
          <button className={view === "faqs" ? "active" : ""} onClick={() => setView("faqs")}><Icon name="message" />Preguntas</button>
          <button className={view === "categories" ? "active" : ""} onClick={() => setView("categories")}><Icon name="folder" />Categorias</button>
          <button className={view === "admins" ? "active" : ""} onClick={() => setView("admins")}><Icon name="users" />Admins</button>
          <button className={view === "settings" ? "active" : ""} onClick={() => setView("settings")}><Icon name="settings" />Configuracion</button>
          <button className="ghost" onClick={() => { clearToken(); updateToken(null); }}><Icon name="logout" />Salir</button>
        </nav>
      </header>
      <main className="container">
        {view === "dashboard" && <Dashboard />}
        {view === "faqs" && <Faqs />}
        {view === "categories" && <Categories />}
        {view === "admins" && <AdminUsers />}
        {view === "settings" && <Settings />}
      </main>
    </>
  );
}

function Login({ onLogin }) {
  const [form, setForm] = useState({ username: "IA1-User", password: "IA1-password@_new" });
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setError("");
    try {
      const data = await apiRequest("/api/auth/login", {
        method: "POST",
        body: JSON.stringify(form),
      });
      onLogin(data.access_token);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <main className="login-page">
      <form className="login-card" onSubmit={submit}>
        <div className="login-orb"><Icon name="bot" /></div>
        <span className="eyebrow">Panel administrativo</span>
        <h1>SmartBot</h1>
        <p>Gestion de respuestas para Telegram</p>
        {error && <div className="alert">{error}</div>}
        <label>Usuario</label>
        <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <label>Contrasena</label>
        <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <button type="submit">Ingresar</button>
      </form>
    </main>
  );
}

function Modal({ title, children, onClose }) {
  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal-card">
        <div className="modal-head">
          <h2>{title}</h2>
          <button type="button" className="ghost icon-button" onClick={onClose}>x</button>
        </div>
        {children}
      </div>
    </div>
  );
}

function ConfirmDialog({ title, message, confirmText = "Confirmar", onCancel, onConfirm }) {
  return (
    <Modal title={title} onClose={onCancel}>
      <p className="modal-copy">{message}</p>
      <div className="modal-actions">
        <button type="button" className="ghost" onClick={onCancel}>Cancelar</button>
        <button type="button" className="danger" onClick={onConfirm}>{confirmText}</button>
      </div>
    </Modal>
  );
}

function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    apiRequest("/api/dashboard").then(setData).catch(console.error);
  }, []);

  if (!data) return <p>Cargando...</p>;

  return (
    <>
      <section className="hero">
        <div>
          <span className="eyebrow">Resumen del sistema</span>
          <h1>Panel administrativo</h1>
          <p>Administra las respuestas que usa el bot de Telegram.</p>
        </div>
        <div className="hero-badge"><Icon name="spark" /> API activa</div>
      </section>
      <section className="stats-grid">
        <article><span className="stat-icon"><Icon name="message" /></span><strong>{data.stats.faqs}</strong><span>Preguntas</span></article>
        <article><span className="stat-icon"><Icon name="folder" /></span><strong>{data.stats.categories}</strong><span>Categorias</span></article>
        <article><span className="stat-icon"><Icon name="chart" /></span><strong>{data.stats.logs}</strong><span>Consultas</span></article>
        <article><span className="stat-icon"><Icon name="users" /></span><strong>{data.stats.users}</strong><span>Usuarios</span></article>
      </section>
      <section className="dashboard-grid">
        <div>
          <h2>Consultas frecuentes</h2>
          <table>
            <thead>
              <tr><th>Consulta</th><th>Chat ID</th><th>Total</th></tr>
            </thead>
            <tbody>
              {data.popular.length === 0 && <tr><td colSpan="3">Aun no hay consultas registradas.</td></tr>}
              {data.popular.map((row) => (
                <tr key={row.query_text}>
                  <td>{row.query_text}</td>
                  <td>{row.telegram_user || "Sin registro"}</td>
                  <td>{row.total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div>
          <h2>Categorias mas consultadas</h2>
          <table>
            <tbody>
              {data.category_stats.length === 0 && <tr><td>Aun no hay categorias consultadas.</td></tr>}
              {data.category_stats.map((row) => <tr key={row.category}><td>{row.category}</td><td>{row.total}</td></tr>)}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function AdminUsers() {
  const [admins, setAdmins] = useState([]);
  const [form, setForm] = useState(emptyAdmin);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  async function load() {
    setAdmins(await apiRequest("/api/admin-users"));
  }

  useEffect(() => { load(); }, []);

  async function save(event) {
    event.preventDefault();
    setError("");
    setSaved(false);
    try {
      await apiRequest("/api/admin-users", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setForm(emptyAdmin);
      setSaved(true);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <section className="page-head">
        <span className="page-icon"><Icon name="users" /></span>
        <div>
          <h1>Administradores</h1>
          <p>Usuarios con acceso al panel administrativo.</p>
        </div>
      </section>
      <form className="panel-form" onSubmit={save}>
        {error && <div className="alert">{error}</div>}
        {saved && <div className="success">Administrador registrado</div>}
        <label>Nuevo usuario administrador</label>
        <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder="usuario_admin" required />
        <label>Contrasena</label>
        <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} placeholder="Minimo 8 caracteres" required />
        <button type="submit">Registrar administrador</button>
      </form>
      <table>
        <thead>
          <tr><th>ID</th><th>Usuario</th></tr>
        </thead>
        <tbody>
          {admins.map((admin) => (
            <tr key={admin.id}><td>{admin.id}</td><td>{admin.username}</td></tr>
          ))}
        </tbody>
      </table>
    </>
  );
}

function Categories() {
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(emptyCategory);
  const [editForm, setEditForm] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    setCategories(await apiRequest("/api/categories"));
  }

  useEffect(() => { load(); }, []);

  async function save(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    try {
      await apiRequest("/api/categories", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setForm(emptyCategory);
      setNotice("Categoria creada correctamente.");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function update(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    try {
      await apiRequest(`/api/categories/${editForm.id}`, {
        method: "PUT",
        body: JSON.stringify(editForm),
      });
      setEditForm(null);
      setNotice("Categoria actualizada correctamente.");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove() {
    setError("");
    setNotice("");
    try {
      await apiRequest(`/api/categories/${deleteTarget.id}`, { method: "DELETE" });
      setDeleteTarget(null);
      setNotice("Categoria eliminada correctamente.");
      await load();
    } catch (err) {
      setDeleteTarget(null);
      setError(err.message);
    }
  }

  return (
    <>
      <section className="page-head">
        <span className="page-icon"><Icon name="folder" /></span>
        <div>
          <h1>Categorias</h1>
          <p>Organiza las preguntas frecuentes por temas.</p>
        </div>
      </section>
      <form className="panel-form" onSubmit={save}>
        {error && <div className="alert">{error}</div>}
        {notice && <div className="success">{notice}</div>}
        <input placeholder="Nombre" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <input placeholder="Descripcion" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <button>Crear categoria</button>
      </form>
      <table>
        <tbody>
          {categories.map((category) => (
            <tr key={category.id}>
              <td>{category.name}</td>
              <td>{category.description}</td>
              <td className="actions">
                <button onClick={() => { setError(""); setNotice(""); setEditForm(category); }}>Editar</button>
                <button className="danger" onClick={() => { setError(""); setNotice(""); setDeleteTarget(category); }}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {editForm && (
        <Modal title="Editar categoria" onClose={() => setEditForm(null)}>
          <form className="modal-form" onSubmit={update}>
            {error && <div className="alert">{error}</div>}
            <label>Nombre</label>
            <input value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} required />
            <label>Descripcion</label>
            <input value={editForm.description} onChange={(e) => setEditForm({ ...editForm, description: e.target.value })} />
            <div className="modal-actions">
              <button type="button" className="ghost" onClick={() => setEditForm(null)}>Cancelar</button>
              <button type="submit">Confirmar cambios</button>
            </div>
          </form>
        </Modal>
      )}
      {deleteTarget && (
        <ConfirmDialog
          title="Eliminar categoria"
          message={`Estas seguro de eliminar la categoria "${deleteTarget.name}"?`}
          confirmText="Eliminar"
          onCancel={() => setDeleteTarget(null)}
          onConfirm={remove}
        />
      )}
    </>
  );
}

function Faqs() {
  const [faqs, setFaqs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(emptyFaq);
  const [editForm, setEditForm] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function load() {
    const [faqData, categoryData] = await Promise.all([
      apiRequest("/api/faqs"),
      apiRequest("/api/categories"),
    ]);
    setFaqs(faqData);
    setCategories(categoryData);
  }

  useEffect(() => { load(); }, []);

  async function save(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    const payload = { ...form, category_id: Number(form.category_id) };
    try {
      await apiRequest("/api/faqs", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setForm(emptyFaq);
      setNotice("Pregunta creada correctamente.");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function update(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    const payload = { ...editForm, category_id: Number(editForm.category_id) };
    try {
      await apiRequest(`/api/faqs/${editForm.id}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      setEditForm(null);
      setNotice("Pregunta actualizada correctamente.");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove() {
    setError("");
    setNotice("");
    try {
      await apiRequest(`/api/faqs/${deleteTarget.id}`, { method: "DELETE" });
      setDeleteTarget(null);
      setNotice("Pregunta eliminada correctamente.");
      await load();
    } catch (err) {
      setDeleteTarget(null);
      setError(err.message);
    }
  }

  return (
    <>
      <section className="page-head">
        <span className="page-icon"><Icon name="message" /></span>
        <div>
          <h1>Preguntas y respuestas</h1>
          <p>Contenido que el bot utiliza para responder consultas.</p>
        </div>
      </section>
      <form className="panel-form" onSubmit={save}>
        {error && <div className="alert">{error}</div>}
        {notice && <div className="success">{notice}</div>}
        <input placeholder="Pregunta" value={form.question} onChange={(e) => setForm({ ...form, question: e.target.value })} required />
        <textarea placeholder="Respuesta" value={form.answer} onChange={(e) => setForm({ ...form, answer: e.target.value })} required />
        <select value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })} required>
          <option value="">Selecciona categoria</option>
          {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
        </select>
        <label className="check">
          <input type="checkbox" checked={form.active} onChange={(e) => setForm({ ...form, active: e.target.checked })} />
          Activa
        </label>
        <button>{form.id ? "Guardar pregunta" : "Crear pregunta"}</button>
      </form>
      <section className="list">
        {faqs.map((faq) => (
          <article className="item" key={faq.id}>
            <div className="item-title">
              <span><Icon name="message" /></span>
              <h3>{faq.question}</h3>
            </div>
            <p>{faq.answer}</p>
            <div className="actions">
              <button onClick={() => { setError(""); setNotice(""); setEditForm(faq); }}>Editar</button>
              <button className="danger" onClick={() => { setError(""); setNotice(""); setDeleteTarget(faq); }}>Eliminar</button>
            </div>
          </article>
        ))}
      </section>
      {editForm && (
        <Modal title="Editar pregunta" onClose={() => setEditForm(null)}>
          <form className="modal-form" onSubmit={update}>
            {error && <div className="alert">{error}</div>}
            <label>Pregunta</label>
            <input value={editForm.question} onChange={(e) => setEditForm({ ...editForm, question: e.target.value })} required />
            <label>Respuesta</label>
            <textarea value={editForm.answer} onChange={(e) => setEditForm({ ...editForm, answer: e.target.value })} required />
            <label>Categoria</label>
            <select value={editForm.category_id} onChange={(e) => setEditForm({ ...editForm, category_id: e.target.value })} required>
              <option value="">Selecciona categoria</option>
              {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
            </select>
            <label className="check">
              <input type="checkbox" checked={editForm.active} onChange={(e) => setEditForm({ ...editForm, active: e.target.checked })} />
              Activa
            </label>
            <div className="modal-actions">
              <button type="button" className="ghost" onClick={() => setEditForm(null)}>Cancelar</button>
              <button type="submit">Confirmar cambios</button>
            </div>
          </form>
        </Modal>
      )}
      {deleteTarget && (
        <ConfirmDialog
          title="Eliminar pregunta"
          message={`Estas seguro de eliminar la pregunta "${deleteTarget.question}"?`}
          confirmText="Eliminar"
          onCancel={() => setDeleteTarget(null)}
          onConfirm={remove}
        />
      )}
    </>
  );
}

function Settings() {
  const [telegramChatId, setTelegramChatId] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    apiRequest("/api/settings").then((data) => setTelegramChatId(data.telegram_chat_id || ""));
  }, []);

  async function save(event) {
    event.preventDefault();
    await apiRequest("/api/settings", {
      method: "PUT",
      body: JSON.stringify({ telegram_chat_id: telegramChatId }),
    });
    setSaved(true);
  }

  return (
    <>
      <section className="page-head">
        <span className="page-icon"><Icon name="settings" /></span>
        <div>
          <h1>Configuracion</h1>
          <p>Define el chat o grupo autorizado para utilizar el bot.</p>
        </div>
      </section>
      <form className="panel-form" onSubmit={save}>
        {saved && <div className="success">Configuracion guardada</div>}
        <label>ID de chat o grupo de Telegram</label>
        <input value={telegramChatId} onChange={(e) => setTelegramChatId(e.target.value)} placeholder="1305253706" />
        <button>Guardar</button>
      </form>
    </>
  );
}

createRoot(document.getElementById("root")).render(<App />);
