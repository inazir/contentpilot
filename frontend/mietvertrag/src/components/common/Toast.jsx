import React, { useEffect, useState } from "react";

/**
 * Toast
 * Shows a transient notification.
 * Props:
 *   visible  - boolean trigger
 *   message  - string
 *   type     - "success" | "error" | "info"
 */
export default function Toast({ visible, message, type = "success" }) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (visible) {
      setShow(true);
      const t = setTimeout(() => setShow(false), 2500);
      return () => clearTimeout(t);
    }
  }, [visible]);

  if (!show) return null;

  return (
    <div className={`toast toast--${type}`} role="status" aria-live="polite">
      <span className="toast__icon">
        {type === "success" ? "✓" : type === "error" ? "✕" : "ℹ"}
      </span>
      {message}
    </div>
  );
}
