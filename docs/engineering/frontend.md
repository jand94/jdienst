# Engineering: Frontend (Next.js & React)

Ergänzt `CLAUDE.md`.

---

## Geltungsbereich

- Dieses Dokument gilt für Frontend-Code in Next.js/React inkl. UI, State, Rendering und API-Integration.
- Sicherheits- und Testanforderungen aus `security.md` und `testing.md` gelten zusätzlich.

---

## Verbindliche Regeln

- Server-first, wo es passt; Client Components nur bei echtem Interaktivitätsbedarf.
- Kleine, zusammensetzbare Komponenten bevorzugen.
- Präsentation und Datenbeschaffung trennen, wenn es Klarheit und Testbarkeit erhöht.
- Globalen State vermeiden, wenn lokaler oder serverseitiger Zustand ausreicht.
- Strikte Typisierung; `any` nur mit triftigem Grund.

---

## Architektur

- Server-first bleibt der Default.
- Client Components nur bei Interaktion, Browser-APIs oder zwingendem Client-State.
- Präsentation und Datenbeschaffung trennen, wenn es die Klarheit verbessert.
- Globalen State vermeiden, wo lokaler oder serverseitiger Zustand ausreicht.

---

## Next.js

- Rendering-Strategie (SSR, SSG, ISR, Client) passend zur Anforderung wählen.
- Performance, SEO und Cacheability berücksichtigen.  
- Kein redundantes Client-Fetching, wenn Server-Daten oder Server Actions ausreichen.

---

## React & TypeScript

- Strikte Typisierung.
- `any` nur mit triftigem Grund und kurzer Begründung (Kommentar oder Doku).
- Props-Typen explizit; Hooks fokussiert; Side-Effect-Ketten schlank halten.  
- Re-Renders und doppelten State vermeiden.

---

## Security im Frontend

- Kein unkontrolliertes Rendering von HTML (`dangerouslySetInnerHTML` nur mit validierter/sanitizierter Quelle).
- Tokens, Secrets oder sensible Diagnosedaten dürfen nicht in UI, Logs oder Client-Speicher geleakt werden.
- Eingaben clientseitig validieren, aber Sicherheitsvalidierung immer serverseitig erzwingen.
- Auth-/Permission-abhängige UI darf Backend-Permissions nicht ersetzen.

---

## UX & Barrierefreiheit

- Semantisches HTML; Tastaturbedienung; sinnvolle Labels und Beschreibungen.  
- Lade-, Leer-, Fehler- und Erfolgszustände **explizit** behandeln.

---

## Performance (Frontend)

- Unnötige Rerenders und Client-Overhead vermeiden.  
- Netzwerk-Roundtrips und Bundle-Größe bei Features mitdenken (ohne voreilige Mikro-Optimierung).

---

## Checkliste

Vor Abschluss einer Frontend-Änderung:

- Rendering-Strategie ist begründet (Server-first vs. Client)
- Typisierung ist strikt und nachvollziehbar
- Loading-, Empty-, Error- und Success-States sind behandelt
- interaktive und kritische Flows sind getestet
- Security-relevante Aspekte (XSS, Leaks, Auth-UI) sind geprüft

---

## Querverweise

- Testanforderungen: `testing.md`
- Sicherheitsanforderungen: `security.md`
- API-Vertrag und Schema: `api.md`
- CI-Durchsetzung: `ci.md`

---

## Verbotene Muster

- unnötige Client Components bei reinem Server-Use-Case
- unkommentiertes `any` in Kernlogik
- fehlende Zustandsbehandlung (Loading/Error/Empty)
- unvalidiertes oder unsanitisiertes HTML-Rendering
- implizite Auth-/Permission-Annahmen nur auf UI-Ebene
