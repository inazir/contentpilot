import React from "react";
import FormField from "../common/FormField.jsx";
import Input from "../common/Input.jsx";
import Textarea from "../common/Textarea.jsx";
import Checkbox from "../common/Checkbox.jsx";
import SectionCard from "../common/SectionCard.jsx";

export default function HouseRulesStep({ form, updateField }) {
  const hr = form.houseRules;
  const sf = form.safety;
  const reg = form.registration;
  const ins = form.insurance;
  const acc = form.access;

  const cb  = (section, field) => (e) => updateField(`${section}.${field}`, e.target.checked);
  const inp = (section, field) => (e) => updateField(`${section}.${field}`, e.target.value);

  return (
    <div className="gap-16">
      <SectionCard title="Hausordnung" icon="📋" defaultOpen>
        <div className="checkbox-grid">
          <Checkbox id="noSmoking"        label="Rauchverbot"             checked={hr.noSmoking}        onChange={cb("houseRules","noSmoking")} />
          <Checkbox id="noShisha"         label="Kein Shisha"             checked={hr.noShisha}         onChange={cb("houseRules","noShisha")} />
          <Checkbox id="noPets"           label="Keine Haustiere"         checked={hr.noPets}           onChange={cb("houseRules","noPets")} />
          <Checkbox id="quietHours"       label="Ruhezeiten"              checked={hr.quietHours}       onChange={cb("houseRules","quietHours")} />
          <Checkbox id="visitorRules"     label="Besucherregelung"        checked={hr.visitorRules}     onChange={cb("houseRules","visitorRules")} />
          <Checkbox id="noOvernightGuests" label="Kein Übernachtungsgast" checked={hr.noOvernightGuests} onChange={cb("houseRules","noOvernightGuests")} />
          <Checkbox id="cleaningRota"     label="Reinigungsplan"          checked={hr.cleaningRota}     onChange={cb("houseRules","cleaningRota")} />
          <Checkbox id="wasteSeparation"  label="Mülltrennung"            checked={hr.wasteSeparation}  onChange={cb("houseRules","wasteSeparation")} />
          <Checkbox id="mailHandling"     label="Postbehandlung"          checked={hr.mailHandling}     onChange={cb("houseRules","mailHandling")} />
          <Checkbox id="noSubletting"     label="Kein Untervermieten"     checked={hr.noSubletting}     onChange={cb("houseRules","noSubletting")} />
        </div>

        {hr.quietHours && (
          <div className="grid-2 mt-16">
            <FormField label="Ruhezeit von">
              <Input type="time" value={hr.quietHoursFrom} onChange={inp("houseRules","quietHoursFrom")} />
            </FormField>
            <FormField label="Ruhezeit bis">
              <Input type="time" value={hr.quietHoursTo} onChange={inp("houseRules","quietHoursTo")} />
            </FormField>
          </div>
        )}

        <FormField label="Individuelle Hausordnungsregeln" className="mt-16">
          <Textarea
            value={hr.customRules}
            onChange={inp("houseRules","customRules")}
            placeholder="Weitere Regeln hier eintragen..."
            rows={3}
          />
        </FormField>
      </SectionCard>

      <SectionCard title="Sicherheit" icon="🔥" defaultOpen={false}>
        <div className="checkbox-grid">
          <Checkbox id="fireSafety"            label="Brandschutzpflicht"      checked={sf.fireSafety}            onChange={cb("safety","fireSafety")} />
          <Checkbox id="noOpenFlames"          label="Offene Flammen verboten" checked={sf.noOpenFlames}          onChange={cb("safety","noOpenFlames")} />
          <Checkbox id="noCandles"             label="Kerzenverbot"            checked={sf.noCandles}             onChange={cb("safety","noCandles")} />
          <Checkbox id="waterDamagePrevention" label="Wasserschadensschutz"    checked={sf.waterDamagePrevention} onChange={cb("safety","waterDamagePrevention")} />
          <Checkbox id="moldPrevention"        label="Schimmelprävention"      checked={sf.moldPrevention}        onChange={cb("safety","moldPrevention")} />
        </div>
      </SectionCard>

      <SectionCard title="Zutrittsrechte des Vermieters" icon="🚪" defaultOpen={false}>
        <div className="checkbox-grid">
          <Checkbox id="repairsAccess"      label="Reparaturen"           checked={acc.repairsAccess}      onChange={cb("access","repairsAccess")} />
          <Checkbox id="inspectionAccess"   label="Besichtigungen (jährl.)"checked={acc.inspectionAccess}  onChange={cb("access","inspectionAccess")} />
          <Checkbox id="saleViewings"       label="Bei Verkauf"           checked={acc.saleViewings}       onChange={cb("access","saleViewings")} />
          <Checkbox id="newTenantViewings"  label="Nachmietersuche"       checked={acc.newTenantViewings}  onChange={cb("access","newTenantViewings")} />
        </div>
        <FormField label="Voranmeldefrist (Stunden)" className="mt-16">
          <Input
            type="number"
            value={acc.noticeDays}
            onChange={inp("access","noticeDays")}
            min="1"
            max="72"
            placeholder="24"
          />
        </FormField>
      </SectionCard>

      <SectionCard title="Anmeldung & Versicherung" icon="📝" defaultOpen={false}>
        <div className="checkbox-grid">
          <Checkbox id="wohnungsgeberbestaetigung" label="Wohnungsgeberbestätigung ausstellen" checked={reg.wohnungsgeberbestaetigung} onChange={cb("registration","wohnungsgeberbestaetigung")} />
          <Checkbox id="anmeldungRequired"         label="Anmeldepflicht des Mieters"          checked={reg.anmeldungRequired}         onChange={cb("registration","anmeldungRequired")} />
          <Checkbox id="liabilityRequired"         label="Haftpflichtversicherung Pflicht"     checked={ins.liabilityRequired}         onChange={cb("insurance","liabilityRequired")} />
        </div>
      </SectionCard>

      <style>{`
        .checkbox-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px,1fr)); gap: 12px; }
      `}</style>
    </div>
  );
}
