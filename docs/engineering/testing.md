# Engineering: Testing

Ergaenzt `CLAUDE.md`. Dieses Dokument ist der Owner fuer Testpflicht, Testtiefe und Testqualitaet.

---

## Zweck und Scope

- Definiert, wann Tests verpflichtend sind.
- Legt Testarten und Mindesttiefe fest.
- Sichert reproduzierbare, robuste Testausfuehrung.

---

## Verbindliche Regeln

### Wann Tests Pflicht sind

Tests muessen erstellt oder angepasst werden bei:

- neuer oder geaenderter Geschaeftslogik
- Bugfixes (inklusive reproduzierendem Test)
- API-Aenderungen (Request/Response/Status/Permissions)
- Validierungs- oder Sicherheitsaenderungen
- Aenderungen an LLM-Integration

### Testarten

- Unit-Tests fuer reine Logik.
- Integrations-Tests fuer Datenbank, API und Workflows.
- E2E nur fuer kritische Journeys mit klarem Mehrwert.

### Testtiefe

- Nicht nur Happy Path.
- Valid, invalid, Grenz- und Fehlerfaelle abdecken.

### Testqualitaet

- Tests deterministisch und nicht brittle halten.
- Externe Systeme in Standard-Tests mocken/isolationieren.
- Flaky Tests als Defekt behandeln.

### LLM in Tests

- Standard: Mock/Fake.
- Parsing- und Validierungslogik explizit testen.
- Reale LLM-Integrationstests nur gezielt und kontrolliert.

---

## Verbotene Muster

- Aenderungen ohne passende Tests.
- Tests nur auf Happy Path.
- Unkontrollierte echte externe Calls in Standard-Tests.

---

## Abgrenzung zu anderen Modulen

- API-Dokumentationsregeln liegen in `api.md`.
- CI-Ausfuehrungsregeln liegen in `ci.md`.
- Domaenen- und Schichtregeln liegen in `backend-rules.md` bzw. `frontend.md`.