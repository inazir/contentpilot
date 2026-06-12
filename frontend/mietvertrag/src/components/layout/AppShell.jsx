import React from "react";
import TopBar from "./TopBar.jsx";
import Footer from "./Footer.jsx";

/**
 * AppShell
 * Wraps every page with the top bar, main content area, and footer.
 * Accepts `dark` prop to apply dark mode class on the root element.
 */
export default function AppShell({ children, dark, onToggleDark }) {
  return (
    <div className={`app-shell${dark ? " dark" : ""}`}>
      <TopBar dark={dark} onToggleDark={onToggleDark} />
      <main className="app-main">{children}</main>
      <Footer />
    </div>
  );
}
