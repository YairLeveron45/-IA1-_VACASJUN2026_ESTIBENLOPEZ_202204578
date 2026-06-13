import { useEffect, useState } from "react";

import {
  createAdminFailure,
  createAdminRecommendation,
  createAdminRule,
  createAdminSymptom,
  deleteAdminFailure,
  deleteAdminRecommendation,
  deleteAdminRule,
  deleteAdminSymptom,
  fetchAdminKnowledge,
  fetchAdminConfig,
  updateAdminConfig,
  updateAdminFailure,
  updateAdminRecommendation,
  updateAdminRule,
  updateAdminSymptom,
} from "../api";

function formatText(value) {
  return value.replaceAll("_", " ");
}

function buildRuleSymptoms(symptom1, symptom2) {
  return [symptom1, symptom2].filter(Boolean);
}

const RECOMMENDED_TELEGRAM_TEMPLATE = `🩺 DOCTOR BYTE - DIAGNOSTICO
--------------------------------
📅 Fecha y hora: {fecha}

⚠️ Falla detectada:
{falla}

🧩 Sintomas evaluados:
{sintomas}

🛠️ Recomendacion:
{recomendacion}

✅ Diagnostico generado correctamente por el sistema experto Doctor Byte.`;

function confirmDelete(label) {
  return window.confirm(`Seguro que deseas eliminar ${label}?`);
}

function AdminPanel({ token, onLogout }) {
  const [adminSection, setAdminSection] = useState("summary");
  const [knowledge, setKnowledge] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [newSymptom, setNewSymptom] = useState("");
  const [newFailure, setNewFailure] = useState("");
  const [newRecommendation, setNewRecommendation] = useState({
    failure: "",
    text: "",
  });
  const [newRule, setNewRule] = useState({
    failure: "",
    symptom1: "",
    symptom2: "",
  });
  const [telegramConfig, setTelegramConfig] = useState(null);
  const [editing, setEditing] = useState(null);

  async function loadKnowledge() {
    setLoading(true);
    setError("");

    try {
      const response = await fetchAdminKnowledge(token);
      setKnowledge(response);
      const configResponse = await fetchAdminConfig(token);
      setTelegramConfig(configResponse);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  async function runAction(successMessage, action) {
    setSaving(true);
    setError("");
    setMessage("");

    try {
      await action();
      await loadKnowledge();
      setEditing(null);
      setMessage(successMessage);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => {
    loadKnowledge();
  }, [token]);

  const symptoms = knowledge?.symptoms || [];
  const failures = knowledge?.failures || [];
  const recommendations = knowledge?.recommendations || [];
  const rules = knowledge?.rules || [];
  const failuresWithRecommendation = new Set(
    recommendations.map((recommendation) => recommendation.failure)
  );
  const selectedRecommendation = recommendations.find(
    (recommendation) => recommendation.failure === newRecommendation.failure
  );
  const sectionTabs = [
    ["summary", "Resumen"],
    ["symptoms", "Sintomas"],
    ["failures", "Fallas"],
    ["recommendations", "Recomendaciones"],
    ["rules", "Reglas"],
    ["telegram", "Telegram"],
  ];

  return (
    <section className="admin-panel">
      <div className="admin-toolbar">
        <div>
          <h2>Panel administrador</h2>
          <p>Gestion de conocimiento cargada desde los archivos Prolog.</p>
        </div>
        <div className="admin-toolbar-actions">
          <button className="ghost-button" type="button" onClick={loadKnowledge}>
            Refrescar
          </button>
          <button className="ghost-button" type="button" onClick={onLogout}>
            Salir
          </button>
        </div>
      </div>

      {error ? <p className="alert alert-error">{error}</p> : null}
      {message ? <p className="alert alert-success">{message}</p> : null}
      {loading ? <p className="muted">Cargando base de conocimiento...</p> : null}

      {!loading && knowledge ? (
        <>
          <nav className="admin-section-tabs" aria-label="Menu de administrador">
            {sectionTabs.map(([section, label]) => (
              <button
                className={
                  adminSection === section
                    ? "admin-section-tab active"
                    : "admin-section-tab"
                }
                key={section}
                type="button"
                onClick={() => {
                  setAdminSection(section);
                  setEditing(null);
                  setError("");
                  setMessage("");
                }}
              >
                {label}
              </button>
            ))}
          </nav>

          {adminSection === "summary" ? (
            <div className="admin-summary-grid">
              <article className="panel admin-summary-card">
                <span>Sintomas</span>
                <strong>{symptoms.length}</strong>
              </article>
              <article className="panel admin-summary-card">
                <span>Fallas</span>
                <strong>{failures.length}</strong>
              </article>
              <article className="panel admin-summary-card">
                <span>Recomendaciones</span>
                <strong>{recommendations.length}</strong>
              </article>
              <article className="panel admin-summary-card">
                <span>Reglas</span>
                <strong>{rules.length}</strong>
              </article>
            </div>
          ) : null}

          <div className="admin-grid admin-section-grid">
            {adminSection === "symptoms" ? (
            <section className="panel">
              <div className="panel-header">
                <h3 className="panel-title">Sintomas</h3>
                <span className="panel-badge"></span>
              </div>

              <form
                className="admin-form"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction("Sintoma agregado.", async () => {
                    await createAdminSymptom(token, newSymptom);
                    setNewSymptom("");
                  });
                }}
              >
                <input
                  value={newSymptom}
                  onChange={(event) => setNewSymptom(event.target.value)}
                  placeholder="nuevo sintoma"
                />
                <button className="primary-button" disabled={saving || !newSymptom.trim()}>
                  Agregar
                </button>
              </form>

              <div className="admin-list">
                {symptoms.map((symptom) => {
                  const isEditing = editing?.type === "symptom" && editing.id === symptom;
                  return (
                    <article className="admin-list-item" key={symptom}>
                      {isEditing ? (
                        <input
                          value={editing.name}
                          onChange={(event) =>
                            setEditing({ ...editing, name: event.target.value })
                          }
                        />
                      ) : (
                        <strong>{formatText(symptom)}</strong>
                      )}
                      <div className="admin-row-actions">
                        {isEditing ? (
                          <>
                          <button
                            className="ghost-button"
                            type="button"
                            onClick={() =>
                              runAction("Sintoma actualizado.", () =>
                                updateAdminSymptom(token, symptom, editing.name)
                              )
                            }
                          >
                            Guardar
                          </button>
                          <button
                            className="ghost-button"
                            type="button"
                            onClick={() => setEditing(null)}
                          >
                            Cancelar
                          </button>
                          </>
                        ) : (
                          <button
                            className="ghost-button"
                            type="button"
                            onClick={() =>
                              setEditing({ type: "symptom", id: symptom, name: symptom })
                            }
                          >
                            Editar
                          </button>
                        )}
                        <button
                          className="ghost-button danger-button"
                          type="button"
                          onClick={() => {
                            if (!confirmDelete(formatText(symptom))) return;
                            runAction("Sintoma eliminado.", () =>
                              deleteAdminSymptom(token, symptom)
                            );
                          }}
                        >
                          Eliminar
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>
            ) : null}

            {adminSection === "failures" ? (
            <section className="panel">
              <div className="panel-header">
                <h3 className="panel-title">Fallas</h3>
                <span className="panel-badge"></span>
              </div>

              <form
                className="admin-form"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction("Falla agregada.", async () => {
                    await createAdminFailure(token, newFailure);
                    setNewFailure("");
                  });
                }}
              >
                <input
                  value={newFailure}
                  onChange={(event) => setNewFailure(event.target.value)}
                  placeholder="nueva falla"
                />
                <button className="primary-button" disabled={saving || !newFailure.trim()}>
                  Agregar
                </button>
              </form>

              <div className="admin-list">
                {failures.map((failure) => {
                  const isEditing = editing?.type === "failure" && editing.id === failure;
                  return (
                    <article className="admin-list-item" key={failure}>
                      {isEditing ? (
                        <input
                          value={editing.name}
                          onChange={(event) =>
                            setEditing({ ...editing, name: event.target.value })
                          }
                        />
                      ) : (
                        <strong>{formatText(failure)}</strong>
                      )}
                      <div className="admin-row-actions">
                        {isEditing ? (
                          <>
                          <button
                            className="ghost-button"
                            type="button"
                            onClick={() =>
                              runAction("Falla actualizada.", () =>
                                updateAdminFailure(token, failure, editing.name)
                              )
                            }
                          >
                            Guardar
                          </button>
                          <button
                            className="ghost-button"
                            type="button"
                            onClick={() => setEditing(null)}
                          >
                            Cancelar
                          </button>
                          </>
                        ) : (
                          <button
                            className="ghost-button"
                            type="button"
                            onClick={() =>
                              setEditing({ type: "failure", id: failure, name: failure })
                            }
                          >
                            Editar
                          </button>
                        )}
                        <button
                          className="ghost-button danger-button"
                          type="button"
                          onClick={() => {
                            if (!confirmDelete(formatText(failure))) return;
                            runAction("Falla eliminada.", () =>
                              deleteAdminFailure(token, failure)
                            );
                          }}
                        >
                          Eliminar
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>
            ) : null}

            {adminSection === "recommendations" ? (
            <section className="panel">
              <div className="panel-header">
                <h3 className="panel-title">Recomendaciones</h3>
                <span className="panel-badge"></span>
              </div>

              <form
                className="admin-form admin-form-wide"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction("Recomendacion guardada.", async () => {
                    if (selectedRecommendation) {
                      await updateAdminRecommendation(
                        token,
                        newRecommendation.failure,
                        newRecommendation.failure,
                        newRecommendation.text
                      );
                    } else {
                      await createAdminRecommendation(
                        token,
                        newRecommendation.failure,
                        newRecommendation.text
                      );
                    }
                    setNewRecommendation({ failure: "", text: "" });
                  });
                }}
              >
                <select
                  value={newRecommendation.failure}
                  onChange={(event) =>
                    setNewRecommendation({
                      ...newRecommendation,
                      failure: event.target.value,
                      text:
                        recommendations.find(
                          (item) => item.failure === event.target.value
                        )?.text || "",
                    })
                  }
                >
                  <option value="">Selecciona una falla</option>
                  {failures.map((failure) => (
                    <option
                      key={failure}
                      value={failure}
                    >
                      {formatText(failure)}
                      {failuresWithRecommendation.has(failure)
                        ? " - ya tiene recomendacion"
                        : ""}
                    </option>
                  ))}
                </select>
                <textarea
                  value={newRecommendation.text}
                  onChange={(event) =>
                    setNewRecommendation({
                      ...newRecommendation,
                      text: event.target.value,
                    })
                  }
                  placeholder="recomendacion"
                />
                <button
                  className="primary-button"
                  disabled={
                    saving ||
                    !newRecommendation.failure ||
                    !newRecommendation.text.trim()
                  }
                >
                  {selectedRecommendation ? "Actualizar" : "Agregar"}
                </button>
              </form>

              <div className="admin-list">
                {recommendations.map((recommendation) => {
                  const isEditing =
                    editing?.type === "recommendation" &&
                    editing.id === recommendation.failure;
                  return (
                    <article className="admin-list-item" key={recommendation.failure}>
                      {isEditing ? (
                        <>
                          <select
                            value={editing.failure}
                            onChange={(event) =>
                              setEditing({ ...editing, failure: event.target.value })
                            }
                          >
                            {failures.map((failure) => (
                              <option key={failure} value={failure}>
                                {formatText(failure)}
                              </option>
                            ))}
                          </select>
                          <textarea
                            value={editing.text}
                            onChange={(event) =>
                              setEditing({ ...editing, text: event.target.value })
                            }
                          />
                        </>
                      ) : (
                        <>
                          <strong>{formatText(recommendation.failure)}</strong>
                          <p>{recommendation.text}</p>
                        </>
                      )}
                      <div className="admin-row-actions">
                        {isEditing ? (
                          <>
                          <button
                            className="ghost-button"
                            type="button"
                            onClick={() =>
                              runAction("Recomendacion actualizada.", () =>
                                updateAdminRecommendation(
                                  token,
                                  recommendation.failure,
                                  editing.failure,
                                  editing.text
                                )
                              )
                            }
                          >
                            Guardar
                          </button>
                          <button
                            className="ghost-button"
                            type="button"
                            onClick={() => setEditing(null)}
                          >
                            Cancelar
                          </button>
                          </>
                        ) : (
                          <button
                            className="ghost-button"
                            type="button"
                            onClick={() =>
                              setEditing({
                                type: "recommendation",
                                id: recommendation.failure,
                                failure: recommendation.failure,
                                text: recommendation.text,
                              })
                            }
                          >
                            Editar
                          </button>
                        )}
                        <button
                          className="ghost-button danger-button"
                          type="button"
                          onClick={() => {
                            if (!confirmDelete(formatText(recommendation.failure))) return;
                            runAction("Recomendacion eliminada.", () =>
                              deleteAdminRecommendation(token, recommendation.failure)
                            );
                          }}
                        >
                          Eliminar
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>
            ) : null}

            {adminSection === "rules" ? (
            <section className="panel">
              <div className="panel-header">
                <h3 className="panel-title">Reglas</h3>
                <span className="panel-badge"></span>
              </div>

              <form
                className="admin-form admin-form-wide"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction("Regla agregada.", async () => {
                    await createAdminRule(
                      token,
                      newRule.failure,
                      buildRuleSymptoms(newRule.symptom1, newRule.symptom2)
                    );
                    setNewRule({ failure: "", symptom1: "", symptom2: "" });
                  });
                }}
              >
                <select
                  value={newRule.failure}
                  onChange={(event) =>
                    setNewRule({ ...newRule, failure: event.target.value })
                  }
                >
                  <option value="">Selecciona una falla</option>
                  {failures.map((failure) => (
                    <option key={failure} value={failure}>
                      {formatText(failure)}
                    </option>
                  ))}
                </select>
                <select
                  value={newRule.symptom1}
                  onChange={(event) =>
                    setNewRule({ ...newRule, symptom1: event.target.value })
                  }
                >
                  <option value="">Sintoma 1</option>
                  {symptoms.map((symptom) => (
                    <option key={symptom} value={symptom}>
                      {formatText(symptom)}
                    </option>
                  ))}
                </select>
                <select
                  value={newRule.symptom2}
                  onChange={(event) =>
                    setNewRule({ ...newRule, symptom2: event.target.value })
                  }
                >
                  <option value="">Sintoma 2</option>
                  {symptoms.map((symptom) => (
                    <option key={symptom} value={symptom}>
                      {formatText(symptom)}
                    </option>
                  ))}
                </select>
                <button
                  className="primary-button"
                  disabled={saving || !newRule.failure || !newRule.symptom1}
                >
                  Agregar
                </button>
              </form>

              <div className="admin-list">
                {rules.map((rule) => {
                  const isEditing = editing?.type === "rule" && editing.id === rule.failure;
                  return (
                    <article className="admin-list-item" key={rule.failure}>
                      {isEditing ? (
                        <>
                          <select
                            value={editing.failure}
                            onChange={(event) =>
                              setEditing({ ...editing, failure: event.target.value })
                            }
                          >
                            {failures.map((failure) => (
                              <option key={failure} value={failure}>
                                {formatText(failure)}
                              </option>
                            ))}
                          </select>
                          <select
                            value={editing.symptom1}
                            onChange={(event) =>
                              setEditing({ ...editing, symptom1: event.target.value })
                            }
                          >
                            {symptoms.map((symptom) => (
                              <option key={symptom} value={symptom}>
                                {formatText(symptom)}
                              </option>
                            ))}
                          </select>
                          <select
                            value={editing.symptom2}
                            onChange={(event) =>
                              setEditing({ ...editing, symptom2: event.target.value })
                            }
                          >
                            <option value="">Sin segundo sintoma</option>
                            {symptoms.map((symptom) => (
                              <option key={symptom} value={symptom}>
                                {formatText(symptom)}
                              </option>
                            ))}
                          </select>
                        </>
                      ) : (
                        <>
                          <strong>{formatText(rule.failure)}</strong>
                          <div className="chip-list">
                            {rule.symptoms.map((symptom) => (
                              <span className="chip" key={`${rule.failure}-${symptom}`}>
                                {formatText(symptom)}
                              </span>
                            ))}
                          </div>
                        </>
                      )}
                      <div className="admin-row-actions">
                        {isEditing ? (
                          <>
                          <button
                            className="ghost-button"
                            type="button"
                            onClick={() =>
                              runAction("Regla actualizada.", () =>
                                updateAdminRule(
                                  token,
                                  rule.failure,
                                  editing.failure,
                                  buildRuleSymptoms(
                                    editing.symptom1,
                                    editing.symptom2
                                  )
                                )
                              )
                            }
                          >
                            Guardar
                          </button>
                          <button
                            className="ghost-button"
                            type="button"
                            onClick={() => setEditing(null)}
                          >
                            Cancelar
                          </button>
                          </>
                        ) : (
                          <button
                            className="ghost-button"
                            type="button"
                            onClick={() =>
                              setEditing({
                                type: "rule",
                                id: rule.failure,
                                failure: rule.failure,
                                symptom1: rule.symptoms[0] || "",
                                symptom2: rule.symptoms[1] || "",
                              })
                            }
                          >
                            Editar
                          </button>
                        )}
                        <button
                          className="ghost-button danger-button"
                          type="button"
                          onClick={() => {
                            if (!confirmDelete(formatText(rule.failure))) return;
                            runAction("Regla eliminada.", () =>
                              deleteAdminRule(token, rule.failure)
                            );
                          }}
                        >
                          Eliminar
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            </section>
            ) : null}

            {adminSection === "telegram" && telegramConfig ? (
            <section className="panel">
              <div className="panel-header">
                <div>
                  <h3 className="panel-title">Configuracion Telegram</h3>
                  <p className="panel-subtitle">
                    Define si el bot envia mensajes, a que chat llegan y como se ven.
                  </p>
                </div>
                <span className="panel-badge">Bot</span>
              </div>

              <div className="telegram-help-grid">
                <article className="telegram-help-card">
                  <strong>1. Activar bot</strong>
                  <p>Enciende o apaga el envio automatico de diagnosticos.</p>
                </article>
                <article className="telegram-help-card">
                  <strong>2. Chat ID</strong>
                  <p>Es el identificador del chat donde Telegram recibira el mensaje.</p>
                </article>
                <article className="telegram-help-card">
                  <strong>3. Mensaje</strong>
                  <p>Edita el texto usando variables como falla y recomendacion.</p>
                </article>
              </div>

              <form
                className="admin-form admin-form-wide"
                onSubmit={(event) => {
                  event.preventDefault();
                  runAction("Configuracion de Telegram guardada.", () =>
                    updateAdminConfig(token, telegramConfig)
                  );
                }}
              >
                <label className="admin-toggle-line">
                  <input
                    checked={telegramConfig.telegram_enabled}
                    type="checkbox"
                    onChange={(event) =>
                      setTelegramConfig({
                        ...telegramConfig,
                        telegram_enabled: event.target.checked,
                      })
                    }
                  />
                  <span>
                    {telegramConfig.telegram_enabled
                      ? "Bot activo: se enviaran diagnosticos a Telegram"
                      : "Bot inactivo: no se enviaran mensajes"}
                  </span>
                </label>

                <label className="field-group">
                  <span className="field-label">Chat ID de destino</span>
                  <input
                    value={telegramConfig.telegram_chat_id}
                    onChange={(event) =>
                      setTelegramConfig({
                        ...telegramConfig,
                        telegram_chat_id: event.target.value,
                      })
                    }
                    placeholder="ID del chat de Telegram"
                  />
                  <small className="field-help">
                    Si lo dejas vacio, el backend intentara usar TELEGRAM_CHAT_ID del
                    archivo .env.
                  </small>
                </label>

                <label className="field-group">
                  <span className="field-label">Plantilla del mensaje del bot</span>
                  <textarea
                    className="telegram-template-area"
                    value={telegramConfig.telegram_message_template}
                    onChange={(event) =>
                      setTelegramConfig({
                        ...telegramConfig,
                        telegram_message_template: event.target.value,
                      })
                    }
                  />
                  <small className="field-help">
                    No borres las variables obligatorias; el sistema las reemplaza con
                    los datos del diagnostico.
                  </small>
                </label>

                <div className="telegram-token-list">
                  <span>{"{fecha}"} = fecha y hora</span>
                  <span>{"{falla}"} = falla detectada</span>
                  <span>{"{sintomas}"} = sintomas evaluados</span>
                  <span>{"{recomendacion}"} = recomendacion generada</span>
                </div>

                <div className="admin-row-actions">
                  <button className="primary-button" disabled={saving}>
                    Guardar configuracion
                  </button>
                  <button
                    className="ghost-button"
                    type="button"
                    onClick={() =>
                      setTelegramConfig({
                        ...telegramConfig,
                        telegram_message_template: RECOMMENDED_TELEGRAM_TEMPLATE,
                      })
                    }
                  >
                    Usar plantilla recomendada
                  </button>
                </div>
              </form>
            </section>
            ) : null}
          </div>
        </>
      ) : null}
    </section>
  );
}

export default AdminPanel;
