import re
import unicodedata
from pathlib import Path


PROLOG_DIR = Path(__file__).resolve().parents[3] / "PROLOG"
SYMPTOMS_FILE = PROLOG_DIR / "sintomas.pl"
FAILURES_FILE = PROLOG_DIR / "fallas.pl"
RECOMMENDATIONS_FILE = PROLOG_DIR / "recomendaciones.pl"
RULES_FILE = PROLOG_DIR / "doctor_byte.pl"
ATOM_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
RULE_PATTERN = re.compile(
    r"regla_diagnostico\(\s*([a-zA-Z0-9_]+)\s*,\s*\[([^\]]*)\]\s*\)\.",
    flags=re.DOTALL,
)


def _read_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"No se encontro el archivo Prolog: {path}")

    return path.read_text(encoding="utf-8")


def _write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    try:
        from app.services.prolog_service import reload_prolog_service

        reload_prolog_service()
    except Exception:
        pass


def _normalize_atom(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    atom = re.sub(r"\s+", "_", ascii_value)
    atom = re.sub(r"[^a-z0-9_]", "", atom)
    atom = re.sub(r"_+", "_", atom).strip("_")

    if not atom or not ATOM_PATTERN.match(atom):
        raise ValueError(
            "El nombre debe iniciar con una letra y solo puede contener letras, numeros y guion bajo."
        )

    return atom


def _parse_single_atom_facts(content: str, predicate: str) -> list[str]:
    pattern = rf"{predicate}\(\s*([a-zA-Z0-9_]+)\s*\)\."
    return sorted(re.findall(pattern, content))


def _format_atom_facts(predicate: str, atoms: list[str], header: str) -> str:
    lines = [header, ""]
    lines.extend(f"{predicate}({atom})." for atom in atoms)
    return "\n".join(lines) + "\n"


def _format_recommendations(recommendations: list[dict]) -> str:
    lines = ["% Recomendaciones asociadas a las fallas detectadas.", ""]

    for recommendation in sorted(recommendations, key=lambda item: item["failure"]):
        lines.extend(
            [
                "recomendacion(",
                f"    {recommendation['failure']},",
                f"    '{recommendation['text']}'",
                ").",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def _format_rules(rules: list[dict]) -> str:
    blocks = []

    for rule in sorted(rules, key=lambda item: item["failure"]):
        symptoms = ", ".join(rule["symptoms"])
        blocks.append(
            "regla_diagnostico(\n"
            f"    {rule['failure']},\n"
            f"    [{symptoms}]\n"
            ")."
        )

    return "\n\n".join(blocks)


def _write_rules(rules: list[dict]) -> None:
    content = _read_file(RULES_FILE)
    formatted_rules = _format_rules(rules)

    if RULE_PATTERN.search(content):
        updated_content = RULE_PATTERN.sub("", content)
        updated_content = re.sub(
            r"(% Reglas de inferencia\.)\s*",
            rf"\1\n{formatted_rules}\n\n",
            updated_content,
            count=1,
        )
    else:
        updated_content = content.rstrip() + "\n\n% Reglas de inferencia.\n"
        updated_content += formatted_rules + "\n"

    updated_content = re.sub(r"\n{3,}", "\n\n", updated_content).rstrip() + "\n"
    _write_file(RULES_FILE, updated_content)


def _normalize_recommendation_text(value: str) -> str:
    text = " ".join(value.strip().split())

    if not text:
        raise ValueError("La recomendacion no puede estar vacia.")

    if "'" in text:
        raise ValueError("La recomendacion no puede contener comillas simples.")

    return text


def _replace_rule_symptom(old_symptom: str, new_symptom: str) -> None:
    content = _read_file(RULES_FILE)
    updated_content = re.sub(
        rf"(?<![a-zA-Z0-9_]){re.escape(old_symptom)}(?![a-zA-Z0-9_])",
        new_symptom,
        content,
    )
    _write_file(RULES_FILE, updated_content)


def _replace_atom_in_file(path: Path, old_atom: str, new_atom: str) -> None:
    content = _read_file(path)
    updated_content = re.sub(
        rf"(?<![a-zA-Z0-9_]){re.escape(old_atom)}(?![a-zA-Z0-9_])",
        new_atom,
        content,
    )
    _write_file(path, updated_content)


def get_symptoms() -> list[str]:
    return _parse_single_atom_facts(_read_file(SYMPTOMS_FILE), "sintoma")


def get_failures() -> list[str]:
    return _parse_single_atom_facts(_read_file(FAILURES_FILE), "falla")


def get_recommendations() -> list[dict]:
    content = _read_file(RECOMMENDATIONS_FILE)
    pattern = r"recomendacion\(\s*([a-zA-Z0-9_]+)\s*,\s*'([^']*)'\s*\)\."

    return [
        {
            "failure": failure,
            "text": text,
        }
        for failure, text in re.findall(pattern, content, flags=re.DOTALL)
    ]


def get_rules() -> list[dict]:
    content = _read_file(RULES_FILE)
    rules = []

    for failure, symptoms_text in RULE_PATTERN.findall(content):
        symptoms = [
            symptom.strip()
            for symptom in symptoms_text.split(",")
            if symptom.strip()
        ]
        rules.append(
            {
                "failure": failure,
                "symptoms": symptoms,
            }
        )

    return rules


def get_knowledge_base() -> dict:
    return {
        "symptoms": get_symptoms(),
        "failures": get_failures(),
        "recommendations": get_recommendations(),
        "rules": get_rules(),
    }


def get_symptom_suggestions(selected_symptoms: list[str]) -> dict:
    selected = {_normalize_atom(symptom) for symptom in selected_symptoms}
    if not selected:
        return {"items": [], "matches": []}

    available_symptoms = set(get_symptoms())
    invalid_symptoms = sorted(selected - available_symptoms)
    if invalid_symptoms:
        raise ValueError(
            "Se recibieron sintomas no registrados: "
            + ", ".join(invalid_symptoms)
        )

    suggestions = set()
    matches = []

    for rule in get_rules():
        rule_symptoms = set(rule["symptoms"])
        if selected.issubset(rule_symptoms):
            missing_symptoms = sorted(rule_symptoms - selected)
            suggestions.update(missing_symptoms)
            matches.append(
                {
                    "failure": rule["failure"],
                    "matched_symptoms": sorted(selected),
                    "missing_symptoms": missing_symptoms,
                }
            )

    return {
        "items": sorted(suggestions),
        "matches": matches,
    }


def create_symptom(name: str) -> dict:
    symptom = _normalize_atom(name)
    symptoms = get_symptoms()

    if symptom in symptoms:
        raise ValueError(f"El sintoma '{symptom}' ya existe.")

    symptoms.append(symptom)
    _write_file(
        SYMPTOMS_FILE,
        _format_atom_facts(
            "sintoma",
            sorted(symptoms),
            "% Hechos de sintomas disponibles para el diagnostico.",
        ),
    )

    return {"name": symptom}


def update_symptom(current_name: str, new_name: str) -> dict:
    current_symptom = _normalize_atom(current_name)
    new_symptom = _normalize_atom(new_name)
    symptoms = get_symptoms()

    if current_symptom not in symptoms:
        raise ValueError(f"El sintoma '{current_symptom}' no existe.")

    if new_symptom != current_symptom and new_symptom in symptoms:
        raise ValueError(f"El sintoma '{new_symptom}' ya existe.")

    updated_symptoms = [
        new_symptom if symptom == current_symptom else symptom
        for symptom in symptoms
    ]
    _write_file(
        SYMPTOMS_FILE,
        _format_atom_facts(
            "sintoma",
            sorted(updated_symptoms),
            "% Hechos de sintomas disponibles para el diagnostico.",
        ),
    )

    if new_symptom != current_symptom:
        _replace_rule_symptom(current_symptom, new_symptom)

    return {"name": new_symptom}


def delete_symptom(name: str) -> dict:
    symptom = _normalize_atom(name)
    symptoms = get_symptoms()

    if symptom not in symptoms:
        raise ValueError(f"El sintoma '{symptom}' no existe.")

    rules_using_symptom = [
        rule["failure"]
        for rule in get_rules()
        if symptom in rule["symptoms"]
    ]
    if rules_using_symptom:
        raise ValueError(
            "No se puede eliminar el sintoma porque esta asociado a reglas: "
            + ", ".join(rules_using_symptom)
        )

    updated_symptoms = [item for item in symptoms if item != symptom]
    _write_file(
        SYMPTOMS_FILE,
        _format_atom_facts(
            "sintoma",
            sorted(updated_symptoms),
            "% Hechos de sintomas disponibles para el diagnostico.",
        ),
    )

    return {"name": symptom}


def create_failure(name: str) -> dict:
    failure = _normalize_atom(name)
    failures = get_failures()

    if failure in failures:
        raise ValueError(f"La falla '{failure}' ya existe.")

    failures.append(failure)
    _write_file(
        FAILURES_FILE,
        _format_atom_facts(
            "falla",
            sorted(failures),
            "% Catalogo de fallas diagnosticables.",
        ),
    )

    return {"name": failure}


def update_failure(current_name: str, new_name: str) -> dict:
    current_failure = _normalize_atom(current_name)
    new_failure = _normalize_atom(new_name)
    failures = get_failures()

    if current_failure not in failures:
        raise ValueError(f"La falla '{current_failure}' no existe.")

    if new_failure != current_failure and new_failure in failures:
        raise ValueError(f"La falla '{new_failure}' ya existe.")

    updated_failures = [
        new_failure if failure == current_failure else failure
        for failure in failures
    ]
    _write_file(
        FAILURES_FILE,
        _format_atom_facts(
            "falla",
            sorted(updated_failures),
            "% Catalogo de fallas diagnosticables.",
        ),
    )

    if new_failure != current_failure:
        _replace_atom_in_file(RECOMMENDATIONS_FILE, current_failure, new_failure)
        _replace_atom_in_file(RULES_FILE, current_failure, new_failure)

    return {"name": new_failure}


def delete_failure(name: str) -> dict:
    failure = _normalize_atom(name)
    failures = get_failures()

    if failure not in failures:
        raise ValueError(f"La falla '{failure}' no existe.")

    has_recommendation = any(
        recommendation["failure"] == failure
        for recommendation in get_recommendations()
    )
    has_rule = any(rule["failure"] == failure for rule in get_rules())

    blocking_reasons = []
    if has_recommendation:
        blocking_reasons.append("recomendaciones")
    if has_rule:
        blocking_reasons.append("reglas")

    if blocking_reasons:
        raise ValueError(
            "No se puede eliminar la falla porque esta asociada a: "
            + ", ".join(blocking_reasons)
        )

    updated_failures = [item for item in failures if item != failure]
    _write_file(
        FAILURES_FILE,
        _format_atom_facts(
            "falla",
            sorted(updated_failures),
            "% Catalogo de fallas diagnosticables.",
        ),
    )

    return {"name": failure}


def create_recommendation(failure_name: str, text: str) -> dict:
    failure = _normalize_atom(failure_name)
    recommendation_text = _normalize_recommendation_text(text)

    if failure not in get_failures():
        raise ValueError(f"La falla '{failure}' no existe.")

    recommendations = get_recommendations()
    if any(item["failure"] == failure for item in recommendations):
        raise ValueError(f"La falla '{failure}' ya tiene recomendacion.")

    recommendations.append({"failure": failure, "text": recommendation_text})
    _write_file(RECOMMENDATIONS_FILE, _format_recommendations(recommendations))

    return {"failure": failure, "text": recommendation_text}


def update_recommendation(current_failure_name: str, failure_name: str, text: str) -> dict:
    current_failure = _normalize_atom(current_failure_name)
    new_failure = _normalize_atom(failure_name)
    recommendation_text = _normalize_recommendation_text(text)

    if new_failure not in get_failures():
        raise ValueError(f"La falla '{new_failure}' no existe.")

    recommendations = get_recommendations()
    current_recommendation = next(
        (item for item in recommendations if item["failure"] == current_failure),
        None,
    )

    if current_recommendation is None:
        raise ValueError(f"La falla '{current_failure}' no tiene recomendacion.")

    if new_failure != current_failure and any(
        item["failure"] == new_failure for item in recommendations
    ):
        raise ValueError(f"La falla '{new_failure}' ya tiene recomendacion.")

    updated_recommendations = [
        {"failure": new_failure, "text": recommendation_text}
        if item["failure"] == current_failure
        else item
        for item in recommendations
    ]
    _write_file(RECOMMENDATIONS_FILE, _format_recommendations(updated_recommendations))

    return {"failure": new_failure, "text": recommendation_text}


def delete_recommendation(failure_name: str) -> dict:
    failure = _normalize_atom(failure_name)
    recommendations = get_recommendations()

    if not any(item["failure"] == failure for item in recommendations):
        raise ValueError(f"La falla '{failure}' no tiene recomendacion.")

    updated_recommendations = [
        item for item in recommendations if item["failure"] != failure
    ]
    _write_file(RECOMMENDATIONS_FILE, _format_recommendations(updated_recommendations))

    return {"failure": failure}


def _normalize_rule_payload(failure_name: str, symptom_names: list[str]) -> dict:
    failure = _normalize_atom(failure_name)
    symptoms = []

    for symptom_name in symptom_names:
        symptom = _normalize_atom(symptom_name)
        if symptom not in symptoms:
            symptoms.append(symptom)

    if not symptoms:
        raise ValueError("La regla debe tener al menos un sintoma.")

    available_failures = set(get_failures())
    available_symptoms = set(get_symptoms())
    failures_with_recommendation = {
        recommendation["failure"] for recommendation in get_recommendations()
    }

    if failure not in available_failures:
        raise ValueError(f"La falla '{failure}' no existe.")

    if failure not in failures_with_recommendation:
        raise ValueError(f"La falla '{failure}' no tiene recomendacion asociada.")

    invalid_symptoms = [
        symptom for symptom in symptoms if symptom not in available_symptoms
    ]
    if invalid_symptoms:
        raise ValueError(
            "La regla contiene sintomas no registrados: "
            + ", ".join(invalid_symptoms)
        )

    return {"failure": failure, "symptoms": symptoms}


def create_rule(failure_name: str, symptom_names: list[str]) -> dict:
    rule = _normalize_rule_payload(failure_name, symptom_names)
    rules = get_rules()

    if any(item["failure"] == rule["failure"] for item in rules):
        raise ValueError(f"La falla '{rule['failure']}' ya tiene regla.")

    rules.append(rule)
    _write_rules(rules)

    return rule


def update_rule(
    current_failure_name: str,
    failure_name: str,
    symptom_names: list[str],
) -> dict:
    current_failure = _normalize_atom(current_failure_name)
    rule = _normalize_rule_payload(failure_name, symptom_names)
    rules = get_rules()

    current_rule = next(
        (item for item in rules if item["failure"] == current_failure),
        None,
    )
    if current_rule is None:
        raise ValueError(f"La falla '{current_failure}' no tiene regla.")

    if rule["failure"] != current_failure and any(
        item["failure"] == rule["failure"] for item in rules
    ):
        raise ValueError(f"La falla '{rule['failure']}' ya tiene regla.")

    updated_rules = [
        rule if item["failure"] == current_failure else item
        for item in rules
    ]
    _write_rules(updated_rules)

    return rule


def delete_rule(failure_name: str) -> dict:
    failure = _normalize_atom(failure_name)
    rules = get_rules()

    if not any(item["failure"] == failure for item in rules):
        raise ValueError(f"La falla '{failure}' no tiene regla.")

    updated_rules = [item for item in rules if item["failure"] != failure]
    _write_rules(updated_rules)

    return {"failure": failure}
