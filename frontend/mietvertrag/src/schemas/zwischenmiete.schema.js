const zwischenmieteSchema = {
  id: "zwischenmiete",
  label: "Zwischenmiete",

  visibleSections: [
    "contractType","landlords","tenants","property","rentalPeriod",
    "rent","bank","deposit","inventory","keys","houseRules",
    "specialAgreements","signatures",
  ],

  requiredFields: [
    "landlords[0].firstName","landlords[0].lastName",
    "tenants[0].firstName","tenants[0].lastName",
    "property.street","property.houseNumber",
    "property.postalCode","property.city",
    "rentalPeriod.startDate","rentalPeriod.endDate","rent.coldRent",
  ],

  defaultHouseRules: {
    noSmoking: true, quietHours: true, noSubletting: true,
  },

  defaultSharedAreas: {},
  defaultInventoryFurnished: () => [],
  defaultInventoryUnfurnished: () => [],

  clauses: {
    mietobjekt: `Dieses Mietverhältnis ist als Zwischenmiete ausgestaltet. Der Vermieter (Hauptmieter) vermietet die Wohnung/das Zimmer für einen befristeten Zeitraum weiter.`,
    befristung: `Der Vertrag ist zwingend auf den vereinbarten Zeitraum befristet. Eine automatische Verlängerung findet nicht statt. Der Mieter ist verpflichtet, die Unterkunft am vereinbarten Enddatum zu räumen und zu übergeben.`,
    nutzung: `Der Mieter darf die Unterkunft nur zu Wohnzwecken nutzen. Eine weitere Untervermietung ist nicht gestattet.`,
    kündigung: `Eine ordentliche Kündigung während der Laufzeit ist ausgeschlossen. Das außerordentliche Kündigungsrecht bleibt unberührt.`,
    allgemeinesPflichten: `Der Mieter übernimmt die Wohnung in dem beschriebenen Zustand und ist verpflichtet, sie in gleichem Zustand zurückzugeben.`,
  },

  documents: ["mietvertrag","uebergabeprotokoll","schluesselprotokoll","inventarliste"],
};

export default zwischenmieteSchema;
