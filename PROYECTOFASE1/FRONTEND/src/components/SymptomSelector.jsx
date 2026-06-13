function formatSymptomLabel(symptom) {
  return symptom.replaceAll("_", " ");
}

function SymptomSelector({
  symptoms,
  selectedSymptoms,
  suggestedSymptoms = [],
  loading,
  onToggle,
  onClear,
}) {
  const suggestedSet = new Set(suggestedSymptoms);

  return (
    <section className="panel panel-large">
      <h2>Síntomas</h2>
      <p>Marca los síntomas que presenta la computadora.</p>

      {loading ? <p className="muted">Cargando síntomas...</p> : null}

      {!loading && symptoms.length === 0 ? (
        <p className="muted">No hay síntomas disponibles.</p>
      ) : null}

      {!loading && symptoms.length > 0 ? (
        <div className="symptom-list">
          {symptoms.map((symptom) => {
            const selected = selectedSymptoms.includes(symptom);
            const suggested = suggestedSet.has(symptom) && !selected;

            return (
              <label
                className={
                  suggested ? "symptom-item symptom-suggested" : "symptom-item"
                }
                key={symptom}
              >
                <input
                  type="checkbox"
                  checked={selected}
                  onChange={() => onToggle(symptom)}
                />
                <span>{formatSymptomLabel(symptom)}</span>
                {suggested ? <small>match</small> : null}
              </label>
            );
          })}
        </div>
      ) : null}

      <div className="inline-actions">
        <span className="badge">Seleccionados: {selectedSymptoms.length}</span>

        <button
          className="ghost-button"
          type="button"
          onClick={onClear}
          disabled={selectedSymptoms.length === 0}
        >
          Limpiar
        </button>
      </div>
    </section>
  );
}

export default SymptomSelector;
