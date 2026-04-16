# Engineering: Frontend Responsiveness

Ergaenzt `frontend.md` fuer responsive Layout- und Breakpoint-Standards.

---

## Ziel

- Einheitliche responsive Entscheidungen im gesamten Frontend.
- Keine doppelten oder widerspruechlichen Breakpoint-Definitionen.
- Klare Trennung zwischen CSS-Responsiveness und JS-Responsiveness.

---

## Source of Truth

- Breakpoints sind zentral in `frontend/lib/responsiveness.ts` definiert.
- Wiederverwendbare Klassenpakete sind zentral in `frontend/lib/responsive-tokens.ts` definiert.
- Tailwind Utility-Responsiveness (`sm:`, `md:`, `lg:`) bleibt Standard fuer reine Darstellung.

---

## Wann was verwenden?

- **Tailwind direkt**:
  - Bei rein visuellen Anpassungen (Spacing, Grid, Sichtbarkeit, Typografie).
  - Beispiel: `className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3"`.

- **`responsiveTokens`**:
  - Bei projektweit wiederkehrenden Klassenkombinationen.
  - Beispiel: Container-Breiten/Padding in `Navbar`, `Footer`, `layout.tsx`.

- **`use-breakpoint` / `use-media-query`**:
  - Nur wenn Laufzeitlogik auf Viewport reagieren muss.
  - Beispiel: unterschiedliche Drawer-Breite oder konditionale Interaktionslogik.

---

## SSR und Client-Regeln

- Hooks mit `window`/`matchMedia` nur in Client Components (`"use client"`).
- Server Components duerfen keine Browser-API-basierte Breakpoint-Logik enthalten.
- Bei Hooks immer einen sinnvollen Default fuer SSR-Hydration setzen.

---

## Verbotene Muster

- Breakpoints lokal hart codieren, wenn `lib/responsiveness.ts` bereits passende Werte bietet.
- Logik in CSS und JS doppelt modellieren, wenn ein Ansatz ausreicht.
- `use-breakpoint` fuer rein visuelle Aufgaben einsetzen.

---

## Referenzbeispiele

- Breakpoint-Utilities: `frontend/lib/responsiveness.ts`
- Responsive-Tokens: `frontend/lib/responsive-tokens.ts`
- Hook-Layer: `frontend/hooks/use-media-query.ts`, `frontend/hooks/use-breakpoint.ts`
- Integration: `frontend/components/layout/Navbar.tsx`, `frontend/app/layout.tsx`
