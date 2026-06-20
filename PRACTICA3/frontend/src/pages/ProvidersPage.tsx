import {
  Building2,
  ChevronLeft,
  ChevronRight,
  MapPin,
  Pencil,
  Plus,
  Search,
  Truck,
  UserRoundX,
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useMemo, useState } from "react";
import {
  createProvider,
  deactivateProvider,
  listProviders,
  updateProvider,
} from "../api/providers";
import { Modal } from "../components/Modal";
import type {
  Provider,
  ProviderPayload,
  ProviderUpdatePayload,
} from "../types/provider";
import { getApiErrorMessage } from "../utils/apiError";

type ProviderModalState =
  | { mode: "create" }
  | { mode: "edit"; provider: Provider }
  | null;

const emptyForm: ProviderPayload = {
  name: "",
  nit: "",
  email: null,
  phone: null,
  address: null,
};

export function ProvidersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [modal, setModal] = useState<ProviderModalState>(null);
  const [confirmProvider, setConfirmProvider] = useState<Provider | null>(null);
  const [feedback, setFeedback] = useState<{
    tone: "success" | "error";
    message: string;
  } | null>(null);
  const queryClient = useQueryClient();

  const providersQuery = useQuery({
    queryKey: ["providers", page],
    queryFn: () => listProviders(page, 20),
  });

  const filteredProviders = useMemo(() => {
    const providers = providersQuery.data?.items ?? [];
    const term = search.trim().toLowerCase();
    if (!term) return providers;
    return providers.filter((provider) =>
      [provider.name, provider.nit, provider.email, provider.phone]
        .filter(Boolean)
        .some((value) => value?.toLowerCase().includes(term)),
    );
  }, [providersQuery.data?.items, search]);

  const invalidateProviders = async () => {
    await queryClient.invalidateQueries({ queryKey: ["providers"] });
  };

  const deactivateMutation = useMutation({
    mutationFn: deactivateProvider,
    onSuccess: async () => {
      await invalidateProviders();
      setConfirmProvider(null);
      setFeedback({
        tone: "success",
        message: "Proveedor desactivado correctamente.",
      });
    },
    onError: (error) =>
      setFeedback({ tone: "error", message: getApiErrorMessage(error) }),
  });

  const totalPages = Math.max(
    1,
    Math.ceil((providersQuery.data?.total ?? 0) / 20),
  );

  return (
    <div className="management-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Directorio</span>
          <h1>Proveedores</h1>
          <p>Administra los datos comerciales y tributarios de tus proveedores.</p>
        </div>
        <button
          className="primary-button page-action"
          onClick={() => setModal({ mode: "create" })}
        >
          <Plus size={18} />
          Nuevo proveedor
        </button>
      </section>

      {feedback && (
        <div className={`inline-alert inline-alert--${feedback.tone}`}>
          {feedback.message}
          <button onClick={() => setFeedback(null)}>Cerrar</button>
        </div>
      )}

      <section className="management-card">
        <div className="management-toolbar">
          <div className="search-box">
            <Search size={17} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Buscar por nombre, NIT, correo o teléfono"
            />
          </div>
          <div className="management-summary">
            <Truck size={17} />
            <span>
              <strong>{providersQuery.data?.total ?? 0}</strong> proveedores
            </span>
          </div>
        </div>

        {providersQuery.isLoading ? (
          <ProviderSkeleton />
        ) : providersQuery.isError ? (
          <div className="empty-state">
            <UserRoundX size={30} />
            <strong>No fue posible cargar los proveedores</strong>
            <button onClick={() => providersQuery.refetch()}>
              Intentar de nuevo
            </button>
          </div>
        ) : filteredProviders.length === 0 ? (
          <div className="empty-state">
            <Building2 size={30} />
            <strong>No encontramos proveedores</strong>
            <span>Registra uno nuevo o prueba con otra búsqueda.</span>
          </div>
        ) : (
          <div className="table-scroll">
            <table className="data-table provider-table">
              <thead>
                <tr>
                  <th>Proveedor</th>
                  <th>Contacto</th>
                  <th>Estado</th>
                  <th>Dirección</th>
                  <th aria-label="Acciones" />
                </tr>
              </thead>
              <tbody>
                {filteredProviders.map((provider) => (
                  <tr key={provider.id}>
                    <td>
                      <div className="table-user">
                        <div className="table-avatar">
                          {provider.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <strong>{provider.name}</strong>
                          <span>NIT {provider.nit}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="provider-contact">
                        <strong>{provider.email || "Sin correo"}</strong>
                        <span>{provider.phone || "Sin teléfono"}</span>
                      </div>
                    </td>
                    <td>
                      <span
                        className={`status-badge ${
                          provider.is_active
                            ? "status-badge--active"
                            : "status-badge--inactive"
                        }`}
                      >
                        {provider.is_active ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td>
                      <div className="provider-address">
                        <MapPin size={14} />
                        <span>{provider.address || "Sin dirección"}</span>
                      </div>
                    </td>
                    <td>
                      <div className="table-actions">
                        <button
                          title="Editar proveedor"
                          onClick={() =>
                            setModal({ mode: "edit", provider })
                          }
                        >
                          <Pencil size={16} />
                        </button>
                        <button
                          title="Desactivar proveedor"
                          className="table-action--danger"
                          disabled={!provider.is_active}
                          onClick={() => setConfirmProvider(provider)}
                        >
                          <UserRoundX size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <footer className="pagination">
          <span>
            Página {page} de {totalPages}
          </span>
          <div>
            <button
              disabled={page === 1}
              onClick={() => setPage((value) => value - 1)}
              aria-label="Página anterior"
            >
              <ChevronLeft size={17} />
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((value) => value + 1)}
              aria-label="Página siguiente"
            >
              <ChevronRight size={17} />
            </button>
          </div>
        </footer>
      </section>

      {modal && (
        <ProviderFormModal
          state={modal}
          onClose={() => setModal(null)}
          onSuccess={async (message) => {
            await invalidateProviders();
            setModal(null);
            setFeedback({ tone: "success", message });
          }}
        />
      )}

      {confirmProvider && (
        <Modal
          title="Desactivar proveedor"
          description="El proveedor permanecerá en el historial, pero no estará activo."
          width="small"
          onClose={() => setConfirmProvider(null)}
        >
          <div className="confirm-content">
            <p>
              ¿Deseas desactivar a <strong>{confirmProvider.name}</strong>?
            </p>
            <div className="modal-actions">
              <button
                className="ghost-button"
                onClick={() => setConfirmProvider(null)}
              >
                Cancelar
              </button>
              <button
                className="danger-button"
                disabled={deactivateMutation.isPending}
                onClick={() => deactivateMutation.mutate(confirmProvider.id)}
              >
                {deactivateMutation.isPending
                  ? "Desactivando..."
                  : "Desactivar"}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

function ProviderFormModal({
  state,
  onClose,
  onSuccess,
}: {
  state: Exclude<ProviderModalState, null>;
  onClose: () => void;
  onSuccess: (message: string) => void;
}) {
  const isEditing = state.mode === "edit";
  const [form, setForm] = useState<ProviderPayload>(() =>
    isEditing
      ? {
          name: state.provider.name,
          nit: state.provider.nit,
          email: state.provider.email,
          phone: state.provider.phone,
          address: state.provider.address,
        }
      : emptyForm,
  );
  const [isActive, setIsActive] = useState(
    isEditing ? state.provider.is_active : true,
  );
  const [error, setError] = useState("");

  const mutation = useMutation({
    mutationFn: () => {
      const normalized: ProviderPayload = {
        name: form.name.trim(),
        nit: form.nit.trim(),
        email: form.email?.trim() || null,
        phone: form.phone?.trim() || null,
        address: form.address?.trim() || null,
      };
      if (isEditing) {
        const payload: ProviderUpdatePayload = {
          ...normalized,
          is_active: isActive,
        };
        return updateProvider(state.provider.id, payload);
      }
      return createProvider(normalized);
    },
    onSuccess: () =>
      onSuccess(
        isEditing
          ? "Proveedor actualizado correctamente."
          : "Proveedor creado correctamente.",
      ),
    onError: (requestError) => setError(getApiErrorMessage(requestError)),
  });

  const updateField = (field: keyof ProviderPayload, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    mutation.mutate();
  };

  return (
    <Modal
      title={isEditing ? "Editar proveedor" : "Nuevo proveedor"}
      description="Completa los datos comerciales y de contacto."
      onClose={onClose}
    >
      <form className="entity-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            Nombre o razón social
            <input
              value={form.name}
              onChange={(event) => updateField("name", event.target.value)}
              minLength={2}
              maxLength={160}
              required
            />
          </label>
          <label>
            NIT
            <input
              value={form.nit}
              onChange={(event) => updateField("nit", event.target.value)}
              minLength={2}
              maxLength={30}
              required
            />
          </label>
          <label>
            Correo electrónico
            <input
              type="email"
              value={form.email ?? ""}
              onChange={(event) => updateField("email", event.target.value)}
            />
          </label>
          <label>
            Teléfono
            <input
              value={form.phone ?? ""}
              onChange={(event) => updateField("phone", event.target.value)}
              maxLength={30}
            />
          </label>
          <label className="form-field--full">
            Dirección
            <textarea
              value={form.address ?? ""}
              onChange={(event) => updateField("address", event.target.value)}
              maxLength={300}
              rows={3}
            />
          </label>
        </div>

        {isEditing && (
          <label className="switch-row">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(event) => setIsActive(event.target.checked)}
            />
            <span>
              <strong>Proveedor activo</strong>
              <small>Permite utilizarlo en nuevos registros de facturas.</small>
            </span>
          </label>
        )}

        {error && <div className="form-error">{error}</div>}

        <div className="modal-actions">
          <button type="button" className="ghost-button" onClick={onClose}>
            Cancelar
          </button>
          <button
            type="submit"
            className="primary-button modal-primary"
            disabled={mutation.isPending}
          >
            {mutation.isPending
              ? "Guardando..."
              : isEditing
                ? "Guardar cambios"
                : "Crear proveedor"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function ProviderSkeleton() {
  return (
    <div className="table-skeleton">
      {Array.from({ length: 5 }).map((_, index) => (
        <div key={index}>
          <i />
          <i />
          <i />
          <i />
        </div>
      ))}
    </div>
  );
}
