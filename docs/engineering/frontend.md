# Engineering: Frontend (Next.js & React)

Ergaenzt `CLAUDE.md`. Dieses Dokument ist der Owner fuer Frontend-Architektur, Rendering-Strategien und UI-Qualitaetsregeln.

---

## Zweck und Scope

- Leitlinien fuer Next.js-/React-Umsetzung.
- Regeln fuer Typisierung, State-Nutzung und UX-Zustaende.
- Performance-Basics fuer Frontend-Auslieferung.

---

## Verbindliche Regeln

### Architektur

- Server-first, wenn Interaktivitaet keinen Client-Zwang erzeugt.
- Client Components nur bei echtem Interaktionsbedarf.
- Komponenten klein, komposabel und klar abgegrenzt halten.

### React/TypeScript

- Strikte Typisierung; `any` nur mit begruendeter Ausnahme.
- Props und oeffentliche Komponenten-APIs explizit halten.
- Side-Effect-Ketten und doppelten State vermeiden.

### UX und Accessibility

- Semantisches HTML und Tastaturbedienbarkeit sicherstellen.
- Loading-, Empty-, Error- und Success-State explizit abbilden.

### Performance

- Unnoetige Rerenders vermeiden.
- Netzwerk-/Bundle-Kosten bei Entscheidungen beruecksichtigen.

---

## Verbotene Muster

- Unnoetige Client-Fetches bei serverseitig loesbaren Faellen.
- Globale Zustaende ohne klare Notwendigkeit.
- Fehlende Zustandsbehandlung fuer Error/Empty/Loading.

---

## Abgrenzung zu anderen Modulen

- API-Vertragsregeln liegen in `api.md`.
- Testanforderungen fuer UI-Verhalten liegen in `testing.md`.
- Sicherheitsregeln fuer Daten und Tokens liegen in `security.md`.
