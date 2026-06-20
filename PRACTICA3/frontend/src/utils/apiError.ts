import axios from "axios";

/** Extrae un mensaje seguro de Axios o utiliza un texto de respaldo. */
export function getApiErrorMessage(
  error: unknown,
  fallback = "No fue posible completar la operación.",
): string {
  // Los errores desconocidos no se muestran directamente al usuario.
  if (!axios.isAxiosError(error)) return fallback;

  const detail = error.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg)
      .filter(Boolean)
      .join(" ");
  }
  return fallback;
}
