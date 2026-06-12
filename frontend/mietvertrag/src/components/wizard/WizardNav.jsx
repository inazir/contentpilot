import React from "react";
import Button from "../common/Button.jsx";

/**
 * WizardNav
 * Bottom navigation bar for the wizard (Back / Next / Generate).
 */
export default function WizardNav({
  onBack,
  onNext,
  onSaveDraft,
  isFirst,
  isLast,
  nextLabel = "Weiter →",
  backLabel = "← Zurück",
  saved,
}) {
  return (
    <div className="wizard-nav">
      <div className="wizard-nav__left">
        {!isFirst && (
          <Button variant="secondary" onClick={onBack}>
            {backLabel}
          </Button>
        )}
      </div>

      <div className="wizard-nav__center">
        <Button
          variant="ghost"
          size="sm"
          onClick={onSaveDraft}
          icon="💾"
        >
          {saved ? "Gespeichert ✓" : "Entwurf speichern"}
        </Button>
      </div>

      <div className="wizard-nav__right">
        <Button
          variant={isLast ? "primary" : "primary"}
          onClick={onNext}
          icon={isLast ? "📄" : undefined}
        >
          {isLast ? "Dokumente generieren" : nextLabel}
        </Button>
      </div>
    </div>
  );
}
