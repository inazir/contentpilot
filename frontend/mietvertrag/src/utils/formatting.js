/**
 * Shared formatting utilities used across the application.
 */

/** Format a value for display — returns em dash if empty/nullish */
export function fmt(v) {
  if (v === null || v === undefined || v === "") return "—";
  return String(v);
}

/** Format a number as Euro currency string */
export function formatEur(value) {
  const num = parseFloat(value);
  if (isNaN(num)) return "0,00 €";
  return num.toLocaleString("de-DE", {
    style: "currency",
    currency: "EUR",
  });
}

/** Format a date string (YYYY-MM-DD) to German format (DD.MM.YYYY) */
export function formatDate(dateStr) {
  if (!dateStr) return "—";
  const [y, m, d] = dateStr.split("-");
  if (!y || !m || !d) return dateStr;
  return `${d}.${m}.${y}`;
}

/** Return today's date as YYYY-MM-DD */
export function todayIso() {
  return new Date().toISOString().split("T")[0];
}

/** Capitalise the first letter of a string */
export function capitalize(str) {
  if (!str) return "";
  return str.charAt(0).toUpperCase() + str.slice(1);
}
