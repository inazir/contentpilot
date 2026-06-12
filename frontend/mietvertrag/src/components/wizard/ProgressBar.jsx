import React from "react";

/**
 * ProgressBar
 * Shows numbered step indicators with labels.
 *
 * steps:   [{ id, label, icon }]
 * current: index of active step
 */
export default function ProgressBar({ steps, current, onStepClick }) {
  return (
    <nav className="progress-bar" aria-label="Fortschritt">
      <div className="progress-bar__track">
        <div
          className="progress-bar__fill"
          style={{ width: `${(current / (steps.length - 1)) * 100}%` }}
        />
      </div>
      <ol className="progress-bar__steps">
        {steps.map((step, i) => {
          const done    = i < current;
          const active  = i === current;
          const locked  = i > current;

          return (
            <li
              key={step.id}
              className={[
                "progress-step",
                done   ? "progress-step--done"   : "",
                active ? "progress-step--active" : "",
                locked ? "progress-step--locked" : "",
              ]
                .filter(Boolean)
                .join(" ")}
            >
              <button
                type="button"
                className="progress-step__btn"
                onClick={() => done && onStepClick && onStepClick(i)}
                disabled={locked}
                aria-current={active ? "step" : undefined}
                title={step.label}
              >
                <span className="progress-step__circle">
                  {done ? "✓" : step.icon || i + 1}
                </span>
                <span className="progress-step__label">{step.label}</span>
              </button>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
