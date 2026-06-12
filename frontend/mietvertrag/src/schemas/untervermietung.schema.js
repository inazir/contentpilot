const untervermietungSchema = {
  id: "untervermietung",
  label: "Untervermietung",

  visibleSections: [
    "contractType","landlords","tenants","property","rentalPeriod",
    "rent","bank","deposit","inventory","keys","sharedAreas",
    "houseRules","specialAgreements","signatures",
  ],

  requiredFields: [
    "landlords[0].firstName","landlords[0].lastName",
    "tenants[0].firstName","tenants[0].lastName",
    "property.street","property.houseNumber",
    "property.postalCode","property.city",
    "rentalPeriod.startDate","rent.coldRent",
  ],

  defaultHouseRules: {
    noSmoking: true, quietHours: true,
    sharedKitchen: true, sharedBathroom: true, noSubletting: true,
  },

  defaultSharedAreas: {
    kitchen: true, bathroom: true,
  },

  defaultInventoryFurnished: () => [],
  defaultInventoryUnfurnished: () => [],

  clauses: {
    mietobjekt: `Dieses Mietverhältnis ist ein Untermietvertrag. Der Untervermieter (Hauptmieter) handelt mit Genehmigung des Hauptvermieters. Eine Kopie der Genehmigung ist diesem Vertrag beizulegen.`,
    genehmigung: `Der Untervermieter versichert, dass eine schriftliche Genehmigung des Hauptvermieters zur Untervermietung vorliegt. Bei Erlöschen dieser Genehmigung endet auch dieses Untermietverhältnis.`,
    nutzung: `Der Untermieter darf das Zimmer/die Fläche ausschließlich zu Wohnzwecken nutzen. Eine weitere Untervermietung ist untersagt.`,
    kündigung: `Das Untermietverhältnis endet spätestens mit dem Hauptmietverhältnis. Die vereinbarte Kündigungsfrist gilt für beide Parteien.`,
    allgemeinesPflichten: `Der Untermieter ist verpflichtet, die Hausordnung des Gebäudes einzuhalten und das Verhältnis zu den übrigen Bewohnern nicht zu beeinträchtigen.`,
  },

  documents: ["mietvertrag","uebergabeprotokoll","schluesselprotokoll","inventarliste","hausordnung"],
};

export default untervermietungSchema;
