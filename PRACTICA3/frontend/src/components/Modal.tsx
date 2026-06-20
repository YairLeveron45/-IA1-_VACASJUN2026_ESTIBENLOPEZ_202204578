import { X } from "lucide-react";
import type { ReactNode } from "react";

interface ModalProps {
  title: string;
  description?: string;
  children: ReactNode;
  onClose: () => void;
  width?: "normal" | "small" | "large";
}

export function Modal({
  title,
  description,
  children,
  onClose,
  width = "normal",
}: ModalProps) {
  return (
    <div className="modal-layer" role="presentation">
      <button
        className="modal-backdrop"
        onClick={onClose}
        aria-label="Cerrar modal"
      />
      <section
        className={`modal-card modal-card--${width}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <header className="modal-card__header">
          <div>
            <h2>{title}</h2>
            {description && <p>{description}</p>}
          </div>
          <button
            type="button"
            className="icon-button"
            onClick={onClose}
            aria-label="Cerrar"
          >
            <X size={18} />
          </button>
        </header>
        {children}
      </section>
    </div>
  );
}
