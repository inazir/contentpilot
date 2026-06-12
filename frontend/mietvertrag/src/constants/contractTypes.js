/**
 * Master registry of all supported contract types.
 * To add a new type: append one entry here.
 * The wizard, schema loader, and generator all read from this list.
 */

export const CONTRACT_TYPES = [
  // ── WG ──────────────────────────────────────────────────────
  {
    id: "wg_furnished",
    label: "WG Zimmer (möbliert)",
    group: "WG",
    icon: "🛏",
    schemaId: "wg",
    isFurnished: true,
    isShared: true,
  },
  {
    id: "wg_unfurnished",
    label: "WG Zimmer (unmöbliert)",
    group: "WG",
    icon: "🚪",
    schemaId: "wg",
    isFurnished: false,
    isShared: true,
  },

  // ── Wohnung ──────────────────────────────────────────────────
  {
    id: "apartment_furnished",
    label: "Möblierte Wohnung",
    group: "Wohnung",
    icon: "🏠",
    schemaId: "apartment",
    isFurnished: true,
    isShared: false,
  },
  {
    id: "apartment_unfurnished",
    label: "Unmöblierte Wohnung",
    group: "Wohnung",
    icon: "🏢",
    schemaId: "apartment",
    isFurnished: false,
    isShared: false,
  },

  // ── Haus ─────────────────────────────────────────────────────
  {
    id: "house",
    label: "Haus",
    group: "Haus",
    icon: "🏡",
    schemaId: "house",
    isFurnished: false,
    isShared: false,
  },

  // ── Nebengebäude / Sonderobjekte ─────────────────────────────
  {
    id: "garage",
    label: "Garage",
    group: "Sonderobjekte",
    icon: "🚗",
    schemaId: "garage",
    isFurnished: false,
    isShared: false,
  },
  {
    id: "stellplatz",
    label: "Stellplatz",
    group: "Sonderobjekte",
    icon: "🅿️",
    schemaId: "garage",
    isFurnished: false,
    isShared: false,
  },
  {
    id: "keller",
    label: "Kellerraum",
    group: "Sonderobjekte",
    icon: "🗄",
    schemaId: "storage",
    isFurnished: false,
    isShared: false,
  },
  {
    id: "lager",
    label: "Lagerraum",
    group: "Sonderobjekte",
    icon: "📦",
    schemaId: "storage",
    isFurnished: false,
    isShared: false,
  },

  // ── Gewerbe ──────────────────────────────────────────────────
  {
    id: "buero",
    label: "Büro",
    group: "Gewerbe",
    icon: "💼",
    schemaId: "commercial",
    isFurnished: false,
    isShared: false,
  },
  {
    id: "gewerberaum",
    label: "Gewerberaum",
    group: "Gewerbe",
    icon: "🏪",
    schemaId: "commercial",
    isFurnished: false,
    isShared: false,
  },

  // ── Spezialverträge ──────────────────────────────────────────
  {
    id: "zwischenmiete",
    label: "Zwischenmiete",
    group: "Spezialverträge",
    icon: "⏱",
    schemaId: "zwischenmiete",
    isFurnished: true,
    isShared: false,
  },
  {
    id: "untervermietung",
    label: "Untervermietung",
    group: "Spezialverträge",
    icon: "🔑",
    schemaId: "untervermietung",
    isFurnished: false,
    isShared: true,
  },
  {
    id: "studentenwohnheim",
    label: "Studentenwohnheim",
    group: "Spezialverträge",
    icon: "🎓",
    schemaId: "wg",
    isFurnished: true,
    isShared: true,
  },
];

/** Helper: get a contract type definition by id */
export function getContractType(id) {
  return CONTRACT_TYPES.find((t) => t.id === id) || null;
}

/** Helper: group contract types for the selection UI */
export function getContractTypeGroups() {
  const groups = {};
  for (const ct of CONTRACT_TYPES) {
    if (!groups[ct.group]) groups[ct.group] = [];
    groups[ct.group].push(ct);
  }
  return groups;
}
