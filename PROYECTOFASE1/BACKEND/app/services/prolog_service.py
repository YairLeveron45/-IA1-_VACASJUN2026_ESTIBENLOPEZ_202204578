import unicodedata
from pathlib import Path

from pyswip import Prolog


class PrologDiagnosisService:
    def __init__(self) -> None:
        self.prolog = Prolog()
        self.prolog_file = self._get_prolog_file_path()
        self.prolog.consult(str(self.prolog_file))

    def _get_prolog_file_path(self) -> Path:
        prolog_path = Path(__file__).resolve().parents[3] / "PROLOG" / "doctor_byte.pl"
        if not prolog_path.exists():
            raise FileNotFoundError(f"No se encontro el archivo Prolog: {prolog_path}")
        return prolog_path

    def _normalize_atom(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value.strip().lower())
        ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
        return ascii_value.replace(" ", "_")

    def _run_query(self, query: str) -> list[dict]:
        return list(self.prolog.query(query))

    def reload(self) -> None:
        self.prolog.consult(str(self.prolog_file))

    def get_available_symptoms(self) -> list[str]:
        result = self._run_query("sintoma(Sintoma)")
        symptoms = {str(item["Sintoma"]) for item in result}
        return sorted(symptoms)

    def run_diagnosis(self, symptoms: list[str]) -> dict:
        normalized_symptoms = [self._normalize_atom(symptom) for symptom in symptoms]
        available_symptoms = set(self.get_available_symptoms())
        invalid_symptoms = sorted(
            {symptom for symptom in normalized_symptoms if symptom not in available_symptoms}
        )

        if invalid_symptoms:
            raise ValueError(
                "Se recibieron sintomas no registrados: "
                + ", ".join(invalid_symptoms)
            )

        prolog_list = "[" + ",".join(normalized_symptoms) + "]"
        result = self._run_query(
            "diagnostico_con_recomendacion("
            f"{prolog_list}, Falla, Recomendacion"
            ")"
        )

        if not result:
            raise ValueError(
                "No se encontro un diagnostico con la combinacion de sintomas proporcionada."
            )

        diagnosis = result[0]
        return {
            "failure": str(diagnosis["Falla"]),
            "recommendation": str(diagnosis["Recomendacion"]),
            "matched_symptoms": normalized_symptoms,
        }


_prolog_service: PrologDiagnosisService | None = None


def get_prolog_service() -> PrologDiagnosisService:
    global _prolog_service
    if _prolog_service is None:
        _prolog_service = PrologDiagnosisService()
    return _prolog_service


def get_available_symptoms() -> list[str]:
    return get_prolog_service().get_available_symptoms()


def run_diagnosis(symptoms: list[str]) -> dict:
    return get_prolog_service().run_diagnosis(symptoms)


def reload_prolog_service() -> None:
    if _prolog_service is not None:
        _prolog_service.reload()
