import { useCallback, useState } from "react";
import { useLocalStorage } from "./useLocalStorage.js";

const DRAFT_KEY = "mietvertrag_draft";
const DRAFT_META_KEY = "mietvertrag_draft_meta";

/**
 * Manages autosave draft persistence.
 *
 * Features:
 * - saveDraft(formState)   → persists current form to localStorage
 * - loadDraft()            → returns saved form state or null
 * - clearDraft()           → removes saved draft
 * - hasDraft               → boolean, true if a draft exists
 * - draftMeta              → { savedAt: ISO string, contractTypeId }
 * - saved                  → transient toast flag (resets after 2.5s)
 */
export function useDraft() {
  const [draft, setDraft, clearStoredDraft] = useLocalStorage(DRAFT_KEY, null);
  const [draftMeta, setDraftMeta, clearDraftMeta] = useLocalStorage(
    DRAFT_META_KEY,
    null
  );
  const [saved, setSaved] = useState(false);

  const saveDraft = useCallback(
    (formState) => {
      setDraft(formState);
      setDraftMeta({
        savedAt: new Date().toISOString(),
        contractTypeId: formState?.contractTypeId ?? "unknown",
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    },
    [setDraft, setDraftMeta]
  );

  const loadDraft = useCallback(() => {
    return draft ?? null;
  }, [draft]);

  const clearDraft = useCallback(() => {
    clearStoredDraft();
    clearDraftMeta();
  }, [clearStoredDraft, clearDraftMeta]);

  return {
    saveDraft,
    loadDraft,
    clearDraft,
    hasDraft: draft !== null,
    draftMeta,
    saved,
  };
}

export default useDraft;
