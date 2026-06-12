# POST DEPLOYMENT CHECKLIST
## Mietvertrag Generator v2.0 — Full Refactor

---

## 1. FILES ADDED (new files that did not exist before)

### src/config/
- `src/config/siteConfig.js`

### src/constants/
- `src/constants/contractTypes.js`
- `src/constants/footerLinks.js`

### src/utils/
- `src/utils/uid.js`
- `src/utils/formatting.js`
- `src/utils/calcRent.js`

### src/data/
- `src/data/defaultState.js`

### src/schemas/
- `src/schemas/index.js`
- `src/schemas/wg.schema.js`
- `src/schemas/apartment.schema.js`
- `src/schemas/house.schema.js`
- `src/schemas/garage.schema.js`
- `src/schemas/storage.schema.js`
- `src/schemas/commercial.schema.js`
- `src/schemas/zwischenmiete.schema.js`
- `src/schemas/untervermietung.schema.js`

### src/hooks/
- `src/hooks/useLocalStorage.js`
- `src/hooks/useDraft.js`
- `src/hooks/useContract.js`

### src/services/
- `src/services/storageService.js`
- `src/services/validationService.js`
- `src/services/contractGenerator.js`
- `src/services/pdfGenerator.js`

### src/styles/
- `src/styles/global.css`

### src/components/layout/
- `src/components/layout/AppShell.jsx`
- `src/components/layout/TopBar.jsx`
- `src/components/layout/Footer.jsx`

### src/components/common/
- `src/components/common/Button.jsx`
- `src/components/common/FormField.jsx`
- `src/components/common/Input.jsx`
- `src/components/common/Select.jsx`
- `src/components/common/Textarea.jsx`
- `src/components/common/Checkbox.jsx`
- `src/components/common/RadioGroup.jsx`
- `src/components/common/SectionCard.jsx`
- `src/components/common/Toast.jsx`
- `src/components/common/Badge.jsx`
- `src/components/common/Divider.jsx`

### src/components/wizard/
- `src/components/wizard/ProgressBar.jsx`
- `src/components/wizard/WizardNav.jsx`
- `src/components/wizard/DraftBanner.jsx`
- `src/components/wizard/ContentPilotBanner.jsx`

### src/components/steps/
- `src/components/steps/ContractTypeStep.jsx`
- `src/components/steps/PartiesStep.jsx`
- `src/components/steps/PropertyStep.jsx`
- `src/components/steps/RentalPeriodStep.jsx`
- `src/components/steps/RentStep.jsx`
- `src/components/steps/DepositStep.jsx`
- `src/components/steps/InventoryStep.jsx`
- `src/components/steps/KeysAndAreasStep.jsx`
- `src/components/steps/HouseRulesStep.jsx`
- `src/components/steps/SpecialAgreementsStep.jsx`
- `src/components/steps/PreviewAndGenerateStep.jsx`

### src/pages/
- `src/pages/ContractWizard.jsx`

### Root files (new or replaced):
- `.env.example`

---

## 2. FILES MODIFIED (existing files that must be replaced)

| File | Change |
|---|---|
| `src/App.jsx` | Full replacement — now a thin shell (dark mode + AppShell only) |
| `src/main.jsx` | Minor update — unchanged structure, verify it matches batch 6 |
| `package.json` | Added `jspdf` dependency, bumped version to 2.0.0 |
| `vite.config.js` | Added `manualChunks` to split jsPDF into separate bundle chunk |
| `Dockerfile` | Added `ARG`/`ENV` declarations for all VITE_ build args |
| `docker-compose.yml` | Added `build.args` block for all VITE_ environment variables |

---

## 3. NPM PACKAGES TO INSTALL

```bash
cd ~/repos/contentpilot/frontend/mietvertrag
npm install jspdf
```

That is the only new runtime dependency.
`jspdf` version `^2.5.1` — stable, no peer dependency issues with React 18.

**Full dependency list after install:**
- `react` ^18.2.0
- `react-dom` ^18.2.0
- `jspdf` ^2.5.1

---

## 4. ENVIRONMENT VARIABLES TO ADD

All variables are prefixed `VITE_` — Vite bakes them into the bundle at build time.

| Variable | Required | Example value |
|---|---|---|
| `VITE_CONTENTPILOT_URL` | No | `https://mycontentpilot.de` |
| `VITE_CONTENTPILOT_NAME` | No | `ContentPilot` |
| `VITE_PRODUCT_NAME` | No | `Mietvertrag Generator` |
| `VITE_PRODUCT_DOMAIN` | No | `mietvertrag.mycontentpilot.de` |
| `VITE_IMPRESSUM_URL` | No | `https://mycontentpilot.de/impressum` |
| `VITE_DATENSCHUTZ_URL` | No | `https://mycontentpilot.de/datenschutz` |
| `VITE_AGB_URL` | No | `https://mycontentpilot.de/agb` |
| `VITE_CONTACT_URL` | No | `https://mycontentpilot.de/kontakt` |
| `VITE_SUPPORT_EMAIL` | No | `support@mycontentpilot.de` |

All variables have hardcoded fallbacks in `src/config/siteConfig.js`.
The app will not break if none are set — it uses the fallback values.

### How to set them for Docker:

**Option A — .env file on VPS (for local dev / non-Docker):**
```bash
cp .env.example .env
# Edit .env with your values
```

**Option B — docker-compose.yml build args (production, recommended):**
The updated `docker-compose.yml` already reads them from the host shell
environment via `${VITE_X:-fallback}` syntax.

Set them on your VPS before building:
```bash
export VITE_CONTENTPILOT_URL=https://mycontentpilot.de
export VITE_IMPRESSUM_URL=https://mycontentpilot.de/impressum
# ... etc
docker compose build --no-cache
```

Or store them in a `.env` file next to `docker-compose.yml` —
Docker Compose reads it automatically.

---

## 5. URLS TO CONFIGURE

| What | Where to set |
|---|---|
| ContentPilot homepage | `VITE_CONTENTPILOT_URL` |
| Impressum page | `VITE_IMPRESSUM_URL` |
| Datenschutz page | `VITE_DATENSCHUTZ_URL` |
| AGB page | `VITE_AGB_URL` |
| Kontakt page | `VITE_CONTACT_URL` |

---

## 6. FOOTER LINKS TO CONFIGURE

The footer renders these 5 links dynamically from `src/constants/footerLinks.js`
which reads from `siteConfig.js` which reads from env vars:

1. Impressum → `VITE_IMPRESSUM_URL`
2. Datenschutz → `VITE_DATENSCHUTZ_URL`
3. AGB → `VITE_AGB_URL`
4. Kontakt → `VITE_CONTACT_URL`
5. ContentPilot → `VITE_CONTENTPILOT_URL`

If any URL is not set, it falls back to a relative path (e.g. `/impressum`).
These relative paths will 404 unless you create those pages or redirect them
in your Nginx config (see section 8).

---

## 7. CONTENTPILOT HOMEPAGE URL

Set via `VITE_CONTENTPILOT_URL`.

It appears in:
- TopBar "ContentPilot →" link
- ContentPilotBanner CTA button (shown on step 1)
- Footer last link
- Footer copyright line

Default fallback: `https://mycontentpilot.de`

---

## 8. NGINX CHANGES REQUIRED

**Minimal change required** — add a `try_files` fallback for React client-side routing.

Your existing `nginx/mietvertrag.mycontentpilot.de.conf` needs this inside the
`location /` block if it does not already have it:

```nginx
location / {
    root   /usr/share/nginx/html;
    index  index.html;
    try_files $uri $uri/ /index.html;   # ← ADD THIS LINE
}
```

Without `try_files`, a hard refresh on any non-root URL returns 404.

**Optional — redirect footer legal links to your main domain:**
```nginx
location /impressum  { return 301 https://mycontentpilot.de/impressum; }
location /datenschutz { return 301 https://mycontentpilot.de/datenschutz; }
location /agb        { return 301 https://mycontentpilot.de/agb; }
location /kontakt    { return 301 https://mycontentpilot.de/kontakt; }
```
This is only needed if you use relative URLs in env vars (i.e. `/impressum`)
rather than absolute URLs (`https://mycontentpilot.de/impressum`).
If you set full absolute URLs in env vars, this is not needed.

---

## 9. DOCKER CHANGES REQUIRED

Two files are updated in Batch 6:

### Dockerfile
The new Dockerfile adds `ARG` and `ENV` declarations for all VITE_ variables
so they are available to the Vite build inside the container.
**Replace your existing Dockerfile with the one from Batch 6.**

### docker-compose.yml
The new docker-compose.yml adds a `build.args` block that forwards host
environment variables into the Docker build.
**Replace your existing docker-compose.yml with the one from Batch 6.**

**Rebuild command after changes:**
```bash
cd ~/repos/contentpilot/frontend/mietvertrag
docker compose build --no-cache
docker compose up -d
```

---

## 10. VITE CHANGES REQUIRED

`vite.config.js` is updated with one addition:

```js
rollupOptions: {
  output: {
    manualChunks: {
      jspdf: ["jspdf"],   // ← splits jsPDF into separate chunk
    },
  },
},
```

This keeps the main JS bundle small by putting jsPDF (~300 KB) in its own
chunk that loads only when needed.
**Replace your existing vite.config.js with the one from Batch 6.**

---

## 11. LEGAL PAGES REQUIRED

The footer links to these pages. You have two options:

**Option A (recommended):** Set all `VITE_*_URL` variables to absolute URLs
pointing to existing pages on `mycontentpilot.de`. No new pages needed.

**Option B:** Create dedicated pages within the mietvertrag app. This would
require adding a router (e.g. `react-router-dom`) and new page components.
This is NOT included in this refactor — the current architecture has no router
since the wizard is a single-page flow.

**Minimum legal requirement for Germany:**
- Impressum (§ 5 TMG) — required
- Datenschutzerklärung (DSGVO) — required
- AGB — recommended if this is a commercial service

---

## 12. ADDITIONAL ROUTES REQUIRED

**None** — the application is a single-page app with no client-side routing.
The wizard uses step state (not URL routes) for navigation.

If you later want deep-linkable wizard steps or a separate `/settings` page,
add `react-router-dom` and wrap `App.jsx` with `<BrowserRouter>`.

---

## 13. MANUAL STEPS AFTER DEPLOYMENT

Run these in order:

```bash
# 1. Navigate to the app directory
cd ~/repos/contentpilot/frontend/mietvertrag

# 2. Unzip all batch zips (if not already done)
cd ~/repos/contentpilot
unzip mietvertrag_batch1_foundation.zip
unzip mietvertrag_batch2_schemas.zip
unzip mietvertrag_batch3_hooks_services.zip
unzip mietvertrag_batch4_pdf_components_styles.zip
unzip mietvertrag_batch5_wizard_steps.zip
unzip mietvertrag_batch6_final.zip

# 3. Install the new dependency
cd frontend/mietvertrag
npm install

# 4. Create your .env file
cp .env.example .env
# Edit .env with your actual URLs

# 5. Test the build locally (optional but recommended)
npm run build
npm run preview

# 6. Rebuild the Docker image
docker compose build --no-cache

# 7. Restart the container
docker compose up -d

# 8. Verify the container is running
docker compose ps
docker compose logs mietvertrag --tail=20

# 9. Test in browser
# Open https://mietvertrag.mycontentpilot.de
# Verify: TopBar shows product name
# Verify: ContentPilot banner shows on step 1
# Verify: All 11 wizard steps are navigable
# Verify: PDF generates and downloads on final step
# Verify: Footer links resolve correctly
# Verify: Dark mode toggle works
# Verify: Draft save/restore works (fill form, refresh page)
```

---

## COMPLETE FILE TREE AFTER ALL BATCHES

```
frontend/mietvertrag/
├── .env.example
├── .env                          ← you create this
├── Dockerfile                    ← replaced in batch 6
├── docker-compose.yml            ← replaced in batch 6
├── package.json                  ← replaced in batch 6
├── vite.config.js                ← replaced in batch 6
├── index.html                    ← unchanged
├── nginx/
│   └── mietvertrag.mycontentpilot.de.conf   ← add try_files line
└── src/
    ├── App.jsx                   ← replaced in batch 6
    ├── main.jsx                  ← replaced in batch 6
    ├── config/
    │   └── siteConfig.js
    ├── constants/
    │   ├── contractTypes.js
    │   └── footerLinks.js
    ├── utils/
    │   ├── uid.js
    │   ├── formatting.js
    │   └── calcRent.js
    ├── data/
    │   └── defaultState.js
    ├── schemas/
    │   ├── index.js
    │   ├── wg.schema.js
    │   ├── apartment.schema.js
    │   ├── house.schema.js
    │   ├── garage.schema.js
    │   ├── storage.schema.js
    │   ├── commercial.schema.js
    │   ├── zwischenmiete.schema.js
    │   └── untervermietung.schema.js
    ├── hooks/
    │   ├── useLocalStorage.js
    │   ├── useDraft.js
    │   └── useContract.js
    ├── services/
    │   ├── storageService.js
    │   ├── validationService.js
    │   ├── contractGenerator.js
    │   └── pdfGenerator.js
    ├── styles/
    │   └── global.css
    ├── components/
    │   ├── layout/
    │   │   ├── AppShell.jsx
    │   │   ├── TopBar.jsx
    │   │   └── Footer.jsx
    │   ├── common/
    │   │   ├── Button.jsx
    │   │   ├── FormField.jsx
    │   │   ├── Input.jsx
    │   │   ├── Select.jsx
    │   │   ├── Textarea.jsx
    │   │   ├── Checkbox.jsx
    │   │   ├── RadioGroup.jsx
    │   │   ├── SectionCard.jsx
    │   │   ├── Toast.jsx
    │   │   ├── Badge.jsx
    │   │   └── Divider.jsx
    │   ├── wizard/
    │   │   ├── ProgressBar.jsx
    │   │   ├── WizardNav.jsx
    │   │   ├── DraftBanner.jsx
    │   │   └── ContentPilotBanner.jsx
    │   └── steps/
    │       ├── ContractTypeStep.jsx
    │       ├── PartiesStep.jsx
    │       ├── PropertyStep.jsx
    │       ├── RentalPeriodStep.jsx
    │       ├── RentStep.jsx
    │       ├── DepositStep.jsx
    │       ├── InventoryStep.jsx
    │       ├── KeysAndAreasStep.jsx
    │       ├── HouseRulesStep.jsx
    │       ├── SpecialAgreementsStep.jsx
    │       └── PreviewAndGenerateStep.jsx
    └── pages/
        └── ContractWizard.jsx
```

---

## QUICK SANITY CHECK AFTER DEPLOYMENT

| Check | Expected result |
|---|---|
| App loads | No blank screen, no console errors |
| Step 1 | Contract type grid with 14 options in 5 groups |
| Step navigation | Progress bar advances, back/next work |
| Dark mode | Toggle switches theme, persists on reload |
| Draft save | "Entwurf speichern" button shows "Gespeichert ✓" |
| Draft restore | Refresh page → banner appears → "Entwurf laden" restores form |
| PDF download | Final step → "Alle Dokumente herunterladen" → PDF files download |
| Footer links | All 5 links resolve (no 404) |
| ContentPilot CTA | Banner on step 1 → button opens correct URL |
| Mobile | Layout is usable on 375px viewport |
