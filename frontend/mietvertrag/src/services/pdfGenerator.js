/**
 * PDF Generator Service
 *
 * Consumes document model objects produced by contractGenerator.js
 * and renders them to PDF using jsPDF.
 *
 * Install dependency:
 *   npm install jspdf
 *
 * Each block type from contractGenerator is handled:
 *   heading, paragraph, list, table, signature,
 *   pageBreak, spacer, legalNotice
 */

import { jsPDF } from "jspdf";
import "jspdf/dist/polyfills.es.js";

// ── Constants ──────────────────────────────────────────────────

const PAGE_W      = 210;   // A4 mm
const PAGE_H      = 297;
const MARGIN_L    = 20;
const MARGIN_R    = 20;
const MARGIN_T    = 25;
const MARGIN_B    = 25;
const CONTENT_W   = PAGE_W - MARGIN_L - MARGIN_R;

const FONT_NORMAL = 10;
const FONT_SMALL  = 8;
const FONT_H1     = 16;
const FONT_H2     = 12;
const FONT_H3     = 10;

const LINE_H      = 5.5;   // mm per line at FONT_NORMAL
const SECTION_GAP = 6;
const TABLE_ROW_H = 6;
const SIG_BOX_H   = 18;

const BLUE        = [30, 80, 160];
const DARK        = [30, 30, 30];
const GRAY        = [100, 100, 100];
const LIGHT_GRAY  = [240, 240, 240];
const WHITE       = [255, 255, 255];

// ── State ──────────────────────────────────────────────────────

let doc;
let y;

function newPage() {
  doc.addPage();
  y = MARGIN_T;
}

function checkSpace(needed) {
  if (y + needed > PAGE_H - MARGIN_B) newPage();
}

function x() {
  return MARGIN_L;
}

// ── Cover page ─────────────────────────────────────────────────

function renderCover(document) {
  // Background header bar
  doc.setFillColor(...BLUE);
  doc.rect(0, 0, PAGE_W, 60, "F");

  // Product watermark text
  doc.setFont("helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(...WHITE);
  doc.text("MyContentPilot.de", PAGE_W - MARGIN_R, 8, { align: "right" });

  // Main title
  doc.setFont("helvetica", "bold");
  doc.setFontSize(22);
  doc.setTextColor(...WHITE);
  doc.text(document.title || "MIETVERTRAG", PAGE_W / 2, 32, { align: "center" });

  // Subtitle
  doc.setFont("helvetica", "normal");
  doc.setFontSize(11);
  doc.text(
    `Erstellt am ${new Date(document.generatedAt).toLocaleDateString("de-DE")}`,
    PAGE_W / 2,
    44,
    { align: "center" }
  );

  y = 75;
}

// ── Header / Footer on each page ───────────────────────────────

function addPageDecorations(pageNum, totalPages, docTitle) {
  const savedColor = doc.getTextColor();

  // Header line
  doc.setDrawColor(...BLUE);
  doc.setLineWidth(0.3);
  doc.line(MARGIN_L, 15, PAGE_W - MARGIN_R, 15);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(7);
  doc.setTextColor(...GRAY);
  doc.text(docTitle, MARGIN_L, 12);
  doc.text("MyContentPilot.de", PAGE_W - MARGIN_R, 12, { align: "right" });

  // Footer line
  doc.line(MARGIN_L, PAGE_H - 15, PAGE_W - MARGIN_R, PAGE_H - 15);
  doc.text(
    `Seite ${pageNum} von ${totalPages}`,
    PAGE_W / 2,
    PAGE_H - 10,
    { align: "center" }
  );
  doc.text(
    "Dieses Dokument ist kein Ersatz für eine rechtliche Beratung.",
    MARGIN_L,
    PAGE_H - 10
  );

  doc.setTextColor(savedColor);
}

// ── Block renderers ────────────────────────────────────────────

function renderHeading(block) {
  const sizes   = { 1: FONT_H1, 2: FONT_H2, 3: FONT_H3 };
  const gaps    = { 1: 10, 2: 7, 3: 4 };
  const size    = sizes[block.level] || FONT_H2;
  const gap     = gaps[block.level] || 4;

  checkSpace(size * 0.4 + gap + 4);

  if (block.level === 1) {
    doc.setFillColor(...BLUE);
    doc.rect(MARGIN_L, y - 1, CONTENT_W, size * 0.4 + 4, "F");
    doc.setTextColor(...WHITE);
  } else if (block.level === 2) {
    doc.setDrawColor(...BLUE);
    doc.setLineWidth(0.5);
    doc.line(MARGIN_L, y + size * 0.4 + 1, PAGE_W - MARGIN_R, y + size * 0.4 + 1);
    doc.setTextColor(...BLUE);
  } else {
    doc.setTextColor(...DARK);
  }

  doc.setFont("helvetica", "bold");
  doc.setFontSize(size);
  doc.text(block.text, MARGIN_L + (block.level === 1 ? 3 : 0), y + size * 0.35);
  y += size * 0.4 + gap;
  doc.setTextColor(...DARK);
}

function renderParagraph(block) {
  if (!block.text) return;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(FONT_NORMAL);
  doc.setTextColor(...DARK);
  const lines = doc.splitTextToSize(block.text, CONTENT_W);
  checkSpace(lines.length * LINE_H + 3);
  doc.text(lines, MARGIN_L, y);
  y += lines.length * LINE_H + 3;
}

function renderList(block) {
  if (!block.items || block.items.length === 0) return;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(FONT_NORMAL);
  doc.setTextColor(...DARK);
  for (const item of block.items) {
    if (!item) continue;
    const lines = doc.splitTextToSize(`• ${item}`, CONTENT_W - 4);
    checkSpace(lines.length * LINE_H + 1);
    doc.text(lines, MARGIN_L + 2, y);
    y += lines.length * LINE_H + 1;
  }
  y += 2;
}

function renderTable(block) {
  if (!block.headers || !block.rows) return;

  const colCount = block.headers.length;
  const colW = CONTENT_W / colCount;

  checkSpace(TABLE_ROW_H * 2 + 4);

  // Header row
  doc.setFillColor(...BLUE);
  doc.rect(MARGIN_L, y, CONTENT_W, TABLE_ROW_H, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(FONT_SMALL);
  doc.setTextColor(...WHITE);
  block.headers.forEach((h, i) => {
    doc.text(h, MARGIN_L + i * colW + 2, y + TABLE_ROW_H - 1.5);
  });
  y += TABLE_ROW_H;

  // Data rows
  doc.setFont("helvetica", "normal");
  block.rows.forEach((row, ri) => {
    // Estimate row height (may have wrapped text)
    const cellHeights = row.map((cell, ci) => {
      const lines = doc.splitTextToSize(String(cell ?? ""), colW - 4);
      return lines.length * (LINE_H - 1);
    });
    const rowH = Math.max(TABLE_ROW_H, ...cellHeights) + 2;

    checkSpace(rowH);

    // Alternating background
    if (ri % 2 === 0) {
      doc.setFillColor(...LIGHT_GRAY);
      doc.rect(MARGIN_L, y, CONTENT_W, rowH, "F");
    }

    doc.setTextColor(...DARK);
    doc.setFontSize(FONT_SMALL);
    row.forEach((cell, ci) => {
      const lines = doc.splitTextToSize(String(cell ?? ""), colW - 4);
      doc.text(lines, MARGIN_L + ci * colW + 2, y + LINE_H - 1);
    });

    // Row border
    doc.setDrawColor(200, 200, 200);
    doc.setLineWidth(0.1);
    doc.line(MARGIN_L, y + rowH, MARGIN_L + CONTENT_W, y + rowH);

    y += rowH;
  });

  // Table border
  doc.setDrawColor(...GRAY);
  doc.setLineWidth(0.3);
  doc.rect(MARGIN_L, y - TABLE_ROW_H * (block.rows.length + 1), CONTENT_W,
    TABLE_ROW_H * (block.rows.length + 1));

  y += 4;
}

function renderSignature(block) {
  checkSpace(SIG_BOX_H + 4);

  // Signature box
  doc.setDrawColor(...GRAY);
  doc.setLineWidth(0.2);
  doc.setFillColor(...LIGHT_GRAY);
  doc.roundedRect(MARGIN_L, y, CONTENT_W, SIG_BOX_H, 2, 2, "FD");

  // Signature line
  doc.setDrawColor(...DARK);
  doc.setLineWidth(0.4);
  doc.line(
    MARGIN_L + 8,
    y + SIG_BOX_H - 5,
    MARGIN_L + CONTENT_W - 8,
    y + SIG_BOX_H - 5
  );

  // Label
  doc.setFont("helvetica", "normal");
  doc.setFontSize(FONT_SMALL);
  doc.setTextColor(...GRAY);
  doc.text(block.label, MARGIN_L + 8, y + 6);

  if (block.date) {
    doc.text("Datum: ___________________", MARGIN_L + CONTENT_W / 2, y + 6);
  }

  doc.text("Unterschrift", MARGIN_L + 8, y + SIG_BOX_H - 1);
  y += SIG_BOX_H + 4;
}

function renderPageBreak() {
  newPage();
}

function renderSpacer() {
  y += 5;
}

function renderLegalNotice(block) {
  checkSpace(14);
  doc.setFillColor(255, 248, 220);
  doc.roundedRect(MARGIN_L, y, CONTENT_W, 12, 2, 2, "F");
  doc.setFont("helvetica", "italic");
  doc.setFontSize(FONT_SMALL - 1);
  doc.setTextColor(120, 100, 20);
  const lines = doc.splitTextToSize(block.text, CONTENT_W - 6);
  doc.text(lines, MARGIN_L + 3, y + 4);
  y += 14;
}

// ── Block dispatcher ───────────────────────────────────────────

function renderBlock(block) {
  if (!block) return;
  switch (block.type) {
    case "heading":     renderHeading(block);     break;
    case "paragraph":   renderParagraph(block);   break;
    case "list":        renderList(block);         break;
    case "table":       renderTable(block);        break;
    case "signature":   renderSignature(block);    break;
    case "pageBreak":   renderPageBreak();         break;
    case "spacer":      renderSpacer();            break;
    case "legalNotice": renderLegalNotice(block);  break;
    default:            break;
  }
}

// ── Public API ─────────────────────────────────────────────────

/**
 * Render a single document model to a PDF Blob.
 *
 * @param {object} document - document model from contractGenerator
 * @returns {Blob} PDF blob
 */
export function renderDocumentToPdf(document) {
  doc = new jsPDF({ unit: "mm", format: "a4", orientation: "portrait" });
  doc.setFont("helvetica", "normal");
  doc.setTextColor(...DARK);

  // Cover page (first page)
  renderCover(document);

  // Content pages
  for (const section of document.sections) {
    for (const block of section.blocks) {
      renderBlock(block);
    }
  }

  // Add page numbers & headers/footers to all pages except cover
  const totalPages = doc.getNumberOfPages();
  for (let i = 2; i <= totalPages; i++) {
    doc.setPage(i);
    addPageDecorations(i - 1, totalPages - 1, document.title);
  }

  return doc.output("blob");
}

/**
 * Render a document model and trigger browser download.
 *
 * @param {object} document  - document model from contractGenerator
 * @param {string} [filename] - override filename (without .pdf)
 */
export function downloadDocumentAsPdf(document, filename) {
  doc = new jsPDF({ unit: "mm", format: "a4", orientation: "portrait" });
  doc.setFont("helvetica", "normal");
  doc.setTextColor(...DARK);

  renderCover(document);

  for (const section of document.sections) {
    for (const block of section.blocks) {
      renderBlock(block);
    }
  }

  const totalPages = doc.getNumberOfPages();
  for (let i = 2; i <= totalPages; i++) {
    doc.setPage(i);
    addPageDecorations(i - 1, totalPages - 1, document.title);
  }

  const safeName = (filename || document.title || "dokument")
    .replace(/[^a-z0-9äöüß\-_]/gi, "_")
    .toLowerCase();

  doc.save(`${safeName}.pdf`);
}

/**
 * Render all documents in an array and download each as a separate PDF.
 *
 * @param {object[]} documents - array of document models
 * @param {string}   prefix    - filename prefix (e.g. tenant name)
 */
export function downloadAllDocuments(documents, prefix = "mietvertrag") {
  for (const document of documents) {
    downloadDocumentAsPdf(document, `${prefix}_${document.type}`);
  }
}

export default {
  renderDocumentToPdf,
  downloadDocumentAsPdf,
  downloadAllDocuments,
};
