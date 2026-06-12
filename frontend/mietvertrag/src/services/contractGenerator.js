/**
 * Contract Generator Service
 *
 * Transforms a form state object into structured document models.
 * Each document model is a plain JS object — an array of sections,
 * each section containing typed content blocks.
 *
 * The PDF generator (pdfGenerator.js, Batch 4) consumes these models.
 * This file contains NO rendering or PDF logic — only data transformation.
 *
 * Supported document types:
 *   mietvertrag            Main rental contract
 *   uebergabeprotokoll     Handover protocol
 *   schluesselprotokoll    Key handover protocol
 *   inventarliste          Inventory list
 *   hausordnung            House rules document
 *   wohnungsgeberbestaetigung  Registration confirmation
 *   kuendigungsformular    Termination form
 *   mietbescheinigung      Rent certificate
 */

import { calcWarmmiete, calcDeposit, depositLabel } from "../utils/calcRent.js";
import { fmt, formatDate, formatEur } from "../utils/formatting.js";
import { loadSchema } from "../schemas/index.js";
import { getContractType } from "../constants/contractTypes.js";

// ── Internal helpers ───────────────────────────────────────────

function fullName(person) {
  return `${person.firstName} ${person.lastName}`.trim() || "—";
}

function personBlock(person, role, index) {
  const lines = [
    `${role} ${index + 1}: ${fullName(person)}`,
  ];
  if (person.dob)           lines.push(`Geburtsdatum: ${formatDate(person.dob)}`);
  if (person.placeOfBirth)  lines.push(`Geburtsort: ${fmt(person.placeOfBirth)}`);
  if (person.nationality)   lines.push(`Staatsangehörigkeit: ${fmt(person.nationality)}`);
  if (person.idNumber)      lines.push(`Ausweis-Nr.: ${fmt(person.idNumber)}`);
  if (person.passportNumber) lines.push(`Reisepass-Nr.: ${fmt(person.passportNumber)}`);
  const address = role === "Mieter" ? person.currentAddress : person.address;
  if (address)              lines.push(`Adresse: ${fmt(address)}`);
  if (person.email)         lines.push(`E-Mail: ${fmt(person.email)}`);
  if (person.phone)         lines.push(`Telefon: ${fmt(person.phone)}`);
  if (person.company)       lines.push(`Unternehmen: ${fmt(person.company)}`);
  if (person.legalRepresentative)
    lines.push(`Vertreten durch: ${fmt(person.legalRepresentative)}`);
  return lines;
}

function propertyAddress(property) {
  return `${fmt(property.street)} ${fmt(property.houseNumber)}, ${fmt(property.postalCode)} ${fmt(property.city)}`;
}

function noticePeriodLabel(rentalPeriod) {
  const map = {
    "2weeks":  "2 Wochen",
    "1month":  "1 Monat",
    "3months": "3 Monate",
  };
  return map[rentalPeriod.noticePeriod] || fmt(rentalPeriod.customNotice);
}

function minStayLabel(rentalPeriod) {
  const map = {
    "none":     "Keine Mindestmietdauer",
    "3months":  "3 Monate",
    "6months":  "6 Monate",
    "12months": "12 Monate",
  };
  return map[rentalPeriod.minStay] || fmt(rentalPeriod.customMinStay);
}

// ── Block type constructors ────────────────────────────────────
// These return typed content block objects consumed by the PDF renderer.

function heading(text, level = 1) {
  return { type: "heading", level, text };
}

function paragraph(text) {
  return { type: "paragraph", text };
}

function list(items) {
  return { type: "list", items };
}

function table(headers, rows) {
  return { type: "table", headers, rows };
}

function signatureLine(label, date = true) {
  return { type: "signature", label, date };
}

function pageBreak() {
  return { type: "pageBreak" };
}

function spacer() {
  return { type: "spacer" };
}

function legalNotice() {
  return {
    type: "legalNotice",
    text:
      "Rechtlicher Hinweis: Dieses Dokument wurde mit dem Mietvertrag Generator von MyContentPilot.de erstellt. " +
      "Es stellt keine Rechtsberatung dar. Bei besonderen rechtlichen Anforderungen sollte ein Rechtsanwalt " +
      "oder Mieterverein konsultiert werden.",
  };
}

// ── KEY TYPE LABELS ────────────────────────────────────────────

const KEY_LABELS = {
  wohnungsschluessel: "Wohnungsschlüssel",
  hausschluessel:     "Hausschlüssel",
  zimmerschluessel:   "Zimmerschlüssel",
  briefkastenschluessel: "Briefkastenschlüssel",
  kellerschluessel:   "Kellerschlüssel",
  garagenschluessel:  "Garagenschlüssel",
  muellchipkarte:     "Müll-Chipkarte",
};

// ══════════════════════════════════════════════════════════════
// DOCUMENT: Mietvertrag (main contract)
// ══════════════════════════════════════════════════════════════

export function generateMietvertrag(form) {
  const ct = getContractType(form.contractTypeId);
  const schema = ct ? loadSchema(ct.schemaId) : null;
  const clauses = schema?.clauses || {};
  const warm = calcWarmmiete(form.rent);
  const deposit = calcDeposit(form.deposit, form.rent.coldRent);

  const sections = [];

  // Cover info
  sections.push({
    id: "title",
    blocks: [
      heading("MIETVERTRAG", 1),
      paragraph(`Vertragsart: ${ct?.label || "Mietvertrag"}`),
      paragraph(
        `Erstellt am: ${formatDate(form.contractDate)} in ${fmt(form.contractPlace)}`
      ),
    ],
  });

  // § 1 Vertragsparteien
  sections.push({
    id: "parteien",
    title: "§ 1 Vertragsparteien",
    blocks: [
      heading("§ 1 Vertragsparteien", 2),
      heading("Vermieter", 3),
      ...form.landlords.map((l, i) =>
        list(personBlock(l, "Vermieter", i))
      ),
      spacer(),
      heading("Mieter", 3),
      ...form.tenants.map((t, i) =>
        list(personBlock(t, "Mieter", i))
      ),
    ],
  });

  // § 2 Mietobjekt
  const propBlocks = [
    heading("§ 2 Mietobjekt", 2),
    paragraph(clauses.mietobjekt || ""),
    spacer(),
    list([
      `Adresse: ${propertyAddress(form.property)}`,
      form.property.floor         ? `Etage: ${fmt(form.property.floor)}`            : null,
      form.property.apartmentNumber ? `Wohnungs-Nr.: ${fmt(form.property.apartmentNumber)}` : null,
      form.property.roomNumber    ? `Zimmer-Nr.: ${fmt(form.property.roomNumber)}`  : null,
      form.property.livingArea    ? `Wohnfläche: ${fmt(form.property.livingArea)} m²` : null,
      form.property.totalArea     ? `Gesamtfläche: ${fmt(form.property.totalArea)} m²` : null,
      form.property.buildingYear  ? `Baujahr: ${fmt(form.property.buildingYear)}`  : null,
      form.property.hasBalcony    ? "Balkon: Ja"    : null,
      form.property.hasTerrace    ? "Terrasse: Ja"  : null,
      form.property.hasGarden     ? "Garten: Ja"    : null,
      form.property.hasBasement   ? "Keller: Ja"    : null,
      form.property.hasGarage     ? "Garage: Ja"    : null,
      form.property.hasParking    ? "Stellplatz: Ja": null,
    ].filter(Boolean)),
  ];
  sections.push({ id: "mietobjekt", title: "§ 2 Mietobjekt", blocks: propBlocks });

  // § 3 Mietzeit
  const periodBlocks = [
    heading("§ 3 Mietzeit", 2),
    list([
      `Einzugsdatum: ${formatDate(form.rentalPeriod.moveInDate)}`,
      `Mietbeginn: ${formatDate(form.rentalPeriod.startDate)}`,
      form.rentalPeriod.isFixedTerm
        ? `Befristung: Ja, bis ${formatDate(form.rentalPeriod.endDate)}`
        : "Befristung: Unbefristet",
      form.rentalPeriod.isFixedTerm && form.rentalPeriod.fixedTermReason
        ? `Befristungsgrund: ${fmt(form.rentalPeriod.fixedTermReason)}`
        : null,
      `Mindestmietdauer: ${minStayLabel(form.rentalPeriod)}`,
      `Kündigungsfrist: ${noticePeriodLabel(form.rentalPeriod)}`,
    ].filter(Boolean)),
    spacer(),
    paragraph(clauses.kündigung || ""),
  ];
  sections.push({ id: "mietzeit", title: "§ 3 Mietzeit", blocks: periodBlocks });

  // § 4 Miete und Nebenkosten
  const rentRows = [
    ["Kaltmiete", formatEur(form.rent.coldRent)],
    form.rent.furnitureSurcharge && parseFloat(form.rent.furnitureSurcharge) > 0
      ? ["Möblierungszuschlag", formatEur(form.rent.furnitureSurcharge)] : null,
    form.rent.utilities && parseFloat(form.rent.utilities) > 0
      ? ["Nebenkosten (Vorauszahlung)", formatEur(form.rent.utilities)] : null,
    form.rent.heating && parseFloat(form.rent.heating) > 0
      ? ["Heizkosten", formatEur(form.rent.heating)] : null,
    form.rent.water && parseFloat(form.rent.water) > 0
      ? ["Wasserkosten", formatEur(form.rent.water)] : null,
    form.rent.electricity && parseFloat(form.rent.electricity) > 0
      ? ["Strom", formatEur(form.rent.electricity)] : null,
    form.rent.internet && parseFloat(form.rent.internet) > 0
      ? ["Internet", formatEur(form.rent.internet)] : null,
    form.rent.gez && parseFloat(form.rent.gez) > 0
      ? ["Rundfunkbeitrag (GEZ)", formatEur(form.rent.gez)] : null,
    form.rent.cleaning && parseFloat(form.rent.cleaning) > 0
      ? ["Reinigung", formatEur(form.rent.cleaning)] : null,
    form.rent.housemaster && parseFloat(form.rent.housemaster) > 0
      ? ["Hausmeister", formatEur(form.rent.housemaster)] : null,
    form.rent.parking && parseFloat(form.rent.parking) > 0
      ? ["Stellplatz", formatEur(form.rent.parking)] : null,
    form.rent.otherCosts && parseFloat(form.rent.otherCosts) > 0
      ? [form.rent.otherCostsLabel || "Sonstige Kosten", formatEur(form.rent.otherCosts)] : null,
    ["Warmmiete (gesamt)", formatEur(warm)],
  ].filter(Boolean);

  sections.push({
    id: "miete",
    title: "§ 4 Miete und Nebenkosten",
    blocks: [
      heading("§ 4 Miete und Nebenkosten", 2),
      paragraph(clauses.nebenkosten || ""),
      spacer(),
      table(["Kostenart", "Betrag / Monat"], rentRows),
      spacer(),
      paragraph(
        `Die Miete ist monatlich im Voraus, spätestens am ${fmt(form.rent.paymentDayOfMonth)}. Werktag des Monats zu zahlen.`
      ),
    ],
  });

  // § 5 Bankverbindung
  if (form.bank.iban) {
    sections.push({
      id: "bank",
      title: "§ 5 Bankverbindung",
      blocks: [
        heading("§ 5 Bankverbindung des Vermieters", 2),
        list([
          `Kontoinhaber: ${fmt(form.bank.accountHolder)}`,
          `IBAN: ${fmt(form.bank.iban)}`,
          form.bank.bic      ? `BIC: ${fmt(form.bank.bic)}`           : null,
          form.bank.bankName ? `Bank: ${fmt(form.bank.bankName)}`      : null,
          form.bank.referenceText
            ? `Verwendungszweck: ${fmt(form.bank.referenceText)}` : null,
        ].filter(Boolean)),
      ],
    });
  }

  // § 6 Kaution
  sections.push({
    id: "kaution",
    title: "§ 6 Kaution",
    blocks: [
      heading("§ 6 Kaution", 2),
      paragraph(clauses.kaution || ""),
      spacer(),
      list([
        `Kautionsbetrag: ${depositLabel(form.deposit, form.rent.coldRent)}`,
        form.deposit.installments
          ? `Ratenzahlung: ${fmt(form.deposit.installmentCount)} Raten`
          : "Zahlung: In einer Summe",
        form.deposit.dueDate
          ? `Fälligkeitsdatum: ${formatDate(form.deposit.dueDate)}`
          : null,
      ].filter(Boolean)),
    ],
  });

  // § 7 Hausordnung (conditional)
  const activeRules = [];
  if (form.houseRules.noSmoking)         activeRules.push("Rauchverbot in der gesamten Wohnung/dem gesamten Zimmer.");
  if (form.houseRules.noShisha)          activeRules.push("Shisha-Rauchen ist nicht gestattet.");
  if (form.houseRules.noPets)            activeRules.push("Tierhaltung ist ohne Genehmigung des Vermieters nicht erlaubt.");
  if (form.houseRules.quietHours)
    activeRules.push(
      `Ruhezeiten: ${form.houseRules.quietHoursFrom} – ${form.houseRules.quietHoursTo} Uhr und 13:00 – 15:00 Uhr (Mittagsruhe).`
    );
  if (form.houseRules.visitorRules)      activeRules.push("Besucher dürfen nicht dauerhaft in der Wohnung verbleiben.");
  if (form.houseRules.noOvernightGuests) activeRules.push("Übernachtungsgäste sind nur nach Absprache gestattet.");
  if (form.houseRules.cleaningRota)      activeRules.push("Ein Reinigungsplan für Gemeinschaftsbereiche ist einzuhalten.");
  if (form.houseRules.wasteSeparation)   activeRules.push("Mülltrennung gemäß kommunaler Vorgaben ist verpflichtend.");
  if (form.houseRules.mailHandling)      activeRules.push("Post anderer Mieter ist unberührt zu lassen oder weiterzuleiten.");
  if (form.houseRules.noSubletting)      activeRules.push("Untervermietung ist ohne schriftliche Genehmigung untersagt.");
  if (form.houseRules.customRules)       activeRules.push(form.houseRules.customRules);

  if (activeRules.length > 0) {
    sections.push({
      id: "hausordnung",
      title: "§ 7 Hausordnung",
      blocks: [
        heading("§ 7 Hausordnung", 2),
        list(activeRules),
      ],
    });
  }

  // § 8 Gemeinschaftsbereiche (conditional on shared areas)
  const sharedList = Object.entries(form.sharedAreas)
    .filter(([, v]) => v)
    .map(([k]) => {
      const map = {
        kitchen: "Küche", bathroom: "Badezimmer", toilet: "WC",
        laundry: "Waschküche", storage: "Abstellraum",
        balcony: "Balkon", garden: "Garten",
      };
      return map[k] || k;
    });

  if (sharedList.length > 0) {
    sections.push({
      id: "gemeinschaft",
      title: "§ 8 Gemeinschaftsbereiche",
      blocks: [
        heading("§ 8 Gemeinschaftsbereiche", 2),
        paragraph("Folgende Bereiche werden gemeinschaftlich genutzt:"),
        list(sharedList),
      ],
    });
  }

  // § 9 Inventar (conditional)
  if (form.inventory.length > 0) {
    const invRows = form.inventory.map((item) => [
      fmt(item.name),
      String(item.quantity),
      item.condition,
      fmt(item.notes),
    ]);
    sections.push({
      id: "inventar",
      title: "§ 9 Inventar",
      blocks: [
        heading("§ 9 Inventar / Ausstattung", 2),
        table(
          ["Gegenstand", "Anzahl", "Zustand", "Anmerkungen"],
          invRows
        ),
      ],
    });
  }

  // § 10 Sicherheit
  const safetyItems = [];
  if (form.safety.fireSafety)            safetyItems.push("Der Mieter ist verpflichtet, Brandschutzvorschriften einzuhalten.");
  if (form.safety.noOpenFlames)          safetyItems.push("Offene Flammen und Kerzen sind nicht gestattet.");
  if (form.safety.noCandles)             safetyItems.push("Kerzen dürfen nicht unbeaufsichtigt brennen.");
  if (form.safety.waterDamagePrevention) safetyItems.push("Wasserschäden sind durch regelmäßige Kontrolle von Wasserhähnen und Anschlüssen zu vermeiden.");
  if (form.safety.moldPrevention)        safetyItems.push("Zur Schimmelprävention ist regelmäßiges Lüften (3× täglich mind. 5 Minuten Stoßlüften) erforderlich.");

  if (safetyItems.length > 0) {
    sections.push({
      id: "sicherheit",
      title: "§ 10 Sicherheit",
      blocks: [
        heading("§ 10 Sicherheit und Obhutspflichten", 2),
        list(safetyItems),
      ],
    });
  }

  // § 11 Zutrittsrechte
  const accessItems = [];
  if (form.access.repairsAccess)       accessItems.push(`Für Reparaturen und Instandhaltungsarbeiten mit ${fmt(form.access.noticeDays)} Stunden Voranmeldung.`);
  if (form.access.inspectionAccess)    accessItems.push("Für regelmäßige Besichtigungen (max. 1× pro Jahr) nach Ankündigung.");
  if (form.access.saleViewings)        accessItems.push("Für Besichtigungen bei geplantem Verkauf des Mietobjekts.");
  if (form.access.newTenantViewings)   accessItems.push("Für Besichtigungen bei Nachmietersuche nach Kündigung.");

  if (accessItems.length > 0) {
    sections.push({
      id: "zutritt",
      title: "§ 11 Zutrittsrechte",
      blocks: [
        heading("§ 11 Zutrittsrechte des Vermieters", 2),
        paragraph("Der Vermieter ist berechtigt, das Mietobjekt zu betreten:"),
        list(accessItems),
      ],
    });
  }

  // § 12 Anmeldung / Wohnungsgeberbestätigung
  if (form.registration.wohnungsgeberbestaetigung) {
    sections.push({
      id: "anmeldung",
      title: "§ 12 Anmeldung",
      blocks: [
        heading("§ 12 Anmeldung und Wohnungsgeberbestätigung", 2),
        paragraph(
          "Der Vermieter stellt dem Mieter eine Wohnungsgeberbestätigung gemäß § 19 BMG aus. " +
          "Der Mieter ist verpflichtet, sich innerhalb von zwei Wochen nach Einzug beim zuständigen " +
          "Einwohnermeldeamt anzumelden."
        ),
      ],
    });
  }

  // § 13 Versicherung
  if (form.insurance.liabilityRequired) {
    sections.push({
      id: "versicherung",
      title: "§ 13 Versicherung",
      blocks: [
        heading("§ 13 Haftpflichtversicherung", 2),
        paragraph(
          "Der Mieter ist verpflichtet, für die Dauer des Mietverhältnisses eine private " +
          "Haftpflichtversicherung zu unterhalten und dem Vermieter auf Verlangen einen " +
          "entsprechenden Nachweis zu erbringen."
        ),
      ],
    });
  }

  // § 14 Allgemeine Bestimmungen
  sections.push({
    id: "allgemein",
    title: "§ 14 Allgemeine Bestimmungen",
    blocks: [
      heading("§ 14 Allgemeine Bestimmungen", 2),
      paragraph(clauses.allgemeinesPflichten || ""),
      spacer(),
      list([
        "Änderungen und Ergänzungen dieses Vertrages bedürfen der Schriftform.",
        "Sollten einzelne Bestimmungen dieses Vertrages unwirksam sein, berührt dies die Wirksamkeit der übrigen Bestimmungen nicht.",
        "Es gilt das Recht der Bundesrepublik Deutschland.",
        "Erfüllungsort und Gerichtsstand ist der Ort des Mietobjekts.",
      ]),
    ],
  });

  // § 15 Besondere Vereinbarungen (conditional)
  if (form.specialAgreements?.trim()) {
    sections.push({
      id: "besonderes",
      title: "§ 15 Besondere Vereinbarungen",
      blocks: [
        heading("§ 15 Besondere Vereinbarungen", 2),
        paragraph(form.specialAgreements),
      ],
    });
  }

  // Signatures
  sections.push({
    id: "unterschriften",
    title: "Unterschriften",
    blocks: [
      pageBreak(),
      heading("Unterschriften", 2),
      paragraph(`Ort, Datum: ${fmt(form.contractPlace)}, ${formatDate(form.contractDate)}`),
      spacer(),
      ...form.landlords.map((l) =>
        signatureLine(`Vermieter: ${fullName(l)}`)
      ),
      spacer(),
      ...form.tenants.map((t) =>
        signatureLine(`Mieter: ${fullName(t)}`)
      ),
      spacer(),
      legalNotice(),
    ],
  });

  return {
    type: "mietvertrag",
    title: `Mietvertrag – ${ct?.label || ""}`,
    contractTypeId: form.contractTypeId,
    generatedAt: new Date().toISOString(),
    sections,
  };
}

// ══════════════════════════════════════════════════════════════
// DOCUMENT: Übergabeprotokoll
// ══════════════════════════════════════════════════════════════

export function generateUebergabeprotokoll(form) {
  const ct = getContractType(form.contractTypeId);

  return {
    type: "uebergabeprotokoll",
    title: "Übergabeprotokoll",
    generatedAt: new Date().toISOString(),
    sections: [
      {
        id: "header",
        blocks: [
          heading("ÜBERGABEPROTOKOLL", 1),
          paragraph(`Mietobjekt: ${propertyAddress(form.property)}`),
          paragraph(`Vertragsart: ${ct?.label || ""}`),
          spacer(),
          list([
            `Vermieter: ${form.landlords.map((l) => fullName(l)).join(", ")}`,
            `Mieter: ${form.tenants.map((t) => fullName(t)).join(", ")}`,
            `Übergabedatum: ___________________________`,
            `Uhrzeit: ___________________________`,
          ]),
        ],
      },
      {
        id: "zähler",
        title: "Zählerstände",
        blocks: [
          heading("Zählerstände bei Übergabe", 2),
          table(
            ["Zählerart", "Zählernummer", "Stand", "Einheit"],
            [
              ["Strom", "", "", "kWh"],
              ["Gas",   "", "", "m³"],
              ["Wasser (kalt)", "", "", "m³"],
              ["Wasser (warm)", "", "", "m³"],
              ["Heizung", "", "", ""],
            ]
          ),
        ],
      },
      {
        id: "raeume",
        title: "Zustand der Räume",
        blocks: [
          heading("Zustand der Räume", 2),
          table(
            ["Raum", "Wände/Decke", "Boden", "Fenster/Türen", "Bemerkungen"],
            [
              ["Zimmer / Wohnbereich", "", "", "", ""],
              ["Küche",               "", "", "", ""],
              ["Badezimmer",          "", "", "", ""],
              ["WC",                  "", "", "", ""],
              ["Flur/Diele",          "", "", "", ""],
              ["Keller",              "", "", "", ""],
              ["Sonstiges",           "", "", "", ""],
            ]
          ),
        ],
      },
      {
        id: "inventar",
        title: "Inventarübergabe",
        blocks: [
          heading("Inventarübergabe", 2),
          form.inventory.length > 0
            ? table(
                ["Gegenstand", "Anzahl", "Zustand bei Einzug", "Zustand bei Übergabe", "OK"],
                form.inventory.map((item) => [
                  fmt(item.name),
                  String(item.quantity),
                  item.condition,
                  "",
                  "☐",
                ])
              )
            : paragraph("Kein Inventar vereinbart."),
        ],
      },
      {
        id: "mängel",
        title: "Festgestellte Mängel",
        blocks: [
          heading("Festgestellte Mängel", 2),
          paragraph("Folgende Mängel wurden bei der Übergabe festgestellt:"),
          paragraph("1. ________________________________________"),
          paragraph("2. ________________________________________"),
          paragraph("3. ________________________________________"),
          paragraph("4. ________________________________________"),
        ],
      },
      {
        id: "unterschriften",
        blocks: [
          pageBreak(),
          heading("Unterschriften", 2),
          paragraph(
            "Beide Parteien bestätigen, das Protokoll gelesen und die Übergabe entsprechend durchgeführt zu haben."
          ),
          spacer(),
          ...form.landlords.map((l) => signatureLine(`Vermieter: ${fullName(l)}`)),
          spacer(),
          ...form.tenants.map((t) => signatureLine(`Mieter: ${fullName(t)}`)),
          spacer(),
          legalNotice(),
        ],
      },
    ],
  };
}

// ══════════════════════════════════════════════════════════════
// DOCUMENT: Schlüsselübergabeprotokoll
// ══════════════════════════════════════════════════════════════

export function generateSchluesselprotokoll(form) {
  const keyRows = form.keys.length > 0
    ? form.keys.map((k) => [
        KEY_LABELS[k.type] || fmt(k.type),
        String(k.quantity),
        fmt(k.notes),
        "___",
      ])
    : [
        ["Wohnungsschlüssel",    "___", "", "___"],
        ["Hausschlüssel",        "___", "", "___"],
        ["Briefkastenschlüssel", "___", "", "___"],
        ["Kellerschlüssel",      "___", "", "___"],
      ];

  return {
    type: "schluesselprotokoll",
    title: "Schlüsselübergabeprotokoll",
    generatedAt: new Date().toISOString(),
    sections: [
      {
        id: "header",
        blocks: [
          heading("SCHLÜSSELÜBERGABEPROTOKOLL", 1),
          paragraph(`Mietobjekt: ${propertyAddress(form.property)}`),
          spacer(),
          list([
            `Vermieter: ${form.landlords.map((l) => fullName(l)).join(", ")}`,
            `Mieter: ${form.tenants.map((t) => fullName(t)).join(", ")}`,
            `Übergabedatum: ___________________________`,
          ]),
        ],
      },
      {
        id: "schluessel",
        blocks: [
          heading("Übergebene Schlüssel", 2),
          table(
            ["Schlüsselart", "Anzahl", "Anmerkungen", "Quittung (Unterschrift)"],
            keyRows
          ),
          spacer(),
          paragraph(
            "Der Mieter bestätigt den Empfang der oben aufgeführten Schlüssel. " +
            "Bei Verlust eines Schlüssels trägt der Mieter die Kosten für den Austausch " +
            "der gesamten Schließanlage."
          ),
        ],
      },
      {
        id: "unterschriften",
        blocks: [
          spacer(),
          ...form.landlords.map((l) => signatureLine(`Vermieter: ${fullName(l)}`)),
          spacer(),
          ...form.tenants.map((t) => signatureLine(`Mieter: ${fullName(t)}`)),
          spacer(),
          legalNotice(),
        ],
      },
    ],
  };
}

// ══════════════════════════════════════════════════════════════
// DOCUMENT: Inventarliste (standalone)
// ══════════════════════════════════════════════════════════════

export function generateInventarliste(form) {
  const grouped = { zimmer: [], gemeinschaft: [], wohnung: [] };
  for (const item of form.inventory) {
    const g = grouped[item.room] || grouped.wohnung;
    g.push(item);
  }

  const sectionBlocks = (label, items) => {
    if (items.length === 0) return [];
    return [
      heading(label, 3),
      table(
        ["Gegenstand", "Anzahl", "Zustand", "Zeitwert (€)", "Anmerkungen"],
        items.map((item) => [
          fmt(item.name),
          String(item.quantity),
          item.condition,
          fmt(item.replacementValue),
          fmt(item.notes),
        ])
      ),
      spacer(),
    ];
  };

  return {
    type: "inventarliste",
    title: "Inventarliste",
    generatedAt: new Date().toISOString(),
    sections: [
      {
        id: "header",
        blocks: [
          heading("INVENTARLISTE", 1),
          paragraph(`Mietobjekt: ${propertyAddress(form.property)}`),
          paragraph(`Mieter: ${form.tenants.map((t) => fullName(t)).join(", ")}`),
          spacer(),
        ],
      },
      {
        id: "items",
        blocks: [
          ...sectionBlocks("Zimmer / Privatbereich", grouped.zimmer),
          ...sectionBlocks("Gemeinschaftsbereiche", grouped.gemeinschaft),
          ...sectionBlocks("Gesamte Wohnung", grouped.wohnung),
          form.inventory.length === 0
            ? paragraph("Kein Inventar erfasst.")
            : spacer(),
        ],
      },
      {
        id: "unterschriften",
        blocks: [
          heading("Bestätigung", 2),
          paragraph(
            "Beide Parteien bestätigen die Richtigkeit der Inventarliste."
          ),
          spacer(),
          ...form.landlords.map((l) => signatureLine(`Vermieter: ${fullName(l)}`)),
          spacer(),
          ...form.tenants.map((t) => signatureLine(`Mieter: ${fullName(t)}`)),
          spacer(),
          legalNotice(),
        ],
      },
    ],
  };
}

// ══════════════════════════════════════════════════════════════
// DOCUMENT: Wohnungsgeberbestätigung
// ══════════════════════════════════════════════════════════════

export function generateWohnungsgeberbestaetigung(form) {
  const landlord = form.landlords[0] || {};
  const tenant = form.tenants[0] || {};

  return {
    type: "wohnungsgeberbestaetigung",
    title: "Wohnungsgeberbestätigung",
    generatedAt: new Date().toISOString(),
    sections: [
      {
        id: "content",
        blocks: [
          heading("WOHNUNGSGEBERBESTÄTIGUNG", 1),
          paragraph("gemäß § 19 Bundesmeldegesetz (BMG)"),
          spacer(),
          heading("Angaben zum Wohnungsgeber", 2),
          list([
            `Name: ${fullName(landlord)}`,
            `Adresse: ${fmt(landlord.address)}`,
            `Telefon: ${fmt(landlord.phone)}`,
            `E-Mail: ${fmt(landlord.email)}`,
          ]),
          spacer(),
          heading("Angaben zur Wohnung", 2),
          list([
            `Anschrift: ${propertyAddress(form.property)}`,
            form.property.floor ? `Etage: ${fmt(form.property.floor)}` : null,
            form.property.apartmentNumber
              ? `Wohnungs-Nr.: ${fmt(form.property.apartmentNumber)}`
              : null,
          ].filter(Boolean)),
          spacer(),
          heading("Angaben zum Einziehenden", 2),
          list([
            `Name: ${fullName(tenant)}`,
            `Geburtsdatum: ${formatDate(tenant.dob)}`,
            `Bisherige Adresse: ${fmt(tenant.currentAddress)}`,
          ]),
          spacer(),
          list([
            `Einzugsdatum: ${formatDate(form.rentalPeriod.moveInDate || form.rentalPeriod.startDate)}`,
          ]),
          spacer(),
          paragraph(
            "Der Wohnungsgeber bestätigt, dass die oben genannte Person in die angegebene " +
            "Wohnung eingezogen ist."
          ),
          spacer(),
          signatureLine(`Wohnungsgeber: ${fullName(landlord)}`),
          spacer(),
          legalNotice(),
        ],
      },
    ],
  };
}

// ══════════════════════════════════════════════════════════════
// DOCUMENT: Hausordnung (standalone)
// ══════════════════════════════════════════════════════════════

export function generateHausordnung(form) {
  const rules = [];
  if (form.houseRules.noSmoking)         rules.push("Rauchverbot: Das Rauchen in der Wohnung, im Zimmer und in allen Gemeinschaftsbereichen ist verboten.");
  if (form.houseRules.noShisha)          rules.push("Shisha: Das Rauchen von Shisha ist nicht gestattet.");
  if (form.houseRules.noPets)            rules.push("Tierhaltung: Haustiere sind nur mit ausdrücklicher schriftlicher Genehmigung des Vermieters erlaubt.");
  if (form.houseRules.quietHours)
    rules.push(`Ruhezeiten: Von ${form.houseRules.quietHoursFrom} bis ${form.houseRules.quietHoursTo} Uhr sowie von 13:00 bis 15:00 Uhr (Mittagsruhe) ist auf Lärm zu verzichten.`);
  if (form.houseRules.visitorRules)      rules.push("Besucher: Besucher dürfen nicht dauerhaft in der Wohnung leben oder übernachten.");
  if (form.houseRules.noOvernightGuests) rules.push("Übernachtungsgäste: Nur nach vorheriger Absprache mit dem Vermieter gestattet.");
  if (form.houseRules.cleaningRota)      rules.push("Reinigung: Gemeinschaftsbereiche sind nach dem ausgehängten Reinigungsplan zu pflegen.");
  if (form.houseRules.wasteSeparation)   rules.push("Mülltrennung: Abfall ist gemäß den kommunalen Vorgaben zu trennen. Sperrmüll ist nicht im Hausflur zu lagern.");
  if (form.houseRules.mailHandling)      rules.push("Post: Post anderer Bewohner ist unberührt zu lassen und nicht zu öffnen.");
  if (form.houseRules.noSubletting)      rules.push("Untervermietung: Eine Weitervermietung oder Untervermietung ist ohne schriftliche Genehmigung verboten.");
  if (form.houseRules.customRules)       rules.push(form.houseRules.customRules);

  return {
    type: "hausordnung",
    title: "Hausordnung",
    generatedAt: new Date().toISOString(),
    sections: [
      {
        id: "content",
        blocks: [
          heading("HAUSORDNUNG", 1),
          paragraph(`Mietobjekt: ${propertyAddress(form.property)}`),
          spacer(),
          rules.length > 0
            ? list(rules)
            : paragraph("Keine besonderen Hausordnungsregeln vereinbart."),
          spacer(),
          paragraph(
            "Diese Hausordnung ist Bestandteil des Mietvertrages und für alle Bewohner verbindlich."
          ),
          spacer(),
          ...form.tenants.map((t) => signatureLine(`Mieter: ${fullName(t)}`)),
          spacer(),
          legalNotice(),
        ],
      },
    ],
  };
}

// ══════════════════════════════════════════════════════════════
// DOCUMENT: Kündigungsformular
// ══════════════════════════════════════════════════════════════

export function generateKuendigungsformular(form) {
  return {
    type: "kuendigungsformular",
    title: "Kündigungsformular",
    generatedAt: new Date().toISOString(),
    sections: [
      {
        id: "content",
        blocks: [
          heading("KÜNDIGUNG DES MIETVERHÄLTNISSES", 1),
          spacer(),
          paragraph("Absender (Mieter):"),
          list([
            `Name: ${form.tenants.map((t) => fullName(t)).join(" / ")}`,
            `Adresse des Mietobjekts: ${propertyAddress(form.property)}`,
          ]),
          spacer(),
          paragraph("Empfänger (Vermieter):"),
          list([
            `Name: ${form.landlords.map((l) => fullName(l)).join(" / ")}`,
            `Adresse: ${fmt(form.landlords[0]?.address)}`,
          ]),
          spacer(),
          heading("Kündigung", 2),
          paragraph(
            `hiermit kündige ich / kündigen wir das Mietverhältnis über die oben genannte Wohnung ` +
            `fristgerecht zum nächstmöglichen Termin, spätestens jedoch unter Einhaltung der ` +
            `vereinbarten Kündigungsfrist von ${noticePeriodLabel(form.rentalPeriod)}.`
          ),
          spacer(),
          paragraph("Ich / Wir bitten um schriftliche Bestätigung des Kündigungstermins."),
          spacer(),
          paragraph("Ort, Datum: ___________________________"),
          spacer(),
          ...form.tenants.map((t) => signatureLine(`Mieter: ${fullName(t)}`)),
          spacer(),
          legalNotice(),
        ],
      },
    ],
  };
}

// ══════════════════════════════════════════════════════════════
// DOCUMENT: Mietbescheinigung
// ══════════════════════════════════════════════════════════════

export function generateMietbescheinigung(form) {
  const warm = calcWarmmiete(form.rent);

  return {
    type: "mietbescheinigung",
    title: "Mietbescheinigung",
    generatedAt: new Date().toISOString(),
    sections: [
      {
        id: "content",
        blocks: [
          heading("MIETBESCHEINIGUNG", 1),
          spacer(),
          paragraph("Der Vermieter bestätigt hiermit:"),
          spacer(),
          list([
            `Mieter: ${form.tenants.map((t) => fullName(t)).join(", ")}`,
            `Mietobjekt: ${propertyAddress(form.property)}`,
            `Mietbeginn: ${formatDate(form.rentalPeriod.startDate)}`,
            form.rentalPeriod.isFixedTerm
              ? `Mietende: ${formatDate(form.rentalPeriod.endDate)}`
              : "Befristung: Unbefristet",
            `Kaltmiete: ${formatEur(form.rent.coldRent)} / Monat`,
            `Warmmiete: ${formatEur(warm)} / Monat`,
          ]),
          spacer(),
          paragraph(
            "Diese Bescheinigung wird auf Wunsch des Mieters ausgestellt und dient als " +
            "Nachweis des bestehenden Mietverhältnisses (z.B. für Behörden, Banken, Jobcenter)."
          ),
          spacer(),
          paragraph(`Ausgestellt am: ${formatDate(form.contractDate)}`),
          spacer(),
          ...form.landlords.map((l) => signatureLine(`Vermieter: ${fullName(l)}`)),
          spacer(),
          legalNotice(),
        ],
      },
    ],
  };
}

// ══════════════════════════════════════════════════════════════
// MASTER: Generate all documents for a contract type
// ══════════════════════════════════════════════════════════════

const GENERATORS = {
  mietvertrag:               generateMietvertrag,
  uebergabeprotokoll:        generateUebergabeprotokoll,
  schluesselprotokoll:       generateSchluesselprotokoll,
  inventarliste:             generateInventarliste,
  hausordnung:               generateHausordnung,
  wohnungsgeberbestaetigung: generateWohnungsgeberbestaetigung,
  kuendigungsformular:       generateKuendigungsformular,
  mietbescheinigung:         generateMietbescheinigung,
};

/**
 * Generate one specific document.
 * @param {string} docType - e.g. "mietvertrag"
 * @param {object} form    - current form state
 * @returns document model object
 */
export function generateDocument(docType, form) {
  const gen = GENERATORS[docType];
  if (!gen) throw new Error(`Unknown document type: ${docType}`);
  return gen(form);
}

/**
 * Generate all documents available for the current contract type.
 * @param {object} form - current form state
 * @returns Array of document model objects
 */
export function generateAllDocuments(form) {
  const ct = getContractType(form.contractTypeId);
  const schema = ct ? loadSchema(ct.schemaId) : null;
  const docTypes = schema?.documents || ["mietvertrag"];

  return docTypes
    .map((docType) => {
      try {
        return generateDocument(docType, form);
      } catch (e) {
        console.error(`Failed to generate ${docType}:`, e);
        return null;
      }
    })
    .filter(Boolean);
}

export default {
  generateDocument,
  generateAllDocuments,
  generateMietvertrag,
  generateUebergabeprotokoll,
  generateSchluesselprotokoll,
  generateInventarliste,
  generateHausordnung,
  generateWohnungsgeberbestaetigung,
  generateKuendigungsformular,
  generateMietbescheinigung,
};
