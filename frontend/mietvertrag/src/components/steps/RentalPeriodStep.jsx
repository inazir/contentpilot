import React from "react";
import FormField from "../common/FormField.jsx";
import Input from "../common/Input.jsx";
import Select from "../common/Select.jsx";
import Checkbox from "../common/Checkbox.jsx";
import SectionCard from "../common/SectionCard.jsx";

const NOTICE_OPTIONS = [
  { value: "2weeks",  label: "2 Wochen" },
  { value: "1month",  label: "1 Monat" },
  { value: "3months", label: "3 Monate (gesetzlich)" },
  { value: "custom",  label: "Individuell" },
];

const MIN_STAY_OPTIONS = [
  { value: "none",     label: "Keine" },
  { value: "3months",  label: "3 Monate" },
  { value: "6months",  label: "6 Monate" },
  { value: "12months", label: "12 Monate" },
  { value: "custom",   label: "Individuell" },
];

export default function RentalPeriodStep({ form, updateField, errors }) {
  const rp = form.rentalPeriod;
  const f  = (field) => (e) => updateField(`rentalPeriod.${field}`, e.target.value);
  const err = (field) => errors[`rentalPeriod.${field}`];

  return (
    <div className="gap-16">
      <SectionCard title="Mietdaten" icon="📅" defaultOpen>
        <div className="gap-12">
          <div className="grid-2">
            <FormField label="Einzugsdatum">
              <Input type="date" value={rp.moveInDate} onChange={f("moveInDate")} />
            </FormField>
            <FormField label="Mietbeginn (Vertragsstart)" required error={err("startDate")}>
              <Input type="date" value={rp.startDate} onChange={f("startDate")} />
            </FormField>
          </div>

          <Checkbox
            id="isFixedTerm"
            label="Befristeter Mietvertrag"
            checked={rp.isFixedTerm}
            onChange={(e) => updateField("rentalPeriod.isFixedTerm", e.target.checked)}
          />

          {rp.isFixedTerm && (
            <div className="gap-12">
              <div className="grid-2">
                <FormField label="Mietende" required error={err("endDate")}>
                  <Input type="date" value={rp.endDate} onChange={f("endDate")} />
                </FormField>
                <FormField label="Befristungsgrund" hint="Pflicht bei § 575 BGB Befristung" error={err("fixedTermReason")}>
                  <Input value={rp.fixedTermReason} onChange={f("fixedTermReason")} placeholder="z.B. Eigenbedarf nach Ablauf" />
                </FormField>
              </div>
              <div className="info-box">
                ℹ️ Bei befristeten Verträgen nach § 575 BGB muss ein gesetzlich anerkannter Grund angegeben werden (Eigenbedarf, Abriss/Umbau, Werkswohnung).
              </div>
            </div>
          )}
        </div>
      </SectionCard>

      <SectionCard title="Kündigungsfristen" icon="📋" defaultOpen>
        <div className="gap-12">
          <div className="grid-2">
            <FormField label="Mindestmietdauer">
              <Select
                value={rp.minStay}
                onChange={(e) => updateField("rentalPeriod.minStay", e.target.value)}
                options={MIN_STAY_OPTIONS}
              />
            </FormField>
            {rp.minStay === "custom" && (
              <FormField label="Individuelle Mindestmietdauer" error={err("customMinStay")}>
                <Input value={rp.customMinStay} onChange={f("customMinStay")} placeholder="z.B. 9 Monate" />
              </FormField>
            )}
          </div>

          <div className="grid-2">
            <FormField label="Kündigungsfrist (Mieter)">
              <Select
                value={rp.noticePeriod}
                onChange={(e) => updateField("rentalPeriod.noticePeriod", e.target.value)}
                options={NOTICE_OPTIONS}
              />
            </FormField>
            {rp.noticePeriod === "custom" && (
              <FormField label="Individuelle Frist" error={err("customNotice")}>
                <Input value={rp.customNotice} onChange={f("customNotice")} placeholder="z.B. 6 Wochen" />
              </FormField>
            )}
          </div>
        </div>
      </SectionCard>

      <style>{`
        .info-box {
          background: var(--blue-light); color: var(--blue);
          border-radius: var(--radius); padding: 10px 14px;
          font-size: 13px; line-height: 1.5;
        }
      `}</style>
    </div>
  );
}
