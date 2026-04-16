# Engineering: Frontend (Next.js & React)

Ergänzt `CLAUDE.md`.

---

## Architektur

- **Server-first**, wo es passt; **Client Components** nur bei echtem Interaktivitätsbedarf.  
- Kleine, zusammensetzbare Komponenten.  
- Präsentation und Datenbeschaffung trennen, wenn es die Klarheit verbessert.  
- Globalen State vermeiden, wo lokaler oder serverseitiger Zustand ausreicht.

---

## Next.js

- Rendering-Strategie (SSR, SSG, ISR, Client) **passend zur Anforderung** wählen.  
- Performance, SEO und Cacheability berücksichtigen.  
- Kein redundantes Client-Fetching, wenn Server-Daten oder Server Actions ausreichen.

---

## React & TypeScript

- **Strikte** Typisierung.  
- `any` nur mit triftigem Grund und kurzer Begründung (Kommentar oder Doku).  
- Props-Typen explizit; Hooks fokussiert; Side-Effect-Ketten schlank halten.  
- Re-Renders und doppelten State vermeiden.

---

## UX & Barrierefreiheit

- Semantisches HTML; Tastaturbedienung; sinnvolle Labels und Beschreibungen.  
- Lade-, Leer-, Fehler- und Erfolgszustände **explizit** behandeln.

---

## Performance (Frontend)

- Unnötige Rerenders und Client-Overhead vermeiden.  
- Netzwerk-Roundtrips und Bundle-Größe bei Features mitdenken (ohne voreilige Mikro-Optimierung).
