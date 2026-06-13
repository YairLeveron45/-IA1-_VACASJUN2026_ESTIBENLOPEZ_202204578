const API_BASE_URL = "http://localhost:8000/api";

async function readJson(response) {
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "No se pudo completar la solicitud.");
  }

  return data;
}

export async function fetchSymptoms() {
  const response = await fetch(`${API_BASE_URL}/symptoms`);
  return readJson(response);
}

export async function fetchHistory() {
  const response = await fetch(`${API_BASE_URL}/history`);
  return readJson(response);
}

export async function requestDiagnosis(payload) {
  const response = await fetch(`${API_BASE_URL}/diagnose`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return readJson(response);
}

export async function fetchSymptomSuggestions(symptoms) {
  const response = await fetch(`${API_BASE_URL}/symptom-suggestions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ symptoms }),
  });

  return readJson(response);
}

export async function loginAdmin(password) {
  const response = await fetch(`${API_BASE_URL}/admin/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ password }),
  });

  return readJson(response);
}

export async function fetchAdminKnowledge(token) {
  const response = await fetch(`${API_BASE_URL}/admin/knowledge`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return readJson(response);
}

async function adminRequest(token, path, options = {}) {
  const response = await fetch(`${API_BASE_URL}/admin${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(options.headers || {}),
    },
  });

  return readJson(response);
}

export function createAdminSymptom(token, name) {
  return adminRequest(token, "/symptoms", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export function updateAdminSymptom(token, currentName, name) {
  return adminRequest(token, `/symptoms/${currentName}`, {
    method: "PUT",
    body: JSON.stringify({ name }),
  });
}

export function deleteAdminSymptom(token, name) {
  return adminRequest(token, `/symptoms/${name}`, {
    method: "DELETE",
  });
}

export function createAdminFailure(token, name) {
  return adminRequest(token, "/failures", {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export function updateAdminFailure(token, currentName, name) {
  return adminRequest(token, `/failures/${currentName}`, {
    method: "PUT",
    body: JSON.stringify({ name }),
  });
}

export function deleteAdminFailure(token, name) {
  return adminRequest(token, `/failures/${name}`, {
    method: "DELETE",
  });
}

export function createAdminRecommendation(token, failure, text) {
  return adminRequest(token, "/recommendations", {
    method: "POST",
    body: JSON.stringify({ failure, text }),
  });
}

export function updateAdminRecommendation(token, currentFailure, failure, text) {
  return adminRequest(token, `/recommendations/${currentFailure}`, {
    method: "PUT",
    body: JSON.stringify({ failure, text }),
  });
}

export function deleteAdminRecommendation(token, failure) {
  return adminRequest(token, `/recommendations/${failure}`, {
    method: "DELETE",
  });
}

export function createAdminRule(token, failure, symptoms) {
  return adminRequest(token, "/rules", {
    method: "POST",
    body: JSON.stringify({ failure, symptoms }),
  });
}

export function updateAdminRule(token, currentFailure, failure, symptoms) {
  return adminRequest(token, `/rules/${currentFailure}`, {
    method: "PUT",
    body: JSON.stringify({ failure, symptoms }),
  });
}

export function deleteAdminRule(token, failure) {
  return adminRequest(token, `/rules/${failure}`, {
    method: "DELETE",
  });
}

export function fetchAdminConfig(token) {
  return adminRequest(token, "/config");
}

export function updateAdminConfig(token, config) {
  return adminRequest(token, "/config", {
    method: "PUT",
    body: JSON.stringify(config),
  });
}
