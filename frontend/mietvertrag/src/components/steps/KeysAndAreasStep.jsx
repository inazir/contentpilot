import React from "react";
import FormField from "../common/FormField.jsx";
import Input from "../common/Input.jsx";
import Select from "../common/Select.jsx";
import Checkbox from "../common/Checkbox.jsx";
import Button from "../common/Button.jsx";
import SectionCard from "../common/SectionCard.jsx";

const KEY_TYPE_OPTIONS = [
  { value: "wohnungsschluessel",    label: "Wohnungsschlüssel" },
  { value: "hausschluessel",        label: "Hausschlüssel" },
  { value: "zimmerschluessel",      label: "Zimmerschlüssel" },
  { value: "briefkastenschluessel", label: "Briefkastenschlüssel" },
  { value: "kellerschluessel",      label: "Kellerschlüssel" },
  { value: "garagenschluessel",     label: "Garagenschlüssel" },
  { value: "muellchipkarte",        label: "Müll-Chipkarte" },
];

function KeyRow({ keyItem, onChange, onRemove }) {
  return (
    <div className="key-row">
      <FormField label="Schlüsselart">
        <Select
          value={keyItem.type}
          onChange={(e) => onChange("type", e.target.value)}
          options={KEY_TYPE_OPTIONS}
        />
      </FormField>
      <FormField label="Anzahl">
        <Input
          type="number"
          value={keyItem.quantity}
          onChange={(e) => onChange("quantity", e.target.value)}
          min="1"
        />
      </FormField>
      <FormField label="Anmerkungen">
        <Input
          value={keyItem.notes}
          onChange={(e) => onChange("notes", e.target.value)}
          placeholder="Optional"
        />
      </FormField>
      <Button variant="danger" size="sm" onClick={onRemove}>✕</Button>
    </div>
  );
}

export default function KeysAndAreasStep({ form, updateField, addKey, updateKey, removeKey }) {
  const sa = form.sharedAreas;
  const fb = (field) => (e) => updateField(`sharedAreas.${field}`, e.target.checked);

  return (
    <div className="gap-16">
      <SectionCard title="Schlüsselübergabe" icon="🔑" defaultOpen>
        <div className="gap-12">
          {form.keys.length === 0 && (
            <p style={{ color: "var(--text-muted)", fontSize: 14 }}>
              Noch keine Schlüssel erfasst. Klicken Sie auf „Schlüssel hinzufügen".
            </p>
          )}
          {form.keys.map((k, i) => (
            <KeyRow
              key={k.id}
              keyItem={k}
              onChange={(field, val) => updateKey(i, field, val)}
              onRemove={() => removeKey(i)}
            />
          ))}
          <Button variant="secondary" size="sm" onClick={addKey} icon="＋">
            Schlüssel hinzufügen
          </Button>
        </div>
      </SectionCard>

      <SectionCard title="Gemeinschaftsbereiche" icon="🏠" defaultOpen>
        <p style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 12 }}>
          Welche Bereiche werden gemeinschaftlich genutzt?
        </p>
        <div className="checkbox-grid">
          <Checkbox id="sa_kitchen"  label="Küche"       checked={sa.kitchen}  onChange={fb("kitchen")} />
          <Checkbox id="sa_bathroom" label="Badezimmer"  checked={sa.bathroom} onChange={fb("bathroom")} />
          <Checkbox id="sa_toilet"   label="WC"          checked={sa.toilet}   onChange={fb("toilet")} />
          <Checkbox id="sa_laundry"  label="Waschküche"  checked={sa.laundry}  onChange={fb("laundry")} />
          <Checkbox id="sa_storage"  label="Abstellraum" checked={sa.storage}  onChange={fb("storage")} />
          <Checkbox id="sa_balcony"  label="Balkon"      checked={sa.balcony}  onChange={fb("balcony")} />
          <Checkbox id="sa_garden"   label="Garten"      checked={sa.garden}   onChange={fb("garden")} />
        </div>
      </SectionCard>

      <style>{`
        .key-row { display: grid; grid-template-columns: 2fr 1fr 2fr auto; gap: 10px; align-items: end; padding: 10px; background: var(--gray-light); border-radius: var(--radius); }
        .checkbox-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px,1fr)); gap: 12px; }
        @media (max-width: 640px) { .key-row { grid-template-columns: 1fr 1fr; } }
      `}</style>
    </div>
  );
}
