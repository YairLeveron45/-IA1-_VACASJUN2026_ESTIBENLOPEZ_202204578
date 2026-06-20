import type { LucideIcon } from "lucide-react";

interface PagePlaceholderProps {
  icon: LucideIcon;
  eyebrow: string;
  title: string;
  description: string;
}

export function PagePlaceholder({
  icon: Icon,
  eyebrow,
  title,
  description,
}: PagePlaceholderProps) {
  return (
    <section className="placeholder-card">
      <div className="placeholder-card__icon">
        <Icon size={28} />
      </div>
      <span className="eyebrow">{eyebrow}</span>
      <h1>{title}</h1>
      <p>{description}</p>
      <div className="placeholder-card__line" />
      <span className="placeholder-card__note">
        El backend de este módulo ya está disponible. Conectaremos su interfaz en
        el siguiente bloque.
      </span>
    </section>
  );
}
