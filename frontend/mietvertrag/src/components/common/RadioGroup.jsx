import React from "react";

/**
 * RadioGroup
 * options: [{ value, label }]
 */
export default function RadioGroup({ name, options = [], value, onChange }) {
  return (
    <div className="radio-group" role="radiogroup">
      {options.map((opt) => (
        <label key={opt.value} className="radio">
          <input
            type="radio"
            name={name}
            value={opt.value}
            checked={value === opt.value}
            onChange={() => onChange(opt.value)}
            className="radio__input"
          />
          <span className="radio__dot" />
          <span className="radio__label">{opt.label}</span>
        </label>
      ))}
    </div>
  );
}
