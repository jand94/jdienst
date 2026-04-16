# Engineering: LLM & Ollama (Offline / lokal)

Ergänzt `CLAUDE.md` und `security.md`.

---

## Grundsatz

- LLMs sind **nicht vertrauenswürdig** und müssen wie externe, unsichere Datenquellen behandelt werden.
- LLM-Integration ist Infrastruktur, kein Business-Logik-Ersatz.
- Alle LLM-Interaktionen müssen kontrolliert, validiert und nachvollziehbar sein.

---

## Strategie

- Ollama ist Standard für lokale / datenschutzfreundliche LLM-Integration.
- LLM-Anbindung muss austauschbar sein.
- Domänenlogik darf nicht von Modellverhalten oder Prompt-Details abhängen.

---

## Kapselung (verbindlich)

- LLM-Zugriffe erfolgen ausschließlich über dedizierte Services:
  - `ollama_client.py`
  - `llm_service.py`
  - domänenspezifische KI-Services

### Verboten

- direkte LLM-Aufrufe aus:
  - Views
  - DRF-Serializern
  - Django-Models

---

## Konfiguration & Betrieb

- Modell, Endpoint, Timeout, Retry über Environment oder zentrale Settings steuerbar.
- Timeouts sind verpflichtend.
- Retries müssen bewusst konfiguriert sein.
- System muss bei LLM-Ausfall stabil bleiben.

### Fallback-Verhalten (verbindlich)

Bei Fehlern:

- Timeout → definierter Fallback
- Invalid Output → verwerfen oder erneut versuchen
- Service Down → graceful degradation

Keine kritische Funktion darf ausschließlich vom LLM abhängen.

---

## Prompts (verbindlich)

- Keine Inline-Prompts in Views oder zufälligen Code-Stellen.
- Prompts müssen:
  - versionierbar sein
  - reviewbar sein
  - zentral verwaltet werden, wenn geschäftskritisch

### Struktur

- Trennung von:
  - Prompt-Definition
  - Input-Daten
  - Modell-Aufruf
  - Output-Verarbeitung

---

## Output-Handling (kritisch)

LLM-Output ist immer **untrusted input**.

### Verbindliche Regeln

- Output muss validiert werden.
- Output darf nicht direkt in:
  - Datenbank
  - Entscheidungslogik
  - Sicherheitskritische Prozesse
  übernommen werden.

### Strukturierte Outputs

- Wenn möglich:
  - JSON oder strikt strukturiertes Format verwenden
  - Parsing und Validierung erzwingen

- Fehlerhafte Outputs:
  - dürfen nicht still akzeptiert werden
  - müssen abgefangen werden

---

## Determinismus & Nachvollziehbarkeit

- Kritische LLM-Aufrufe müssen nachvollziehbar sein.
- Wichtige Parameter (Modell, Prompt-Version, Optionen) müssen reproduzierbar sein.
- Verhalten darf nicht komplett „black box“ sein.

---

## Logging & Privacy

- Logging nur mit notwendigem Kontext.
- Keine sensiblen Daten loggen:
  - PII
  - Secrets
  - Geschäftsgeheimnisse
- LLM-Inputs und Outputs nur anonymisiert oder reduziert loggen, wenn notwendig.

---

## Ressourcen & Performance

- LLM-Aufrufe sind teuer (CPU, RAM, Latenz).
- Keine unnötigen oder redundanten Aufrufe.
- Parallelität begrenzen, wenn notwendig.
- Große Prompts vermeiden.
- Response-Zeiten berücksichtigen.

---

## Feature-Design

- LLM-Features müssen deaktivierbar sein.
- Core-System darf nicht von LLM abhängen.
- LLM ergänzt Funktionalität, ersetzt sie nicht.

---

## Sicherheit

- LLM darf keine sicherheitskritischen Entscheidungen allein treffen.
- Keine automatische Ausführung von LLM-generierten Aktionen ohne Validierung.
- Prompt Injection berücksichtigen und mitigieren.
- Input-Daten validieren, bevor sie an das Modell gesendet werden.

---

## Tests

- Standard: LLM wird gemockt.
- Deterministische Tests bevorzugen.
- Integrationstests nur gezielt und kontrolliert gegen reale Instanzen.
- Prompt- und Output-Parsing-Logik muss testbar sein.

---

## Verbotene Muster

- Direkte LLM-Aufrufe in Views oder Serializern
- Unvalidierter Output
- Inline-Prompts ohne Struktur
- Harte Kopplung an ein Modell
- LLM als alleinige Entscheidungsinstanz
- Fehlendes Fallback-Verhalten
- Unkontrollierte Ressourcen-Nutzung