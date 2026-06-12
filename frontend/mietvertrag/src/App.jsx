import React, { useState, useEffect } from "react";
import AppShell from "./components/layout/AppShell.jsx";
import ContractWizard from "./pages/ContractWizard.jsx";
import { loadDarkMode, saveDarkMode } from "./services/storageService.js";
import "./styles/global.css";

/**
 * App.jsx — thin root shell.
 * Owns only: dark mode state + AppShell wrapper.
 * All contract logic lives in ContractWizard → useContract.
 */
export default function App() {
  const [dark, setDark] = useState(() => loadDarkMode());

  const toggleDark = () => {
    setDark((d) => {
      saveDarkMode(!d);
      return !d;
    });
  };

  // Sync dark class onto <html> for any global CSS that needs it
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  return (
    <AppShell dark={dark} onToggleDark={toggleDark}>
      <ContractWizard />
    </AppShell>
  );
}
