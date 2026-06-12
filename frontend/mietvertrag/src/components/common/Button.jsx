import React from "react";

/**
 * Button
 * variant: "primary" | "secondary" | "danger" | "ghost"
 * size:    "sm" | "md" | "lg"
 */
export default function Button({
  children,
  onClick,
  type = "button",
  variant = "primary",
  size = "md",
  disabled = false,
  fullWidth = false,
  icon,
  className = "",
}) {
  const cls = [
    "btn",
    `btn--${variant}`,
    `btn--${size}`,
    fullWidth ? "btn--full" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button type={type} className={cls} onClick={onClick} disabled={disabled}>
      {icon && <span className="btn__icon">{icon}</span>}
      {children}
    </button>
  );
}
