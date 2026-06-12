import React from "react";

/**
 * Input
 * A styled text/date/number/email/tel input.
 */
export default function Input({
  id,
  type = "text",
  value,
  onChange,
  placeholder,
  disabled = false,
  readOnly = false,
  min,
  max,
  step,
  className = "",
}) {
  return (
    <input
      id={id}
      type={type}
      value={value ?? ""}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      readOnly={readOnly}
      min={min}
      max={max}
      step={step}
      className={`input ${className}`}
    />
  );
}
