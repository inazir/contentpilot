import { uid } from "../utils/uid.js";
import { todayIso } from "../utils/formatting.js";

// ── Entity factories ───────────────────────────────────────────

export function emptyLandlord() {
  return {
    id: uid(),
    firstName: "",
    lastName: "",
    dob: "",
    placeOfBirth: "",
    nationality: "",
    passportNumber: "",
    idNumber: "",
    address: "",
    email: "",
    phone: "",
    company: "",
    legalRepresentative: "",
  };
}

export function emptyTenant() {
  return {
    id: uid(),
    firstName: "",
    lastName: "",
    dob: "",
    placeOfBirth: "",
    nationality: "",
    passportNumber: "",
    idNumber: "",
    currentAddress: "",
    email: "",
    phone: "",
    company: "",
    legalRepresentative: "",
  };
}

export function emptyInventoryItem() {
  return {
    id: uid(),
    name: "",
    quantity: 1,
    condition: "gut", // neu | gut | gebraucht | beschädigt
    notes: "",
    replacementValue: "",
    room: "zimmer", // zimmer | gemeinschaft | wohnung
  };
}

export function emptyKey() {
  return {
    id: uid(),
    type: "wohnungsschluessel",
    quantity: 1,
    notes: "",
  };
}

// ── Default form state ─────────────────────────────────────────

export function buildDefaultState(contractTypeId = "wg_furnished") {
  return {
    contractTypeId,
    contractPlace: "",
    contractDate: todayIso(),

    landlords: [emptyLandlord()],
    tenants: [emptyTenant()],

    property: {
      street: "",
      houseNumber: "",
      postalCode: "",
      city: "",
      state: "",
      country: "Deutschland",
      floor: "",
      apartmentNumber: "",
      roomNumber: "",
      livingArea: "",
      totalArea: "",
      buildingYear: "",
      hasBalcony: false,
      hasTerrace: false,
      hasGarden: false,
      hasBasement: false,
      hasGarage: false,
      hasParking: false,
    },

    rentalPeriod: {
      moveInDate: "",
      startDate: "",
      isFixedTerm: false,
      endDate: "",
      fixedTermReason: "",
      minStay: "none",
      customMinStay: "",
      noticePeriod: "3months",
      customNotice: "",
    },

    rent: {
      coldRent: "",
      furnitureSurcharge: "",
      utilities: "",
      heating: "",
      water: "",
      electricity: "",
      internet: "",
      gez: "",
      cleaning: "",
      housemaster: "",
      parking: "",
      otherCosts: "",
      otherCostsLabel: "",
      paymentDayOfMonth: "3",
    },

    bank: {
      accountHolder: "",
      iban: "",
      bic: "",
      bankName: "",
      referenceText: "",
    },

    deposit: {
      type: "twoMonths",
      customAmount: "",
      installments: false,
      installmentCount: "1",
      dueDate: "",
    },

    inventory: [],
    keys: [],

    sharedAreas: {
      kitchen: false,
      bathroom: false,
      toilet: false,
      laundry: false,
      storage: false,
      balcony: false,
      garden: false,
    },

    houseRules: {
      noSmoking: false,
      noShisha: false,
      noPets: false,
      quietHours: false,
      quietHoursFrom: "22:00",
      quietHoursTo: "08:00",
      visitorRules: false,
      noOvernightGuests: false,
      cleaningRota: false,
      wasteSeparation: false,
      mailHandling: false,
      noSubletting: true,
      customRules: "",
    },

    safety: {
      fireSafety: true,
      noOpenFlames: false,
      noCandles: false,
      waterDamagePrevention: true,
      moldPrevention: true,
    },

    registration: {
      wohnungsgeberbestaetigung: true,
      anmeldungRequired: true,
    },

    insurance: {
      liabilityRequired: false,
    },

    access: {
      repairsAccess: true,
      inspectionAccess: true,
      saleViewings: false,
      newTenantViewings: false,
      noticeDays: "24",
    },

    specialAgreements: "",
  };
}
