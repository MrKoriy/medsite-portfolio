# FRONTEND_PLAN.md: Architecture & Wave Decomposition

Based on `FRONTEND_BRIEF.md`. Designed under Vibe Coding Toolkit & Ponytail Escalator (YAGNI, MAX_LINES <= 350).

## 1. Design Tokens & System

```css
:root {
  --bg-page: #090d11;
  --bg-surface: #10171d;
  --bg-subtle: #162028;
  --bg-muted: #1c2732;

  --ink-primary: #f8fafc;
  --ink-secondary: #94a3b8;
  --ink-tertiary: #64748b;
  --ink-inverse: #090d11;

  --accent: #10b981;
  --accent-hover: #059669;
  --accent-subtle: rgba(16, 185, 129, 0.12);
  --accent-line: rgba(16, 185, 129, 0.35);

  --line: #1c2630;
  --line-strong: #293846;

  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
}
```

## 2. Modular File Structure (MAX_LINES <= 350)
- `frontend/css/style.css`: Master theme tokens, typography, grid, header, footer, forms.
- `frontend/css/world.css`: Extracted standalone styles for `.sw-*` scroll-world components and mobile bottom-sheet overrides (isolates engine styling, keeping `style.css` well under 350 lines).
- `frontend/js/scrub-engine.js`: Self-contained vanilla JS scroll-scrub engine (blob seek, rAF, seamless fade).
- `frontend/js/world-init.js`: Scene configuration (5 clinical departments), responsive `diveScroll` detection.
- `frontend/js/app.js`: Main site interactions (appointments, doctor booking slots, services, UTM).
- `frontend/js/api.js`: Fetch client for `/api/appointments`, `/api/doctors`, `/api/services`, `/api/faq`.
- `frontend/index.html`: Semantically structured markup mounting `#world` followed by `#services`, `#doctors`, `#appointment`, `#faq`.

## 3. Wave Decomposition

### Wave 1: Core Theme & Scoped World Styling
- **Task 1.1**: Extract `.sw-*` and mobile responsive overrides to `frontend/css/world.css`. Keep clean separation.
  - `Files:` `frontend/css/world.css`
  - `Depends-on:` none
- **Task 1.2**: Update `frontend/css/style.css` to adopt Dark Obsidian palette cleanly across all form cards, buttons, badges, and headers.
  - `Files:` `frontend/css/style.css`
  - `Depends-on:` none

### Wave 2: World Engine & Responsive Scene Wiring
- **Task 2.1**: Refine `frontend/js/world-init.js` to dynamically calibrate `diveScroll` (0.7 on mobile, 1.1 on desktop) and link CTA to `#appointment`.
  - `Files:` `frontend/js/world-init.js`
  - `Depends-on:` 1.1
- **Task 2.2**: Update `frontend/index.html` to link `css/world.css` and verify semantic structure.
  - `Files:` `frontend/index.html`
  - `Depends-on:` 1.1, 1.2

### Wave 3: Quality Gates & Verification
- **Task 3.1**: Run pytest 16/16 green.
- **Task 3.2**: Headless browser verification at 390x844 (mobile) and 1440x900 (desktop). Confirm zero errors.
- **Task 3.3**: Git commit & push.
