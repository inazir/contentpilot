import React from "react";

/**
 * Badge
 * Small label chip.
 * variant: "blue" | "green" | "orange" | "red" | "gray"
 */
export default function Badge({ children, variant = "blue" }) {
  return <span className={`badge badge--${variant}`}>{children}</span>;
}
