import React from "react";
import siteConfig from "../../config/siteConfig.js";

export default function TopBar({ dark, onToggleDark }) {
  return (
    <header className="topbar">
      <div className="topbar__inner">
        <div className="topbar__brand">
          <span className="topbar__logo">📄</span>
          <span className="topbar__name">{siteConfig.productName}</span>
          <span className="topbar__badge">by {siteConfig.contentPilotName}</span>
        </div>
        <div className="topbar__actions">
          <a
            href={siteConfig.contentPilotUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="topbar__cp-link"
          >
            {siteConfig.contentPilotName} →
          </a>
          <button
            className="topbar__dark-toggle"
            onClick={onToggleDark}
            aria-label="Dark mode umschalten"
            title={dark ? "Hellmodus" : "Dunklermodus"}
          >
            {dark ? "☀️" : "🌙"}
          </button>
        </div>
      </div>
    </header>
  );
}
