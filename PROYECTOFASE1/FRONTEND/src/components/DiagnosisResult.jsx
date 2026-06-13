function formatText(value) {
  return value.replaceAll("_", " ");
}

function DiagnosisResult({ diagnosis, selectedCount, loading }) {
  const matchedSymptoms = diagnosis?.matched_symptoms || [];

  return (
    <section className="panel">
      <h2>Diagnóstico</h2>

      {!diagnosis && !loading ? (
        <p className="muted">
          Selecciona síntomas y genera un diagnóstico. Llevas {selectedCount}{" "}
          síntomas marcados.
        </p>
      ) : null}

      {loading ? <p className="muted">Consultando reglas en Prolog...</p> : null}

      {diagnosis ? (
        <div className="result-stack">
          <div>
            <span className="field-label">Falla detectada</span>
            <h3>{formatText(diagnosis.failure)}</h3>
          </div>

          <div>
            <span className="field-label">Recomendación</span>
            <p>{diagnosis.recommendation}</p>
          </div>

          <div>
            <span className="field-label">Síntomas usados</span>
            <div className="chip-list">
              {matchedSymptoms.map((symptom) => (
                <span className="chip" key={symptom}>
                  {formatText(symptom)}
                </span>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}

export default DiagnosisResult;