import json

from app.services.rpa_simulator_service import RpaSimulatorService


def test_simulator_saves_submission(tmp_path) -> None:
    service = RpaSimulatorService()
    service.output_directory = tmp_path

    registration_id = service.save_submission(
        {
            "invoice_number": "FAC-001",
            "invoice_date": "2026-06-18",
            "provider_name": "Proveedor Ejemplo",
            "nit": "1234K",
            "subtotal": "100.00",
            "taxes": "12.00",
            "total": "112.00",
        }
    )

    files = list(tmp_path.glob("submission-*.json"))
    payload = json.loads(files[0].read_text(encoding="utf-8"))

    assert payload["registration_id"] == registration_id
    assert payload["fields"]["total"] == "112.00"
    assert service.get_submission(registration_id) == payload
    assert service.get_submission("../invalid") is None
