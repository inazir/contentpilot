import React from "react";
import FormField from "../common/FormField.jsx";
import Input from "../common/Input.jsx";
import RadioGroup from "../common/RadioGroup.jsx";
import Checkbox from "../common/Checkbox.jsx";
import SectionCard from "../common/SectionCard.jsx";
import { calcDeposit, depositLabel } from "../../utils/calcRent.js";
import { formatEur } from "../../utils/formatting.js";

const DEPOSIT_OPTIONS = [
  { value: "none",        label: "Keine Kaution" },
  { value: "oneMonth",    label: "1 Monatsmiete" },
  { value: "twoMonths",   label: "2 Monatsmieten" },
  { value: "threeMonths", label: "3 Monatsmieten (max.)"},
  { value: "custom",      label: "Individuell" },
];

export default function DepositStep({ form, updateField, errors }) {
  const d    = form.deposit;
  const err  = (field) => errors[`deposit.${field}`];
  const amount = calcDeposit(d, form.rent.coldRent);

  return (
    <div className="gap-16">
      <SectionCard title="Kautionshöhe" icon="🔒" defaultOpen>
        <div className="gap-12">
          <RadioGroup
            name="depositType"
            options={DEPOSIT_OPTIONS}
            value={d.type}
            onChange={(val) => updateField("deposit.type", val)}
          />

          {d.type === "custom" && (
            <FormField label="Individuelle Kautionshöhe (€)" required error={err("customAmount")}>
              <Input
                type="number"
                value={d.customAmount}
                onChange={(e) => updateField("deposit.customAmount", e.target.value)}
                placeholder="0,00"
                min="0"
                step="0.01"
              />
            </FormField>
          )}

          {d.type !== "none" && (
            <div className="deposit-summary">
              <span className="deposit-summary__label">Kautionsbetrag</span>
              <span className="deposit-summary__amount">{formatEur(amount)}</span>
            </div>
          )}
        </div>
      </SectionCard>

      {d.type !== "none" && (
        <SectionCard title="Zahlungsmodalitäten" icon="📆" defaultOpen={false}>
          <div className="gap-12">
            <Checkbox
              id="installments"
              label="Ratenzahlung erlauben"
              checked={d.installments}
              onChange={(e) => updateField("deposit.installments", e.target.checked)}
            />

            {d.installments && (
              <FormField label="Anzahl der Raten">
                <Input
                  type="number"
                  value={d.installmentCount}
                  onChange={(e) => updateField("deposit.installmentCount", e.target.value)}
                  min="1"
                  max="3"
                  placeholder="3"
                />
              </FormField>
            )}

            <FormField label="Fälligkeitsdatum" hint="Leer lassen = bei Mietbeginn fällig">
              <Input
                type="date"
                value={d.dueDate}
                onChange={(e) => updateField("deposit.dueDate", e.target.value)}
              />
            </FormField>
          </div>
        </SectionCard>
      )}

      <SectionCard title="Bankverbindung des Vermieters" icon="🏦" defaultOpen>
        <div className="gap-12">
          <div className="grid-2">
            <FormField label="Kontoinhaber">
              <Input
                value={form.bank.accountHolder}
                onChange={(e) => updateField("bank.accountHolder", e.target.value)}
                placeholder="Max Mustermann"
              />
            </FormField>
            <FormField label="Bank">
              <Input
                value={form.bank.bankName}
                onChange={(e) => updateField("bank.bankName", e.target.value)}
                placeholder="Sparkasse Stuttgart"
              />
            </FormField>
            <FormField label="IBAN" error={errors["bank.iban"]}>
              <Input
                value={form.bank.iban}
                onChange={(e) => updateField("bank.iban", e.target.value)}
                placeholder="DE12 3456 7890 1234 5678 90"
              />
            </FormField>
            <FormField label="BIC" error={errors["bank.bic"]}>
              <Input
                value={form.bank.bic}
                onChange={(e) => updateField("bank.bic", e.target.value)}
                placeholder="SSKMDEMMXXX"
              />
            </FormField>
          </div>
          <FormField label="Verwendungszweck">
            <Input
              value={form.bank.referenceText}
              onChange={(e) => updateField("bank.referenceText", e.target.value)}
              placeholder="Miete [Monat] [Adresse]"
            />
          </FormField>
        </div>
      </SectionCard>

      <style>{`
        .deposit-summary {
          display: flex; align-items: center; justify-content: space-between;
          background: var(--green-light); border-radius: var(--radius);
          padding: 12px 16px;
        }
        .deposit-summary__label  { font-size: 14px; color: var(--green); font-weight: 500; }
        .deposit-summary__amount { font-size: 20px; font-weight: 700; color: var(--green); }
      `}</style>
    </div>
  );
}
