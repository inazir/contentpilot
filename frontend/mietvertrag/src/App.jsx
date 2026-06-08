import { useState, useCallback, useRef } from "react";

// ── Helpers ───────────────────────────────────────────────────────────────────
const uid = () => Math.random().toString(36).slice(2, 8);
const today = () => new Date().toISOString().split("T")[0];
const fmt = (v) => (v ? v : "—");
const calcWarm = (r) =>
  ["coldRent", "furnitureSurcharge", "utilities", "internet", "parking", "otherCosts"]
    .reduce((s, k) => s + (parseFloat(r[k]) || 0), 0)
    .toFixed(2);

// ── Initial state ─────────────────────────────────────────────────────────────
const emptyLandlord = () => ({
  id: uid(), firstName: "", lastName: "", dob: "", address: "", email: "", phone: "",
});
const emptyTenant = () => ({
  id: uid(), firstName: "", lastName: "", dob: "", currentAddress: "", email: "", phone: "",
});
const emptyItem = () => ({ id: uid(), name: "", qty: 1 });

const PRESETS = {
  wg_furnished: {
    label: "WG Zimmer (möbliert)",
    propertyType: "wg",
    houseRules: { noSmoking: true, quietHours: true, sharedKitchen: true, sharedBathroom: true, visitorRules: true, noPets: false, customRules: "" },
    inventory: [
      { id: uid(), name: "Bett", qty: 1 }, { id: uid(), name: "Matratze", qty: 1 },
      { id: uid(), name: "Schreibtisch", qty: 1 }, { id: uid(), name: "Stuhl", qty: 1 },
      { id: uid(), name: "Kleiderschrank", qty: 1 },
    ],
    furnitureSurcharge: "50",
  },
  wg_unfurnished: {
    label: "WG Zimmer (unmöbliert)",
    propertyType: "wg",
    houseRules: { noSmoking: true, quietHours: true, sharedKitchen: true, sharedBathroom: true, visitorRules: false, noPets: false, customRules: "" },
    inventory: [],
    furnitureSurcharge: "0",
  },
  apartment: {
    label: "Wohnung",
    propertyType: "apartment",
    houseRules: { noSmoking: false, quietHours: true, sharedKitchen: false, sharedBathroom: false, visitorRules: false, noPets: false, customRules: "" },
    inventory: [],
    furnitureSurcharge: "0",
  },
  house: {
    label: "Haus",
    propertyType: "house",
    houseRules: { noSmoking: false, quietHours: false, sharedKitchen: false, sharedBathroom: false, visitorRules: false, noPets: false, customRules: "" },
    inventory: [],
    furnitureSurcharge: "0",
  },
};

const defaultForm = {
  landlords: [emptyLandlord()],
  tenants: [emptyTenant()],
  property: {
    street: "", houseNumber: "", postalCode: "", city: "", type: "wg",
    totalSize: "", roomNumber: "", roomSize: "", floor: "", buildingYear: "",
  },
  contract: {
    moveInDate: "", startDate: "", isFixedTerm: false, endDate: "",
    minStay: "none", noticePeriod: "3months", customNotice: "",
  },
  rent: {
    coldRent: "", furnitureSurcharge: "", utilities: "", internet: "", parking: "", otherCosts: "",
  },
  deposit: { type: "twoMonths", customAmount: "" },
  houseRules: {
    noSmoking: false, noPets: false, quietHours: false,
    sharedKitchen: false, sharedBathroom: false, visitorRules: false, customRules: "",
  },
  inventory: [],
  specialAgreements: "",
  contractPlace: "",
  contractDate: today(),
};

// ── Contract text generator ───────────────────────────────────────────────────
function generateContractText(form) {
  const warm = calcWarm(form.rent);
  const depositAmt =
    form.deposit.type === "custom"
      ? `${form.deposit.customAmount} €`
      : form.deposit.type === "oneMonth"
        ? `${form.rent.coldRent} € (1 Monatsmiete)`
        : form.deposit.type === "twoMonths"
          ? `${(parseFloat(form.rent.coldRent || 0) * 2).toFixed(2)} € (2 Monatsmieten)`
          : `${(parseFloat(form.rent.coldRent || 0) * 3).toFixed(2)} € (3 Monatsmieten)`;

  const propTypeLabel =
    form.property.type === "wg" ? "WG-Zimmer" :
    form.property.type === "apartment" ? "Wohnung" : "Haus";

  const minStayLabel =
    form.contract.minStay === "none" ? "Keine Mindestmietdauer" :
    form.contract.minStay === "3months" ? "3 Monate" :
    form.contract.minStay === "6months" ? "6 Monate" :
    form.contract.minStay === "12months" ? "12 Monate" :
    form.contract.customMinStay || "Individuell";

  const noticeLabel =
    form.contract.noticePeriod === "2weeks" ? "2 Wochen" :
    form.contract.noticePeriod === "1month" ? "1 Monat" :
    form.contract.noticePeriod === "3months" ? "3 Monate" :
    form.contract.customNotice || "Individuell";

  const lines = [];
  const add = (...args) => lines.push(...args);

  add("MIETVERTRAG", "═".repeat(60), "");
  add("§ 1 VERTRAGSPARTEIEN", "─".repeat(40), "", "VERMIETER:");
  form.landlords.forEach((l, i) => {
    add(`  Vermieter ${i + 1}: ${l.firstName} ${l.lastName}`);
    if (l.dob) add(`  Geburtsdatum: ${l.dob}`);
    add(`  Adresse: ${l.address}`);
    if (l.email) add(`  E-Mail: ${l.email}`);
    if (l.phone) add(`  Telefon: ${l.phone}`);
    add("");
  });

  add("MIETER:");
  form.tenants.forEach((t, i) => {
    add(`  Mieter ${i + 1}: ${t.firstName} ${t.lastName}`);
    if (t.dob) add(`  Geburtsdatum: ${t.dob}`);
    add(`  Aktuelle Adresse: ${t.currentAddress}`);
    if (t.email) add(`  E-Mail: ${t.email}`);
    if (t.phone) add(`  Telefon: ${t.phone}`);
    add("");
  });

  add("§ 2 MIETOBJEKT", "─".repeat(40), "");
  add(`Art: ${propTypeLabel}`);
  add(`Adresse: ${form.property.street} ${form.property.houseNumber}, ${form.property.postalCode} ${form.property.city}`);
  if (form.property.type === "wg") {
    add(`Zimmer-Nr.: ${fmt(form.property.roomNumber)}`);
    add(`Zimmergröße: ${fmt(form.property.roomSize)} m²`);
  }
  add(`Gesamtgröße: ${fmt(form.property.totalSize)} m²`);
  if (form.property.floor) add(`Etage: ${form.property.floor}`);
  if (form.property.buildingYear) add(`Baujahr: ${form.property.buildingYear}`);
  add("");

  add("§ 3 MIETZEIT", "─".repeat(40), "");
  add(`Einzugsdatum: ${fmt(form.contract.moveInDate)}`);
  add(`Mietbeginn: ${fmt(form.contract.startDate)}`);
  add(`Befristung: ${form.contract.isFixedTerm ? `Ja, bis ${fmt(form.contract.endDate)}` : "Unbefristet"}`);
  add(`Mindestmietdauer: ${minStayLabel}`);
  add(`Kündigungsfrist: ${noticeLabel}`);
  add("");

  add("§ 4 MIETE UND NEBENKOSTEN", "─".repeat(40), "");
  add(`Kaltmiete: ${form.rent.coldRent} €`);
  if (parseFloat(form.rent.furnitureSurcharge) > 0) add(`Möblierungszuschlag: ${form.rent.furnitureSurcharge} €`);
  if (parseFloat(form.rent.utilities) > 0) add(`Nebenkosten: ${form.rent.utilities} €`);
  if (parseFloat(form.rent.internet) > 0) add(`Internet: ${form.rent.internet} €`);
  if (parseFloat(form.rent.parking) > 0) add(`Stellplatz: ${form.rent.parking} €`);
  if (parseFloat(form.rent.otherCosts) > 0) add(`Sonstige Kosten: ${form.rent.otherCosts} €`);
  add(`Warmmiete (gesamt): ${warm} €`);
  add("");

  add("§ 5 KAUTION", "─".repeat(40), "");
  add(`Kautionsbetrag: ${depositAmt}`);
  add("Die Kaution ist bei Mietbeginn fällig und wird auf einem gesonderten Konto verwahrt.");
  add("");

  const rules = [];
  if (form.houseRules.noSmoking) rules.push("Rauchverbot in der Wohnung");
  if (form.houseRules.noPets) rules.push("Keine Tierhaltung ohne Genehmigung des Vermieters");
  if (form.houseRules.quietHours) rules.push("Ruhezeiten: 22:00 – 08:00 Uhr und 13:00 – 15:00 Uhr");
  if (form.houseRules.sharedKitchen) rules.push("Küche ist gemeinschaftlich zu nutzen und sauber zu halten");
  if (form.houseRules.sharedBathroom) rules.push("Bad ist gemeinschaftlich zu nutzen und sauber zu halten");
  if (form.houseRules.visitorRules) rules.push("Besucher dürfen nicht dauerhaft in der Wohnung verbleiben");
  if (form.houseRules.customRules) rules.push(form.houseRules.customRules);

  if (rules.length > 0) {
    add("§ 6 HAUSORDNUNG", "─".repeat(40), "");
    rules.forEach((r) => add(`• ${r}`));
    add("");
  }

  if (form.inventory.length > 0) {
    add("§ 7 INVENTAR / AUSSTATTUNG", "─".repeat(40), "");
    form.inventory.forEach((item) => add(`• ${item.name}${item.qty > 1 ? ` (${item.qty}×)` : ""}`));
    add("");
  }

  add("§ 8 ALLGEMEINE BESTIMMUNGEN", "─".repeat(40), "");
  add("1. Der Mieter ist verpflichtet, die Mieträume pfleglich zu behandeln.");
  add("2. Schäden, die über normale Abnutzung hinausgehen, sind vom Mieter zu ersetzen.");
  add("3. Bauliche Veränderungen bedürfen der schriftlichen Zustimmung des Vermieters.");
  add("4. Untervermietung ist ohne Genehmigung nicht gestattet.");
  add("5. Die Miete ist monatlich im Voraus, spätestens am 3. Werktag zu zahlen.");
  add("");

  if (form.specialAgreements.trim()) {
    add("§ 9 BESONDERE VEREINBARUNGEN", "─".repeat(40), "", form.specialAgreements, "");
  }

  add("§ 10 UNTERSCHRIFTEN", "─".repeat(40), "");
  add(`Ort, Datum: ${fmt(form.contractPlace)}, ${fmt(form.contractDate)}`);
  add("");
  form.landlords.forEach((l, i) => {
    add(`Vermieter ${i + 1}: ${l.firstName} ${l.lastName}`);
    add("Unterschrift: _______________________________");
    add("");
  });
  form.tenants.forEach((t, i) => {
    add(`Mieter ${i + 1}: ${t.firstName} ${t.lastName}`);
    add("Unterschrift: _______________________________");
    add("");
  });

  add("─".repeat(60));
  add("⚠ RECHTLICHER HINWEIS");
  add("Dieses Dokument stellt keine Rechtsberatung dar.");
  add("Bei besonderen rechtlichen Anforderungen sollte ein");
  add("Rechtsanwalt oder Mieterverein konsultiert werden.");
  add("MyContentPilot.de – Mietvertrag Generator");

  return lines.join("\n");
}

function downloadContract(form) {
  const text = generateContractText(form);
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "Mietvertrag_MyContentPilot.txt";
  a.click();
  URL.revokeObjectURL(url);
}

// ── UI Components ─────────────────────────────────────────────────────────────
function Input({ label, type = "text", value, onChange, placeholder, required }) {
  return (
    <div className="field">
      <label>{label}{required && <span className="req"> *</span>}</label>
      <input type={type} value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} />
    </div>
  );
}

function Select({ label, value, onChange, options }) {
  return (
    <div className="field">
      <label>{label}</label>
      <select value={value} onChange={e => onChange(e.target.value)}>
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );
}

function Checkbox({ label, checked, onChange }) {
  return (
    <label className="check-label">
      <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} />
      <span>{label}</span>
    </label>
  );
}

function Section({ title, children, icon }) {
  const [open, setOpen] = useState(true);
  return (
    <div className="section">
      <button className="section-head" onClick={() => setOpen(o => !o)}>
        <span>{icon} {title}</span>
        <span className="chevron">{open ? "▲" : "▼"}</span>
      </button>
      {open && <div className="section-body">{children}</div>}
    </div>
  );
}

function PersonCard({ person, onUpdate, onRemove, type, index, canRemove }) {
  const up = (field) => (val) => onUpdate({ ...person, [field]: val });
  return (
    <div className="person-card">
      <div className="person-head">
        <span>{type} {index + 1}</span>
        {canRemove && <button className="btn-sm btn-danger" onClick={onRemove}>✕ Entfernen</button>}
      </div>
      <div className="grid-2">
        <Input label="Vorname" value={person.firstName} onChange={up("firstName")} required />
        <Input label="Nachname" value={person.lastName} onChange={up("lastName")} required />
      </div>
      <div className="grid-2">
        <Input label="Geburtsdatum" type="date" value={person.dob} onChange={up("dob")} />
        <Input label="Telefon" value={person.phone} onChange={up("phone")} />
      </div>
      {type === "Mieter" && (
        <Input label="Aktuelle Adresse" value={person.currentAddress || ""} onChange={up("currentAddress")}
          placeholder="Straße, Hausnr., PLZ, Stadt" required />
      )}
      {type === "Vermieter" && (
        <Input label="Adresse" value={person.address || ""} onChange={up("address")}
          placeholder="Straße, Hausnr., PLZ, Stadt" required />
      )}
      <div className="grid-2">
        <Input label="E-Mail" type="email" value={person.email} onChange={up("email")} />
        <span />
      </div>
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────────────────────────
export default function App() {
  const [form, setForm] = useState(() => {
    try {
      const saved = localStorage.getItem("mietvertrag_draft_mcp");
      return saved ? JSON.parse(saved) : defaultForm;
    } catch { return defaultForm; }
  });
  const [dark, setDark] = useState(false);
  const [tab, setTab] = useState("form");
  const [saved, setSaved] = useState(false);

  const upForm = useCallback((path, val) => {
    setForm(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      const keys = path.split(".");
      let obj = next;
      for (let i = 0; i < keys.length - 1; i++) obj = obj[keys[i]];
      obj[keys[keys.length - 1]] = val;
      return next;
    });
  }, []);

  const saveDraft = () => {
    localStorage.setItem("mietvertrag_draft_mcp", JSON.stringify(form));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const applyPreset = (key) => {
    const p = PRESETS[key];
    setForm(prev => ({
      ...prev,
      property: { ...prev.property, type: p.propertyType },
      houseRules: { ...prev.houseRules, ...p.houseRules },
      inventory: p.inventory,
      rent: { ...prev.rent, furnitureSurcharge: p.furnitureSurcharge },
    }));
  };

  const reset = () => { if (confirm("Formular zurücksetzen?")) setForm(defaultForm); };

  const addLandlord = () => setForm(p => ({ ...p, landlords: [...p.landlords, emptyLandlord()] }));
  const upLandlord = (i, val) => setForm(p => { const l = [...p.landlords]; l[i] = val; return { ...p, landlords: l }; });
  const remLandlord = (i) => setForm(p => ({ ...p, landlords: p.landlords.filter((_, j) => j !== i) }));

  const addTenant = () => setForm(p => ({ ...p, tenants: [...p.tenants, emptyTenant()] }));
  const upTenant = (i, val) => setForm(p => { const t = [...p.tenants]; t[i] = val; return { ...p, tenants: t }; });
  const remTenant = (i) => setForm(p => ({ ...p, tenants: p.tenants.filter((_, j) => j !== i) }));

  const addItem = () => setForm(p => ({ ...p, inventory: [...p.inventory, emptyItem()] }));
  const upItem = (i, field, val) => setForm(p => {
    const inv = [...p.inventory];
    inv[i] = { ...inv[i], [field]: val };
    return { ...p, inventory: inv };
  });
  const remItem = (i) => setForm(p => ({ ...p, inventory: p.inventory.filter((_, j) => j !== i) }));

  const warm = calcWarm(form.rent);
  const contractText = generateContractText(form);

  return (
    <div className={`app${dark ? " dark" : ""}`}>
      <style>{`
        :root {
          --bg:#f4f6fb;--bg2:#ffffff;--border:#d0d8e8;--text:#1a2236;--text2:#5a6a88;
          --accent:#1e3a6e;--accent2:#2d5bb5;--accent-light:#e8edf8;--danger:#c0392b;
          --section-bg:#f8faff;--card-shadow:0 2px 12px rgba(30,58,110,0.08);--radius:10px;
        }
        .dark{
          --bg:#0f1420;--bg2:#161e30;--border:#263050;--text:#dde4f4;--text2:#7a90b8;
          --accent:#4a7fd4;--accent2:#6699e8;--accent-light:#1a2540;
          --section-bg:#131a28;--card-shadow:0 2px 12px rgba(0,0,0,0.4);
        }
        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
        body{font-family:'Georgia',serif;}
        .app{min-height:100vh;background:var(--bg);color:var(--text);transition:all 0.3s;}
        .header{background:var(--accent);color:#fff;padding:0 24px;}
        .header-inner{max-width:960px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:64px;}
        .logo{font-size:1.1rem;font-weight:700;letter-spacing:-0.5px;display:flex;align-items:center;gap:10px;}
        .logo-badge{background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);border-radius:5px;padding:3px 8px;font-size:0.72rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;}
        .logo-domain{opacity:0.65;font-size:0.8rem;font-weight:400;}
        .header-btns{display:flex;gap:8px;align-items:center;}
        .btn-icon{background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.2);color:#fff;border-radius:6px;padding:6px 12px;cursor:pointer;font-size:0.82rem;transition:background 0.2s;}
        .btn-icon:hover{background:rgba(255,255,255,0.22);}
        .tabs{background:var(--bg2);border-bottom:2px solid var(--border);}
        .tabs-inner{max-width:960px;margin:0 auto;display:flex;}
        .tab{padding:14px 24px;cursor:pointer;font-size:0.88rem;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all 0.2s;color:var(--text2);}
        .tab.active{color:var(--accent);border-bottom-color:var(--accent);font-weight:600;}
        .main{max-width:960px;margin:0 auto;padding:24px 16px 80px;}
        .presets{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px;}
        .preset-lbl{font-size:0.78rem;font-weight:700;color:var(--text2);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px;}
        .preset-btn{background:var(--bg2);border:1px solid var(--border);color:var(--text);border-radius:20px;padding:6px 16px;font-size:0.8rem;cursor:pointer;transition:all 0.2s;}
        .preset-btn:hover{background:var(--accent-light);border-color:var(--accent);color:var(--accent);}
        .section{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:14px;overflow:hidden;box-shadow:var(--card-shadow);}
        .section-head{width:100%;display:flex;justify-content:space-between;align-items:center;padding:14px 20px;background:var(--section-bg);border:none;cursor:pointer;font-size:0.9rem;font-weight:600;color:var(--text);letter-spacing:0.2px;}
        .section-head:hover{background:var(--accent-light);}
        .chevron{font-size:0.72rem;color:var(--text2);}
        .section-body{padding:20px;}
        .field{margin-bottom:13px;}
        .field label{display:block;font-size:0.78rem;font-weight:700;color:var(--text2);margin-bottom:5px;text-transform:uppercase;letter-spacing:0.5px;}
        .req{color:var(--danger);}
        .field input,.field select,.field textarea{width:100%;padding:9px 12px;background:var(--bg);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:0.88rem;outline:none;transition:border-color 0.2s;}
        .field input:focus,.field select:focus,.field textarea:focus{border-color:var(--accent);}
        .field textarea{min-height:80px;resize:vertical;font-family:inherit;}
        .grid-2{display:grid;grid-template-columns:1fr 1fr;gap:13px;}
        .grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:13px;}
        @media(max-width:600px){.grid-2,.grid-3{grid-template-columns:1fr;}}
        .person-card{background:var(--section-bg);border:1px solid var(--border);border-radius:8px;padding:16px;margin-bottom:13px;}
        .person-head{display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:0.85rem;color:var(--accent);margin-bottom:12px;}
        .btn{padding:9px 18px;border-radius:7px;border:none;cursor:pointer;font-size:0.88rem;font-weight:600;transition:all 0.2s;}
        .btn-primary{background:var(--accent);color:#fff;}
        .btn-primary:hover{background:var(--accent2);}
        .btn-outline{background:transparent;border:1.5px solid var(--accent);color:var(--accent);}
        .btn-outline:hover{background:var(--accent-light);}
        .btn-sm{padding:4px 9px;font-size:0.75rem;border-radius:5px;border:none;cursor:pointer;}
        .btn-danger{background:#fde8e8;color:var(--danger);}
        .btn-add{display:flex;align-items:center;gap:6px;margin-top:4px;}
        .check-label{display:flex;align-items:center;gap:10px;cursor:pointer;padding:7px 0;font-size:0.88rem;}
        .check-label input[type=checkbox]{width:16px;height:16px;accent-color:var(--accent);}
        .checks-grid{display:grid;grid-template-columns:1fr 1fr;gap:0;}
        @media(max-width:600px){.checks-grid{grid-template-columns:1fr;}}
        .warm-box{background:var(--accent-light);border:1.5px solid var(--accent);border-radius:8px;padding:13px 18px;display:flex;justify-content:space-between;align-items:center;margin-top:8px;}
        .warm-box .label{font-size:0.82rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--accent);}
        .warm-box .value{font-size:1.35rem;font-weight:700;color:var(--accent);}
        .inv-row{display:grid;grid-template-columns:1fr 80px 34px;gap:8px;align-items:center;margin-bottom:8px;}
        .inv-row input{padding:8px 10px;background:var(--bg);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:0.88rem;outline:none;}
        .action-bar{position:fixed;bottom:0;left:0;right:0;background:var(--bg2);border-top:1px solid var(--border);padding:12px 24px;display:flex;gap:10px;justify-content:center;z-index:100;box-shadow:0 -4px 20px rgba(0,0,0,0.09);}
        .preview-wrap{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;}
        .preview-toolbar{padding:12px 16px;background:var(--section-bg);border-bottom:1px solid var(--border);display:flex;gap:8px;}
        .preview-content{padding:28px 32px;font-family:'Courier New',monospace;font-size:0.76rem;line-height:1.75;white-space:pre-wrap;max-height:70vh;overflow-y:auto;color:var(--text);}
        .disclaimer{background:#fff8e1;border:1px solid #f0c040;border-radius:8px;padding:13px 18px;font-size:0.8rem;color:#7a5c00;margin-bottom:18px;}
        .dark .disclaimer{background:#2a2000;border-color:#6a4e00;color:#d4a820;}
        .toast{position:fixed;top:78px;right:18px;background:var(--accent);color:#fff;padding:9px 16px;border-radius:8px;font-size:0.82rem;font-weight:700;z-index:999;animation:fadeIn 0.3s;}
        @keyframes fadeIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
        @media print{.header,.tabs,.action-bar,.preset-btn,.chevron,.btn-sm{display:none!important;}.app{background:#fff;color:#000;}.preview-content{max-height:none;font-size:0.85rem;}}
      `}</style>

      {saved && <div className="toast">✓ Entwurf gespeichert</div>}

      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span>📄 Mietvertrag Generator</span>
            <span className="logo-badge">Beta</span>
            <span className="logo-domain">MyContentPilot.de</span>
          </div>
          <div className="header-btns">
            <button className="btn-icon" onClick={saveDraft}>💾</button>
            <button className="btn-icon" onClick={() => setDark(d => !d)}>{dark ? "☀️" : "🌙"}</button>
            <button className="btn-icon" onClick={reset}>↺</button>
          </div>
        </div>
      </header>

      <div className="tabs">
        <div className="tabs-inner">
          <div className={`tab${tab === "form" ? " active" : ""}`} onClick={() => setTab("form")}>📝 Formular</div>
          <div className={`tab${tab === "preview" ? " active" : ""}`} onClick={() => setTab("preview")}>👁 Vorschau & Download</div>
        </div>
      </div>

      <div className="main">
        {tab === "form" ? (
          <>
            <div className="disclaimer">
              ⚠️ <strong>Rechtlicher Hinweis:</strong> Dieses Dokument stellt keine Rechtsberatung dar. Bei besonderen rechtlichen Anforderungen sollte ein Rechtsanwalt oder Mieterverein konsultiert werden.
            </div>

            <div style={{ marginBottom: 20 }}>
              <div className="preset-lbl">Vorlage wählen:</div>
              <div className="presets">
                {Object.entries(PRESETS).map(([k, p]) => (
                  <button key={k} className="preset-btn" onClick={() => applyPreset(k)}>{p.label}</button>
                ))}
              </div>
            </div>

            <Section title="Vermieter" icon="🏠">
              {form.landlords.map((l, i) => (
                <PersonCard key={l.id} person={l} type="Vermieter" index={i}
                  onUpdate={(v) => upLandlord(i, v)} onRemove={() => remLandlord(i)}
                  canRemove={form.landlords.length > 1} />
              ))}
              <button className="btn btn-outline btn-add" onClick={addLandlord}>＋ Weiteren Vermieter hinzufügen</button>
            </Section>

            <Section title="Mieter" icon="👤">
              {form.tenants.map((t, i) => (
                <PersonCard key={t.id} person={t} type="Mieter" index={i}
                  onUpdate={(v) => upTenant(i, v)} onRemove={() => remTenant(i)}
                  canRemove={form.tenants.length > 1} />
              ))}
              <button className="btn btn-outline btn-add" onClick={addTenant}>＋ Weiteren Mieter hinzufügen</button>
            </Section>

            <Section title="Mietobjekt" icon="📍">
              <div className="grid-2">
                <Input label="Straße" value={form.property.street} onChange={v => upForm("property.street", v)} required />
                <Input label="Hausnummer" value={form.property.houseNumber} onChange={v => upForm("property.houseNumber", v)} required />
              </div>
              <div className="grid-2">
                <Input label="Postleitzahl" value={form.property.postalCode} onChange={v => upForm("property.postalCode", v)} required />
                <Input label="Stadt" value={form.property.city} onChange={v => upForm("property.city", v)} required />
              </div>
              <Select label="Art der Immobilie" value={form.property.type} onChange={v => upForm("property.type", v)} options={[
                { value: "wg", label: "WG-Zimmer" },
                { value: "apartment", label: "Wohnung" },
                { value: "house", label: "Haus" },
              ]} />
              {form.property.type === "wg" && (
                <div className="grid-2">
                  <Input label="Zimmer-Nr." value={form.property.roomNumber} onChange={v => upForm("property.roomNumber", v)} />
                  <Input label="Zimmergröße (m²)" type="number" value={form.property.roomSize} onChange={v => upForm("property.roomSize", v)} />
                </div>
              )}
              <div className="grid-3">
                <Input label="Gesamtgröße (m²)" type="number" value={form.property.totalSize} onChange={v => upForm("property.totalSize", v)} />
                <Input label="Etage" value={form.property.floor} onChange={v => upForm("property.floor", v)} />
                <Input label="Baujahr" type="number" value={form.property.buildingYear} onChange={v => upForm("property.buildingYear", v)} />
              </div>
            </Section>

            <Section title="Vertragsdetails" icon="📅">
              <div className="grid-2">
                <Input label="Einzugsdatum" type="date" value={form.contract.moveInDate} onChange={v => upForm("contract.moveInDate", v)} />
                <Input label="Mietbeginn" type="date" value={form.contract.startDate} onChange={v => upForm("contract.startDate", v)} />
              </div>
              <Checkbox label="Befristeter Vertrag" checked={form.contract.isFixedTerm} onChange={v => upForm("contract.isFixedTerm", v)} />
              {form.contract.isFixedTerm && (
                <Input label="Vertragsende" type="date" value={form.contract.endDate} onChange={v => upForm("contract.endDate", v)} />
              )}
              <div className="grid-2">
                <Select label="Mindestmietdauer" value={form.contract.minStay} onChange={v => upForm("contract.minStay", v)} options={[
                  { value: "none", label: "Keine" }, { value: "3months", label: "3 Monate" },
                  { value: "6months", label: "6 Monate" }, { value: "12months", label: "12 Monate" },
                ]} />
                <Select label="Kündigungsfrist" value={form.contract.noticePeriod} onChange={v => upForm("contract.noticePeriod", v)} options={[
                  { value: "2weeks", label: "2 Wochen" }, { value: "1month", label: "1 Monat" },
                  { value: "3months", label: "3 Monate" }, { value: "custom", label: "Individuell" },
                ]} />
              </div>
              {form.contract.noticePeriod === "custom" && (
                <Input label="Individuelle Kündigungsfrist" value={form.contract.customNotice} onChange={v => upForm("contract.customNotice", v)} />
              )}
            </Section>

            <Section title="Miete & Nebenkosten" icon="💶">
              <div className="grid-2">
                <Input label="Kaltmiete (€)" type="number" value={form.rent.coldRent} onChange={v => upForm("rent.coldRent", v)} required />
                <Input label="Möblierungszuschlag (€)" type="number" value={form.rent.furnitureSurcharge} onChange={v => upForm("rent.furnitureSurcharge", v)} />
              </div>
              <div className="grid-2">
                <Input label="Nebenkosten (€)" type="number" value={form.rent.utilities} onChange={v => upForm("rent.utilities", v)} />
                <Input label="Internet (€)" type="number" value={form.rent.internet} onChange={v => upForm("rent.internet", v)} />
              </div>
              <div className="grid-2">
                <Input label="Stellplatz (€)" type="number" value={form.rent.parking} onChange={v => upForm("rent.parking", v)} />
                <Input label="Sonstige Kosten (€)" type="number" value={form.rent.otherCosts} onChange={v => upForm("rent.otherCosts", v)} />
              </div>
              <div className="warm-box">
                <span className="label">Warmmiete (gesamt)</span>
                <span className="value">{warm} €</span>
              </div>
            </Section>

            <Section title="Kaution" icon="🔐">
              <Select label="Kautionshöhe" value={form.deposit.type} onChange={v => upForm("deposit.type", v)} options={[
                { value: "oneMonth", label: "1 Monatsmiete" }, { value: "twoMonths", label: "2 Monatsmieten" },
                { value: "threeMonths", label: "3 Monatsmieten" }, { value: "custom", label: "Individuell" },
              ]} />
              {form.deposit.type === "custom" && (
                <Input label="Kautionsbetrag (€)" type="number" value={form.deposit.customAmount} onChange={v => upForm("deposit.customAmount", v)} />
              )}
              <div style={{ fontSize: "0.83rem", color: "var(--text2)", marginTop: 8 }}>
                Betrag: <strong>{
                  form.deposit.type === "custom" ? `${form.deposit.customAmount || 0} €` :
                  form.deposit.type === "oneMonth" ? `${form.rent.coldRent || 0} €` :
                  form.deposit.type === "twoMonths" ? `${(parseFloat(form.rent.coldRent || 0) * 2).toFixed(2)} €` :
                  `${(parseFloat(form.rent.coldRent || 0) * 3).toFixed(2)} €`
                }</strong>
              </div>
            </Section>

            <Section title="Hausordnung" icon="📋">
              <div className="checks-grid">
                <Checkbox label="Rauchverbot" checked={form.houseRules.noSmoking} onChange={v => upForm("houseRules.noSmoking", v)} />
                <Checkbox label="Keine Haustiere" checked={form.houseRules.noPets} onChange={v => upForm("houseRules.noPets", v)} />
                <Checkbox label="Ruhezeiten" checked={form.houseRules.quietHours} onChange={v => upForm("houseRules.quietHours", v)} />
                <Checkbox label="Gemeinschaftsküche" checked={form.houseRules.sharedKitchen} onChange={v => upForm("houseRules.sharedKitchen", v)} />
                <Checkbox label="Gemeinschaftsbad" checked={form.houseRules.sharedBathroom} onChange={v => upForm("houseRules.sharedBathroom", v)} />
                <Checkbox label="Besucherregelung" checked={form.houseRules.visitorRules} onChange={v => upForm("houseRules.visitorRules", v)} />
              </div>
              <div className="field" style={{ marginTop: 12 }}>
                <label>Individuelle Regelungen</label>
                <textarea value={form.houseRules.customRules} onChange={e => upForm("houseRules.customRules", e.target.value)} placeholder="Weitere Hausordnungsregeln..." />
              </div>
            </Section>

            <Section title="Inventar / Ausstattung" icon="🛋">
              {form.inventory.map((item, i) => (
                <div key={item.id} className="inv-row">
                  <input value={item.name} onChange={e => upItem(i, "name", e.target.value)} placeholder="Gegenstand (z.B. Bett)" />
                  <input type="number" value={item.qty} min={1} onChange={e => upItem(i, "qty", e.target.value)} />
                  <button className="btn-sm btn-danger" onClick={() => remItem(i)}>✕</button>
                </div>
              ))}
              <button className="btn btn-outline btn-add" onClick={addItem}>＋ Gegenstand hinzufügen</button>
            </Section>

            <Section title="Besondere Vereinbarungen" icon="✍️">
              <div className="field">
                <textarea value={form.specialAgreements} onChange={e => setForm(p => ({ ...p, specialAgreements: e.target.value }))}
                  placeholder="Weitere individuelle Vereinbarungen..." style={{ minHeight: 110 }} />
              </div>
            </Section>

            <Section title="Unterschriften" icon="✒️">
              <div className="grid-2">
                <Input label="Ort" value={form.contractPlace} onChange={v => setForm(p => ({ ...p, contractPlace: v }))} placeholder="Berlin" />
                <Input label="Datum" type="date" value={form.contractDate} onChange={v => setForm(p => ({ ...p, contractDate: v }))} />
              </div>
            </Section>
          </>
        ) : (
          <div className="preview-wrap">
            <div className="preview-toolbar">
              <button className="btn btn-primary" onClick={() => downloadContract(form)}>⬇ Vertrag herunterladen (.txt)</button>
              <button className="btn btn-outline" onClick={() => window.print()}>🖨 Drucken</button>
            </div>
            <div className="preview-content">{contractText}</div>
          </div>
        )}
      </div>

      <div className="action-bar">
        <button className="btn btn-outline" onClick={saveDraft}>💾 Entwurf speichern</button>
        <button className="btn btn-primary" onClick={() => setTab(t => t === "form" ? "preview" : "form")}>
          {tab === "form" ? "👁 Vorschau & Download" : "📝 Zurück zum Formular"}
        </button>
        {tab === "preview" && (
          <button className="btn btn-primary" onClick={() => downloadContract(form)}>⬇ Herunterladen</button>
        )}
      </div>
    </div>
  );
}
