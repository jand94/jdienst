# Engineering: LLM & Ollama

Ergaenzt `CLAUDE.md`. Dieses Dokument ist der Owner fuer LLM-Architektur, Prompt-Handling, Output-Validierung und Fallback-Verhalten.

---

## Zweck und Scope

- Sichere und austauschbare LLM-Integration.
- Kapselung von Modellzugriff und Prompt-Logik.
- Deterministisches, validiertes Output-Handling.

---

## Verbindliche Regeln

### Architektur und Kapselung

- LLM-Aufrufe nur ueber dedizierte Services (z. B. `ollama_client.py`, `llm_service.py`).
- Keine direkten Aufrufe aus Views, Serializern oder Models.
- Core-Businesslogik darf nicht von Modellverhalten abhaengen.

### Konfiguration und Robustheit

- Modell, Endpoint, Timeout und Retry zentral konfigurierbar.
- Timeouts sind Pflicht.
- Definierte Fallbacks bei Timeout, Invalid Output oder Service-Ausfall.
- Kritische Funktionen duerfen nicht exklusiv vom LLM abhaengen.

### Prompt- und Output-Handling

- Prompts versionierbar und reviewbar fuehren.
- Trennung zwischen Prompt-Definition, Input-Aufbereitung, Modellaufruf und Output-Verarbeitung.
- LLM-Output als untrusted Input behandeln und strikt validieren.
- Keine direkte Uebernahme in DB oder sicherheitskritische Entscheidungen.

### Datenschutz und Performance

- Keine sensiblen Rohdaten unkontrolliert loggen.
- Redundante oder unnoetig teure LLM-Calls vermeiden.

---

## Verbotene Muster

- Unvalidierter Output in Entscheidungen oder Persistenz.
- Inline-Prompts ohne Struktur.
- Harte Kopplung an ein einzelnes Modell.
- Fehlendes Fallback-Verhalten.

---

## Abgrenzung zu anderen Modulen

- Allgemeine Security-Baseline liegt in `security.md`.
- Testpflicht und Testtiefe liegen in `testing.md`.
- Laufzeit-/Compose-Fragen liegen in `docker.md`.
