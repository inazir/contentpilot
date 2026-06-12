const garageSchema = {
  id: "garage",
  label: "Garage / Stellplatz",

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
    mietobjekt: `Das Mietobjekt ist eine Garage/ein Stellplatz an der genannten Adresse. Das Objekt darf ausschließlich zum Abstellen von Kraftfahrzeugen genutzt werden.`,
    nutzung: `Die Lagerung von feuergefährlichen Stoffen, Chemikalien oder Sperrmüll ist nicht gestattet. Eine Nutzung als Werkstatt ist nur mit ausdrücklicher Genehmigung des Vermieters erlaubt.`,
    kündigung: `Das Mietverhältnis kann von beiden Seiten mit einer Frist von einem Monat zum Monatsende gekündigt werden, sofern nicht anders vereinbart.`,
    allgemeinesPflichten: `Der Mieter ist verpflichtet, die Garage/den Stellplatz ordnungsgemäß zu nutzen und Schäden unverzüglich zu melden.`,
  },

  documents: ["mietvertrag","schluesselprotokoll"],
};

export default garageSchema;
