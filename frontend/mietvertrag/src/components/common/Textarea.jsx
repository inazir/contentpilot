import React from "react";

export default function Textarea({
  id,
  value,
  onChange,
  placeholder,
  rows = 4,
  disabled = false,
  className = "",
}) {
  return (
    <textarea
      id={id}
      value={value ?? ""}
      onChange={onChange}
      placeholder={placeholder}
      rows={rows}
      disabled={disabled}
      className={`textarea ${className}`}
    />
  );
}
