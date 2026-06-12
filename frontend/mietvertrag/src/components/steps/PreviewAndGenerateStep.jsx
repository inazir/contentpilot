import React, { useState } from "react";
import Button from "../common/Button.jsx";
import Badge from "../common/Badge.jsx";
import { loadSchema } from "../../schemas/index.js";
import { getContractType } from "../../constants/contractTypes.js";
import { generateAllDocuments, generateDocument } from "../../services/contractGenerator.js";
import { downloadDocumentAsPdf, downloadAllDocuments } from "../../services/pdfGenerator.js";
import { calcWarmmiete, calcDeposit } from "../../utils/calcRent.js";
import { formatEur, formatDate, fmt } from "../../utils/formatting.js";

const DOC_LABELS = {
  mietvertrag:               { label: "Mietvertrag",               icon: "📄" },
  uebergabeprotokoll:        { label: "Übergabeprotokoll",         icon: "🏠" },
  schluesselprotokoll:       { label: "Schlüsselprotokoll",        icon: "🔑" },
  inventarliste:             { label: "Inventarliste",             icon: "📋" },
  hausordnung:               { label: "Hausordnung",               icon: "📏" },
  wohnungsgeberbestaetigung: { label: "Wohnungsgeberbestätigung",  icon: "📝" },
  kuendigungsformular:       { label: "Kündigungsformular",        icon: "✉️" },
  mietbescheinigung:         { label: "Mietbescheinigung",         icon: "📃" },
};

function SummaryRow({ label, value, highlight }) {
  return (
    <div className={`summary-row${highlight ? " summary-row--highlight" : ""}`}>
      <span className="summary-row__label">{label}</span>
      <span className="summary-row__value">{value}</span>
    </div>
  );
}

export default function PreviewAndGenerateStep({ form }) {
  const [generating, setGenerating] = useState(false);
  const [generatedDocs, setGeneratedDocs] = useState(null);

  const ct     = getContractType(form.contractTypeId);
  const schema = ct ? loadSchema(ct.schemaId) : null;
  const warm   = calcWarmmiete(form.rent);
  const deposit = calcDeposit(form.deposit, form.rent.coldRent);
  const landlord = form.landlords[0] || {};
  const tenant   = form.tenants[0]   || {};

  const availableDocs = schema?.documents || ["mietvertrag"];

  const handleGenerateAll = () => {
    setGenerating(true);
    try {
      const docs = generateAllDocuments(form);
      setGeneratedDocs(docs);
      const prefix = `${tenant.lastName || "mieter"}_${tenant.firstName || ""}`.toLowerCase().replace(/\s/g, "_");
      downloadAllDocuments(docs, prefix);
    } catch (e) {
      console.error("Generation failed:", e);
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateSingle = (docType) => {
    try {
      const doc = generateDocument(docType, form);
      const prefix = `${tenant.lastName || "mieter"}_${docType}`.toLowerCase();
      downloadDocumentAsPdf(doc, prefix);
    } catch (e) {
      console.error("Single doc generation failed:", e);
    }
  };

  return (
    <div className="gap-16">

      {/* Summary */}
      <div className="preview-summary">
        <h3 className="preview-summary__title">Zusammenfassung</h3>
        <div className="summary-grid">
          <SummaryRow label="Vertragsart"  value={ct?.label || "—"} />
          <SummaryRow label="Vermieter"    value={`${fmt(landlord.firstName)} ${fmt(landlord.lastName)}`} />
          <SummaryRow label="Mieter"       value={`${fmt(tenant.firstName)} ${fmt(tenant.lastName)}`} />
          <SummaryRow
            label="Mietobjekt"
            value={`${fmt(form.property.street)} ${fmt(form.property.houseNumber)}, ${fmt(form.property.postalCode)} ${fmt(form.property.city)}`}
          />
          <SummaryRow label="Mietbeginn"  value={formatDate(form.rentalPeriod.startDate)} />
          <SummaryRow label="Befristung"  value={form.rentalPeriod.isFixedTerm ? `bis ${formatDate(form.rentalPeriod.endDate)}` : "Unbefristet"} />
          <SummaryRow label="Kaltmiete"   value={formatEur(form.rent.coldRent)} />
          <SummaryRow label="Warmmiete"   value={formatEur(warm)} highlight />
          <SummaryRow label="Kaution"     value={formatEur(deposit)} />
          {form.landlords.length > 1 && <SummaryRow label="Weitere Vermieter" value={`+${form.landlords.length - 1}`} />}
          {form.tenants.length > 1   && <SummaryRow label="Weitere Mieter"    value={`+${form.tenants.length - 1}`} />}
          {form.inventory.length > 0 && <SummaryRow label="Inventarposten"    value={form.inventory.length} />}
          {form.keys.length > 0      && <SummaryRow label="Schlüssel"         value={form.keys.length + " Typ(en)"} />}
        </div>
      </div>

      {/* Document list */}
      <div className="doc-list">
        <h3 className="doc-list__title">Verfügbare Dokumente</h3>
        <div className="gap-8">
          {availableDocs.map((docType) => {
            const meta = DOC_LABELS[docType] || { label: docType, icon: "📄" };
            return (
              <div key={docType} className="doc-item">
                <span className="doc-item__icon">{meta.icon}</span>
                <span className="doc-item__label">{meta.label}</span>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => handleGenerateSingle(docType)}
                >
                  PDF ↓
                </Button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Generate all */}
      <Button
        variant="primary"
        size="lg"
        fullWidth
        onClick={handleGenerateAll}
        disabled={generating}
        icon="📥"
      >
        {generating ? "Wird generiert…" : `Alle ${availableDocs.length} Dokumente als PDF herunterladen`}
      </Button>

      {generatedDocs && (
        <div className="success-box">
          ✅ {generatedDocs.length} Dokument(e) erfolgreich generiert und heruntergeladen.
        </div>
      )}

      <style>{`
        .preview-summary { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 20px; }
        .preview-summary__title { font-size: 16px; font-weight: 700; margin-bottom: 14px; color: var(--text); }
        .summary-grid { display: flex; flex-direction: column; gap: 0; }
        .summary-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 14px; }
        .summary-row__label { color: var(--text-muted); }
        .summary-row__value { font-weight: 500; color: var(--text); }
        .summary-row--highlight .summary-row__value { color: var(--blue); font-size: 16px; font-weight: 700; }
        .doc-list { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 20px; }
        .doc-list__title { font-size: 16px; font-weight: 700; margin-bottom: 14px; color: var(--text); }
        .doc-item { display: flex; align-items: center; gap: 10px; padding: 10px; background: var(--gray-light); border-radius: var(--radius); }
        .doc-item__icon  { font-size: 20px; }
        .doc-item__label { flex: 1; font-size: 14px; font-weight: 500; color: var(--text); }
        .gap-8  { display: flex; flex-direction: column; gap: 8px; }
        .success-box { background: var(--green-light); color: var(--green); border-radius: var(--radius); padding: 12px 16px; font-size: 14px; font-weight: 500; }
      `}</style>
    </div>
  );
}
