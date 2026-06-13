function formatText(value) {
  return value.replaceAll("_", " ");
}

function formatDate(timestamp) {
  return new Date(timestamp).toLocaleString();
}

function HistoryPanel({ history, loading }) {
  return (
    <section className="panel history-panel">
      <h2>Historial</h2>
      <p>Consultas registradas por el backend.</p>

      {loading ? <p className="muted">Cargando historial...</p> : null}

      {!loading && history.length === 0 ? (
        <p className="muted">
          Todavía no hay diagnósticos guardados.
        </p>
      ) : null}

      {!loading && history.length > 0 ? (
        <div className="history-list">
          {[...history].reverse().map((entry) => {
            const symptoms = entry.matched_symptoms || [];

            return (
              <article className="history-item" key={entry.timestamp}>
                <div className="history-head">
                  <h3>{formatText(entry.failure)}</h3>
                  <span>{formatDate(entry.timestamp)}</span>
                </div>

                <p>{entry.recommendation}</p>

                <div className="chip-list">
                  {symptoms.map((symptom) => (
                    <span
                      className="chip"
                      key={`${entry.timestamp}-${symptom}`}
                    >
                      {formatText(symptom)}
                    </span>
                  ))}
                </div>
              </article>
            );
          })}
        </div>
      ) : null}
    </section>
  );
}

export default HistoryPanel;