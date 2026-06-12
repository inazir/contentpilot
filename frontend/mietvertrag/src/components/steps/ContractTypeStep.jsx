import React from "react";
import { getContractTypeGroups } from "../../constants/contractTypes.js";

export default function ContractTypeStep({ form, onChangeType }) {
  const groups = getContractTypeGroups();

  return (
    <div className="gap-16">
      <div>
        <h2 className="step-title">Vertragsart wählen</h2>
        <p className="step-sub">Wählen Sie die Art des Mietverhältnisses. Die Auswahl bestimmt, welche Felder und Klauseln im Vertrag erscheinen.</p>
      </div>

      {Object.entries(groups).map(([group, types]) => (
        <div key={group}>
          <p className="type-group-label">{group}</p>
          <div className="type-grid">
            {types.map((ct) => (
              <button
                key={ct.id}
                type="button"
                className={`type-card${form.contractTypeId === ct.id ? " type-card--active" : ""}`}
                onClick={() => onChangeType(ct.id)}
              >
                <span className="type-card__icon">{ct.icon}</span>
                <span className="type-card__label">{ct.label}</span>
                {ct.isFurnished && <span className="type-card__tag">möbliert</span>}
                {ct.isShared   && <span className="type-card__tag type-card__tag--shared">WG</span>}
              </button>
            ))}
          </div>
        </div>
      ))}

      <style>{`
        .step-title { font-size: 20px; font-weight: 700; color: var(--text); margin-bottom: 4px; }
        .step-sub   { font-size: 14px; color: var(--text-muted); }
        .type-group-label { font-size: 12px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
        .type-grid  { display: grid; grid-template-columns: repeat(auto-fill, minmax(148px, 1fr)); gap: 10px; }
        .type-card  {
          display: flex; flex-direction: column; align-items: center; gap: 6px;
          padding: 14px 10px; border-radius: var(--radius);
          border: 2px solid var(--border); background: var(--bg-card);
          cursor: pointer; transition: all 0.15s; text-align: center;
        }
        .type-card:hover { border-color: var(--blue-mid); background: var(--blue-light); }
        .type-card--active { border-color: var(--blue); background: var(--blue-light); box-shadow: 0 0 0 3px rgba(30,80,160,0.12); }
        .type-card__icon  { font-size: 26px; }
        .type-card__label { font-size: 13px; font-weight: 500; color: var(--text); }
        .type-card__tag   { font-size: 10px; background: var(--blue-light); color: var(--blue); padding: 1px 6px; border-radius: 10px; }
        .type-card__tag--shared { background: var(--green-light); color: var(--green); }
      `}</style>
    </div>
  );
}
