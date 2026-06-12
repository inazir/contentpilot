/**
 * Storage service.
 *
 * Centralises all localStorage keys and provides
 * typed read/write/clear helpers for the application.
 *
 * Keys are namespaced under "mv_" to avoid collisions
 * with other apps on the same domain.
 */

const KEYS = {
  DRAFT:            "mv_draft",
  DRAFT_META:       "mv_draft_meta",
  DARK_MODE:        "mv_dark_mode",
  LAST_CONTRACT:    "mv_last_contract_type",
  WIZARD_STEP:      "mv_wizard_step",
};

// ── Generic helpers ────────────────────────────────────────────

function read(key, fallback = null) {
  try {
    const raw = window.localStorage.getItem(key);
    if (raw === null) return fallback;
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function write(key, value) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (err) {
    console.warn(`storageService: failed to write "${key}"`, err);
    return false;
  }
}

function remove(key) {
  try {
    window.localStorage.removeItem(key);
    return true;
  } catch {
    return false;
  }
}

// ── Draft ──────────────────────────────────────────────────────

export function saveDraft(formState) {
  const ok = write(KEYS.DRAFT, formState);
  if (ok) {
    write(KEYS.DRAFT_META, {
      savedAt: new Date().toISOString(),
      contractTypeId: formState?.contractTypeId ?? "unknown",
    });
  }
  return ok;
}

export function loadDraft() {
  return read(KEYS.DRAFT, null);
}

export function loadDraftMeta() {
  return read(KEYS.DRAFT_META, null);
}

export function clearDraft() {
  remove(KEYS.DRAFT);
  remove(KEYS.DRAFT_META);
}

export function hasDraft() {
  return window.localStorage.getItem(KEYS.DRAFT) !== null;
}

// ── Preferences ────────────────────────────────────────────────

export function saveDarkMode(isDark) {
  write(KEYS.DARK_MODE, isDark);
}

export function loadDarkMode() {
  return read(KEYS.DARK_MODE, false);
}

export function saveLastContractType(contractTypeId) {
  write(KEYS.LAST_CONTRACT, contractTypeId);
}

export function loadLastContractType() {
  return read(KEYS.LAST_CONTRACT, "wg_furnished");
}

export function saveWizardStep(stepIndex) {
  write(KEYS.WIZARD_STEP, stepIndex);
}

export function loadWizardStep() {
  return read(KEYS.WIZARD_STEP, 0);
}

export function clearWizardStep() {
  remove(KEYS.WIZARD_STEP);
}

// ── Full reset ─────────────────────────────────────────────────

export function clearAll() {
  Object.values(KEYS).forEach(remove);
}

export const storageKeys = KEYS;

export default {
  saveDraft,
  loadDraft,
  loadDraftMeta,
  clearDraft,
  hasDraft,
  saveDarkMode,
  loadDarkMode,
  saveLastContractType,
  loadLastContractType,
  saveWizardStep,
  loadWizardStep,
  clearWizardStep,
  clearAll,
};
