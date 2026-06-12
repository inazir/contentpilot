import React from "react";
import siteConfig from "../../config/siteConfig.js";

/**
 * ContentPilotBanner
 * Hero section shown at the top of the wizard start page.
 * Promotes the ContentPilot ecosystem.
 */
export default function ContentPilotBanner() {
  return (
    <div className="cp-banner">
      <div className="cp-banner__inner">
        <div className="cp-banner__text">
          <p className="cp-banner__eyebrow">Teil des {siteConfig.contentPilotName} Ökosystems</p>
          <h1 className="cp-banner__title">{siteConfig.productName}</h1>
          <p className="cp-banner__sub">
            Professionelle Mietverträge in wenigen Minuten — für WG-Zimmer,
            Wohnungen, Häuser, Gewerberäume und mehr.
          </p>
        </div>
        <a
          href={siteConfig.contentPilotUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="cp-banner__cta"
        >
          {siteConfig.contentPilotName} entdecken →
        </a>
      </div>
    </div>
  );
}
