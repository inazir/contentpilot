import React from "react";

/**
 * Select
 * options: [{ value, label }]
 */
export default function Select({
  id,
  value,
  onChange,
  options = [],
  disabled = false,
  placeholder,
  className = "",
}) {
  return (
    <select
      id={id}
      value={value ?? ""}
      onChange={onChange}
      disabled={disabled}
      className={`select ${className}`}
    >
      {placeholder && (
        <option value="" disabled>
          {placeholder}
        </option>
      )}
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}
