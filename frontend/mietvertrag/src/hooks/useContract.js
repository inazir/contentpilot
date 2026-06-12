import { useState, useCallback, useMemo } from "react";
import { buildDefaultState } from "../data/defaultState.js";
import { loadSchema } from "../schemas/index.js";
import { getContractType } from "../constants/contractTypes.js";
import { validateForm } from "../services/validationService.js";

/**
 * Central contract state hook.
 *
 * Owns:
 * - form state (the full contract data object)
 * - current wizard step
 * - dark mode toggle
 * - contract type switching (resets relevant defaults from schema)
 * - field update helpers (dot-notation path support)
 * - party management (add/remove landlord/tenant)
 * - inventory management
 * - key management
 * - validation errors
 * - reset
 */
export function useContract(initialContractTypeId = "wg_furnished") {
  const [form, setForm] = useState(() =>
    buildDefaultState(initialContractTypeId)
  );
  const [step, setStep] = useState(0);
  const [dark, setDark] = useState(false);
  const [errors, setErrors] = useState({});

  // ── Schema & contract type ─────────────────────────────────
  const contractType = useMemo(
    () => getContractType(form.contractTypeId),
    [form.contractTypeId]
  );

  const schema = useMemo(
    () => (contractType ? loadSchema(contractType.schemaId) : null),
    [contractType]
  );

  // ── Contract type change ───────────────────────────────────
  const changeContractType = useCallback(
    (newTypeId) => {
      const ct = getContractType(newTypeId);
      if (!ct) return;
      const newSchema = loadSchema(ct.schemaId);
      if (!newSchema) return;

      const inventory = ct.isFurnished
        ? newSchema.defaultInventoryFurnished()
        : newSchema.defaultInventoryUnfurnished();

      setForm((prev) => ({
        ...buildDefaultState(newTypeId),
        // Preserve parties entered so far
        landlords: prev.landlords,
        tenants: prev.tenants,
        // Apply schema defaults
        houseRules: {
          ...buildDefaultState(newTypeId).houseRules,
          ...newSchema.defaultHouseRules,
        },
        sharedAreas: {
          ...buildDefaultState(newTypeId).sharedAreas,
          ...newSchema.defaultSharedAreas,
        },
        inventory,
      }));
      setStep(0);
      setErrors({});
    },
    []
  );

  // ── Generic deep field updater ─────────────────────────────
  // Supports dot-notation: "rent.coldRent", "property.street", etc.
  const updateField = useCallback((path, value) => {
    setForm((prev) => {
      const keys = path.split(".");
      if (keys.length === 1) {
        return { ...prev, [path]: value };
      }
      if (keys.length === 2) {
        return {
          ...prev,
          [keys[0]]: { ...prev[keys[0]], [keys[1]]: value },
        };
      }
      if (keys.length === 3) {
        return {
          ...prev,
          [keys[0]]: {
            ...prev[keys[0]],
            [keys[1]]: {
              ...prev[keys[0]][keys[1]],
              [keys[2]]: value,
            },
          },
        };
      }
      return prev;
    });
  }, []);

  // ── Landlord management ────────────────────────────────────
  const addLandlord = useCallback(() => {
    import("../data/defaultState.js").then(({ emptyLandlord }) => {
      setForm((prev) => ({
        ...prev,
        landlords: [...prev.landlords, emptyLandlord()],
      }));
    });
  }, []);

  const updateLandlord = useCallback((index, updated) => {
    setForm((prev) => {
      const landlords = [...prev.landlords];
      landlords[index] = updated;
      return { ...prev, landlords };
    });
  }, []);

  const removeLandlord = useCallback((index) => {
    setForm((prev) => ({
      ...prev,
      landlords: prev.landlords.filter((_, i) => i !== index),
    }));
  }, []);

  // ── Tenant management ──────────────────────────────────────
  const addTenant = useCallback(() => {
    import("../data/defaultState.js").then(({ emptyTenant }) => {
      setForm((prev) => ({
        ...prev,
        tenants: [...prev.tenants, emptyTenant()],
      }));
    });
  }, []);

  const updateTenant = useCallback((index, updated) => {
    setForm((prev) => {
      const tenants = [...prev.tenants];
      tenants[index] = updated;
      return { ...prev, tenants };
    });
  }, []);

  const removeTenant = useCallback((index) => {
    setForm((prev) => ({
      ...prev,
      tenants: prev.tenants.filter((_, i) => i !== index),
    }));
  }, []);

  // ── Inventory management ───────────────────────────────────
  const addInventoryItem = useCallback(() => {
    import("../data/defaultState.js").then(({ emptyInventoryItem }) => {
      setForm((prev) => ({
        ...prev,
        inventory: [...prev.inventory, emptyInventoryItem()],
      }));
    });
  }, []);

  const updateInventoryItem = useCallback((index, field, value) => {
    setForm((prev) => {
      const inventory = [...prev.inventory];
      inventory[index] = { ...inventory[index], [field]: value };
      return { ...prev, inventory };
    });
  }, []);

  const removeInventoryItem = useCallback((index) => {
    setForm((prev) => ({
      ...prev,
      inventory: prev.inventory.filter((_, i) => i !== index),
    }));
  }, []);

  // ── Key management ─────────────────────────────────────────
  const addKey = useCallback(() => {
    import("../data/defaultState.js").then(({ emptyKey }) => {
      setForm((prev) => ({
        ...prev,
        keys: [...prev.keys, emptyKey()],
      }));
    });
  }, []);

  const updateKey = useCallback((index, field, value) => {
    setForm((prev) => {
      const keys = [...prev.keys];
      keys[index] = { ...keys[index], [field]: value };
      return { ...prev, keys };
    });
  }, []);

  const removeKey = useCallback((index) => {
    setForm((prev) => ({
      ...prev,
      keys: prev.keys.filter((_, i) => i !== index),
    }));
  }, []);

  // ── Validation ─────────────────────────────────────────────
  const validate = useCallback(
    (stepId) => {
      if (!schema) return true;
      const result = validateForm(form, schema, stepId);
      setErrors(result.errors);
      return result.valid;
    },
    [form, schema]
  );

  const clearErrors = useCallback(() => setErrors({}), []);

  // ── Reset ──────────────────────────────────────────────────
  const reset = useCallback(() => {
    setForm(buildDefaultState(form.contractTypeId));
    setStep(0);
    setErrors({});
  }, [form.contractTypeId]);

  // ── Restore from draft ─────────────────────────────────────
  const restoreFromDraft = useCallback((draftState) => {
    if (!draftState) return;
    setForm(draftState);
    setStep(0);
    setErrors({});
  }, []);

  return {
    // State
    form,
    step,
    dark,
    errors,
    schema,
    contractType,

    // Setters
    setForm,
    setStep,
    setDark,

    // Field updates
    updateField,

    // Parties
    addLandlord,
    updateLandlord,
    removeLandlord,
    addTenant,
    updateTenant,
    removeTenant,

    // Inventory
    addInventoryItem,
    updateInventoryItem,
    removeInventoryItem,

    // Keys
    addKey,
    updateKey,
    removeKey,

    // Contract type
    changeContractType,

    // Validation
    validate,
    clearErrors,

    // Lifecycle
    reset,
    restoreFromDraft,
  };
}

export default useContract;
