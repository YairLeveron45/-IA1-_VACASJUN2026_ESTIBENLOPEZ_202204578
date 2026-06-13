from fastapi.testclient import TestClient

from app.services import knowledge_service
from app.services import system_config_service
from app.main import app


client = TestClient(app)
ADMIN_HEADERS = {"Authorization": "Bearer doctor-byte-admin-token"}


def test_admin_login_returns_access_token():
    response = client.post("/api/admin/login", json={"password": "admin123"})

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "doctor-byte-admin-token",
        "token_type": "bearer",
    }


def test_admin_routes_require_token():
    response = client.get("/api/admin/knowledge")

    assert response.status_code == 401


def test_admin_knowledge_endpoint_returns_prolog_base():
    response = client.get("/api/admin/knowledge", headers=ADMIN_HEADERS)

    assert response.status_code == 200

    data = response.json()
    assert len(data["symptoms"]) >= 15
    assert len(data["failures"]) >= 10
    assert len(data["recommendations"]) >= 10
    assert len(data["rules"]) >= 10
    assert {
        "failure": "fallo_memoria_ram",
        "symptoms": ["pitidos_al_arrancar", "congelamientos_frecuentes"],
    } in data["rules"]


def test_symptom_suggestions_returns_missing_rule_matches():
    response = client.post(
        "/api/symptom-suggestions",
        json={"symptoms": ["no_enciende"]},
    )

    assert response.status_code == 200

    data = response.json()
    assert "pantalla_negra" in data["items"]
    assert "bateria_no_carga" in data["items"]
    assert any(
        match["failure"] == "problema_fuente_poder"
        and match["missing_symptoms"] == ["pantalla_negra"]
        for match in data["matches"]
    )


def test_admin_config_can_update_telegram_message_template(tmp_path, monkeypatch):
    config_file = tmp_path / "system_config.json"
    monkeypatch.setattr(system_config_service, "CONFIG_FILE", config_file)

    payload = {
        "telegram_enabled": False,
        "telegram_chat_id": "987",
        "telegram_message_template": (
            "Fecha: {fecha}\n"
            "Falla: {falla}\n"
            "Sintomas: {sintomas}\n"
            "Recomendacion: {recomendacion}"
        ),
    }

    update_response = client.put(
        "/api/admin/config",
        json=payload,
        headers=ADMIN_HEADERS,
    )
    assert update_response.status_code == 200
    assert update_response.json() == payload

    read_response = client.get("/api/admin/config", headers=ADMIN_HEADERS)
    assert read_response.status_code == 200
    assert read_response.json() == payload


def test_admin_symptom_crud_uses_prolog_files(tmp_path, monkeypatch):
    symptoms_file = tmp_path / "sintomas.pl"
    rules_file = tmp_path / "doctor_byte.pl"

    symptoms_file.write_text(
        "% Hechos de sintomas disponibles para el diagnostico.\n\n"
        "sintoma(no_enciende).\n",
        encoding="utf-8",
    )
    rules_file.write_text(
        "regla_diagnostico(\n"
        "    problema_fuente_poder,\n"
        "    [no_enciende]\n"
        ").\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(knowledge_service, "SYMPTOMS_FILE", symptoms_file)
    monkeypatch.setattr(knowledge_service, "RULES_FILE", rules_file)

    create_response = client.post(
        "/api/admin/symptoms",
        json={"name": "Pantalla Azul"},
        headers=ADMIN_HEADERS,
    )
    assert create_response.status_code == 201
    assert create_response.json() == {"name": "pantalla_azul"}

    duplicate_response = client.post(
        "/api/admin/symptoms",
        json={"name": "pantalla_azul"},
        headers=ADMIN_HEADERS,
    )
    assert duplicate_response.status_code == 400

    update_response = client.put(
        "/api/admin/symptoms/no_enciende",
        json={"name": "equipo no enciende"},
        headers=ADMIN_HEADERS,
    )
    assert update_response.status_code == 200
    assert update_response.json() == {"name": "equipo_no_enciende"}
    assert "equipo_no_enciende" in rules_file.read_text(encoding="utf-8")

    delete_blocked_response = client.delete(
        "/api/admin/symptoms/equipo_no_enciende",
        headers=ADMIN_HEADERS,
    )
    assert delete_blocked_response.status_code == 400

    delete_response = client.delete(
        "/api/admin/symptoms/pantalla_azul",
        headers=ADMIN_HEADERS,
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {"name": "pantalla_azul"}


def test_admin_failure_crud_updates_related_prolog_files(tmp_path, monkeypatch):
    failures_file = tmp_path / "fallas.pl"
    recommendations_file = tmp_path / "recomendaciones.pl"
    rules_file = tmp_path / "doctor_byte.pl"

    failures_file.write_text(
        "% Catalogo de fallas diagnosticables.\n\n"
        "falla(problema_fuente_poder).\n",
        encoding="utf-8",
    )
    recommendations_file.write_text(
        "recomendacion(\n"
        "    problema_fuente_poder,\n"
        "    'Verificar cable de energia.'\n"
        ").\n",
        encoding="utf-8",
    )
    rules_file.write_text(
        "regla_diagnostico(\n"
        "    problema_fuente_poder,\n"
        "    [no_enciende]\n"
        ").\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(knowledge_service, "FAILURES_FILE", failures_file)
    monkeypatch.setattr(knowledge_service, "RECOMMENDATIONS_FILE", recommendations_file)
    monkeypatch.setattr(knowledge_service, "RULES_FILE", rules_file)

    create_response = client.post(
        "/api/admin/failures",
        json={"name": "Falla Nueva"},
        headers=ADMIN_HEADERS,
    )
    assert create_response.status_code == 201
    assert create_response.json() == {"name": "falla_nueva"}

    duplicate_response = client.post(
        "/api/admin/failures",
        json={"name": "falla_nueva"},
        headers=ADMIN_HEADERS,
    )
    assert duplicate_response.status_code == 400

    update_response = client.put(
        "/api/admin/failures/problema_fuente_poder",
        json={"name": "fuente principal danada"},
        headers=ADMIN_HEADERS,
    )
    assert update_response.status_code == 200
    assert update_response.json() == {"name": "fuente_principal_danada"}
    assert "fuente_principal_danada" in recommendations_file.read_text(encoding="utf-8")
    assert "fuente_principal_danada" in rules_file.read_text(encoding="utf-8")

    delete_blocked_response = client.delete(
        "/api/admin/failures/fuente_principal_danada",
        headers=ADMIN_HEADERS,
    )
    assert delete_blocked_response.status_code == 400

    delete_response = client.delete(
        "/api/admin/failures/falla_nueva",
        headers=ADMIN_HEADERS,
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {"name": "falla_nueva"}


def test_admin_recommendation_crud_uses_prolog_files(tmp_path, monkeypatch):
    failures_file = tmp_path / "fallas.pl"
    recommendations_file = tmp_path / "recomendaciones.pl"

    failures_file.write_text(
        "% Catalogo de fallas diagnosticables.\n\n"
        "falla(problema_fuente_poder).\n"
        "falla(fallo_memoria_ram).\n",
        encoding="utf-8",
    )
    recommendations_file.write_text(
        "recomendacion(\n"
        "    problema_fuente_poder,\n"
        "    'Verificar cable de energia.'\n"
        ").\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(knowledge_service, "FAILURES_FILE", failures_file)
    monkeypatch.setattr(knowledge_service, "RECOMMENDATIONS_FILE", recommendations_file)

    create_response = client.post(
        "/api/admin/recommendations",
        json={
            "failure": "fallo_memoria_ram",
            "text": "Limpiar y reinstalar la memoria RAM.",
        },
        headers=ADMIN_HEADERS,
    )
    assert create_response.status_code == 201
    assert create_response.json() == {
        "failure": "fallo_memoria_ram",
        "text": "Limpiar y reinstalar la memoria RAM.",
    }

    duplicate_response = client.post(
        "/api/admin/recommendations",
        json={
            "failure": "fallo_memoria_ram",
            "text": "Probar otro modulo.",
        },
        headers=ADMIN_HEADERS,
    )
    assert duplicate_response.status_code == 400

    update_response = client.put(
        "/api/admin/recommendations/problema_fuente_poder",
        json={
            "failure": "problema_fuente_poder",
            "text": "Revisar cable de energia y fuente.",
        },
        headers=ADMIN_HEADERS,
    )
    assert update_response.status_code == 200
    assert update_response.json() == {
        "failure": "problema_fuente_poder",
        "text": "Revisar cable de energia y fuente.",
    }
    assert "Revisar cable de energia y fuente." in recommendations_file.read_text(
        encoding="utf-8"
    )

    invalid_text_response = client.put(
        "/api/admin/recommendations/problema_fuente_poder",
        json={
            "failure": "problema_fuente_poder",
            "text": "Revisar el equipo 'principal'.",
        },
        headers=ADMIN_HEADERS,
    )
    assert invalid_text_response.status_code == 400

    delete_response = client.delete(
        "/api/admin/recommendations/fallo_memoria_ram",
        headers=ADMIN_HEADERS,
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {"failure": "fallo_memoria_ram"}


def test_admin_rule_crud_keeps_doctor_byte_engine(tmp_path, monkeypatch):
    symptoms_file = tmp_path / "sintomas.pl"
    failures_file = tmp_path / "fallas.pl"
    recommendations_file = tmp_path / "recomendaciones.pl"
    rules_file = tmp_path / "doctor_byte.pl"

    symptoms_file.write_text(
        "sintoma(no_enciende).\n"
        "sintoma(pantalla_negra).\n"
        "sintoma(pitidos_al_arrancar).\n",
        encoding="utf-8",
    )
    failures_file.write_text(
        "falla(problema_fuente_poder).\n"
        "falla(fallo_memoria_ram).\n",
        encoding="utf-8",
    )
    recommendations_file.write_text(
        "recomendacion(\n"
        "    problema_fuente_poder,\n"
        "    'Verificar cable de energia.'\n"
        ").\n"
        "recomendacion(\n"
        "    fallo_memoria_ram,\n"
        "    'Limpiar RAM.'\n"
        ").\n",
        encoding="utf-8",
    )
    rules_file.write_text(
        ":- consult('sintomas.pl').\n\n"
        "% Reglas de inferencia.\n"
        "regla_diagnostico(\n"
        "    problema_fuente_poder,\n"
        "    [no_enciende]\n"
        ").\n\n"
        "diagnosticar(SintomasSeleccionados, Falla) :-\n"
        "    regla_diagnostico(Falla, SintomasClave),\n"
        "    presenta_todos(SintomasSeleccionados, SintomasClave),\n"
        "    !.\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(knowledge_service, "SYMPTOMS_FILE", symptoms_file)
    monkeypatch.setattr(knowledge_service, "FAILURES_FILE", failures_file)
    monkeypatch.setattr(knowledge_service, "RECOMMENDATIONS_FILE", recommendations_file)
    monkeypatch.setattr(knowledge_service, "RULES_FILE", rules_file)

    create_response = client.post(
        "/api/admin/rules",
        json={
            "failure": "fallo_memoria_ram",
            "symptoms": ["pitidos_al_arrancar", "pitidos_al_arrancar"],
        },
        headers=ADMIN_HEADERS,
    )
    assert create_response.status_code == 201
    assert create_response.json() == {
        "failure": "fallo_memoria_ram",
        "symptoms": ["pitidos_al_arrancar"],
    }

    duplicate_response = client.post(
        "/api/admin/rules",
        json={
            "failure": "fallo_memoria_ram",
            "symptoms": ["pitidos_al_arrancar"],
        },
        headers=ADMIN_HEADERS,
    )
    assert duplicate_response.status_code == 400

    update_response = client.put(
        "/api/admin/rules/problema_fuente_poder",
        json={
            "failure": "problema_fuente_poder",
            "symptoms": ["no_enciende", "pantalla_negra"],
        },
        headers=ADMIN_HEADERS,
    )
    assert update_response.status_code == 200
    assert update_response.json() == {
        "failure": "problema_fuente_poder",
        "symptoms": ["no_enciende", "pantalla_negra"],
    }

    invalid_symptom_response = client.put(
        "/api/admin/rules/problema_fuente_poder",
        json={
            "failure": "problema_fuente_poder",
            "symptoms": ["sintoma_inexistente"],
        },
        headers=ADMIN_HEADERS,
    )
    assert invalid_symptom_response.status_code == 400

    delete_response = client.delete(
        "/api/admin/rules/fallo_memoria_ram",
        headers=ADMIN_HEADERS,
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {"failure": "fallo_memoria_ram"}

    rules_content = rules_file.read_text(encoding="utf-8")
    assert "diagnosticar(SintomasSeleccionados, Falla)" in rules_content
    assert "regla_diagnostico(" in rules_content
    assert "fallo_memoria_ram" not in rules_content
