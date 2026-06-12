import React from "react";
import FormField from "../common/FormField.jsx";
import Input from "../common/Input.jsx";
import Select from "../common/Select.jsx";
import Button from "../common/Button.jsx";
import SectionCard from "../common/SectionCard.jsx";

const CONDITION_OPTIONS = [
  { value: "neu",        label: "Neu" },
  { value: "gut",        label: "Gut" },
  { value: "gebraucht",  label: "Gebraucht" },
  { value: "beschädigt", label: "Beschädigt" },
];

const ROOM_OPTIONS = [
  { value: "zimmer",       label: "Zimmer / Privatbereich" },
  { value: "gemeinschaft", label: "Gemeinschaftsbereich" },
  { value: "wohnung",      label: "Gesamte Wohnung" },
];

function InventoryRow({ item, onChange, onRemove }) {
  const f = (field) => (e) => onChange(field, e.target.value);

  return (
    <div className="inv-row">
      <div className="inv-row__main">
        <FormField label="Gegenstand">
          <Input value={item.name} onChange={f("name")} placeholder="z.B. Bett" />
        </FormField>
        <FormField label="Anzahl">
          <Input type="number" value={item.quantity} onChange={f("quantity")} min="1" />
        </FormField>
        <FormField label="Zustand">
          <Select value={item.condition} onChange={f("condition")} options={CONDITION_OPTIONS} />
        </FormField>
        <FormField label="Bereich">
          <Select value={item.room} onChange={f("room")} options={ROOM_OPTIONS} />
        </FormField>
        <FormField label="Zeitwert (€)">
          <Input type="number" value={item.replacementValue} onChange={f("replacementValue")} placeholder="0" min="0" />
        </FormField>
      </div>
      <FormField label="Anmerkungen">
        <Input value={item.notes} onChange={f("notes")} placeholder="Optional" />
      </FormField>
      <Button variant="danger" size="sm" onClick={onRemove}>✕ Entfernen</Button>
    </div>
  );
}

export default function InventoryStep({ form, addInventoryItem, updateInventoryItem, removeInventoryItem }) {
  const grouped = {
    zimmer:       form.inventory.filter((i) => i.room === "zimmer"),
    gemeinschaft: form.inventory.filter((i) => i.room === "gemeinschaft"),
    wohnung:      form.inventory.filter((i) => i.room === "wohnung"),
  };

  const groupLabel = { zimmer: "Zimmer", gemeinschaft: "Gemeinschaftsbereich", wohnung: "Gesamte Wohnung" };
  const allIndexed = form.inventory.map((item, i) => ({ item, i }));

  return (
    <div className="gap-16">
      <div className="info-box">
        💡 Inventar wird in die Inventarliste und in das Übergabeprotokoll übernommen. Für unmöblierte Objekte können Sie diesen Schritt überspringen.
      </div>

      {form.inventory.length === 0 ? (
        <SectionCard title="Kein Inventar erfasst" icon="📦" defaultOpen>
          <p style={{ color: "var(--text-muted)", fontSize: 14 }}>
            Klicken Sie auf „Gegenstand hinzufügen" um Inventar zu erfassen.
          </p>
        </SectionCard>
      ) : (
        Object.entries(grouped).map(([roomKey, items]) =>
          items.length > 0 ? (
            <SectionCard
              key={roomKey}
              title={groupLabel[roomKey]}
              icon="📋"
              badge={`${items.length} Gegenstand/Gegenstände`}
              defaultOpen
            >
              <div className="gap-16">
                {allIndexed
                  .filter(({ item }) => item.room === roomKey)
                  .map(({ item, i }) => (
                    <InventoryRow
                      key={item.id}
                      item={item}
                      onChange={(field, val) => updateInventoryItem(i, field, val)}
                      onRemove={() => removeInventoryItem(i)}
                    />
                  ))}
              </div>
            </SectionCard>
          ) : null
        )
      )}

      <Button variant="secondary" onClick={addInventoryItem} icon="＋" fullWidth>
        Gegenstand hinzufügen
      </Button>

      <style>{`
        .inv-row {
          display: flex; flex-direction: column; gap: 10px;
          padding: 14px; background: var(--gray-light);
          border-radius: var(--radius); border: 1px solid var(--border);
        }
        .inv-row__main { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 10px; }
        .info-box {
          background: var(--blue-light); color: var(--blue);
          border-radius: var(--radius); padding: 10px 14px; font-size: 13px;
        }
        @media (max-width: 640px) { .inv-row__main { grid-template-columns: 1fr 1fr; } }
      `}</style>
    </div>
  );
}
