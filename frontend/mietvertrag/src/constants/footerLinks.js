import siteConfig from "../config/siteConfig.js";

/**
 * Footer link definitions.
 * Reads from siteConfig (which reads from env vars).
 * Import this array wherever footer links are rendered.
 */
export function getFooterLinks() {
  return [
    { label: "Impressum", href: siteConfig.impressumUrl, external: false },
    { label: "Datenschutz", href: siteConfig.datenschutzUrl, external: false },
    { label: "AGB", href: siteConfig.agbUrl, external: false },
    { label: "Kontakt", href: siteConfig.contactUrl, external: false },
    {
      label: siteConfig.contentPilotName,
      href: siteConfig.contentPilotUrl,
      external: true,
    },
  ];
}
