# Engineering: Security

Ergaenzt `CLAUDE.md`. Dieses Dokument ist der Owner fuer allgemeine Sicherheitsstandards (Validation, AuthZ, Secrets, OWASP-Basics).

---

## Zweck und Scope

- Security-by-default in allen Schichten.
- Verbindliche Regeln fuer Eingabevalidierung, Autorisierung und Secret-Handling.
- Baseline fuer sichere Fehlerbehandlung, Logging und Web-Schutzmassnahmen.

---

## Verbindliche Regeln

### Validierung und Zugriff

- Externe Eingaben muessen validiert werden.
- Geschuetzte Operationen brauchen explizite Berechtigungspruefung.
- Objekt-Level-Checks bei sensiblen Daten durchfuehren.

### Secrets und Datenlecks

- Secrets nie im Code, in Logs oder Responses.
- Sensible Daten in Logs minimieren und schuetzen.

### Fehler und Audit

- Keine Stacktraces oder internen Details in API-Responses.
- Sicherheitsrelevante Ereignisse nachvollziehbar loggen.

### Web-Schutz

- OWASP-Risiken aktiv mitigieren (Access Control, Injection, XSS, CSRF, IDOR).
- CORS restriktiv konfigurieren; sichere Cookie-Defaults verwenden.
- Rate Limiting fuer sensible/oeffentliche Endpunkte beruecksichtigen.

---

## Verbotene Muster

- Unvalidierte Eingaben.
- Implizite oder fehlende Berechtigungspruefungen.
- Hardcodierte Secrets.
- Offen konfigurierte CORS-Regeln ohne Begruendung.

---

## Abgrenzung zu anderen Modulen

- LLM-spezifische Sicherheitsregeln (Prompt Injection, Output-Handling) liegen primaer in `llm.md`.
- Testanforderungen fuer Sicherheitsgrenzen liegen in `testing.md`.
