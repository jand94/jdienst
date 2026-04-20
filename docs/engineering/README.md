# Engineering Docs Guide

Dieses Verzeichnis enthält verbindliche Detailregeln als Ergänzung zu `CLAUDE.md`.

## Regelpriorität

- Bei Konflikten gilt die Priorität aus `CLAUDE.md`.
- Innerhalb von `docs/engineering/*.md` gewinnt die spezifischere Regel.

## Einheitliches Dokument-Template

Jedes Engineering-Dokument sollte folgende Struktur verwenden:

1. `# Engineering: <Thema>`
2. Kurzkontext: "Ergänzt `CLAUDE.md` ..."
3. `## Geltungsbereich`
4. `## Verbindliche Regeln`
5. `## Entscheidungslogik` (wenn sinnvoll)
6. `## Checkliste`
7. `## Querverweise`
8. `## Verbotene Muster`

Optionale Abschnitte:

- `## Ziele / Nicht-Ziele`
- `## Operationalisierung im Repository` (Ist/Soll, konkrete Pfade)
- `## Beispiele`

## Qualitätskriterien für Dokumente

- Regeln sind operationalisierbar und reviewbar formuliert.
- "Soll"-Aussagen enthalten, wo sinnvoll, einen Verweis auf den aktuellen Ist-Zustand.
- Wiederholungen über mehrere Dokumente werden vermieden; stattdessen verlinken.
- Sicherheits-, Test- und CI-Auswirkungen werden bei relevanten Themen explizit benannt.

## Kanonische Audit-Referenzen

Für Regeln mit Audit-Bezug ist `apps/common` die verbindliche Referenz. Nutze dafür:

- `../backend/common/README.md`
- `../backend/common/audit-basics.md`
- `../backend/common/audit-interfaces.md`

## Empfohlene Lesereihenfolge

Für neue Features oder größere Änderungen:

1. `backend.md` bzw. `frontend.md`
2. `api.md`
3. `testing.md`
4. `security.md`
5. `ci.md`

Bei Notification-bezogenen Änderungen zusätzlich:

- `notifications.md`
- `../backend/notification/README.md`
- `../backend/notification/operations-runbook.md`
