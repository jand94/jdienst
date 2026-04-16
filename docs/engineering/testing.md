# Engineering: Tests

Ergänzt `CLAUDE.md`.

---

## Grundsatz

- Tests sind verpflichtender Bestandteil jeder nicht-trivialen Änderung.
- Änderungen ohne ausreichende Tests gelten als unvollständig.
- Verhalten, das nicht getestet ist, gilt als nicht abgesichert.

---

## Wann Tests erforderlich sind (verbindlich)

Tests müssen erstellt oder angepasst werden bei:

- neuer Geschäftslogik
- Änderungen an bestehender Logik
- neuen API-Endpunkten
- Änderungen an Request-/Response-Strukturen
- Änderungen an Permissions oder Security-Verhalten
- Änderungen an Validierung
- Änderungen an LLM-Integration
- Bugfixes (inkl. Reproduktions-Test)

---

## Was testen?

Priorisiert:

- Geschäftslogik inkl. Edge Cases
- Fehlerfälle und Grenzwerte
- Permissions und Security-Grenzen
- Serializer und Validierung
- API-Verträge:
  - Statuscodes
  - Response-Strukturen
  - Fehlerfälle
- Service-Logik und Workflows
- Integrationen mit externer Infrastruktur
- Komplexes UI-Verhalten

---

## Testarten (Pflichtstruktur)

### Unit-Tests

- Für reine Logik ohne I/O
- Schnell und deterministisch
- Keine externen Abhängigkeiten

### Integrations-Tests

- Datenbankverhalten
- API-Endpunkte
- Service-Workflows
- Serializer + Validation

### E2E-Tests

- Für kritische User-Journeys
- Nur dort, wo sie echten Mehrwert liefern

---

## Testtiefe (verbindlich)

- Happy Path allein reicht nicht.
- Mindestens enthalten:

  - gültige Eingaben
  - ungültige Eingaben
  - Grenzfälle
  - Fehlerfälle

---

## API-Tests (verbindlich)

- Jeder relevante Endpoint muss getestet werden auf:
  - Statuscodes
  - Response-Struktur
  - Validierungsfehler
  - Permission-Verhalten

- API-Tests müssen mit dem OpenAPI-Schema konsistent sein (`api.md`).

---

## Frontend-Tests

- UI-Zustände müssen getestet werden:
  - Loading
  - Error
  - Empty
  - Success

- Interaktive Komponenten müssen getestet werden.
- Keine impliziten Annahmen über API-Verhalten ohne Mock oder Integrationstest.

---

## Testqualität

- Tests dürfen nicht brittle sein.
- Tests dürfen sich nicht auf interne Implementierungsdetails verlassen.
- Tests müssen deterministisch sein.

### Verboten

- Flaky Tests
- Zeitabhängige Tests ohne Kontrolle
- echte externe Calls in Standard-Tests

---

## Mocking & Isolation

- Externe Systeme müssen gemockt oder isoliert werden:
  - APIs
  - LLM / Ollama
  - externe Services

- Integrationstests gegen reale Systeme nur gezielt und kontrolliert.

---

## Ollama / LLM

- Standard: Mock oder Fake verwenden.
- LLM-Output deterministisch simulieren.
- Parsing- und Validierungslogik muss getestet werden.

---

## Teststruktur

- Tests sind klar strukturiert und nachvollziehbar.
- Nähe zum getesteten Code ist zu bevorzugen.
- Naming muss den Zweck des Tests klar machen.

---

## Refactoring & Tests

- Refactoring darf bestehende Tests nicht brechen, außer Verhalten ändert sich bewusst.
- Bestehende Tests dürfen verbessert werden, wenn sie unklar oder unzuverlässig sind.

---

## Verbotene Muster

- Änderungen ohne Tests
- Tests nur für Happy Path
- Ungetestete API-Änderungen
- Tests mit echten externen Abhängigkeiten
- Ignorierte Fehlerfälle
- Nicht reproduzierbare Tests