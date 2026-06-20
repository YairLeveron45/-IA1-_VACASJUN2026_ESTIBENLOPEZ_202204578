import {
  ChevronLeft,
  ChevronRight,
  KeyRound,
  Pencil,
  Plus,
  Search,
  ShieldCheck,
  UserRoundX,
  Users,
} from "lucide-react";
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { type FormEvent, useMemo, useState } from "react";
import {
  createUser,
  deactivateUser,
  listUsers,
  resetUserPassword,
  updateUser,
} from "../api/users";
import { Modal } from "../components/Modal";
import { useAuthStore } from "../store/authStore";
import type { User, UserRole } from "../types/auth";
import type { UserCreatePayload, UserUpdatePayload } from "../types/user";
import { getApiErrorMessage } from "../utils/apiError";

type UserModalState =
  | { mode: "create" }
  | { mode: "edit"; user: User }
  | null;

const initialForm: UserCreatePayload = {
  name: "",
  email: "",
  password: "",
  role: "operator",
};

export function UsersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [modal, setModal] = useState<UserModalState>(null);
  const [passwordUser, setPasswordUser] = useState<User | null>(null);
  const [confirmUser, setConfirmUser] = useState<User | null>(null);
  const [feedback, setFeedback] = useState<{
    tone: "success" | "error";
    message: string;
  } | null>(null);
  const currentUser = useAuthStore((state) => state.user);
  const queryClient = useQueryClient();

  const usersQuery = useQuery({
    queryKey: ["users", page],
    queryFn: () => listUsers(page, 20),
  });

  const filteredUsers = useMemo(() => {
    const users = usersQuery.data?.items ?? [];
    const term = search.trim().toLowerCase();
    if (!term) return users;
    return users.filter(
      (user) =>
        user.name.toLowerCase().includes(term) ||
        user.email.toLowerCase().includes(term) ||
        user.role.includes(term),
    );
  }, [search, usersQuery.data?.items]);

  const invalidateUsers = async () => {
    await queryClient.invalidateQueries({ queryKey: ["users"] });
  };

  const deactivateMutation = useMutation({
    mutationFn: deactivateUser,
    onSuccess: async () => {
      await invalidateUsers();
      setConfirmUser(null);
      setFeedback({
        tone: "success",
        message: "Usuario desactivado correctamente.",
      });
    },
    onError: (error) =>
      setFeedback({ tone: "error", message: getApiErrorMessage(error) }),
  });

  const totalPages = Math.max(
    1,
    Math.ceil((usersQuery.data?.total ?? 0) / 20),
  );

  return (
    <div className="management-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Administración</span>
          <h1>Usuarios y roles</h1>
          <p>
            Controla quién puede acceder y qué operaciones puede realizar.
          </p>
        </div>
        <button
          className="primary-button page-action"
          onClick={() => setModal({ mode: "create" })}
        >
          <Plus size={18} />
          Nuevo usuario
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
              placeholder="Buscar por nombre, correo o rol"
            />
          </div>
          <div className="management-summary">
            <Users size={17} />
            <span>
              <strong>{usersQuery.data?.total ?? 0}</strong> usuarios
            </span>
          </div>
        </div>

        {usersQuery.isLoading ? (
          <TableSkeleton />
        ) : usersQuery.isError ? (
          <div className="empty-state">
            <UserRoundX size={30} />
            <strong>No fue posible cargar los usuarios</strong>
            <button onClick={() => usersQuery.refetch()}>Intentar de nuevo</button>
          </div>
        ) : filteredUsers.length === 0 ? (
          <div className="empty-state">
            <Search size={30} />
            <strong>No encontramos coincidencias</strong>
            <span>Prueba con otro nombre, correo o rol.</span>
          </div>
        ) : (
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th>Creación</th>
                  <th aria-label="Acciones" />
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user) => (
                  <tr key={user.id}>
                    <td>
                      <div className="table-user">
                        <div className="table-avatar">
                          {user.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <strong>{user.name}</strong>
                          <span>{user.email}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className={`role-badge role-badge--${user.role}`}>
                        {user.role === "admin" && <ShieldCheck size={14} />}
                        {user.role === "admin" ? "Administrador" : "Operador"}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`status-badge ${
                          user.is_active
                            ? "status-badge--active"
                            : "status-badge--inactive"
                        }`}
                      >
                        {user.is_active ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td className="table-muted">
                      {new Intl.DateTimeFormat("es-GT", {
                        dateStyle: "medium",
                      }).format(new Date(user.created_at))}
                    </td>
                    <td>
                      <div className="table-actions">
                        <button
                          title="Editar usuario"
                          onClick={() => setModal({ mode: "edit", user })}
                        >
                          <Pencil size={16} />
                        </button>
                        <button
                          title="Restablecer contraseña"
                          onClick={() => setPasswordUser(user)}
                        >
                          <KeyRound size={16} />
                        </button>
                        <button
                          title="Desactivar usuario"
                          className="table-action--danger"
                          disabled={
                            !user.is_active || user.id === currentUser?.id
                          }
                          onClick={() => setConfirmUser(user)}
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
        <UserFormModal
          state={modal}
          onClose={() => setModal(null)}
          onSuccess={async (message) => {
            await invalidateUsers();
            setModal(null);
            setFeedback({ tone: "success", message });
          }}
        />
      )}

      {passwordUser && (
        <PasswordModal
          user={passwordUser}
          onClose={() => setPasswordUser(null)}
          onSuccess={() => {
            setPasswordUser(null);
            setFeedback({
              tone: "success",
              message: "Contraseña restablecida correctamente.",
            });
          }}
        />
      )}

      {confirmUser && (
        <Modal
          title="Desactivar usuario"
          description="El usuario perderá acceso al sistema inmediatamente."
          width="small"
          onClose={() => setConfirmUser(null)}
        >
          <div className="confirm-content">
            <p>
              ¿Deseas desactivar a <strong>{confirmUser.name}</strong>?
            </p>
            <div className="modal-actions">
              <button
                className="ghost-button"
                onClick={() => setConfirmUser(null)}
              >
                Cancelar
              </button>
              <button
                className="danger-button"
                disabled={deactivateMutation.isPending}
                onClick={() => deactivateMutation.mutate(confirmUser.id)}
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

function UserFormModal({
  state,
  onClose,
  onSuccess,
}: {
  state: Exclude<UserModalState, null>;
  onClose: () => void;
  onSuccess: (message: string) => void;
}) {
  const isEditing = state.mode === "edit";
  const [form, setForm] = useState<UserCreatePayload>(() =>
    isEditing
      ? {
          name: state.user.name,
          email: state.user.email,
          password: "",
          role: state.user.role,
        }
      : initialForm,
  );
  const [isActive, setIsActive] = useState(
    isEditing ? state.user.is_active : true,
  );
  const [error, setError] = useState("");

  const mutation = useMutation({
    mutationFn: async () => {
      if (isEditing) {
        const payload: UserUpdatePayload = {
          name: form.name,
          email: form.email,
          role: form.role,
          is_active: isActive,
        };
        return updateUser(state.user.id, payload);
      }
      return createUser(form);
    },
    onSuccess: () =>
      onSuccess(
        isEditing
          ? "Usuario actualizado correctamente."
          : "Usuario creado correctamente.",
      ),
    onError: (requestError) => setError(getApiErrorMessage(requestError)),
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    mutation.mutate();
  };

  return (
    <Modal
      title={isEditing ? "Editar usuario" : "Nuevo usuario"}
      description={
        isEditing
          ? "Actualiza la información y los permisos de acceso."
          : "Crea una cuenta para un administrador u operador."
      }
      onClose={onClose}
    >
      <form className="entity-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label>
            Nombre completo
            <input
              value={form.name}
              onChange={(event) =>
                setForm((value) => ({ ...value, name: event.target.value }))
              }
              minLength={2}
              required
            />
          </label>
          <label>
            Correo electrónico
            <input
              type="email"
              value={form.email}
              onChange={(event) =>
                setForm((value) => ({ ...value, email: event.target.value }))
              }
              required
            />
          </label>
          <label>
            Rol
            <select
              value={form.role}
              onChange={(event) =>
                setForm((value) => ({
                  ...value,
                  role: event.target.value as UserRole,
                }))
              }
            >
              <option value="operator">Operador</option>
              <option value="admin">Administrador</option>
            </select>
          </label>
          {!isEditing && (
            <label>
              Contraseña temporal
              <input
                type="password"
                value={form.password}
                onChange={(event) =>
                  setForm((value) => ({
                    ...value,
                    password: event.target.value,
                  }))
                }
                minLength={8}
                required
              />
            </label>
          )}
        </div>

        {isEditing && (
          <label className="switch-row">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(event) => setIsActive(event.target.checked)}
            />
            <span>
              <strong>Cuenta activa</strong>
              <small>Permite que el usuario inicie sesión.</small>
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
                : "Crear usuario"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function PasswordModal({
  user,
  onClose,
  onSuccess,
}: {
  user: User;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");

  const mutation = useMutation({
    mutationFn: () =>
      resetUserPassword(user.id, { new_password: password }),
    onSuccess,
    onError: (requestError) => setError(getApiErrorMessage(requestError)),
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    if (password !== confirmation) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    mutation.mutate();
  };

  return (
    <Modal
      title="Restablecer contraseña"
      description={`Define una nueva contraseña para ${user.name}.`}
      width="small"
      onClose={onClose}
    >
      <form className="entity-form" onSubmit={handleSubmit}>
        <label>
          Nueva contraseña
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            minLength={8}
            required
          />
        </label>
        <label>
          Confirmar contraseña
          <input
            type="password"
            value={confirmation}
            onChange={(event) => setConfirmation(event.target.value)}
            minLength={8}
            required
          />
        </label>
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
            {mutation.isPending ? "Guardando..." : "Cambiar contraseña"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function TableSkeleton() {
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
