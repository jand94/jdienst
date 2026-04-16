# Engineering: Agents Runtime Pack

Diese Dateien operationalisieren `docs/engineering/agents.md` in wiederverwendbare Artefakte fuer den Alltag.

## Inhalt

- `solution-architect.prompt.md`
- `backend-implementer.prompt.md`
- `api-contract-guardian.prompt.md`
- `frontend-implementer.prompt.md`
- `security-reviewer.prompt.md`
- `test-engineer.prompt.md`
- `infra-compose-engineer.prompt.md`
- `code-reviewer.prompt.md`
- `llm-integrator.prompt.md` (optional)
- `ci-governor.prompt.md` (optional)
- `manifest.json` (maschinenlesbare Agenten-Metadaten)
- `handover-template.md`

## Nutzung

1. Aufgabe mit `solution-architect` zuschneiden.
2. Passenden Implementer starten (`backend-implementer` und/oder `frontend-implementer`).
3. Bei API-Aenderung `api-contract-guardian` nachziehen.
4. `test-engineer` und `security-reviewer` ausfuehren.
5. Bei Infra-Change `infra-compose-engineer` einbinden.
6. Abschliessend `code-reviewer` fuer Merge-Entscheidung.

## Verpflichtende Referenzen pro Agent

Jeder Agent-Prompt setzt voraus:

- `CLAUDE.md`
- relevante Regeln aus `docs/engineering/*.md`
- Handover im Format aus `handover-template.md`

## Hinweis

Die Promptdateien sind bewusst knapp gehalten, damit sie in Agent-Tools direkt eingefuegt oder als System-/Task-Prompt verwendet werden koennen.

`manifest.json` kann fuer Automatisierung genutzt werden (z. B. zur Agentenauswahl, Workflow-Steuerung und Validierung verpflichtender Referenzdokumente).
