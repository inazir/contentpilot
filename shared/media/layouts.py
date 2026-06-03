# shared/media/layouts.py
"""
Visual branding layout templates for ContentPilot.

Three distinct templates, each targeting a different aesthetic:

    Layout A — Editorial Top & Bottom Bands
        Solid-colour header band (brand name + tagline)
        Solid-colour footer band (CTA + website)
        Clean, editorial newspaper feel.

    Layout B — Modern Bottom Overlay & Corner Logo  (DEFAULT)
        Main image stays fully clean.
        Semi-transparent card in bottom-left with CTA + website.
        Brand name / logo pinned to top-right corner.
        Modern social media card aesthetic.

    Layout C — Minimalist Gradient Typography
        Subtle vertical gradient shadow over bottom portion.
        Bold typography overlaid on gradient (website + CTA).
        High-end editorial / magazine look.

All layouts use ONLY relative coordinate math (fractions of canvas
width/height) — never hardcoded pixel offsets — so they scale correctly
across every social format.

Each function signature:
    apply_layout_X(img: PIL.Image, profile: BrandProfile) -> PIL.Image

Returns a new PIL Image (never mutates the input).
On any internal error, returns the original img unchanged.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shared.media.branding import BrandProfile

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Layout A — Editorial Bands
# ---------------------------------------------------------------------------

def apply_layout_a(img, profile: "BrandProfile"):
    """
    Layout A: solid header + footer colour bands.

    Header band (top):   brand name  |  tagline
    Footer band (bottom): CTA text   |  website URL
    """
    try:
        from PIL import Image, ImageDraw
        from shared.media.utils import (
            rel_y, rel_x, rel_font_size,
            load_font, load_logo, hex_to_rgb,
            wrap_text, draw_text_block,
        )

        result = img.convert("RGBA").copy()
        W, H = result.size
        draw = ImageDraw.Draw(result)

        band_h = rel_y(H, 0.10)          # 10% of height per band
        pad_x  = rel_x(W, 0.04)
        pad_y  = int(band_h * 0.18)

        primary_rgba  = hex_to_rgb(profile.primary_color, 230)
        accent_rgba   = hex_to_rgb(profile.accent_color, 255)
        text_color    = (255, 255, 255, 255)

        font_brand    = load_font(rel_font_size(W, 0.032, 16, 52), "bold")
        font_tagline  = load_font(rel_font_size(W, 0.022, 12, 36), "regular")
        font_cta      = load_font(rel_font_size(W, 0.026, 14, 42), "semibold")
        font_website  = load_font(rel_font_size(W, 0.020, 11, 32), "regular")

        # --- Header band ---
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        header_draw = ImageDraw.Draw(overlay)
        header_draw.rectangle([(0, 0), (W, band_h)], fill=primary_rgba)
        result = Image.alpha_composite(result, overlay)
        draw = ImageDraw.Draw(result)

        # Brand name — left side of header
        brand_name = profile.display_name()
        name_lines = wrap_text(draw, brand_name, font_brand, int(W * 0.55))
        draw_text_block(draw, name_lines, font_brand, pad_x, pad_y, text_color)

        # Tagline — right side of header (if present)
        if profile.tagline:
            tag_max_w = int(W * 0.38)
            tag_lines = wrap_text(draw, profile.tagline, font_tagline, tag_max_w)
            tag_x = W - tag_max_w - pad_x
            draw_text_block(draw, tag_lines, font_tagline, tag_x, pad_y,
                            (220, 220, 220, 220), align="right", max_width=tag_max_w)

        # Logo in header (if available)
        logo = load_logo(profile.logo_path, int(band_h * 0.65))
        if logo:
            lx = W - logo.width - pad_x
            ly = (band_h - logo.height) // 2
            base = result.convert("RGBA")
            base.paste(logo, (lx, ly), mask=logo)
            result = base

        # --- Footer band ---
        footer_top = H - band_h
        overlay2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        footer_draw = ImageDraw.Draw(overlay2)
        footer_draw.rectangle([(0, footer_top), (W, H)], fill=primary_rgba)
        result = Image.alpha_composite(result.convert("RGBA"), overlay2)
        draw = ImageDraw.Draw(result)

        # CTA — left side of footer
        if profile.primary_cta:
            cta_lines = wrap_text(draw, profile.primary_cta, font_cta, int(W * 0.55))
            draw_text_block(draw, cta_lines, font_cta, pad_x,
                            footer_top + pad_y, accent_rgba)

        # Website — right side of footer
        if profile.website:
            web_lines = wrap_text(draw, profile.website, font_website, int(W * 0.42))
            web_x = W - int(W * 0.42) - pad_x
            draw_text_block(draw, web_lines, font_website, web_x,
                            footer_top + pad_y,
                            (210, 210, 210, 220), align="right", max_width=int(W * 0.42))

        logger.debug("layout_a_applied | size=%dx%d | band_h=%d", W, H, band_h)
        return result.convert("RGB")

    except Exception as exc:
        logger.error("layout_a_failed | error=%s | returning_original", exc)
        return img


# ---------------------------------------------------------------------------
# Layout B — Modern Bottom Card + Corner Logo  (default)
# ---------------------------------------------------------------------------

def apply_layout_b(img, profile: "BrandProfile"):
    """
    Layout B: clean image with semi-transparent bottom card + top-right brand.

    Top-right corner: logo (if available) or brand name text.
    Bottom-left card: CTA + website in a rounded semi-transparent panel.
    """
    try:
        from PIL import Image, ImageDraw
        from shared.media.utils import (
            rel_y, rel_x, rel_font_size,
            load_font, load_logo, hex_to_rgb,
            wrap_text, draw_text_block,
        )

        result = img.convert("RGBA").copy()
        W, H = result.size

        pad_x = rel_x(W, 0.04)
        pad_y = rel_y(H, 0.025)

        primary_rgba = hex_to_rgb(profile.primary_color, 210)
        accent_rgba  = hex_to_rgb(profile.accent_color, 255)
        text_white   = (255, 255, 255, 255)
        text_muted   = (210, 210, 210, 220)

        font_brand   = load_font(rel_font_size(W, 0.028, 14, 44), "bold")
        font_cta     = load_font(rel_font_size(W, 0.030, 15, 48), "semibold")
        font_website = load_font(rel_font_size(W, 0.022, 12, 34), "regular")

        draw = ImageDraw.Draw(result)

        # --- Top-right: brand name or logo ---
        logo = load_logo(profile.logo_path, rel_y(H, 0.07))
        if logo:
            lx = W - logo.width - pad_x
            ly = pad_y
            result.paste(logo, (lx, ly), mask=logo)
        else:
            brand_name = profile.display_name()
            if brand_name:
                # Semi-transparent pill behind text
                name_bbox = draw.textbbox((0, 0), brand_name, font=font_brand)
                name_w = name_bbox[2] - name_bbox[0]
                name_h = name_bbox[3] - name_bbox[1]
                pill_pad = rel_x(W, 0.015)
                pill_x1 = W - name_w - pill_pad * 2 - pad_x
                pill_y1 = pad_y - pill_pad // 2
                pill_x2 = W - pad_x
                pill_y2 = pad_y + name_h + pill_pad // 2

                pill_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                pill_draw  = ImageDraw.Draw(pill_layer)
                pill_draw.rectangle(
                    [(pill_x1, pill_y1), (pill_x2, pill_y2)],
                    fill=hex_to_rgb(profile.primary_color, 190),
                )
                result = Image.alpha_composite(result, pill_layer)
                draw = ImageDraw.Draw(result)
                draw.text((pill_x1 + pill_pad, pad_y), brand_name,
                          font=font_brand, fill=text_white)

        # --- Bottom-left card ---
        has_cta     = bool(profile.primary_cta)
        has_website = bool(profile.website)

        if not has_cta and not has_website:
            return result.convert("RGB")

        # Measure card content
        cta_max_w = int(W * 0.52)
        cta_lines = wrap_text(draw, profile.primary_cta or "", font_cta, cta_max_w)
        web_lines = wrap_text(draw, profile.website or "", font_website, cta_max_w)

        cta_h  = sum(
            draw.textbbox((0, 0), ln, font=font_cta)[3] - draw.textbbox((0, 0), ln, font=font_cta)[1]
            for ln in cta_lines
        ) if cta_lines else 0
        web_h  = sum(
            draw.textbbox((0, 0), ln, font=font_website)[3] - draw.textbbox((0, 0), ln, font=font_website)[1]
            for ln in web_lines
        ) if web_lines else 0

        inner_pad   = rel_x(W, 0.025)
        line_gap    = rel_y(H, 0.010)
        card_w      = cta_max_w + inner_pad * 2
        card_h      = (cta_h + web_h + inner_pad * 2 +
                       (line_gap if cta_lines and web_lines else 0))
        card_h      = max(card_h, rel_y(H, 0.10))

        card_x1 = pad_x
        card_y1 = H - pad_y - card_h
        card_x2 = card_x1 + card_w
        card_y2 = H - pad_y

        card_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        card_draw  = ImageDraw.Draw(card_layer)
        card_draw.rectangle([(card_x1, card_y1), (card_x2, card_y2)], fill=primary_rgba)
        result = Image.alpha_composite(result, card_layer)
        draw   = ImageDraw.Draw(result)

        # Accent left border stripe
        stripe_w = rel_x(W, 0.006)
        stripe_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        stripe_draw  = ImageDraw.Draw(stripe_layer)
        stripe_draw.rectangle(
            [(card_x1, card_y1), (card_x1 + stripe_w, card_y2)],
            fill=hex_to_rgb(profile.accent_color, 255),
        )
        result = Image.alpha_composite(result, stripe_layer)
        draw   = ImageDraw.Draw(result)

        # Draw CTA
        text_x = card_x1 + inner_pad + stripe_w + rel_x(W, 0.008)
        text_y = card_y1 + inner_pad
        if cta_lines:
            text_y = draw_text_block(draw, cta_lines, font_cta,
                                     text_x, text_y, accent_rgba,
                                     line_spacing=1.25)
            text_y += line_gap

        # Draw website
        if web_lines:
            draw_text_block(draw, web_lines, font_website,
                            text_x, text_y, text_muted,
                            line_spacing=1.2)

        logger.debug("layout_b_applied | size=%dx%d | card=%dx%d", W, H, card_w, card_h)
        return result.convert("RGB")

    except Exception as exc:
        logger.error("layout_b_failed | error=%s | returning_original", exc)
        return img


# ---------------------------------------------------------------------------
# Layout C — Minimalist Gradient Typography
# ---------------------------------------------------------------------------

def apply_layout_c(img, profile: "BrandProfile"):
    """
    Layout C: subtle bottom gradient with bold typography overlay.

    A vertical gradient shadow fades from transparent to semi-opaque over
    the bottom 45% of the image. Brand name, CTA, and website URL are
    rendered as clean bold typography on top of the gradient.
    """
    try:
        from PIL import Image, ImageDraw
        from shared.media.utils import (
            rel_y, rel_x, rel_font_size,
            load_font, load_logo, hex_to_rgb,
            wrap_text, draw_text_block,
            draw_gradient_overlay,
        )

        # Apply gradient
        result = draw_gradient_overlay(
            img,
            start_y_fraction=0.52,
            alpha_top=0,
            alpha_bottom=200,
            color=(0, 0, 0),
        ).convert("RGBA")

        W, H = result.size
        draw = ImageDraw.Draw(result)

        pad_x    = rel_x(W, 0.05)
        text_max = int(W * 0.85)

        accent_rgba  = hex_to_rgb(profile.accent_color, 255)
        text_white   = (255, 255, 255, 255)
        text_muted   = (200, 200, 200, 220)

        font_brand   = load_font(rel_font_size(W, 0.036, 18, 58), "bold")
        font_cta     = load_font(rel_font_size(W, 0.028, 14, 46), "semibold")
        font_website = load_font(rel_font_size(W, 0.020, 11, 32), "regular")

        # Logo top-left (optional)
        logo = load_logo(profile.logo_path, rel_y(H, 0.065))
        if logo:
            result_base = result.copy()
            result_base.paste(logo, (pad_x, rel_y(H, 0.03)), mask=logo)
            result = result_base
            draw = ImageDraw.Draw(result)

        # Stack text from bottom up
        bottom_pad = rel_y(H, 0.04)

        # Website (lowest)
        website_y = H - bottom_pad
        if profile.website:
            web_lines = wrap_text(draw, profile.website, font_website, text_max)
            # Draw upward: measure total block height first
            web_h_total = sum(
                (draw.textbbox((0, 0), ln, font=font_website)[3] -
                 draw.textbbox((0, 0), ln, font=font_website)[1])
                for ln in web_lines
            )
            website_y -= web_h_total
            draw_text_block(draw, web_lines, font_website,
                            pad_x, website_y, text_muted)
        else:
            website_y -= rel_y(H, 0.02)

        # CTA above website
        cta_y = website_y - rel_y(H, 0.015)
        if profile.primary_cta:
            cta_lines = wrap_text(draw, profile.primary_cta, font_cta, text_max)
            cta_h_total = sum(
                (draw.textbbox((0, 0), ln, font=font_cta)[3] -
                 draw.textbbox((0, 0), ln, font=font_cta)[1])
                for ln in cta_lines
            )
            cta_y -= cta_h_total
            draw_text_block(draw, cta_lines, font_cta,
                            pad_x, cta_y, accent_rgba)
        else:
            cta_y -= rel_y(H, 0.02)

        # Brand name above CTA
        brand_y = cta_y - rel_y(H, 0.018)
        brand_name = profile.display_name()
        if brand_name:
            name_lines = wrap_text(draw, brand_name, font_brand, text_max)
            name_h_total = sum(
                (draw.textbbox((0, 0), ln, font=font_brand)[3] -
                 draw.textbbox((0, 0), ln, font=font_brand)[1])
                for ln in name_lines
            )
            brand_y -= name_h_total
            draw_text_block(draw, name_lines, font_brand,
                            pad_x, brand_y, text_white)

        logger.debug("layout_c_applied | size=%dx%d", W, H)
        return result.convert("RGB")

    except Exception as exc:
        logger.error("layout_c_failed | error=%s | returning_original", exc)
        return img
