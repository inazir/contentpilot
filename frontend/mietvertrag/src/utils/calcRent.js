/**
 * Rent calculation utilities.
 * Centralised so that both the form UI and document
 * generators produce consistent values.
 */

/**
 * Calculate Warmmiete (total monthly payment) from a rent object.
 * Accepts any rent object — unknown keys are ignored.
 */
export function calcWarmmiete(rent) {
  const fields = [
    "coldRent",
    "furnitureSurcharge",
    "utilities",
    "heating",
    "water",
    "electricity",
    "internet",
    "gez",
    "cleaning",
    "housemaster",
    "parking",
    "otherCosts",
  ];
  return fields.reduce((sum, key) => {
    const val = parseFloat(rent?.[key]);
    return sum + (isNaN(val) ? 0 : val);
  }, 0);
}

/**
 * Calculate deposit amount from deposit config + cold rent.
 * Returns a numeric value in EUR.
 */
export function calcDeposit(deposit, coldRent) {
  const base = parseFloat(coldRent) || 0;
  switch (deposit?.type) {
    case "oneMonth":
      return base;
    case "twoMonths":
      return base * 2;
    case "threeMonths":
      return base * 3;
    case "none":
      return 0;
    case "custom":
      return parseFloat(deposit.customAmount) || 0;
    default:
      return base * 2;
  }
}

/**
 * Return a human-readable deposit description string (German).
 */
export function depositLabel(deposit, coldRent) {
  const amount = calcDeposit(deposit, coldRent);
  const eur = amount.toLocaleString("de-DE", {
    style: "currency",
    currency: "EUR",
  });

  switch (deposit?.type) {
    case "none":
      return "Keine Kaution";
    case "oneMonth":
      return `${eur} (1 Monatsmiete)`;
    case "twoMonths":
      return `${eur} (2 Monatsmieten)`;
    case "threeMonths":
      return `${eur} (3 Monatsmieten)`;
    case "custom":
      return `${eur} (individuelle Kaution)`;
    default:
      return eur;
  }
}
