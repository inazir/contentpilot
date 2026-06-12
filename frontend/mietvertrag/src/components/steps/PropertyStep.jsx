import React from "react";
import FormField from "../common/FormField.jsx";
import Input from "../common/Input.jsx";
import Select from "../common/Select.jsx";
import Checkbox from "../common/Checkbox.jsx";
import SectionCard from "../common/SectionCard.jsx";

const DE_STATES = [
  "Baden-Württemberg","Bayern","Berlin","Brandenburg","Bremen",
  "Hamburg","Hessen","Mecklenburg-Vorpommern","Niedersachsen",
  "Nordrhein-Westfalen","Rheinland-Pfalz","Saarland","Sachsen",
  "Sachsen-Anhalt","Schleswig-Holstein","Thüringen",
].map((s) => ({ value: s, label: s }));

export default function PropertyStep({ form, updateField, errors }) {
  const p = form.property;
  const f = (field) => (e) => updateField(`property.${field}`, e.target.value);
  const fb = (field) => (e) => updateField(`property.${field}`, e.target.checked);
  const err = (field) => errors[`property.${field}`];

  return (
    <div className="gap-16">
      <SectionCard title="Adresse des Mietobjekts" icon="📍" defaultOpen>
        <div className="gap-12">
          <div className="grid-2">
            <FormField label="Straße" required error={err("street")}>
              <Input value={p.street} onChange={f("street")} placeholder="Musterstraße" />
            </FormField>
            <FormField label="Hausnummer" required error={err("houseNumber")}>
              <Input value={p.houseNumber} onChange={f("houseNumber")} placeholder="12a" />
            </FormField>
            <FormField label="PLZ" required error={err("postalCode")}>
              <Input value={p.postalCode} onChange={f("postalCode")} placeholder="70173" />
            </FormField>
            <FormField label="Stadt" required error={err("city")}>
              <Input value={p.city} onChange={f("city")} placeholder="Stuttgart" />
            </FormField>
          </div>
          <div className="grid-2">
            <FormField label="Bundesland">
              <Select
                value={p.state}
                onChange={(e) => updateField("property.state", e.target.value)}
                options={DE_STATES}
                placeholder="Bundesland wählen"
              />
            </FormField>
            <FormField label="Land">
              <Input value={p.country} onChange={f("country")} />
            </FormField>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Details zum Mietobjekt" icon="🏗" defaultOpen>
        <div className="gap-12">
          <div className="grid-3">
            <FormField label="Etage">
              <Input value={p.floor} onChange={f("floor")} placeholder="2. OG" />
            </FormField>
            <FormField label="Wohnungs-Nr.">
              <Input value={p.apartmentNumber} onChange={f("apartmentNumber")} placeholder="4" />
            </FormField>
            <FormField label="Zimmer-Nr.">
              <Input value={p.roomNumber} onChange={f("roomNumber")} placeholder="2" />
            </FormField>
            <FormField label="Wohnfläche (m²)" error={err("livingArea")}>
              <Input type="number" value={p.livingArea} onChange={f("livingArea")} placeholder="20" min="1" />
            </FormField>
            <FormField label="Gesamtfläche (m²)" error={err("totalArea")}>
              <Input type="number" value={p.totalArea} onChange={f("totalArea")} placeholder="85" min="1" />
            </FormField>
            <FormField label="Baujahr">
              <Input type="number" value={p.buildingYear} onChange={f("buildingYear")} placeholder="1990" min="1800" max="2030" />
            </FormField>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Ausstattung / Extras" icon="✨" defaultOpen={false}>
        <div className="checkbox-grid">
          <Checkbox id="hasBalcony"  label="Balkon"     checked={p.hasBalcony}  onChange={fb("hasBalcony")} />
          <Checkbox id="hasTerrace"  label="Terrasse"   checked={p.hasTerrace}  onChange={fb("hasTerrace")} />
          <Checkbox id="hasGarden"   label="Garten"     checked={p.hasGarden}   onChange={fb("hasGarden")} />
          <Checkbox id="hasBasement" label="Keller"     checked={p.hasBasement} onChange={fb("hasBasement")} />
          <Checkbox id="hasGarage"   label="Garage"     checked={p.hasGarage}   onChange={fb("hasGarage")} />
          <Checkbox id="hasParking"  label="Stellplatz" checked={p.hasParking}  onChange={fb("hasParking")} />
        </div>
      </SectionCard>

      <style>{`
        .checkbox-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px,1fr)); gap: 12px; }
      `}</style>
    </div>
  );
}
