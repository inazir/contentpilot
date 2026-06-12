const storageSchema = {
  id: "storage",
  label: "Keller / Lagerraum",

  visibleSections: [
    "contractType","landlords","tenants","property","rentalPeriod",
    "rent","bank","deposit","keys","specialAgreements","signatures",
  ],

  requiredFields: [
    "landlords[0].firstName","landlords[0].lastName",
    "tenants[0].firstName","tenants[0].lastName",
    "property.street","property.houseNumber",
    "property.postalCode","property.city",
    "rentalPeriod.startDate","rent.coldRent",
  ],

  defaultHouseRules: {},
  defaultSharedAreas: {},
  defaultInventoryFurnished: () => [],
  defaultInventoryUnfurnished: () => [],

  clauses: {
    mietobjekt: `Das Mietobjekt ist ein Kellerraum/Lagerraum im genannten Gebäude. Der Raum darf ausschließlich zur Lagerung genutzt werden.`,
    nutzung: `Die Lagerung von feuergefährlichen, explosiven oder gesundheitsschädlichen Stoffen ist untersagt. Lebendige Tiere dürfen nicht im Raum gehalten werden.`,
    kündigung: `Das Mietverhältnis kann von beiden Seiten mit einer Frist von einem Monat zum Monatsende schriftlich gekündigt werden.`,
    allgemeinesPflichten: `Der Mieter ist für die ordnungsgemäße Nutzung und Sauberkeit des Lagerraums verantwortlich.`,
  },

  documents: ["mietvertrag","schluesselprotokoll"],
};

export default storageSchema;
