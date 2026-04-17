# Documentation Index

## Zweck

Dieses Verzeichnis trennt verbindliche Engineering-Regeln von domänenspezifischer Backend-Dokumentation.

## Schnellstart

1. Regeln lesen: `docs/engineering/README.md`
2. Projektleitplanken lesen: `CLAUDE.md`
3. Domänenspezifische Inhalte in `docs/backend/` nachschlagen

## Struktur

- `docs/engineering/`: verbindliche Standards für Architektur, API, Testing, Security und CI.
- `docs/backend/`: fachliche und technische Doku je Backend-App.
- `docs/engineering/agents/`: Prompt- und Agent-Artefakte für AI-Workflows.

## Empfohlene Lesepfade

- **Backend-Feature umsetzen:** `CLAUDE.md` -> `docs/engineering/backend.md` -> `docs/engineering/api.md` -> passende Datei in `docs/backend/<app>/`.
- **Audit/Compliance-Themen:** `docs/backend/common/README.md` -> `docs/backend/common/audit-basics.md` -> `docs/backend/common/audit-operations.md`.
- **API-Vertrag prüfen:** `docs/engineering/api.md` und `/api/schema/` im laufenden Backend.
