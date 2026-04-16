# Engineering: Backend (Django & DRF)

Ergaenzt `CLAUDE.md`. Dieses Dokument ist der Owner fuer Backend-Schichten, Service-Layer, Query-Patterns und Celery-Integration.

---

## Zweck und Scope

- Architekturregeln fuer Django/DRF im Backend.
- Klare Verantwortlichkeiten von Model, Serializer, Service, View, Permission.
- Performance- und Robustheitsregeln fuer Datenbankzugriffe und Background Jobs.

---

## Verbindliche Regeln

### Schichten

- Views bleiben duenn und delegieren Fachlogik an Services.
- Serializer validieren und transformieren; keine Orchestrierung.
- Nicht-triviale Logik liegt im Service-Layer (`api/v1/services/`).
- Mehrschrittige atomare Writes laufen ueber Transaktionen im Service-Layer.

### Datenbank und Queries

- N+1 aktiv vermeiden (`select_related`/`prefetch_related`).
- Komplexe Queries gehoeren nicht in Views.
- Querysets bewusst auswerten, keine unnoetige Fruehevaluierung.
- Bulk-Operationen nutzen, wenn sie korrekt und lesbar sind.

### Fehlerbehandlung und Observability

- Business-Fehler klar von Systemfehlern trennen.
- Keine sensiblen Details in API-Fehlern.
- Wichtige Zustandsaenderungen nachvollziehbar loggen.

### Celery

- Tasks idempotent gestalten.
- Retries bewusst konfigurieren.
- Business-Logik nicht in Task-Entrypoints verstecken, sondern an Services delegieren.

---

## Verbotene Muster

- Business-Logik in Serializern oder Views.
- Ungesteuerte DB-Queries in API-Views.
- Implizite Transaktionen in falscher Schicht.
- Fat Models mit domaenenfremder Orchestrierung.

---

## Abgrenzung zu anderen Modulen

- OpenAPI/Schema-Regeln sind in `api.md` fuehrend.
- Sicherheitsregeln sind in `security.md` fuehrend.
- Testpflicht und Testtiefe sind in `testing.md` fuehrend.
- LLM-spezifische Regeln sind in `llm.md` fuehrend.
