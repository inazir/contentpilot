import React, { useEffect, useCallback } from "react";
import { useContract } from "../hooks/useContract.js";
import { useDraft } from "../hooks/useDraft.js";
import { loadSchema } from "../schemas/index.js";
import { getContractType } from "../constants/contractTypes.js";
import { loadLastContractType, saveLastContractType } from "../services/storageService.js";

import ProgressBar from "../components/wizard/ProgressBar.jsx";
import WizardNav from "../components/wizard/WizardNav.jsx";
import DraftBanner from "../components/wizard/DraftBanner.jsx";
import ContentPilotBanner from "../components/wizard/ContentPilotBanner.jsx";
import Toast from "../components/common/Toast.jsx";

import ContractTypeStep       from "../components/steps/ContractTypeStep.jsx";
import PartiesStep            from "../components/steps/PartiesStep.jsx";
import PropertyStep           from "../components/steps/PropertyStep.jsx";
import RentalPeriodStep       from "../components/steps/RentalPeriodStep.jsx";
import RentStep               from "../components/steps/RentStep.jsx";
import DepositStep            from "../components/steps/DepositStep.jsx";
import InventoryStep          from "../components/steps/InventoryStep.jsx";
import KeysAndAreasStep       from "../components/steps/KeysAndAreasStep.jsx";
import HouseRulesStep         from "../components/steps/HouseRulesStep.jsx";
import SpecialAgreementsStep  from "../components/steps/SpecialAgreementsStep.jsx";
import PreviewAndGenerateStep from "../components/steps/PreviewAndGenerateStep.jsx";

// ── Step definitions ───────────────────────────────────────────
// Each entry maps to a schema visibleSection id.
// Steps whose sectionId is NOT in the current schema are hidden.

const ALL_STEPS = [
  { id: "contractType",      label: "Vertragsart",    icon: "📄" },
  { id: "parties",           label: "Parteien",       icon: "👤" },
  { id: "property",          label: "Objekt",         icon: "🏠" },
  { id: "rentalPeriod",      label: "Mietzeit",       icon: "📅" },
  { id: "rent",              label: "Miete",          icon: "💶" },
  { id: "deposit",           label: "Kaution",        icon: "🔒" },
  { id: "inventory",         label: "Inventar",       icon: "📦" },
  { id: "keysAreas",         label: "Schlüssel",      icon: "🔑" },
  { id: "houseRules",        label: "Hausordnung",    icon: "📋" },
  { id: "special",           label: "Sonstiges",      icon: "✍️" },
  { id: "preview",           label: "Generieren",     icon: "📥" },
];

// Map step id → schema visibleSection id(s) used to decide visibility
const STEP_SECTION_MAP = {
  contractType:  ["contractType"],
  parties:       ["landlords", "tenants"],
  property:      ["property"],
  rentalPeriod:  ["rentalPeriod"],
  rent:          ["rent"],
  deposit:       ["deposit", "bank"],
  inventory:     ["inventory"],
  keysAreas:     ["keys", "sharedAreas"],
  houseRules:    ["houseRules", "safety", "registration", "insurance", "access"],
  special:       ["specialAgreements"],
  preview:       ["signatures"],
};

function getVisibleSteps(schema) {
  if (!schema) return ALL_STEPS;
  return ALL_STEPS.filter((step) => {
    const sections = STEP_SECTION_MAP[step.id] || [];
    // Always show contractType and preview
    if (step.id === "contractType" || step.id === "preview") return true;
    return sections.some((s) => schema.visibleSections.includes(s));
  });
}

// ── Autosave interval (ms) ─────────────────────────────────────
const AUTOSAVE_MS = 30_000;

export default function ContractWizard() {
  const lastType = loadLastContractType();

  const {
    form, step, errors, schema, contractType,
    setStep,
    updateField,
    addLandlord, updateLandlord, removeLandlord,
    addTenant,   updateTenant,   removeTenant,
    addInventoryItem, updateInventoryItem, removeInventoryItem,
    addKey, updateKey, removeKey,
    changeContractType,
    validate,
    reset,
    restoreFromDraft,
  } = useContract(lastType);

  const {
    saveDraft, loadDraft, clearDraft,
    hasDraft, draftMeta, saved,
  } = useDraft();

  const visibleSteps = getVisibleSteps(schema);
  const currentStep  = visibleSteps[step] || visibleSteps[0];
  const isFirst      = step === 0;
  const isLast       = step === visibleSteps.length - 1;

  // ── Autosave ─────────────────────────────────────────────────
  useEffect(() => {
    const id = setInterval(() => saveDraft(form), AUTOSAVE_MS);
    return () => clearInterval(id);
  }, [form, saveDraft]);

  // ── Persist last used contract type ──────────────────────────
  useEffect(() => {
    saveLastContractType(form.contractTypeId);
  }, [form.contractTypeId]);

  // ── Navigation ────────────────────────────────────────────────
  const handleNext = useCallback(() => {
    const stepValid = validate(currentStep.id);
    if (!stepValid) {
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    if (!isLast) {
      setStep((s) => Math.min(s + 1, visibleSteps.length - 1));
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, [validate, currentStep, isLast, setStep, visibleSteps.length]);

  const handleBack = useCallback(() => {
    setStep((s) => Math.max(s - 1, 0));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [setStep]);

  const handleStepClick = useCallback((index) => {
    setStep(index);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [setStep]);

  const handleSaveDraft = useCallback(() => {
    saveDraft(form);
  }, [saveDraft, form]);

  const handleRestoreDraft = useCallback(() => {
    const draft = loadDraft();
    if (draft) {
      restoreFromDraft(draft);
      clearDraft();
    }
  }, [loadDraft, restoreFromDraft, clearDraft]);

  const handleDiscardDraft = useCallback(() => {
    clearDraft();
  }, [clearDraft]);

  const handleChangeType = useCallback((typeId) => {
    changeContractType(typeId);
  }, [changeContractType]);

  // ── Step renderer ─────────────────────────────────────────────
  const renderStep = () => {
    const stepId = currentStep?.id;
    const commonProps = { form, errors, updateField };

    switch (stepId) {
      case "contractType":
        return <ContractTypeStep form={form} onChangeType={handleChangeType} />;
      case "parties":
        return (
          <PartiesStep
            {...commonProps}
            updateLandlord={updateLandlord} addLandlord={addLandlord} removeLandlord={removeLandlord}
            updateTenant={updateTenant}     addTenant={addTenant}     removeTenant={removeTenant}
          />
        );
      case "property":
        return <PropertyStep {...commonProps} />;
      case "rentalPeriod":
        return <RentalPeriodStep {...commonProps} />;
      case "rent":
        return <RentStep {...commonProps} />;
      case "deposit":
        return <DepositStep {...commonProps} />;
      case "inventory":
        return (
          <InventoryStep
            form={form}
            addInventoryItem={addInventoryItem}
            updateInventoryItem={updateInventoryItem}
            removeInventoryItem={removeInventoryItem}
          />
        );
      case "keysAreas":
        return (
          <KeysAndAreasStep
            form={form}
            updateField={updateField}
            addKey={addKey}
            updateKey={updateKey}
            removeKey={removeKey}
          />
        );
      case "houseRules":
        return <HouseRulesStep form={form} updateField={updateField} />;
      case "special":
        return <SpecialAgreementsStep form={form} updateField={updateField} />;
      case "preview":
        return <PreviewAndGenerateStep form={form} />;
      default:
        return <p>Unbekannter Schritt.</p>;
    }
  };

  // ── Error summary ─────────────────────────────────────────────
  const errorCount = Object.keys(errors).length;

  return (
    <div className="wizard">
      {/* Show ContentPilot banner only on first step */}
      {step === 0 && <ContentPilotBanner />}

      {/* Draft recovery banner */}
      {hasDraft && step === 0 && (
        <DraftBanner
          draftMeta={draftMeta}
          onRestore={handleRestoreDraft}
          onDiscard={handleDiscardDraft}
        />
      )}

      {/* Progress bar */}
      <ProgressBar
        steps={visibleSteps}
        current={step}
        onStepClick={handleStepClick}
      />

      {/* Validation error summary */}
      {errorCount > 0 && (
        <div className="wizard__error-banner">
          ⚠️ Bitte {errorCount} Pflichtfeld{errorCount > 1 ? "er" : ""} ausfüllen.
        </div>
      )}

      {/* Step content */}
      <div className="wizard__body">
        <div className="wizard__step-header">
          <span className="wizard__step-icon">{currentStep?.icon}</span>
          <div>
            <h2 className="wizard__step-title">{currentStep?.label}</h2>
            <p className="wizard__step-count">
              Schritt {step + 1} von {visibleSteps.length}
            </p>
          </div>
        </div>

        <div className="wizard__content">
          {renderStep()}
        </div>
      </div>

      {/* Navigation */}
      <WizardNav
        onBack={handleBack}
        onNext={handleNext}
        onSaveDraft={handleSaveDraft}
        isFirst={isFirst}
        isLast={isLast}
        saved={saved}
        nextLabel={isLast ? "Dokumente generieren" : "Weiter →"}
      />

      {/* Autosave toast */}
      <Toast visible={saved} message="Entwurf gespeichert" type="success" />

      <style>{`
        .wizard { display: flex; flex-direction: column; gap: 0; }
        .wizard__error-banner {
          background: var(--red-light); color: var(--red);
          border-radius: var(--radius); padding: 10px 16px;
          font-size: 14px; font-weight: 500; margin-bottom: 12px;
        }
        .wizard__body {
          background: var(--bg-card); border: 1px solid var(--border);
          border-radius: var(--radius-lg); padding: 24px;
          box-shadow: var(--shadow);
        }
        .wizard__step-header {
          display: flex; align-items: center; gap: 14px;
          margin-bottom: 24px; padding-bottom: 16px;
          border-bottom: 1px solid var(--border);
        }
        .wizard__step-icon  { font-size: 32px; line-height: 1; }
        .wizard__step-title { font-size: 18px; font-weight: 700; color: var(--text); }
        .wizard__step-count { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
        .wizard__content    { min-height: 200px; }
      `}</style>
    </div>
  );
}
