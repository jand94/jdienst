# base

Lokaler Full-Stack-Workspace mit Django-Backend, Next.js-Frontend und PostgreSQL ueber Docker Compose.

## Voraussetzungen

- Docker Desktop (inkl. `docker compose`)
- Git
- Optional fuer lokale Tooling-Aufrufe ohne Container:
  - Python 3.12+
  - Node.js 22+
  - GNU Make

## Schnellstart

Im Repository-Root:

```bash
make bootstrap
```

Das erledigt:

- `.env` aus `.env.example` anlegen (falls noch nicht vorhanden)
- den gesamten Stack bauen und starten

Standard-URLs:

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000](http://localhost:8000)
- Django Admin: [http://localhost:8000/admin](http://localhost:8000/admin)

## Wichtige Make-Targets

- `make help` - alle verfuegbaren Targets anzeigen
- `make init-env` - `.env` initialisieren
- `make up` - Stack im Vordergrund starten
- `make up-d` - Stack im Hintergrund starten
- `make down` - Stack stoppen
- `make logs` - Logs aller Services folgen
- `make be-shell` - Shell im Backend-Container
- `make fe-shell` - Shell im Frontend-Container
- `make migrate` - Django Migrationen ausfuehren
- `make test-be` - Backend-Tests ausfuehren
- `make ci` - lokaler CI-aehnlicher Lauf (Policy + Conventions + Backend-Tests)

## Notification-Ops (neu)

Fuer den Notification-Betrieb stehen folgende Diagnose- und Recovery-Befehle zur Verfuegung:

- `make notification-health` - Pipeline-/SLO-Snapshot als JSON
- `make notification-dispatch` - faellige Deliveries sofort verarbeiten
- `make notification-digest-build` - Digest-Backlog aufbauen
- `make notification-digest-dispatch` - ausstehende Digests versenden
- `make notification-pipeline-recover` - Recovery-Reihenfolge (Dispatch -> Digest Build/Dispatch -> Health)
- `make notification-seed-fixture TENANT_SLUG=<slug> USER_EMAIL=<mail>` - Diagnosedaten fuer Notification-Flows

Details:

- `docs/backend/notification/README.md`
- `docs/backend/notification/operations-runbook.md`

## Projektstruktur

- `backend/` - Django App
- `frontend/` - Next.js App (App Router)
- `docs/engineering/` - verbindliche Engineering-Regeln
- `.github/workflows/ci.yml` - CI-Pipeline
- `scripts/` - Validierungs- und Hilfsskripte

## Responsives Frontend

Fuer responsive Entscheidungen gelten zentral:

- `frontend/lib/responsiveness.ts`
  - typisierte Breakpoints + Media-Query-Utilities
- `frontend/lib/responsive-tokens.ts`
  - zentrale, wiederverwendbare Klassen-Tokens fuer responsives Verhalten
- `frontend/hooks/use-media-query.ts` und `frontend/hooks/use-breakpoint.ts`
  - SSR-sichere Runtime-Hooks fuer responsives Laufzeitverhalten

Verwendungsregeln:

- Tailwind-Utilities direkt fuer reine Darstellung (`sm:`, `md:`, `lg:`)
- `responsiveTokens` fuer wiederkehrende Klassenkombinationen
- Breakpoint-Hooks nur fuer echte Laufzeitlogik

Details: `docs/engineering/frontend-responsiveness.md`

## Engineering-Regeln

Bitte vor Aenderungen lesen:

- `docs/engineering/README.md`
- `docs/engineering/frontend.md`
- `docs/engineering/backend.md`
- `docs/engineering/testing.md`
- `docs/engineering/security.md`
- `docs/engineering/ci.md`

Die Regeln sind verbindlich und ergaenzen projektweite Vorgaben.
