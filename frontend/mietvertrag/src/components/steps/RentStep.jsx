import React from "react";
import FormField from "../common/FormField.jsx";
import Input from "../common/Input.jsx";
import Select from "../common/Select.jsx";
import SectionCard from "../common/SectionCard.jsx";
import { calcWarmmiete } from "../../utils/calcRent.js";
import { formatEur } from "../../utils/formatting.js";

const PAYMENT_DAYS = Array.from({ length: 28 }, (_, i) => ({
  value: String(i + 1),
  label: `${i + 1}. des Monats`,
}));

function RentRow({ label, field, value, onChange, hint, placeholder = "0,00" }) {
  return (
    <div className="rent-row">
      <span className="rent-row__label">{label}</span>
      <div className="rent-row__input">
        <Input
          type="number"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          min="0"
          step="0.01"
        />
        <span className="rent-row__eur">€</span>
      </div>
    </div>
  );
}

export default function RentStep({ form, updateField, errors }) {
  const r   = form.rent;
  const f   = (field) => (val) => updateField(`rent.${field}`, val);
  const err = (field) => errors[`rent.${field}`];
  const warm = calcWarmmiete(r);

  return (
    <div className="gap-16">
      <SectionCard title="Miete" icon="💶" defaultOpen>
        <div className="gap-4">
          <RentRow label="Kaltmiete *"         field="coldRent"         value={r.coldRent}         onChange={f("coldRent")} />
          <RentRow label="Möblierungszuschlag" field="furnitureSurcharge" value={r.furnitureSurcharge} onChange={f("furnitureSurcharge")} />
        </div>
        {err("coldRent") && <p className="field-error">{err("coldRent")}</p>}
      </SectionCard>

      <SectionCard title="Nebenkosten" icon="🔧" defaultOpen={false}>
        <div className="gap-4">
          <RentRow label="Nebenkosten (NK-Vorauszahlung)" value={r.utilities}   onChange={f("utilities")} />
          <RentRow label="Heizkosten"   value={r.heating}     onChange={f("heating")} />
          <RentRow label="Wasserkosten" value={r.water}       onChange={f("water")} />
          <RentRow label="Strom"        value={r.electricity} onChange={f("electricity")} />
          <RentRow label="Internet"     value={r.internet}    onChange={f("internet")} />
          <RentRow label="Rundfunkbeitrag (GEZ)" value={r.gez} onChange={f("gez")} />
          <RentRow label="Reinigung"    value={r.cleaning}    onChange={f("cleaning")} />
          <RentRow label="Hausmeister"  value={r.housemaster} onChange={f("housemaster")} />
          <RentRow label="Stellplatz"   value={r.parking}     onChange={f("parking")} />
        </div>
      </SectionCard>

      <SectionCard title="Sonstige Kosten" icon="➕" defaultOpen={false}>
        <div className="gap-12">
          <FormField label="Bezeichnung (sonstige Kosten)">
            <Input
              value={r.otherCostsLabel}
              onChange={(e) => updateField("rent.otherCostsLabel", e.target.value)}
              placeholder="z.B. Tierpauschale"
            />
          </FormField>
          <RentRow label="Betrag" value={r.otherCosts} onChange={f("otherCosts")} />
        </div>
      </SectionCard>

      <SectionCard title="Zahlung" icon="🏦" defaultOpen>
        <FormField label="Zahlungstermin">
          <Select
            value={r.paymentDayOfMonth}
            onChange={(e) => updateField("rent.paymentDayOfMonth", e.target.value)}
            options={PAYMENT_DAYS}
          />
        </FormField>
      </SectionCard>

      {/* Warmmiete summary */}
      <div className="warm-summary">
        <div className="warm-summary__row">
          <span>Kaltmiete</span>
          <span>{formatEur(r.coldRent)}</span>
        </div>
        {parseFloat(r.furnitureSurcharge) > 0 && (
          <div className="warm-summary__row">
            <span>Möblierungszuschlag</span>
            <span>{formatEur(r.furnitureSurcharge)}</span>
          </div>
        )}
        <div className="warm-summary__row warm-summary__row--total">
          <span>Warmmiete (gesamt)</span>
          <span>{formatEur(warm)}</span>
        </div>
      </div>

      <style>{`
        .rent-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); gap: 12px; }
        .rent-row__label { font-size: 14px; color: var(--text); flex: 1; }
        .rent-row__input { display: flex; align-items: center; gap: 6px; width: 140px; flex-shrink: 0; }
        .rent-row__input .input { text-align: right; }
        .rent-row__eur  { font-size: 14px; color: var(--text-muted); }
        .warm-summary {
          background: var(--bg-card); border: 2px solid var(--blue);
          border-radius: var(--radius-lg); padding: 16px 20px;
        }
        .warm-summary__row { display: flex; justify-content: space-between; padding: 4px 0; font-size: 14px; color: var(--text-muted); }
        .warm-summary__row--total { font-size: 16px; font-weight: 700; color: var(--text); border-top: 1px solid var(--border); padding-top: 10px; margin-top: 6px; }
        .field-error { color: var(--red); font-size: 12px; margin-top: 4px; }
        .gap-4 { display: flex; flex-direction: column; gap: 0; }
      `}</style>
    </div>
  );
}
