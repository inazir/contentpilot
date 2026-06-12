import React from "react";
import Button from "../common/Button.jsx";
import { formatDate } from "../../utils/formatting.js";

/**
 * DraftBanner
 * Shown at the top of the wizard when a saved draft is detected.
 */
export default function DraftBanner({ draftMeta, onRestore, onDiscard }) {
  if (!draftMeta) return null;

  const savedAt = draftMeta.savedAt
    ? new Date(draftMeta.savedAt).toLocaleString("de-DE")
    : "Unbekannt";

  return (
    <div className="draft-banner">
      <div className="draft-banner__text">
        <span className="draft-banner__icon">💾</span>
        <span>
          Gespeicherter Entwurf gefunden — zuletzt gespeichert am{" "}
          <strong>{savedAt}</strong>
          {draftMeta.contractTypeId && ` (${draftMeta.contractTypeId})`}
        </span>
      </div>
      <div className="draft-banner__actions">
        <Button size="sm" variant="primary" onClick={onRestore}>
          Entwurf laden
        </Button>
        <Button size="sm" variant="ghost" onClick={onDiscard}>
          Verwerfen
        </Button>
      </div>
    </div>
  );
}
