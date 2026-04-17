# Engineering: Tests

Ergänzt `CLAUDE.md`.

---

## Geltungsbereich

- Dieses Dokument definiert Mindestanforderungen für Tests bei Backend-, Frontend-, API- und Integrationsänderungen.
- Es ergänzt `CLAUDE.md` und wird in CI gemäß `ci.md` technisch abgesichert.

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
- Änderungen an Write-Services oder sonstigen Mutationspfaden
- Änderungen an Validierung
- Änderungen an LLM-Integration
- Bugfixes (inkl. Reproduktions-Test)

---

## Test-Matrix (Änderungstyp -> Pflichttestarten)

| Änderungstyp | Unit | Integration | E2E |
|---|---|---|---|
| Neue Geschäftslogik im Service | Pflicht | Pflicht bei DB/API-Beteiligung | Optional, falls User-Flow kritisch |
| Änderung bestehender Geschäftslogik | Pflicht | Pflicht bei Schnittstellen-/DB-Effekt | Optional nach Risiko |
| Neuer API-Endpunkt | Pflicht für Serializer/Service | Pflicht | Optional, wenn kritischer End-to-End-Flow |
| Änderung Request-/Response-Struktur | Pflicht | Pflicht | Optional |
| Permission-/Security-Änderung | Pflicht | Pflicht | Empfohlen bei kritischen Journeys |
| Validierungsänderung | Pflicht | Pflicht | Optional |
| LLM-Integration | Pflicht (Parsing/Guards) | Pflicht (Service-Flow mit Mock/Fake) | Optional, gezielt |
| Bugfix | Pflicht (Reproduktion + Guard) | Pflicht, wenn Fehler integrationsnah war | Optional |
| Komplexes UI-Verhalten | Pflicht (Komponenten-/Hook-Logik) | Optional | Pflicht bei kritischem Nutzerfluss |

Für alle Backend-Write-Pfade in den ersten fünf Zeilen der Matrix gilt zusätzlich: Audit-Event-Erzeugung über `apps/common` muss mitgetestet werden.

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
- Audit-Event-Coverage für sicherheits- und fachkritische Mutationen
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

## Audit-Tests (verbindlich)

- Bei neuen oder geänderten Backend-Mutationspfaden müssen Tests die Erzeugung von Audit-Events über `apps.common.api.v1.services.audit_service.record_audit_event(...)` absichern.
- Mindestens folgende Eventfelder sind zu prüfen:
  - `action`
  - `target_model`
  - `target_id`
  - `metadata.source`
- Für sicherheitsrelevante Flows ist zusätzlich zu prüfen, dass sensible Metadaten sanitisiert sind (keine Tokens/Passwörter/Secrets im Event).
- Audit-Tests sind als Unit- und/oder Integrationstests umzusetzen; reine Happy-Path-Tests ohne Audit-Assertion sind nicht ausreichend.
- Ohne Audit-Testabdeckung gilt eine Write-Änderung als unvollständig.

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

## Checkliste

Vor Abschluss einer Änderung:

- Passende Testarten sind mit der Matrix abgeglichen
- neue oder geänderte Logik ist durch mindestens einen aussagekräftigen Test abgesichert
- Fehler-, Rand- und Permission-Fälle sind berücksichtigt
- API-Änderungen sind gegen Schema und Verhalten getestet
- externe Abhängigkeiten sind kontrolliert gemockt oder gezielt integriert
- Audit-Coverage für betroffene Mutationspfade ist über Tests nachgewiesen

---

## Querverweise

- API-Vertrag: `api.md`
- Sicherheitsanforderungen: `security.md`
- LLM-Integrationen: `llm.md`
- CI-Durchsetzung: `ci.md`

---

## Verbotene Muster

- Änderungen ohne Tests
- Tests nur für Happy Path
- Ungetestete API-Änderungen
- Tests mit echten externen Abhängigkeiten
- Ignorierte Fehlerfälle
- Nicht reproduzierbare Tests