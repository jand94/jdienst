"""Validate docs/engineering/agents/manifest.json integrity.

Checks:
- Manifest JSON can be parsed.
- Required top-level fields are present.
- Referenced files exist.
- Agent IDs are unique and structurally valid.
- Workflow steps only reference known agent IDs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "docs/engineering/agents/manifest.json"


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _check_path(path_value: str, label: str, errors: list[str]) -> None:
    candidate = REPO_ROOT / path_value
    if not candidate.exists():
        errors.append(f"{label} fehlt: {path_value}")


def validate_manifest(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_keys = {
        "version",
        "schemaVersion",
        "project",
        "source",
        "handoverTemplate",
        "agents",
        "workflows",
    }

    missing = sorted(required_keys - set(data.keys()))
    if missing:
        errors.append(f"Fehlende Top-Level-Felder: {', '.join(missing)}")
        return errors

    if not _is_non_empty_string(data["version"]):
        errors.append("'version' muss ein nicht-leerer String sein.")
    if not isinstance(data["schemaVersion"], int):
        errors.append("'schemaVersion' muss eine Integer-Zahl sein.")
    if not _is_non_empty_string(data["project"]):
        errors.append("'project' muss ein nicht-leerer String sein.")

    if _is_non_empty_string(data["source"]):
        _check_path(data["source"], "source", errors)
    else:
        errors.append("'source' muss ein nicht-leerer String sein.")

    if _is_non_empty_string(data["handoverTemplate"]):
        _check_path(data["handoverTemplate"], "handoverTemplate", errors)
    else:
        errors.append("'handoverTemplate' muss ein nicht-leerer String sein.")

    agents = data["agents"]
    if not isinstance(agents, list) or not agents:
        errors.append("'agents' muss eine nicht-leere Liste sein.")
        return errors

    known_agent_ids: set[str] = set()
    for idx, agent in enumerate(agents):
        prefix = f"agents[{idx}]"
        if not isinstance(agent, dict):
            errors.append(f"{prefix} muss ein Objekt sein.")
            continue

        for field in ("id", "optional", "promptFile", "requiredDocs"):
            if field not in agent:
                errors.append(f"{prefix} fehlt Feld '{field}'.")

        agent_id = agent.get("id")
        if not _is_non_empty_string(agent_id):
            errors.append(f"{prefix}.id muss ein nicht-leerer String sein.")
        else:
            if agent_id in known_agent_ids:
                errors.append(f"Doppelte Agent-ID: {agent_id}")
            known_agent_ids.add(agent_id)

        if not isinstance(agent.get("optional"), bool):
            errors.append(f"{prefix}.optional muss boolean sein.")

        prompt_file = agent.get("promptFile")
        if _is_non_empty_string(prompt_file):
            _check_path(prompt_file, f"{prefix}.promptFile", errors)
        else:
            errors.append(f"{prefix}.promptFile muss ein nicht-leerer String sein.")

        required_docs = agent.get("requiredDocs")
        if not isinstance(required_docs, list) or not required_docs:
            errors.append(f"{prefix}.requiredDocs muss eine nicht-leere Liste sein.")
        else:
            for doc_idx, doc_path in enumerate(required_docs):
                if not _is_non_empty_string(doc_path):
                    errors.append(f"{prefix}.requiredDocs[{doc_idx}] ist ungueltig.")
                    continue
                _check_path(doc_path, f"{prefix}.requiredDocs[{doc_idx}]", errors)

    workflows = data["workflows"]
    if not isinstance(workflows, dict) or not workflows:
        errors.append("'workflows' muss ein nicht-leeres Objekt sein.")
        return errors

    for wf_name, steps in workflows.items():
        if not isinstance(steps, list) or not steps:
            errors.append(f"Workflow '{wf_name}' muss eine nicht-leere Liste sein.")
            continue

        for step_idx, step in enumerate(steps):
            if not _is_non_empty_string(step):
                errors.append(f"Workflow '{wf_name}' Schritt {step_idx} ist ungueltig.")
                continue

            options = [opt.strip() for opt in step.split("|") if opt.strip()]
            if not options:
                errors.append(
                    f"Workflow '{wf_name}' Schritt {step_idx} enthaelt keine Agent-ID."
                )
                continue
            unknown = [opt for opt in options if opt not in known_agent_ids]
            if unknown:
                errors.append(
                    f"Workflow '{wf_name}' Schritt {step_idx} referenziert "
                    f"unbekannte Agent-ID(s): {', '.join(unknown)}"
                )

    return errors


def main() -> int:
    if not MANIFEST_PATH.exists():
        print(f"ERROR: Manifest nicht gefunden: {MANIFEST_PATH}")
        return 1

    try:
        raw = MANIFEST_PATH.read_text(encoding="utf-8")
        manifest = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Ungueltiges JSON in {MANIFEST_PATH}: {exc}")
        return 1
    except OSError as exc:
        print(f"ERROR: Manifest konnte nicht gelesen werden: {exc}")
        return 1

    if not isinstance(manifest, dict):
        print("ERROR: Manifest muss ein JSON-Objekt sein.")
        return 1

    errors = validate_manifest(manifest)
    if errors:
        print("ERROR: Manifest-Validierung fehlgeschlagen.")
        for entry in errors:
            print(f"- {entry}")
        return 1

    print("OK: Manifest ist gueltig.")
    print(f"- Datei: {MANIFEST_PATH.relative_to(REPO_ROOT)}")
    print(f"- Agenten: {len(manifest['agents'])}")
    print(f"- Workflows: {len(manifest['workflows'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
