# Dashboard Design Contract

This dashboard follows the Revolut-inspired design direction supplied on 2026-05-12.

Core rules:

- Canvas alternates between true black `#000000` and white `#ffffff`.
- Black bands are used for storytelling and top-level project entry.
- White bands are used for catalogue, settings, review, tables, and operational browsing.
- Primary brand accent is cobalt violet `#494fdf`.
- Cobalt is scarce: active states, featured/selected cards, badges, and secondary emphasis only.
- Primary CTAs on dark surfaces are white pills with black text.
- Primary CTAs on light surfaces are black pills with white text.
- Display typography uses Aeonik Pro when available, with Inter Display, General Sans, Inter, and system fallbacks.
- Body and control typography uses Inter.
- Buttons, tabs, and pills use `9999px` radius.
- Cards use `20px` radius; inputs use `12px` radius.
- Cards do not use drop shadows; depth comes from canvas switches, surface colour, and hairline borders.
- Full absolute paths and dense technical metadata should ellipsize rather than force horizontal overflow.

Operational adaptation:

- Forge is a production dashboard, so controls keep accessible hit areas and dense layouts remain scannable.
- The Projects page is the dark hero/control-plane entry.
- Internal dashboard views use white catalogue surfaces with dark text for operational clarity.
- Future dashboard changes should edit `styles.css`, `index.html`, and `scripts/*`, then rebuild with `python3 src/build_forge.py`.
