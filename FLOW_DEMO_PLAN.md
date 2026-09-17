# Flow Demo Implementation Plan

## Objective
Implement a bounded two-scene video flow transition in `#world` using two 720x1280 video/poster assets (`clinic-lobby-demo` and `clinic-flow-demo`), with a scroll-driven overlay transition ("От знакомства к диагностике") to mask visual mismatches between scenes, keeping the core engine (`scrub-engine.js`) and backend unchanged.

---

## 1. Scene & Overlay Configuration (`frontend/js/world-init.js`)
- **Scenes**:
  1. Scene 1 (`lobby`): `assets/world/clinic-lobby-demo.mp4` / `.webp`, `scroll: 2.5`, `linger: 0`, title: "Пространство для заботы", eyebrow: "ПОРТФОЛИО · ВИДЕОКОНЦЕПТ".
  2. Scene 2 (`flow`): `assets/world/clinic-flow-demo.mp4` / `.webp`, `scroll: 2.5`, `linger: 0`, title: "Консультация и диагностика", CTA: `#appointment`.
- **Engine Options**: `crossfade: 0.08`, `atmosphere: false`, `nav: false`, `connectors: []`.
- **Scroll-driven Overlay**:
  - Injected fixed overlay inside `#world` with heading `От знакомства к диагностике`.
  - Opacity computed via `window.scrollY`: boundary $2.5 \times \text{innerHeight}$, plateau $|y/\text{vh} - 2.5| \le 0.12$, linear fade to zero at distance $0.55$.
  - Passive event listeners (`scroll`, `resize`) throttled with `requestAnimationFrame`.
  - Hidden away (`display: none`, `visibility: hidden`) and `aria-hidden="true"` when opacity is near 0.
  - Reduced motion check (`prefers-reduced-motion: reduce`) disables overlay animation.

---

## 2. Layout & Styles Overrides (`frontend/css/world.css`)
- **Desktop Portrait Contain**: Scoped `@media (min-width: 861px)` containing 9:16 videos on the right half (`left: 50%`, `width: 50%`, `object-fit: contain`) with text copy on the left half.
- **Mobile Responsive**: Preserve compact bottom-card styling for mobile viewports (`<= 860px`).
- **UI Cleanup**: Hide route navigation, particles, topbar, and hints (`display: none !important`).
- **Overlay Styling**: Fixed full-screen dark background (`#090d11`), centered white heading (`max-width: 700px`, responsive `clamp` font size).

---

## 3. HTML Updates (`frontend/index.html`)
- Update section label: `aria-label="Видеообзор клиники"`.
- Meta viewport: append `viewport-fit=cover`.
- Cache bust static assets: append `?v=flow2` to `css/world.css` and `js/world-init.js`.

---

## 4. Four Lenses Review
- **Security**: Strict DOM sanitization/safe node creation without `eval`/`innerHTML` injection; defensive element presence checks; `pointer-events: none` on overlay prevents input hijacking.
- **Architecture**: Zero changes to core engine (`scrub-engine.js`) or backend services. Isolated scene definitions and visual overrides within bounded files.
- **Types**: Precise numeric scroll math (`vh` units, normalized clamped distance calculation); defensive type/existence checks.
- **Idioms**: Standard vanilla JS patterns, passive event listeners, rAF frame batching, accessible ARIA state attributes, standard CSS custom property usage.
