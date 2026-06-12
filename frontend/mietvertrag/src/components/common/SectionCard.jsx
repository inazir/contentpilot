import React, { useState } from "react";

/**
 * SectionCard
 * A collapsible card wrapping a form section.
 */
export default function SectionCard({
  title,
  icon,
  children,
  defaultOpen = true,
  badge,
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={`section-card${open ? " section-card--open" : ""}`}>
      <button
        type="button"
        className="section-card__header"
        onClick={() => setOpen((v) => !v)}
      >
        <span className="section-card__title">
          {icon && <span className="section-card__icon">{icon}</span>}
          {title}
        </span>
        <span className="section-card__meta">
          {badge && <span className="section-card__badge">{badge}</span>}
          <span className="section-card__chevron">{open ? "▲" : "▼"}</span>
        </span>
      </button>
      {open && <div className="section-card__body">{children}</div>}
    </div>
  );
}
