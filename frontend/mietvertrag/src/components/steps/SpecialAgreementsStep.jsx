import React from "react";
import FormField from "../common/FormField.jsx";
import Textarea from "../common/Textarea.jsx";
import Input from "../common/Input.jsx";
import SectionCard from "../common/SectionCard.jsx";

const SUGGESTIONS = [
  "Der Mieter verpflichtet sich, Haustiere nur nach schriftlicher Zustimmung aller Mitbewohner zu halten.",
  "Die Kosten für einen Internetanschluss werden zu gleichen Teilen unter allen Mitbewohnern aufgeteilt.",
  "Der Mieter übernimmt die Kosten für die monatliche Reinigung des Badezimmers in Höhe von pauschal 20 €.",
  "Ein Fahrzeug des Mieters darf auf dem Stellplatz Nummer ___ abgestellt werden.",
  "Der Mieter erhält einen separaten Kellerabteil (Nr. ___) zur alleinigen Nutzung.",
];

export default function SpecialAgreementsStep({ form, updateField }) {
  const appendSuggestion = (text) => {
    const current = form.specialAgreements?.trim();
    const newVal  = current ? `${current}\n\n${text}` : text;
    updateField("specialAgreements", newVal);
  };

  return (
    <div className="gap-16">
      <SectionCard title="Vertragsort & -datum" icon="📌" defaultOpen>
        <div className="grid-2">
          <FormField label="Vertragsort">
            <Input
              value={form.contractPlace}
              onChange={(e) => updateField("contractPlace", e.target.value)}
              placeholder="Stuttgart"
            />
          </FormField>
          <FormField label="Vertragsdatum">
            <Input
              type="date"
              value={form.contractDate}
              onChange={(e) => updateField("contractDate", e.target.value)}
            />
          </FormField>
        </div>
      </SectionCard>

      <SectionCard title="Besondere Vereinbarungen" icon="✍️" defaultOpen>
        <div className="gap-12">
          <FormField
            label="Freie Vereinbarungen"
            hint="Hier können individuelle Regelungen eingetragen werden, die im Vertrag erscheinen."
          >
            <Textarea
              value={form.specialAgreements}
              onChange={(e) => updateField("specialAgreements", e.target.value)}
              placeholder="Besondere Vereinbarungen zwischen Vermieter und Mieter..."
              rows={6}
            />
          </FormField>

          <div>
            <p className="suggestions-label">💡 Häufig genutzte Klauseln:</p>
            <div className="suggestions-list">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  type="button"
                  className="suggestion-chip"
                  onClick={() => appendSuggestion(s)}
                  title="Klicken zum Einfügen"
                >
                  {s.length > 72 ? s.slice(0, 72) + "…" : s}
                </button>
              ))}
            </div>
          </div>
        </div>
      </SectionCard>

      <style>{`
        .suggestions-label { font-size: 13px; color: var(--text-muted); margin-bottom: 8px; }
        .suggestions-list  { display: flex; flex-direction: column; gap: 6px; }
        .suggestion-chip {
          text-align: left; background: var(--gray-light);
          border: 1px solid var(--border); border-radius: var(--radius);
          padding: 8px 12px; font-size: 12px; color: var(--text-muted);
          cursor: pointer; transition: all 0.15s;
        }
        .suggestion-chip:hover { background: var(--blue-light); color: var(--blue); border-color: var(--blue-mid); }
      `}</style>
    </div>
  );
}
