import { useEffect, useState } from "react";
import {
  createCity,
  createConnection,
  fetchAllRoutes,
  fetchBestRoute,
  fetchCities,
} from "./api";

const initialRouteForm = { origin: "", destination: "" };
const initialCityForm = { name: "" };
const initialConnectionForm = { origin: "", destination: "", distance: "" };

const IconPin = ({ color = "currentColor", size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
    <circle cx="12" cy="10" r="3"/>
  </svg>
);

const IconArrow = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12"/>
    <polyline points="12 5 19 12 12 19"/>
  </svg>
);

const IconSearch = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"/>
    <line x1="21" y1="21" x2="16.65" y2="16.65"/>
  </svg>
);

const IconList = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="8" y1="6" x2="21" y2="6"/>
    <line x1="8" y1="12" x2="21" y2="12"/>
    <line x1="8" y1="18" x2="21" y2="18"/>
    <line x1="3" y1="6" x2="3.01" y2="6"/>
    <line x1="3" y1="12" x2="3.01" y2="12"/>
    <line x1="3" y1="18" x2="3.01" y2="18"/>
  </svg>
);

const IconPlus = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"/>
    <line x1="5" y1="12" x2="19" y2="12"/>
  </svg>
);

const IconRuler = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21.3 8.7 8.7 21.3a2.98 2.98 0 0 1-4.2 0l-1.8-1.8a2.98 2.98 0 0 1 0-4.2L15.3 2.7a2.98 2.98 0 0 1 4.2 0l1.8 1.8a2.98 2.98 0 0 1 0 4.2z"/>
    <line x1="7.5" y1="10.5" x2="9" y2="12"/>
    <line x1="10.5" y1="7.5" x2="12" y2="9"/>
    <line x1="13.5" y1="4.5" x2="15" y2="6"/>
  </svg>
);

const IconCheck = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const IconX = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
);

const IconRoute = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="6" cy="19" r="3"/>
    <path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/>
    <circle cx="18" cy="5" r="3"/>
  </svg>
);

const IconCity = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="9" width="7" height="12"/>
    <rect x="14" y="4" width="7" height="17"/>
    <rect x="14" y="17" width="7" height="4"/>
    <line x1="3" y1="21" x2="21" y2="21"/>
  </svg>
);

const IconNetwork = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="5" r="3"/>
    <circle cx="6" cy="12" r="3"/>
    <circle cx="18" cy="12" r="3"/>
    <line x1="12" y1="8" x2="6" y2="12"/>
    <line x1="12" y1="8" x2="18" y2="12"/>
    <circle cx="12" cy="19" r="3"/>
    <line x1="6" cy="12" x2="12" y2="19"/>
    <line x1="18" y1="12" x2="12" y2="19"/>
  </svg>
);

const IconDistance = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="3" y1="12" x2="21" y2="12"/>
    <polyline points="3 9 3 15 9 12 3 9"/>
    <polyline points="21 9 21 15 15 12 21 9"/>
  </svg>
);

const IconSettings = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3"/>
    <path d="M12 1v6m0 6v6M4.22 4.22l4.24 4.24m6.08 0l4.24-4.24M1 12h6m6 0h6m-15.78 7.78l4.24-4.24m6.08 0l4.24 4.24"/>
  </svg>
);

const IconMap = ({ size = 14 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/>
    <line x1="8" y1="2" x2="8" y2="18"/>
    <line x1="16" y1="6" x2="16" y2="22"/>
  </svg>
);

function FieldInput({ name, value, onChange, placeholder, type = "text", min, cities }) {
  const isNumber = type === "number";

  return (
    <div className="input-wrap">
      {isNumber ? <IconRuler /> : <IconPin />}

      {cities && type === "text" ? (
        <select name={name} value={value} onChange={onChange} required>
          <option value="">{placeholder || "Seleccionar ciudad"}</option>
          {cities.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      ) : (
        <input
          name={name}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          type={type}
          min={min}
          required
        />
      )}
    </div>
  );
}

function App() {
  const [cities, setCities] = useState([]);
  const [bestRouteForm, setBestRouteForm] = useState(initialRouteForm);
  const [routesForm, setRoutesForm] = useState(initialRouteForm);
  const [cityForm, setCityForm] = useState(initialCityForm);
  const [connectionForm, setConnectionForm] = useState(initialConnectionForm);
  const [bestRoute, setBestRoute] = useState(null);
  const [allRoutes, setAllRoutes] = useState([]);
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [loadingSection, setLoadingSection] = useState("");
  const [activeTab, setActiveTab] = useState("search");

  useEffect(() => { loadCities(); }, []);

  function clearMessages() { setStatusMessage(""); setErrorMessage(""); }

  async function loadCities() {
    try { setCities(await fetchCities()); }
    catch (e) { setErrorMessage(e.message); }
  }

  function makeHandler(setter) {
    return (e) => {
      const { name, value } = e.target;
      setter((f) => ({ ...f, [name]: value }));
    };
  }

  async function withLoading(key, fn) {
    clearMessages();
    setLoadingSection(key);
    try { await fn(); }
    finally { setLoadingSection(""); }
  }

  async function handleBestRouteSubmit(e) {
    e.preventDefault();
    await withLoading("best-route", async () => {
      try {
        const result = await fetchBestRoute(bestRouteForm);
        setBestRoute(result);
        setAllRoutes([]);
        setStatusMessage("Ruta encontrada correctamente.");
      } catch (err) { 
        setBestRoute(null);
        setErrorMessage(err.message); 
      }
    });
  }

  async function handleAllRoutesSubmit(e) {
    e.preventDefault();
    await withLoading("routes", async () => {
      try {
        setBestRoute(null);
        setAllRoutes(await fetchAllRoutes(routesForm));
        setStatusMessage("Rutas consultadas correctamente.");
      } catch (err) { setAllRoutes([]); setErrorMessage(err.message); }
    });
  }

  async function handleCitySubmit(e) {
    e.preventDefault();
    await withLoading("city", async () => {
      try {
        const result = await createCity(cityForm);
        setStatusMessage(result.message);
        setCityForm(initialCityForm);
        await loadCities();
      } catch (err) { setErrorMessage(err.message); }
    });
  }

  async function handleConnectionSubmit(e) {
    e.preventDefault();
    await withLoading("connection", async () => {
      try {
        const result = await createConnection({ ...connectionForm, distance: Number(connectionForm.distance) });
        setStatusMessage(result.message);
        setConnectionForm(initialConnectionForm);
      } catch (err) { setErrorMessage(err.message); }
    });
  }

  return (
    <div className="page-shell">
      <header className="hero">
        <div className="hero-top">
          <div>
            <p className="hero__eyebrow">Practica 1 — IA1</p>
            <h1>Rutas entre ciudades</h1>
            <p className="hero__text">Consulta recorridos, compara distancias y administra ciudades.</p>
          </div>
          <div className="hero-stats">
            <div className="hero-stat">
              <div className="hero-stat-label">Ciudades</div>
              <div className="hero-stat-value">{cities.length}</div>
            </div>
            <div className="hero-stat">
              <div className="hero-stat-label">Rutas</div>
              <div className="hero-stat-value">{bestRoute ? 1 : allRoutes.length || 0}</div>
            </div>
          </div>
        </div>
      </header>

      {(statusMessage || errorMessage) && (
        <div className={`banner ${errorMessage ? "banner--error" : "banner--ok"}`}>
          {errorMessage ? <IconX size={15} /> : <IconCheck size={15} />}
          {errorMessage || statusMessage}
        </div>
      )}

      <main className="grid-layout">
        <div className="sidebar-wrapper">
          <div className="tabs-nav">
            <button 
              className={`tab-btn ${activeTab === "search" ? "active" : ""}`}
              onClick={() => setActiveTab("search")}
            >
              <IconSearch size={14} />
              Buscar
            </button>
            <button 
              className={`tab-btn ${activeTab === "manage" ? "active" : ""}`}
              onClick={() => setActiveTab("manage")}
            >
              <IconPlus size={14} />
              Gestionar
            </button>
          </div>

          {activeTab === "search" && (
            <>
              <section className="card">
                <div className="card-header">
                  <div className="card-icon card-icon--cyan">
                    <IconRoute size={16} />
                  </div>
                  <h2>Ruta más corta</h2>
                </div>
                <p className="card-desc">Encuentra el camino óptimo.</p>
                <form className="form" onSubmit={handleBestRouteSubmit}>
                  <label>
                    <span>Origen</span>
                    <FieldInput
                      name="origin" value={bestRouteForm.origin}
                      onChange={makeHandler(setBestRouteForm)} placeholder="Selecciona una ciudad origen" cities={cities}
                    />
                  </label>
                  <label>
                    <span>Destino</span>
                    <FieldInput
                      name="destination" value={bestRouteForm.destination}
                      onChange={makeHandler(setBestRouteForm)} placeholder="Selecciona una ciudad destino" cities={cities}
                    />
                  </label>
                  <button type="submit" className="btn--blue" disabled={loadingSection === "best-route"}>
                    <IconSearch size={14} />
                    {loadingSection === "best-route" ? "Buscando..." : "Buscar"}
                  </button>
                </form>
              </section>

              <section className="card">
                <div className="card-header">
                  <div className="card-icon card-icon--emerald">
                    <IconNetwork size={16} />
                  </div>
                  <h2>Todas las rutas</h2>
                </div>
                <p className="card-desc">Ver rutas disponibles ordenadas.</p>
                <form className="form" onSubmit={handleAllRoutesSubmit}>
                  <label>
                    <span>Origen</span>
                    <FieldInput
                      name="origin" value={routesForm.origin}
                      onChange={makeHandler(setRoutesForm)} placeholder="Selecciona una ciudad origen" cities={cities}
                    />
                  </label>
                  <label>
                    <span>Destino</span>
                    <FieldInput
                      name="destination" value={routesForm.destination}
                      onChange={makeHandler(setRoutesForm)} placeholder="Selecciona una ciudad destino" cities={cities}
                    />
                  </label>
                  <button type="submit" className="btn--teal" disabled={loadingSection === "routes"}>
                    <IconList size={14} />
                    {loadingSection === "routes" ? "Cargando..." : "Ver rutas"}
                  </button>
                </form>
              </section>
            </>
          )}

          {activeTab === "manage" && (
            <>
              <section className="card">
                <div className="card-header">
                  <div className="card-icon card-icon--orange">
                    <IconCity size={16} />
                  </div>
                  <h2>Agregar ciudad</h2>
                </div>
                <p className="card-desc">Nueva ciudad en la base.</p>
                <form className="form" onSubmit={handleCitySubmit}>
                  <label>
                    <span>Nombre</span>
                    <FieldInput
                      name="name" value={cityForm.name}
                      onChange={makeHandler(setCityForm)} placeholder="totonicapan"
                    />
                  </label>
                  <button type="submit" className="btn--amber" disabled={loadingSection === "city"}>
                    <IconPlus size={14} />
                    {loadingSection === "city" ? "Guardando..." : "Agregar"}
                  </button>
                </form>
              </section>

              <section className="card">
                <div className="card-header">
                  <div className="card-icon card-icon--purple">
                    <IconDistance size={16} />
                  </div>
                  <h2>Agregar conexión</h2>
                </div>
                <p className="card-desc">Nueva carretera entre ciudades.</p>
                <form className="form" onSubmit={handleConnectionSubmit}>
                  <label>
                    <span>Origen</span>
                    <FieldInput
                      name="origin" value={connectionForm.origin}
                      onChange={makeHandler(setConnectionForm)} placeholder="Selecciona una ciudad origen" cities={cities}
                    />
                  </label>
                  <label>
                    <span>Destino</span>
                    <FieldInput
                      name="destination" value={connectionForm.destination}
                      onChange={makeHandler(setConnectionForm)} placeholder="Selecciona una ciudad destino" cities={cities}
                    />
                  </label>
                  <label>
                    <span>Distancia (km)</span>
                    <FieldInput
                      name="distance" value={connectionForm.distance}
                      onChange={makeHandler(setConnectionForm)} placeholder="45" type="number" min="1"
                    />
                  </label>
                  <button type="submit" className="btn--purple" disabled={loadingSection === "connection"}>
                    <IconPlus size={14} />
                    {loadingSection === "connection" ? "Guardando..." : "Agregar"}
                  </button>
                </form>
              </section>
            </>
          )}
        </div>

        <div className="info-panel">
          {bestRoute ? (
            <div className="panel-section">
              <h3 className="panel-title">Mejor ruta encontrada</h3>
              <div className="result">
                <div className="result-label">Recorrido</div>
                <div className="result-route">
                  {bestRoute.route.map((city, i) => (
                    <span key={i} style={{ display: "contents" }}>
                      <span className="route-stop">{city}</span>
                      {i < bestRoute.route.length - 1 && <span className="route-arrow">→</span>}
                    </span>
                  ))}
                </div>
                <div className="result-distance">
                  <IconRuler size={12} />
                  {bestRoute.distance} km en total
                </div>
              </div>
            </div>
          ) : null}

          {allRoutes.length > 0 ? (
            <div className="panel-section">
              <h3 className="panel-title">Rutas disponibles ({allRoutes.length})</h3>
              <div className="routes-list">
                {allRoutes.map((item, i) => (
                  <div className="result" key={`${item.route.join("-")}-${i}`}>
                    <div className="result-route">
                      {item.route.map((city, j) => (
                        <span key={j} style={{ display: "contents" }}>
                          <span className="route-stop">{city}</span>
                          {j < item.route.length - 1 && <span className="route-arrow">→</span>}
                        </span>
                      ))}
                    </div>
                    <div className="result-distance">
                      <IconRuler size={12} />
                      {item.distance} km
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : null}

          {!bestRoute && allRoutes.length === 0 && (
            <div className="panel-empty">
              <div className="empty-icon">📍</div>
              <h3>Información de rutas</h3>
              <p>Busca o carga rutas para verlas aquí</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
