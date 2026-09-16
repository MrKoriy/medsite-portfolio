# BRIEF: Redesign & Scroll-World Integration for МедСфера (Medsite)

## 1. Goal
Overhaul the frontend of `МедСфера` (/root/coding/medsite) to eliminate the pale beige "hospital clunky" look and transform it into an ultra-premium Swiss Evidence-Based Clinic experience. Fix mobile UX completely (eliminating cramped clipping, trapped scroll, double navbars, and unreadable overlays).

## 2. Hard Constraints & Rules
1. **Design Direction**: Dark Obsidian (`#090d11`) with Surgical Mint/Emerald (`#10b981`) and deep slate (`#94a3b8`). Frosted dark glassmorphic cards (`rgba(16, 23, 29, 0.9)` with 1px hairline borders).
2. **Mobile-First Discipline**:
   - On viewports <= 860px, double headers must not exist.
   - Scene copy must be formatted as an iOS-native glass bottom-sheet that never occludes the interactive telemetry/diorama.
   - Scrub threshold on mobile must be fast and responsive (`diveScroll <= 0.7`).
3. **Architecture & File Limits**:
   - `MAX_LINES <= 350` for all modular scripts and CSS files.
   - Separation of concerns: `scrub-engine.js` (core engine), `world-init.js` (scene definitions), `app.js` (appointments, doctors, services DOM handlers), `assistant.js` (AI widget), `api.js` (fetch client).
4. **Backend Invariants**:
   - Zero changes to backend routes that break tests.
   - Pytest suite must remain 100% green (16 passed).
   - No secrets, tokens, or SQLite `.db` committed to git.

## 3. Non-Goals
- Re-architecting database models (already working and tested).
- External heavy CSS frameworks (Tailwind/Bootstrap) — keep native CSS custom properties for speed and zero build-step overhead.
