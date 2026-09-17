# Architecture Plan: Light Clinic Redesign (`LIGHT_REDESIGN_PLAN.md`)

## 1. Overview & System Standards

This plan outlines the complete light editorial redesign of the MedSfera clinic web application, transforming the UI from dark obsidian glassmorphism to a warm, accessible light healthcare experience aligned with video assets.

### Design Tokens & Palette Override
- **Warm Ivory (`#F7F5F0`)**: Page canvas & main section background.
- **Pure White (`#FFFEFB`)**: Surfaces, cards, input backgrounds, modal panels.
- **Stone Hairline (`#EAE5DC`)**: Thin structural borders, table dividers, card outlines.
- **Sage Accent (`#48614F`)**: Primary brand actions, active state, focused elements, highlights.
- **Sage Hover (`#3A4E3F`)**: Button hover states.
- **Ink Primary (`#29332C`)**: High-contrast body text, headings, crisp typography.
- **Muted Text (`#62685F`)**: Secondary text, subtitles, table headers, captions.
- **Accent Soft (`rgba(72, 97, 79, 0.08)`)**: Subtle background highlights, tags, pill badges.

### Core Architectural Principles
- **Typography**: Self-hosted `Golos Text` Cyrillic variable font loaded via `css/fonts.css`, with system sans-serif fallback. Primary body size 16px for readability.
- **Accessibility & UX**: 44px touch targets minimum, visible 2px sage focus rings (`outline: 2px solid #48614F`), WCAG AA contrast (Ink `#29332C` on `#F7F5F0` / `#FFFEFB`).
- **Editorial Layout**: Thin rules (`1px solid #EAE5DC`), low corner radii (4px–8px max), generous whitespace, no heavy glass or dark panels.
- **Interlude & Video Alignment**: Warm opaque chapter interlude overlay (`#F7F5F0`) transitioning seamlessly between scenes. Un-stretched desktop portrait videos (`object-fit: contain`). Compact mobile editorial copy cards.

---

## 2. Affected Files & Dependencies Summary

### CSS Files (`frontend/css/`)
1. `style.css`: Fix malformed CSS tokens outside `:root` (lines 55–59), replace dark obsidian tokens with light warm palette, refactor layout, cards, buttons, forms, tables, and typography into modular blocks (≤350 lines per modular section/file where practical).
2. `world.css`: Replace dark obsidian video overlays, dark mobile copy card styles, and transition colors with warm ivory (`#F7F5F0`) / white (`#FFFEFB`) light editorial styling.
3. `fonts.css`: Verify `@font-face` definitions for Golos Text Cyrillic.

### JS Files (`frontend/js/`)
1. `world-init.js`: Maintain chapter interlude overlay logic, ensuring opaque transition matches `#F7F5F0` background color.
2. `assistant.js`: Update assistant DOM structure or inline/CSS styling classes to render light editorial card style matching warm ivory/sage palette.
3. `app.js`, `api.js`, `admin.js`, `config.js`: Ensure zero regression in data attributes, API handlers, form bindings, and DOM selectors.

### HTML Files (`frontend/`)
1. `index.html`
2. `services.html`
3. `doctors.html`
4. `faq.html`
5. `admin.html`
*(Preserve all `data-*` attributes, form field IDs, and structure while updating class hooks if necessary).*

---

## 3. Concrete Actionable Tasks

### Task 1: Fix & Refactor CSS Variables & Base Foundation (`frontend/css/style.css`)
- **Fix Syntax Error**: Move orphan `--radius-*` tokens (lines 55–59 in `style.css`) inside the `:root` selector.
- **Replace Root Design Tokens**:
  - Replace dark page backgrounds (`#090d11`, `#10171d`) with `#F7F5F0` and `#FFFEFB`.
  - Replace dark ink variables with Ink `#29332C` and Muted `#62685F`.
  - Replace emerald accents with Sage `#48614F` and subtle Sage highlights.
  - Set border color to Stone `#EAE5DC`.
- **Refactor Core Component Styles**:
  - **Header & Nav**: Light header background (`#FFFEFB`/`#F7F5F0`), thin border bottom (`#EAE5DC`), crisp link hover states in Sage `#48614F`.
  - **Buttons**: Sage `#48614F` primary buttons with white text, crisp 4px radius, 44px minimum touch height; secondary buttons with Stone border (`#EAE5DC`) and Ink text.
  - **Cards & Grid**: Re-architect cards to use low corner radius (4px–6px), `#FFFEFB` background, thin `#EAE5DC` border, gentle subtle shadow or clean flat hairline border. Remove dark heavy glass blur.
  - **Forms & Inputs**: Light input backgrounds (`#FFFEFB`), Stone hairline borders, visible focus state in Sage `#48614F`.
  - **Tables (Admin)**: Light editorial table layout, crisp `#EAE5DC` row borders, muted header text, clear status badge pills (`#48614F` soft tint for confirmed, warm neutral for new).

### Task 2: Video Scroll & Chapter Interlude Overrides (`frontend/css/world.css` & `frontend/js/world-init.js`)
- **Flow Transition Overlay (`.flow-overlay`)**:
  - Update `background` from `#090d11` to warm opaque `#F7F5F0`.
  - Update heading text color to Ink `#29332C`.
  - Preserve chapter title "От знакомства к диагностике" and scroll opacity advance/reverse transition logic in `world-init.js`.
- **Desktop Portrait Video Container**:
  - Maintain `object-fit: contain` for desktop video player (`> 860px`), keeping video centered without distortion.
- **Mobile Editorial Copy Card (`< 860px`)**:
  - Change `.sw-copy` background from dark glass `rgba(16, 23, 29, 0.94)` to clean `#FFFEFB` or light ivory `#F7F5F0` with thin Stone border (`#EAE5DC`) and low radius (8px).
  - Update eyebrow/number styling to Sage `#48614F` and body/title text to Ink `#29332C` and Muted `#62685F`.
  - Update CTA buttons and tag pills inside `.sw-copy` to light sage palette.

### Task 3: Clinical Assistant Widget Refactoring (`frontend/js/assistant.js` & `frontend/css/style.css`)
- Update assistant floating button (FAB) and chat popup window (`.ai-chat`):
  - Replace dark popup styling with `#FFFEFB` background, `#EAE5DC` hairline border, soft shadow.
  - Header: Sage background or light warm header with Ink title and status hint.
  - Message bubbles: User messages in soft Sage tint (`rgba(72, 97, 79, 0.1)`), Assistant messages in light neutral (`#F7F5F0`).
  - Inputs & Send Button: Light warm input, Sage send button with SVG icon.

### Task 4: HTML Pages Layout & Structural Polish
- **`index.html`**: Verify hero video section integration, service/doctor card grids, appointment registration form styling.
- **`services.html`**: Clean editorial service listing layout with price tags in Sage `#48614F`.
- **`doctors.html`**: Doctor profile cards in light format with qualification badges.
- **`faq.html`**: Accordion/list styling using clean Stone hairline dividers (`#EAE5DC`).
- **`admin.html`**: Light administrative dashboard layout, clean filters, legible data table with status indicators.

### Task 5: Modular CSS Separation & Code Cleanliness
- Ensure CSS files stay under 350 lines per modular unit where applicable.
- Eliminate old dark obsidian overrides rather than adding cumulative CSS layers.

### Task 6: Comprehensive Verification Loop (4 Lenses)
1. **Visual & Aesthetic Lens**: Verify warm light clinic theme across all 5 pages at 375px, 390px, and 1440px viewports. Confirm no horizontal overflow.
2. **Typography & Assets Lens**: Confirm `Golos Text` Cyrillic font is properly rendered; verify videos display un-stretched on desktop and mobile.
3. **Accessibility Lens**: Test 44px min target size, visible focus outline on interactive elements, and high text contrast.
4. **Functional & Test Lens**: Verify all form submissions, interactive scroll engine, assistant chat, admin panel functions, and backend Pytest suite (`pytest backend/tests`).

---

## 4. Execution Sequence & Dependencies

```
[Task 1: CSS Root Variables & Base System]
           │
           ▼
[Task 2: Video Scroll & Interlude (world.css / world-init.js)]
           │
           ▼
[Task 3: Assistant Widget Styling (assistant.js / style.css)]
           │
           ▼
[Task 4: Component & HTML Page Verification (5 HTML Pages)]
           │
           ▼
[Task 5: CSS Modular Cleanup & Formatting Verification]
           │
           ▼
[Task 6: Multi-Viewport & Pytest Backend Verification]
```

---

## 5. Non-Functional Constraints & Safety Guardrails
- **Untouched Directories**: `media-review/` and backend logic files must remain completely untouched.
- **No Git Commits**: No `git commit` commands executed during agent operations.
- **Preserved Attributes**: Maintain all `data-*` attributes and existing IDs required by `app.js`, `api.js`, `admin.js`, and `scrub-engine.js`.
