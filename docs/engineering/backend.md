# Engineering: Backend (Django & DRF)

Ergänzt `CLAUDE.md`. Bei Widerspruch gilt die Regel-Priorität aus `CLAUDE.md`.

---

## Schichten & Verantwortlichkeiten

Klar trennen:

- Modelle  
- Admin-Registrierung (`admin/`)  
- Serializer (Validierung, Repräsentation)  
- **Services (Pflicht für nicht-triviale Logik)**  
- Views / Endpoints  
- Permissions  
- OpenAPI-Schema (`api/v1/schema/`)  

### Verbindliche Regeln

- Views sind **immer dünn**.
- Serializer enthalten **keine Geschäftslogik und keine Orchestrierung**.
- **Service-Layer ist verpflichtend**, wenn:
  - mehr als ein Modell beteiligt ist
  - Side Effects auftreten (z. B. externe Calls, Celery)
  - mehrere Schritte orchestriert werden
  - Transaktionen benötigt werden
- Query-Logik gehört nicht in Views → ggf. in dedizierte Selector-/Query-Funktionen auslagern.

---

## Service Layer

- Services kapseln Geschäftslogik und Workflows.
- Services sind deterministisch, testbar und klar abgegrenzt.
- Keine direkten HTTP-, Request- oder Response-Abhängigkeiten.
- Keine versteckten Side Effects.

### Struktur

- `api/v1/services/<domain>_service.py`
- Funktionen oder klar strukturierte Service-Klassen
- Klare Eingaben und Rückgaben

---

## Django-Modelle

- Modelle repräsentieren Domänenzustand, nicht Workflows.
- Keine Orchestrierung über mehrere Aggregate hinweg.
- Constraints und Integrität möglichst auf DB-Ebene.
- Indizes bewusst setzen.

---

## Django REST Framework

- APIs sind konsistent, vorhersehbar und versioniert.
- Serializer:
  - nur Validierung und Transformation
  - keine DB-Queries außer trivialen Lookups
  - keine Side Effects
- Views:
  - orchestrieren minimal
  - delegieren an Services
- Permissions:
  - liegen in `api/v1/permissions/`
  - sind explizit und nicht implizit vererbt
  - keine versteckten Default-Policies

---

## Fehlerhandling

- Keine ungefangenen Exceptions in API-Schichten.
- Business-Fehler klar von Systemfehlern trennen.
- Konsistente API-Fehlerstruktur verwenden.
- Keine sensiblen Daten in Fehlermeldungen.

---

## Datenbank & Queries

- N+1 ist standardmäßig zu vermeiden.
- `select_related` / `prefetch_related` aktiv einsetzen.
- Komplexe Read-Queries nicht in Views implementieren.
- Querysets nicht unnötig früh evaluieren.
- Bulk-Operationen nutzen, wenn sinnvoll.

### Query-Struktur

- Komplexe Query-Logik optional in dedizierte Funktionen auslagern:
  - `selectors/`
  - oder innerhalb Services klar gekapselt

---

## Transaktionen

- Mehrschrittige Writes → **immer bewusst transactional**
- Transaktionen gehören in den Service-Layer
- Keine impliziten Transaktionen in Views oder Serializer

---

## Performance (Backend)

- DB-Zugriffe minimieren
- Serialisierungskosten beachten
- Keine unnötigen Roundtrips
- Caching nur mit klarer Invalidierungsstrategie

---

## Background Jobs (Celery)

- Tasks sind idempotent
- Retries bewusst konfiguriert
- Keine Business-Logik in Task-Definition selbst → delegieren an Services
- Logging ohne sensitive Daten

---

## Auditierbarkeit & Observability

- Wichtige Zustandsänderungen nachvollziehbar machen
- Strukturierte Logs bevorzugen
- Fehler müssen reproduzierbar sein
- Kritische Flows observierbar machen

---

## Refactoring

- Nur bei echtem Mehrwert
- Keine großflächigen Nebenbei-Änderungen
- Verhalten stabil halten
- Kleine, reviewbare Diffs

---

## Enterprise-Hinweise

- Explizitheit vor Magie
- Stabilität vor Hype
- Wartbarkeit vor Cleverness
- Systeme für Betrieb und Audit denken

---

## Verbotene Muster (Backend)

- Business-Logik in Serializer
- DB-Zugriffe in Views ohne Grund
- Services umgehen
- Fat Models
- Implizite Permissions
- Unstrukturierte Query-Logik