import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { apiRequest, clearToken, getToken, setToken } from "./api";
import "./styles.css";

const emptyFaq = { question: "", answer: "", category_id: "", active: true };
const emptyCategory = { name: "", description: "" };
const emptyAdmin = { username: "", password: "" };

function App() {
  const [token, updateToken] = useState(getToken());
  const [view, setView] = useState("dashboard");

  if (!token) {
    return <Login onLogin={(newToken) => { setToken(newToken); updateToken(newToken); }} />;
  }

  return (
    <>
      <header className="topbar">
        <strong>SmartBot</strong>
        <nav>
          <button onClick={() => setView("dashboard")}>Inicio</button>
          <button onClick={() => setView("faqs")}>Preguntas</button>
          <button onClick={() => setView("categories")}>Categorias</button>
          <button onClick={() => setView("admins")}>Admins</button>
          <button onClick={() => setView("settings")}>Configuracion</button>
          <button className="ghost" onClick={() => { clearToken(); updateToken(null); }}>Salir</button>
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
        <h1>SmartBot</h1>
        <p>Panel administrativo</p>
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

function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    apiRequest("/api/dashboard").then(setData).catch(console.error);
  }, []);

  if (!data) return <p>Cargando...</p>;

  return (
    <>
      <section className="hero">
        <h1>Panel administrativo</h1>
        <p>Administra las respuestas que usa el bot de Telegram.</p>
      </section>
      <section className="stats-grid">
        <article><strong>{data.stats.faqs}</strong><span>Preguntas</span></article>
        <article><strong>{data.stats.categories}</strong><span>Categorias</span></article>
        <article><strong>{data.stats.logs}</strong><span>Consultas</span></article>
        <article><strong>{data.stats.users}</strong><span>Usuarios</span></article>
      </section>
      <section className="dashboard-grid">
        <div>
          <h2>Consultas frecuentes</h2>
          <table>
            <tbody>
              {data.popular.length === 0 && <tr><td>Aun no hay consultas registradas.</td></tr>}
              {data.popular.map((row) => <tr key={row.query_text}><td>{row.query_text}</td><td>{row.total}</td></tr>)}
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
      <h1>Administradores</h1>
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
  const [error, setError] = useState("");

  async function load() {
    setCategories(await apiRequest("/api/categories"));
  }

  useEffect(() => { load(); }, []);

  async function save(event) {
    event.preventDefault();
    setError("");
    try {
      await apiRequest(form.id ? `/api/categories/${form.id}` : "/api/categories", {
        method: form.id ? "PUT" : "POST",
        body: JSON.stringify(form),
      });
      setForm(emptyCategory);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove(id) {
    await apiRequest(`/api/categories/${id}`, { method: "DELETE" });
    await load();
  }

  return (
    <>
      <h1>Categorias</h1>
      <form className="panel-form" onSubmit={save}>
        {error && <div className="alert">{error}</div>}
        <input placeholder="Nombre" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <input placeholder="Descripcion" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <button>{form.id ? "Guardar categoria" : "Crear categoria"}</button>
      </form>
      <table>
        <tbody>
          {categories.map((category) => (
            <tr key={category.id}>
              <td>{category.name}</td>
              <td>{category.description}</td>
              <td className="actions">
                <button onClick={() => setForm(category)}>Editar</button>
                <button className="danger" onClick={() => remove(category.id)}>Eliminar</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}

function Faqs() {
  const [faqs, setFaqs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(emptyFaq);

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
    const payload = { ...form, category_id: Number(form.category_id) };
    await apiRequest(form.id ? `/api/faqs/${form.id}` : "/api/faqs", {
      method: form.id ? "PUT" : "POST",
      body: JSON.stringify(payload),
    });
    setForm(emptyFaq);
    await load();
  }

  async function remove(id) {
    await apiRequest(`/api/faqs/${id}`, { method: "DELETE" });
    await load();
  }

  return (
    <>
      <h1>Preguntas y respuestas</h1>
      <form className="panel-form" onSubmit={save}>
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
            <h3>{faq.question}</h3>
            <p>{faq.answer}</p>
            <div className="actions">
              <button onClick={() => setForm(faq)}>Editar</button>
              <button className="danger" onClick={() => remove(faq.id)}>Eliminar</button>
            </div>
          </article>
        ))}
      </section>
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
      <h1>Configuracion</h1>
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
