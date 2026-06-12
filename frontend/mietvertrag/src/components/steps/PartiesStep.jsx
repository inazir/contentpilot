import React from "react";
import FormField from "../common/FormField.jsx";
import Input from "../common/Input.jsx";
import Button from "../common/Button.jsx";
import Divider from "../common/Divider.jsx";
import SectionCard from "../common/SectionCard.jsx";

function PersonForm({ person, onChange, onRemove, role, index, canRemove, errors = {} }) {
  const f = (field) => (e) => onChange({ ...person, [field]: e.target.value });
  const err = (field) => errors[`${role}s[${index}].${field}`];

  return (
    <div className="person-form">
      <div className="person-form__header">
        <span className="person-form__title">{role === "landlord" ? "Vermieter" : "Mieter"} {index + 1}</span>
        {canRemove && (
          <Button size="sm" variant="danger" onClick={onRemove}>Entfernen</Button>
        )}
      </div>

      <div className="grid-2">
        <FormField label="Vorname" required error={err("firstName")}>
          <Input value={person.firstName} onChange={f("firstName")} placeholder="Max" />
        </FormField>
        <FormField label="Nachname" required error={err("lastName")}>
          <Input value={person.lastName} onChange={f("lastName")} placeholder="Mustermann" />
        </FormField>
        <FormField label="Geburtsdatum" error={err("dob")}>
          <Input type="date" value={person.dob} onChange={f("dob")} />
        </FormField>
        <FormField label="Geburtsort" error={err("placeOfBirth")}>
          <Input value={person.placeOfBirth} onChange={f("placeOfBirth")} placeholder="Berlin" />
        </FormField>
        <FormField label="Staatsangehörigkeit" error={err("nationality")}>
          <Input value={person.nationality} onChange={f("nationality")} placeholder="Deutsch" />
        </FormField>
        <FormField label="Ausweis-Nr." error={err("idNumber")}>
          <Input value={person.idNumber} onChange={f("idNumber")} placeholder="L01X00T47" />
        </FormField>
        <FormField label="Reisepass-Nr." error={err("passportNumber")}>
          <Input value={person.passportNumber} onChange={f("passportNumber")} />
        </FormField>
        <FormField label="E-Mail" error={err("email")}>
          <Input type="email" value={person.email} onChange={f("email")} placeholder="max@beispiel.de" />
        </FormField>
        <FormField label="Telefon" error={err("phone")}>
          <Input type="tel" value={person.phone} onChange={f("phone")} placeholder="+49 170 1234567" />
        </FormField>
        <FormField label="Firma (optional)" error={err("company")}>
          <Input value={person.company} onChange={f("company")} />
        </FormField>
      </div>

      <FormField label={role === "landlord" ? "Adresse" : "Aktuelle Adresse"} error={err(role === "landlord" ? "address" : "currentAddress")} className="mt-8">
        <Input
          value={role === "landlord" ? person.address : person.currentAddress}
          onChange={f(role === "landlord" ? "address" : "currentAddress")}
          placeholder="Musterstraße 1, 70173 Stuttgart"
        />
      </FormField>

      <FormField label="Gesetzlicher Vertreter (optional)" error={err("legalRepresentative")} className="mt-8">
        <Input value={person.legalRepresentative} onChange={f("legalRepresentative")} placeholder="Nur bei Minderjährigen oder GmbH" />
      </FormField>
    </div>
  );
}

export default function PartiesStep({
  form, errors,
  updateLandlord, addLandlord, removeLandlord,
  updateTenant, addTenant, removeTenant,
}) {
  return (
    <div className="gap-16">
      <SectionCard title="Vermieter" icon="🏠" badge={`${form.landlords.length} Person(en)`}>
        <div className="gap-16">
          {form.landlords.map((l, i) => (
            <React.Fragment key={l.id}>
              {i > 0 && <Divider />}
              <PersonForm
                person={l} role="landlord" index={i}
                onChange={(updated) => updateLandlord(i, updated)}
                onRemove={() => removeLandlord(i)}
                canRemove={form.landlords.length > 1}
                errors={errors}
              />
            </React.Fragment>
          ))}
          <Button variant="secondary" size="sm" onClick={addLandlord} icon="＋">
            Weiteren Vermieter hinzufügen
          </Button>
        </div>
      </SectionCard>

      <SectionCard title="Mieter" icon="👤" badge={`${form.tenants.length} Person(en)`}>
        <div className="gap-16">
          {form.tenants.map((t, i) => (
            <React.Fragment key={t.id}>
              {i > 0 && <Divider />}
              <PersonForm
                person={t} role="tenant" index={i}
                onChange={(updated) => updateTenant(i, updated)}
                onRemove={() => removeTenant(i)}
                canRemove={form.tenants.length > 1}
                errors={errors}
              />
            </React.Fragment>
          ))}
          <Button variant="secondary" size="sm" onClick={addTenant} icon="＋">
            Weiteren Mieter hinzufügen
          </Button>
        </div>
      </SectionCard>

      <style>{`
        .person-form { display: flex; flex-direction: column; gap: 12px; }
        .person-form__header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
        .person-form__title  { font-weight: 600; font-size: 15px; color: var(--text); }
      `}</style>
    </div>
  );
}
