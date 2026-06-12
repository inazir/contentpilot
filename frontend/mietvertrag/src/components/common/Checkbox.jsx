import React from "react";

/**
 * Checkbox
 * Renders a styled checkbox + inline label.
 */
export default function Checkbox({ id, label, checked, onChange, disabled = false }) {
  return (
    <label className={`checkbox${disabled ? " checkbox--disabled" : ""}`} htmlFor={id}>
      <input
        id={id}
        type="checkbox"
        checked={!!checked}
        onChange={onChange}
        disabled={disabled}
        className="checkbox__input"
      />
      <span className="checkbox__box" />
      <span className="checkbox__label">{label}</span>
    </label>
  );
}
