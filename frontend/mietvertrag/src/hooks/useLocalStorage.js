import { useState, useEffect, useCallback } from "react";

/**
 * A hook that syncs state with localStorage.
 * - Reads initial value from localStorage on mount.
 * - Writes to localStorage on every state change.
 * - Handles JSON serialisation/deserialisation safely.
 *
 * @param {string} key        - localStorage key
 * @param {*}      initialValue - fallback if key is not in storage
 * @returns [value, setValue, clearValue]
 */
export function useLocalStorage(key, initialValue) {
  const readFromStorage = useCallback(() => {
    try {
      const raw = window.localStorage.getItem(key);
      if (raw === null) return initialValue;
      return JSON.parse(raw);
    } catch {
      return initialValue;
    }
  }, [key]); // eslint-disable-line react-hooks/exhaustive-deps

  const [storedValue, setStoredValue] = useState(readFromStorage);

  const setValue = useCallback(
    (value) => {
      try {
        const valueToStore =
          value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      } catch (err) {
        console.warn(`useLocalStorage: failed to write key "${key}"`, err);
      }
    },
    [key, storedValue]
  );

  const clearValue = useCallback(() => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (err) {
      console.warn(`useLocalStorage: failed to clear key "${key}"`, err);
    }
  }, [key]); // eslint-disable-line react-hooks/exhaustive-deps

  // Keep state in sync if the key changes externally (e.g. other tab)
  useEffect(() => {
    const handler = (e) => {
      if (e.key === key) {
        setStoredValue(readFromStorage());
      }
    };
    window.addEventListener("storage", handler);
    return () => window.removeEventListener("storage", handler);
  }, [key, readFromStorage]);

  return [storedValue, setValue, clearValue];
}

export default useLocalStorage;
