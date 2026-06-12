/**
 * Central site configuration.
 * All URLs and branding values come from Vite env vars.
 * Falls back to sensible defaults so the app never breaks
 * if a variable is not yet defined.
 */
const siteConfig = {
  // ContentPilot ecosystem
  contentPilotUrl:
    import.meta.env.VITE_CONTENTPILOT_URL || "https://mycontentpilot.de",
  contentPilotName:
    import.meta.env.VITE_CONTENTPILOT_NAME || "ContentPilot",

  // Product identity
  productName:
    import.meta.env.VITE_PRODUCT_NAME || "Mietvertrag Generator",
  productDomain:
    import.meta.env.VITE_PRODUCT_DOMAIN || "mycontentpilot.de",

  // Legal / footer links
  impressumUrl:
    import.meta.env.VITE_IMPRESSUM_URL || "/impressum",
  datenschutzUrl:
    import.meta.env.VITE_DATENSCHUTZ_URL || "/datenschutz",
  agbUrl:
    import.meta.env.VITE_AGB_URL || "/agb",
  contactUrl:
    import.meta.env.VITE_CONTACT_URL || "/kontakt",

  // Support / social (optional)
  supportEmail:
    import.meta.env.VITE_SUPPORT_EMAIL || "",
};

export default siteConfig;
