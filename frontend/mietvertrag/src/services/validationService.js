/**
 * Validation service.
 *
 * validateForm(form, schema, stepId?)
 *   → { valid: boolean, errors: { [fieldPath]: string } }
 *
 * If stepId is provided, only validates fields relevant to that step.
 * If stepId is omitted, validates all required fields.
 */

// Map wizard step IDs to the form field prefixes they own
const STEP_FIELD_MAP = {
  contractType:      [],
  landlords:         ["landlords"],
  tenants:           ["tenants"],
  property:          ["property"],
  rentalPeriod:      ["rentalPeriod"],
  rent:              ["rent"],
  bank:              ["bank"],
  deposit:           ["deposit"],
  inventory:         ["inventory"],
  keys:              ["keys"],
  sharedAreas:       ["sharedAreas"],
  houseRules:        ["houseRules"],
  safety:            ["safety"],
  registration:      ["registration"],
  insurance:         ["insurance"],
  access:            ["access"],
  specialAgreements: ["specialAgreements"],
  signatures:        ["contractPlace", "contractDate"],
};

/**
 * Resolve a dot-notation path against an object.
 * Supports array indexing: "landlords[0].firstName"
 */
function resolvePath(obj, path) {
  return path
    .replace(/\[(\d+)\]/g, ".$1")
    .split(".")
    .reduce((acc, key) => (acc != null ? acc[key] : undefined), obj);
}

/**
 * Validate a single field value.
 * Returns an error string or null.
 */
function validateField(value, path) {
  // All required fields must be non-empty strings or truthy values
  if (value === undefined || value === null || value === "") {
    return "Pflichtfeld – bitte ausfüllen.";
  }

  // IBAN format check
  if (path.endsWith(".iban") && value) {
    const clean = value.replace(/\s/g, "").toUpperCase();
    if (!/^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$/.test(clean)) {
      return "Ungültiges IBAN-Format.";
    }
  }

  // BIC format check
  if (path.endsWith(".bic") && value) {
    if (!/^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$/.test(value.toUpperCase())) {
      return "Ungültiges BIC-Format.";
    }
  }

  // Email format check
  if (path.endsWith(".email") && value) {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
      return "Ungültige E-Mail-Adresse.";
    }
  }

  // Postal code: German 5-digit
  if (path.endsWith(".postalCode") && value) {
    if (!/^\d{5}$/.test(value)) {
      return "Bitte gültige PLZ eingeben (5 Ziffern).";
    }
  }

  // Date must be a valid date string
  if (
    (path.endsWith("Date") || path.endsWith("date")) &&
    value &&
    isNaN(Date.parse(value))
  ) {
    return "Ungültiges Datum.";
  }

  // Numeric fields must be >= 0
  if (
    (path.includes("coldRent") ||
      path.includes("Rent") ||
      path.includes("Amount") ||
      path.includes("Area") ||
      path.includes("Surcharge")) &&
    value !== ""
  ) {
    const num = parseFloat(value);
    if (isNaN(num) || num < 0) {
      return "Bitte eine gültige Zahl eingeben.";
    }
  }

  return null;
}

/**
 * Main validation entry point.
 *
 * @param {object} form     - current form state
 * @param {object} schema   - schema for the active contract type
 * @param {string} [stepId] - if provided, only validate this step's fields
 * @returns {{ valid: boolean, errors: object }}
 */
export function validateForm(form, schema, stepId) {
  const errors = {};

  // Determine which required fields to check
  let fieldsToCheck = schema.requiredFields || [];

  if (stepId) {
    const prefixes = STEP_FIELD_MAP[stepId] || [];
    fieldsToCheck = fieldsToCheck.filter((fieldPath) =>
      prefixes.some((prefix) => fieldPath.startsWith(prefix))
    );
  }

  for (const path of fieldsToCheck) {
    const value = resolvePath(form, path);
    const error = validateField(value, path);
    if (error) {
      errors[path] = error;
    }
  }

  // Cross-field validation: if fixed term, endDate is required
  if (
    (!stepId || stepId === "rentalPeriod") &&
    form.rentalPeriod?.isFixedTerm &&
    !form.rentalPeriod?.endDate
  ) {
    errors["rentalPeriod.endDate"] =
      "Bei befristetem Vertrag ist ein Enddatum erforderlich.";
  }

  // Cross-field: endDate must be after startDate
  if (
    form.rentalPeriod?.isFixedTerm &&
    form.rentalPeriod?.startDate &&
    form.rentalPeriod?.endDate
  ) {
    if (
      new Date(form.rentalPeriod.endDate) <=
      new Date(form.rentalPeriod.startDate)
    ) {
      errors["rentalPeriod.endDate"] =
        "Enddatum muss nach dem Startdatum liegen.";
    }
  }

  // Cross-field: custom deposit amount required if type=custom
  if (
    (!stepId || stepId === "deposit") &&
    form.deposit?.type === "custom" &&
    !form.deposit?.customAmount
  ) {
    errors["deposit.customAmount"] =
      "Bitte individuelle Kautionshöhe angeben.";
  }

  // Cross-field: custom notice period text required if noticePeriod=custom
  if (
    (!stepId || stepId === "rentalPeriod") &&
    form.rentalPeriod?.noticePeriod === "custom" &&
    !form.rentalPeriod?.customNotice
  ) {
    errors["rentalPeriod.customNotice"] =
      "Bitte individuelle Kündigungsfrist angeben.";
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Validate a single field live (for inline field-level feedback).
 *
 * @param {string} path   - dot-notation field path
 * @param {*}      value  - current field value
 * @returns {string|null} - error message or null
 */
export function validateSingleField(path, value) {
  return validateField(value, path);
}

export default { validateForm, validateSingleField };
