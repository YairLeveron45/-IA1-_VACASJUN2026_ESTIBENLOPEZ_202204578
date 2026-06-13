from app.services import diagnosis_service


def test_telegram_message_uses_configured_template(monkeypatch):
    sent_messages = []

    def fake_run_diagnosis(symptoms):
        return {
            "failure": "fallo_memoria_ram",
            "recommendation": "Limpiar y reinstalar la memoria RAM.",
            "matched_symptoms": ["pitidos_al_arrancar", "congelamientos_frecuentes"],
        }

    def fake_send_message(message, chat_id=None):
        sent_messages.append((message, chat_id))
        return True

    monkeypatch.setattr(diagnosis_service, "run_diagnosis", fake_run_diagnosis)
    monkeypatch.setattr(diagnosis_service, "send_diagnosis_message", fake_send_message)
    monkeypatch.setattr(diagnosis_service, "save_history", lambda record: None)
    monkeypatch.setattr(
        diagnosis_service,
        "get_system_config",
        lambda: {
            "telegram_enabled": True,
            "telegram_chat_id": "123",
            "telegram_message_template": (
                "Reporte {fecha}\n"
                "Falla: {falla}\n"
                "Sintomas: {sintomas}\n"
                "Solucion: {recomendacion}"
            ),
        },
    )

    response = diagnosis_service.build_diagnosis(
        symptoms=["pitidos_al_arrancar"],
        notify_telegram=True,
        chat_id="123",
    )

    assert response.telegram_sent is True
    assert sent_messages

    message, chat_id = sent_messages[0]
    assert chat_id == "123"
    assert "Reporte " in message
    assert "Falla: Fallo Memoria Ram" in message
    assert "Sintomas: Pitidos Al Arrancar, Congelamientos Frecuentes" in message
    assert "Solucion: Limpiar y reinstalar la memoria RAM." in message
