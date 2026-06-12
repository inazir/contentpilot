import { uid } from "../utils/uid.js";

const apartmentSchema = {
  id: "apartment",
  label: "Wohnung",

  visibleSections: [
    "contractType","landlords","tenants","property","rentalPeriod",
    "rent","bank","deposit","inventory","keys","houseRules",
    "safety","registration","insurance","access","specialAgreements","signatures",
  ],

  requiredFields: [
    "landlords[0].firstName","landlords[0].lastName",
    "tenants[0].firstName","tenants[0].lastName",
    "property.street","property.houseNumber",
    "property.postalCode","property.city","property.livingArea",
    "rentalPeriod.startDate","rent.coldRent",
  ],

  defaultHouseRules: {
    quietHours: true, wasteSeparation: true, noSubletting: true,
  },

  defaultSharedAreas: {},

  defaultInventoryFurnished: () => [
    { id: uid(), name: "Küche (Einbauküche)", quantity: 1, condition: "gut", notes: "", replacementValue: "", room: "wohnung" },
    { id: uid(), name: "Kühlschrank", quantity: 1, condition: "gut", notes: "", replacementValue: "", room: "wohnung" },
    { id: uid(), name: "Herd/Ofen", quantity: 1, condition: "gut", notes: "", replacementValue: "", room: "wohnung" },
  ],

  defaultInventoryUnfurnished: () => [],

  clauses: {
    mietobjekt: `Das Mietobjekt ist eine Wohnung im beschriebenen Gebäude. Die Wohnung wird dem Mieter zur alleinigen Nutzung überlassen.`,
    nutzung: `Der Mieter darf die Wohnung ausschließlich zu Wohnzwecken nutzen. Eine gewerbliche Nutzung bedarf der ausdrücklichen schriftlichen Zustimmung des Vermieters.`,
    nebenkosten: `Die Nebenkosten werden als Vorauszahlung erhoben und jährlich abgerechnet. Der Mieter erhält innerhalb von 12 Monaten nach Ende des Abrechnungszeitraums eine Abrechnung.`,
    kaution: `Die Kaution ist bei Mietbeginn fällig. Die Rückzahlung erfolgt nach Beendigung des Mietverhältnisses und Prüfung des Zustands der Wohnung, spätestens jedoch innerhalb von 6 Monaten, abzüglich berechtigter Forderungen.`,
    kündigung: `Die ordentliche Kündigung bedarf der Schriftform. Für den Mieter gilt eine Kündigungsfrist von 3 Monaten zum Monatsende. Für den Vermieter gelten die gesetzlichen Fristen gemäß § 573c BGB.`,
    schönheitsreparaturen: `Schönheitsreparaturen werden gemäß den gesetzlichen Bestimmungen geregelt. Starre Fristenregelungen sind nicht Bestandteil dieses Vertrages.`,
    untervermietung: `Eine Untervermietung oder sonstige Gebrauchsüberlassung an Dritte bedarf der vorherigen schriftlichen Genehmigung des Vermieters.`,
    allgemeinesPflichten: `Der Mieter ist verpflichtet:\n1. Die Wohnung pfleglich zu behandeln und in ordnungsgemäßem Zustand zu erhalten.\n2. Schäden unverzüglich dem Vermieter zu melden.\n3. Die Miete monatlich im Voraus, spätestens am dritten Werktag des Monats zu zahlen.\n4. Die Hausordnung einzuhalten.\n5. Lüftung und Heizung zur Vermeidung von Schimmelbildung sicherzustellen.`,
  },

  documents: [
    "mietvertrag","uebergabeprotokoll","schluesselprotokoll",
    "inventarliste","hausordnung","wohnungsgeberbestaetigung",
    "kuendigungsformular","mietbescheinigung",
  ],
};

export default apartmentSchema;
