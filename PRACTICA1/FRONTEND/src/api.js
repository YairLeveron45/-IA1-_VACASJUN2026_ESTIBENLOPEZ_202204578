const API_BASE_URL = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  const data = await response.json();

  if (!response.ok) {
    const message = data.detail ?? "Ocurrio un error al consultar el backend.";
    throw new Error(message);
  }

  return data;
}

export async function fetchBestRoute(payload) {
  return request("/best-route", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchCities() {
  return request("/cities");
}

export async function fetchAllRoutes(payload) {
  return request("/routes", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createCity(payload) {
  return request("/cities", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createConnection(payload) {
  return request("/connections", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
