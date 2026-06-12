import React from "react";

/**
 * FormField
 * Wraps a label + input/select/textarea with consistent layout and error display.
 * Pass `error` string to show validation feedback.
 */
export default function FormField({
  label,
  htmlFor,
  error,
  required,
  hint,
  children,
  className = "",
}) {
  return (
    <div className={`form-field${error ? " form-field--error" : ""} ${className}`}>
      {label && (
        <label className="form-field__label" htmlFor={htmlFor}>
          {label}
          {required && <span className="form-field__required"> *</span>}
        </label>
      )}
      {children}
      {hint && !error && <p className="form-field__hint">{hint}</p>}
      {error && <p className="form-field__error">{error}</p>}
    </div>
  );
}
