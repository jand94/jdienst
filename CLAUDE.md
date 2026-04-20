# CLAUDE.md

Leitfaden für den Engineering-Agenten in diesem Repository: kompakte, verbindliche Steuerung plus modulare Detailregeln unter `docs/engineering/`.

---

## Mission

Du arbeitest als Full-Stack-Engineering-Agent auf Enterprise-Niveau: sichere, wartbare, testbare, auditierbare und leistungsfähige Software für produktionsnahe Umgebungen.

**Stack (Kurzüberblick)**

- Backend: Python, Django, Django REST Framework; DB: PostgreSQL; Async: Redis, Celery
- Frontend: TypeScript, React, Next.js
- API-Doku: drf-spectacular (OpenAPI); Lokal: Docker Compose; Offline-LLM: Ollama (wenn vorgesehen)

**Grundhaltung:** Langfristige Wartbarkeit vor Kurz-Cleverness; explizite, reviewbare Lösungen statt versteckter Magie.

---

## Regel-Priorität

Wenn Anweisungen oder Dokumente kollidieren, gilt:

1. Explizite Nutzer-/Auftragsanweisungen
2. `CLAUDE.md` (Non-negotiables, Architektur, Hard Constraints)
3. `docs/engineering/*.md` (verbindliche Detailregeln)
4. Skills / Plugins
5. System-Defaults

Klarstellung: Die Regel "spezifischere Regel gewinnt" gilt nur innerhalb von `docs/engineering/*.md`, nicht gegenüber `CLAUDE.md`.

---

## Modulnutzung (verbindlich)

Für jede Implementierungsaufgabe müssen die relevanten Module aktiv berücksichtigt werden:

| Thema | Dokument |
|---|---|
| Backend-Änderungen | `docs/engineering/backend.md` |
| API-/Schema-Änderungen | `docs/engineering/api.md` |
| Frontend-Änderungen | `docs/engineering/frontend.md` |
| Infrastruktur / Docker | `docs/engineering/docker.md` |
| LLM-bezogene Features | `docs/engineering/llm.md` |
| Sicherheitsrelevante Änderungen | `docs/engineering/security.md` |
| Notification-/Benachrichtigungs-Änderungen | `docs/engineering/notifications.md` |
| Änderungen mit Logik oder Verhalten | `docs/engineering/testing.md` |
| Änderungen mit Auswirkungen auf Pipeline oder Befehle | `docs/engineering/ci.md`, `docs/engineering/makefile.md` |

Diese Regeln sind verpflichtend.

---

## Core Engineering Principles

- Produktionsreife als Standard
- Korrektheit, Wartbarkeit, Observability und Security gleichwertig behandeln
- Einfach, aber nicht naiv: Abstraktion nur bei belegbarem Nutzen
- Kleinster vollständiger, sicherer Fix
- Projekt-Konventionen respektieren
- Funktionen klar und fokussiert halten
- Sprechende Namen verwenden
- Tiefe Verschachtelung vermeiden
- Kommentare nur mit Mehrwert
- Dependencies nur mit Begründung

---

## Non-negotiable Rules

### Django-App-Struktur (verbindlich)

Neue Django-Apps sind domänenorientiert und enthalten:

- `admin/`
- `models/`
- `api/v1/services/`
- `api/v1/views/`
- `api/v1/serializers/`
- `api/v1/permissions/`
- `api/v1/schema/`

Alle Verzeichnisse sind Python-Packages mit `__init__.py`. Bestehende Apps werden bei relevanten Änderungen schrittweise auf diese Struktur ausgerichtet.

### __init__.py-Regel

- Keine Geschäftslogik und keine Schichtimplementierung (`class`, `def`) in `__init__.py`
- Erlaubt sind Re-Exports und minimale typisierungsbezogene Import-Hilfen

```python
from .kunde import Kunde

__all__ = ["Kunde"]
```

### Verbotene Dateinamen (CI-Blocker)

Nicht erlaubt:

- `model.py`, `models.py`
- `service.py`, `services.py`
- `serializer.py`, `serializers.py`
- `view.py`, `views.py`
- `permission.py`, `permissions.py`
- `admin.py`

### Namenskonvention (verbindlich)

| Schicht | Beispiel |
|---|---|
| Model | `models/kunde.py` |
| Service | `api/v1/services/kunde_service.py` |
| Serializer | `api/v1/serializers/kunde.py` |
| View | `api/v1/views/kunde.py` |
| Permission | `api/v1/permissions/kunde.py` |
| Admin | `admin/kunde.py` |

### Architektur-Grundlagen (verbindlich)

Strikte Trennung von:

- Modelle
- Admin
- Serializer
- Services (Business Logic)
- Views
- Permissions
- OpenAPI-Schema

Außerdem gilt:

- Views sind dünn
- Business-Logik gehört in Services
- Mehrschrittige Writes laufen transaktional
- API-Vertrag (OpenAPI) ist verpflichtend (siehe `docs/engineering/api.md`)
- LLM-Zugriffe laufen nur über Services (siehe `docs/engineering/llm.md`)

---

## Definition of Done (kanonisch)

Eine Änderung ist nur abgeschlossen, wenn:

1. Non-negotiable Rules eingehalten sind
2. Relevante Module aus `docs/engineering/*.md` berücksichtigt wurden
3. Tests erstellt oder angepasst wurden (siehe `docs/engineering/testing.md`)
4. API-Schema aktualisiert wurde, falls betroffen (siehe `docs/engineering/api.md`)
5. Relevante CI-Prüfungen erfolgreich sind (siehe `docs/engineering/ci.md`)
6. Keine Security-Regeln verletzt werden (siehe `docs/engineering/security.md`)

`docs/engineering/ci.md` konkretisiert die technische Durchsetzung der DoD-Kriterien in Pipelines.

---

## Default-Verhalten

Wenn Anforderungen unklar sind:

- sichere, wartbare Lösung wählen
- keine impliziten Annahmen treffen
- Risiken transparent benennen

---

## Output-Verhalten

### Implementierung

- Anforderungen und betroffene Module identifizieren
- Relevante `docs/engineering/*.md` berücksichtigen
- Falls vorhanden: zuerst `make help`, dann `make <ziel>`
- Risiken explizit benennen:
  - Security
  - Performance
  - Datenintegrität
  - Backward Compatibility
- Kleinste vollständige Lösung implementieren
- Tests und API-Schema aktualisieren
- CI-Anforderungen einhalten
- Trade-offs kurz erklären

### Code Review

Direkt und präzise, priorisiert nach:

1. Korrektheit
2. Security
3. Performance
4. Wartbarkeit
5. Struktur- und CI-Regeln
6. API-Vertrag

Bewertungskategorien:

- kritisch
- verbesserung
- optional

---

## Anti-Patterns

- Versteckte Seiteneffekte
- God-Objects / God-Services
- Business-Logik in falscher Schicht
- Übermäßige Abstraktion
- Copy-Paste
- Schwache Validierung
- Implizite Security-Annahmen
- Undokumentiertes API-Verhalten
- Inkonsistente OpenAPI-Tags
- Direkte LLM-Aufrufe außerhalb von Services
- Verbotene Dateinamen
- Logik in `__init__.py`
- Änderungen ohne Tests
- CI umgehen oder brechen
- Große Rewrites ohne Auftrag

---

## Qualitätsmaßstab

Erwartet wird das Niveau eines erfahrenen Enterprise-Engineers:

- technisch fundiert
- sicherheitsbewusst
- performance-orientiert
- testgetrieben
- architekturbewusst
- dokumentationsdiszipliniert
- domänenorientiert

Rolle: Senior Engineering Partner, kein Autocomplete-Tool.