import { useEffect, useState } from "react";

import {
  fetchHistory,
  fetchSymptoms,
  fetchSymptomSuggestions,
  requestDiagnosis,
} from "./api";
import AdminLogin from "./components/AdminLogin";
import AdminPanel from "./components/AdminPanel";
import DiagnosisResult from "./components/DiagnosisResult";
import HistoryPanel from "./components/HistoryPanel";
import SymptomSelector from "./components/SymptomSelector";
import TelegramForm from "./components/TelegramForm";

function App() {
  const [currentView, setCurrentView] = useState("diagnosis");
  const [adminToken, setAdminToken] = useState(
    () => localStorage.getItem("doctor-byte-admin-token") || ""
  );
  const [symptoms, setSymptoms] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [suggestedSymptoms, setSuggestedSymptoms] = useState([]);
  const [diagnosis, setDiagnosis] = useState(null);
  const [history, setHistory] = useState([]);
  const [notifyTelegram, setNotifyTelegram] = useState(false);
  const [loadingSymptoms, setLoadingSymptoms] = useState(true);
  const [submittingDiagnosis, setSubmittingDiagnosis] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState("");

  async function loadDiagnosisData() {
    setLoadingSymptoms(true);
    setLoadingHistory(true);

    try {
      const [symptomsResponse, historyResponse] = await Promise.all([
        fetchSymptoms(),
        fetchHistory(),
      ]);
      setSymptoms(symptomsResponse.items);
      setHistory(historyResponse.items);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoadingSymptoms(false);
      setLoadingHistory(false);
    }
  }

  useEffect(() => {
    loadDiagnosisData();
  }, []);

  useEffect(() => {
    if (currentView === "diagnosis") {
      loadDiagnosisData();
    }
  }, [currentView]);

  useEffect(() => {
    async function loadSuggestions() {
      if (selectedSymptoms.length === 0) {
        setSuggestedSymptoms([]);
        return;
      }

      try {
        const response = await fetchSymptomSuggestions(selectedSymptoms);
        setSuggestedSymptoms(response.items);
      } catch {
        setSuggestedSymptoms([]);
      }
    }

    loadSuggestions();
  }, [selectedSymptoms]);

  function handleSymptomToggle(symptom) {
    setSelectedSymptoms((prev) =>
      prev.includes(symptom)
        ? prev.filter((item) => item !== symptom)
        : [...prev, symptom]
    );
  }

  function handleClearSelection() {
    setSelectedSymptoms([]);
    setSuggestedSymptoms([]);
    setDiagnosis(null);
    setError("");
  }

  function handleAdminLogin(token) {
    localStorage.setItem("doctor-byte-admin-token", token);
    setAdminToken(token);
  }

  function handleAdminLogout() {
    localStorage.removeItem("doctor-byte-admin-token");
    setAdminToken("");
  }

  async function handleSubmitDiagnosis(event) {
    event.preventDefault();
    setSubmittingDiagnosis(true);
    setError("");

    try {
      const diagnosisResponse = await requestDiagnosis({
        symptoms: selectedSymptoms,
        notify_telegram: notifyTelegram,
        chat_id: null,
      });
      setDiagnosis(diagnosisResponse);

      const historyResponse = await fetchHistory();
      setHistory(historyResponse.items);
    } catch (requestError) {
      setDiagnosis(null);
      setError(requestError.message);
    } finally {
      setSubmittingDiagnosis(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <div className="hero-left">
          <div className="hero-icon">
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M3 12a9 9 0 1 0 18 0 9 9 0 0 0-18 0" />
              <path d="M12 8v4l2.5 2.5" />
            </svg>
          </div>
          <div>
            <h1 className="hero-title">
              Doctor <span>Byte</span>
            </h1>
            <p className="hero-sub">
              Selecciona sintomas del equipo y recibe un diagnostico preliminar
              generado por Prolog.
            </p>
          </div>
        </div>
        <span className="status-pill">
          <span className="status-dot" />
          Sistema activo - Fase 1
        </span>
      </header>

      <nav className="view-tabs" aria-label="Navegacion principal">
        <button
          className={currentView === "diagnosis" ? "view-tab active" : "view-tab"}
          type="button"
          onClick={() => setCurrentView("diagnosis")}
        >
          Diagnostico
        </button>
        <button
          className={currentView === "admin" ? "view-tab active" : "view-tab"}
          type="button"
          onClick={() => setCurrentView("admin")}
        >
          Admin
        </button>
      </nav>

      {currentView === "diagnosis" && error ? (
        <p className="alert alert-error">{error}</p>
      ) : null}

      {currentView === "diagnosis" ? (
        <section className="workspace">
          <form className="dashboard-grid" onSubmit={handleSubmitDiagnosis}>
            <SymptomSelector
              symptoms={symptoms}
              selectedSymptoms={selectedSymptoms}
              suggestedSymptoms={suggestedSymptoms}
              loading={loadingSymptoms}
              onToggle={handleSymptomToggle}
              onClear={handleClearSelection}
            />

            <div className="side-stack">
              <DiagnosisResult
                diagnosis={diagnosis}
                selectedCount={selectedSymptoms.length}
                loading={submittingDiagnosis}
              />

              <TelegramForm
                notifyTelegram={notifyTelegram}
                onToggle={setNotifyTelegram}
              />

              <div className="panel actions-panel">
                <div className="panel-header">
                  <div className="panel-heading">
                    <div className="panel-heading-icon">
                      <svg
                        width="15"
                        height="15"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <polygon points="5 3 19 12 5 21 5 3" />
                      </svg>
                    </div>
                    <div>
                      <div className="panel-title">Generar diagnostico</div>
                    </div>
                  </div>
                </div>
                <p className="actions-desc">
                  Cuando hayas seleccionado los sintomas, el backend de Prolog
                  procesara la consulta y devolvera un diagnostico preliminar.
                </p>
                <button
                  className="primary-button"
                  type="submit"
                  disabled={submittingDiagnosis || selectedSymptoms.length === 0}
                >
                  {submittingDiagnosis ? "Analizando..." : "Generar diagnostico"}
                </button>
              </div>
            </div>

            <HistoryPanel history={history} loading={loadingHistory} />
          </form>
        </section>
      ) : (
        <section className="workspace">
          {adminToken ? (
            <AdminPanel token={adminToken} onLogout={handleAdminLogout} />
          ) : (
            <AdminLogin onLogin={handleAdminLogin} />
          )}
        </section>
      )}
    </main>
  );
}

export default App;
