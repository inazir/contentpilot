const houseSchema = {
  id: "house",
  label: "Haus",

  visibleSections: [
    "contractType","landlords","tenants","property","rentalPeriod",
    "rent","bank","deposit","inventory","keys","houseRules",
    "safety","registration","insurance","access","specialAgreements","signatures",
  ],

  requiredFields: [
    "landlords[0].firstName","landlords[0].lastName",
    "tenants[0].firstName","tenants[0].lastName",
    "property.street","property.houseNumber",
    "property.postalCode","property.city","property.totalArea",
    "rentalPeriod.startDate","rent.coldRent",
  ],

  defaultHouseRules: {
    quietHours: true, wasteSeparation: true, noSubletting: true,
  },

  defaultSharedAreas: {},
  defaultInventoryFurnished: () => [],
  defaultInventoryUnfurnished: () => [],

  clauses: {
    mietobjekt: `Das Mietobjekt ist ein Einfamilienhaus/Doppelhaus/Reihenhaus gemäß Beschreibung. Garten, Garage und Nebengebäude sind in der Mietfläche enthalten, sofern nicht gesondert ausgewiesen.`,
    nutzung: `Der Mieter darf das Haus und das Grundstück ausschließlich zu Wohnzwecken nutzen. Tierhaltung im Garten ist nach Absprache mit dem Vermieter gestattet.`,
    nebenkosten: `Nebenkosten werden als Vorauszahlung erhoben und jährlich abgerechnet. Kosten für Müllabfuhr, Straßenreinigung, Schornsteinfeger und Grundsteuer werden anteilig auf den Mieter umgelegt.`,
    kaution: `Die Kaution ist spätestens bei Schlüsselübergabe fällig. Die Rückzahlung erfolgt nach Beendigung des Mietverhältnisses und Abnahme des Hauses und Grundstücks.`,
    kündigung: `Es gelten die gesetzlichen Kündigungsfristen gemäß §§ 573, 573c BGB. Für den Mieter beträgt die Frist 3 Monate, für den Vermieter staffelt sie sich nach Mietdauer.`,
    garten: `Der Mieter ist verpflichtet, den Garten ordnungsgemäß zu pflegen und in gepflegtem Zustand zu erhalten. Baumfällungen und bauliche Veränderungen im Garten bedürfen der schriftlichen Zustimmung des Vermieters.`,
    allgemeinesPflichten: `Der Mieter ist verpflichtet:\n1. Das Haus und Grundstück pfleglich zu behandeln.\n2. Kleinreparaturen bis zu einem Betrag von 100 € pro Einzelfall selbst zu tragen.\n3. Schäden unverzüglich zu melden.\n4. Heizung und Wasserleitungen im Winter frostsicher zu halten.\n5. Die Miete pünktlich zu zahlen.`,
  },

  documents: [
    "mietvertrag","uebergabeprotokoll","schluesselprotokoll",
    "inventarliste","wohnungsgeberbestaetigung",
    "kuendigungsformular","mietbescheinigung",
  ],
};

export default houseSchema;
