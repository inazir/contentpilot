import { uid } from "../utils/uid.js";

const wgSchema = {
  id: "wg",
  label: "WG-Zimmer",

  visibleSections: [
    "contractType","landlords","tenants","property","rentalPeriod",
    "rent","bank","deposit","inventory","keys","sharedAreas",
    "houseRules","safety","registration","insurance","access",
    "specialAgreements","signatures",
  ],

  requiredFields: [
    "landlords[0].firstName","landlords[0].lastName",
    "tenants[0].firstName","tenants[0].lastName",
    "property.street","property.houseNumber",
    "property.postalCode","property.city",
    "property.roomNumber","property.livingArea",
    "rentalPeriod.startDate","rent.coldRent",
  ],

  defaultHouseRules: {
    noSmoking: true, quietHours: true, sharedKitchen: true,
    sharedBathroom: true, visitorRules: true,
    wasteSeparation: true, noSubletting: true,
  },

  defaultSharedAreas: {
    kitchen: true, bathroom: true, toilet: true, laundry: true,
  },

  defaultInventoryFurnished: () => [
    { id: uid(), name: "Bett", quantity: 1, condition: "gut", notes: "", replacementValue: "", room: "zimmer" },
    { id: uid(), name: "Matratze", quantity: 1, condition: "gut", notes: "", replacementValue: "", room: "zimmer" },
    { id: uid(), name: "Schreibtisch", quantity: 1, condition: "gut", notes: "", replacementValue: "", room: "zimmer" },
    { id: uid(), name: "Stuhl", quantity: 1, condition: "gut", notes: "", replacementValue: "", room: "zimmer" },
    { id: uid(), name: "Kleiderschrank", quantity: 1, condition: "gut", notes: "", replacementValue: "", room: "zimmer" },
    { id: uid(), name: "Regal", quantity: 1, condition: "gut", notes: "", replacementValue: "", room: "zimmer" },
  ],

  defaultInventoryUnfurnished: () => [],

  clauses: {
    mietobjekt: `Das Mietobjekt ist ein möbliertes/unmöbliertes WG-Zimmer in einer Wohngemeinschaft. Die Gemeinschaftsräume (Küche, Bad, Flur) werden gemeinsam mit weiteren Mitbewohnern genutzt.`,
    nutzung: `Der Mieter darf das Zimmer ausschließlich zu Wohnzwecken nutzen. Eine gewerbliche Nutzung ist nicht gestattet.`,
    nebenkosten: `Die Nebenkosten sind als Pauschale vereinbart und umfassen anteilige Kosten für Heizung, Wasser, Strom und Internet gemäß gesonderter Aufstellung.`,
    kaution: `Die Kaution ist bei Mietbeginn in voller Höhe fällig und wird auf einem gesonderten Kautionskonto des Vermieters verwahrt. Die Rückzahlung erfolgt innerhalb von 3 Monaten nach Beendigung des Mietverhältnisses und vollständiger Schlüsselrückgabe, abzüglich berechtigter Forderungen.`,
    kündigung: `Die Kündigung bedarf der Schriftform. Die gesetzliche Kündigungsfrist beträgt für den Mieter drei Monate zum Monatsende, sofern nicht anders vereinbart.`,
    schönheitsreparaturen: `Der Mieter ist verpflichtet, das Zimmer in dem Zustand zurückzugeben, in dem er es übernommen hat, unter Berücksichtigung normaler Abnutzung. Schäden, die über normale Abnutzung hinausgehen, sind vom Mieter zu beheben oder zu ersetzen.`,
    untervermietung: `Eine Untervermietung des Zimmers oder von Teilen davon ist ohne ausdrückliche schriftliche Genehmigung des Vermieters nicht gestattet.`,
    tierhaltung: `Die Haltung von Haustieren (ausgenommen Kleintiere wie Fische oder Hamster) bedarf der schriftlichen Zustimmung des Vermieters und der übrigen Mitbewohner.`,
    allgemeinesPflichten: `Der Mieter ist verpflichtet:\n1. Das Mietobjekt pfleglich zu behandeln.\n2. Gemeinschaftsräume sauber und ordentlich zu hinterlassen.\n3. Schäden unverzüglich dem Vermieter zu melden.\n4. Die Hausordnung einzuhalten.\n5. Die Miete pünktlich zu zahlen.`,
  },

  documents: [
    "mietvertrag","uebergabeprotokoll","schluesselprotokoll",
    "inventarliste","hausordnung","wohnungsgeberbestaetigung",
  ],
};

export default wgSchema;
