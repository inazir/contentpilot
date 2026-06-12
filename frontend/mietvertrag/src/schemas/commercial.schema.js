const commercialSchema = {
  id: "commercial",
  label: "Büro / Gewerberaum",

  visibleSections: [
    "contractType","landlords","tenants","property","rentalPeriod",
    "rent","bank","deposit","inventory","keys","access",
    "specialAgreements","signatures",
  ],

  requiredFields: [
    "landlords[0].firstName","landlords[0].lastName",
    "tenants[0].firstName","tenants[0].lastName",
    "property.street","property.houseNumber",
    "property.postalCode","property.city","property.totalArea",
    "rentalPeriod.startDate","rent.coldRent",
  ],

  defaultHouseRules: {},
  defaultSharedAreas: {},
  defaultInventoryFurnished: () => [],
  defaultInventoryUnfurnished: () => [],

  clauses: {
    mietobjekt: `Das Mietobjekt ist ein Büro-/Gewerberaum im genannten Gebäude. Der Raum darf ausschließlich für die vereinbarte gewerbliche Nutzung verwendet werden.`,
    nutzung: `Eine Änderung des Nutzungszwecks bedarf der schriftlichen Genehmigung des Vermieters. Bauliche Veränderungen sind nur mit schriftlicher Erlaubnis gestattet und bei Auszug rückgängig zu machen.`,
    nebenkosten: `Nebenkosten werden monatlich als Vorauszahlung geleistet und jährlich abgerechnet. Der Mieter trägt die auf das Mietobjekt entfallenden Betriebskosten gemäß Betriebskostenverordnung.`,
    kündigung: `Die ordentliche Kündigung von Gewerberaummietverhältnissen richtet sich nach den vertraglichen Vereinbarungen. Eine Mindestlaufzeit kann gesondert vereinbart werden.`,
    allgemeinesPflichten: `Der Mieter ist verpflichtet, alle für seinen Gewerbebetrieb erforderlichen Genehmigungen selbst einzuholen und auf eigene Kosten zu unterhalten.`,
  },

  documents: ["mietvertrag","uebergabeprotokoll","schluesselprotokoll","inventarliste"],
};

export default commercialSchema;
