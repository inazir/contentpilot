import React from "react";
import { getFooterLinks } from "../../constants/footerLinks.js";
import siteConfig from "../../config/siteConfig.js";

export default function Footer() {
  const links = getFooterLinks();
  const year  = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="app-footer__inner">
        <div className="app-footer__links">
          {links.map((link) => (
            <a
              key={link.label}
              href={link.href}
              target={link.external ? "_blank" : "_self"}
              rel={link.external ? "noopener noreferrer" : undefined}
              className="app-footer__link"
            >
              {link.label}
            </a>
          ))}
        </div>
        <p className="app-footer__copy">
          © {year} {siteConfig.productName} · Teil des{" "}
          <a
            href={siteConfig.contentPilotUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            {siteConfig.contentPilotName}
          </a>{" "}
          Ökosystems · Kein Ersatz für Rechtsberatung.
        </p>
      </div>
    </footer>
  );
}
