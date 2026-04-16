# Engineering: Makefile-Konvention

Ergaenzt `CLAUDE.md`. Dieses Dokument ist der Owner fuer die Nutzung einer optionalen Root-`Makefile` als Befehls-Fassade.

---

## Zweck und Scope

- Einheitliche Einstiegspunkte fuer wiederkehrende Befehle.
- Weniger Drift zwischen README, lokaler Nutzung und CI.
- Vorhersagbare Bedienung fuer Team und Agenten.

---

## Verbindliche Regeln

### Grundsatz

- Die Regel gilt, **wenn** eine Root-`Makefile`/`makefile` existiert.
- Existiert keine `Makefile`, bleiben README und Engineering-Docs massgeblich.

### Zielstruktur

- Oeffentliche Ziele klar benennen und stabil halten.
- `make help` als bevorzugter Einstieg fuer kanonische Targets.
- Uebliche Ziele: `up`, `down`, `build`, `logs`, `shell`, `migrate`, `test`, `lint`, `ci`.

### Implementierung

- Keine Secrets hardcoden.
- `.PHONY` fuer nicht-dateibasierte Ziele setzen.
- Exit-Codes korrekt propagieren.
- Ziele moeglichst deterministisch und wiederholbar halten.

### Agent-Verhalten

1. Vor wiederholten Shell-Aktionen pruefen, ob eine Root-`Makefile` existiert.
2. Falls vorhanden: zuerst `make help`, dann `make <ziel>`.
3. Keine fiktive `Makefile` annehmen oder automatisch anlegen.

---

## Verbotene Muster

- Undokumentierte oeffentliche Targets.
- Irrefuehrende oder doppelte Zielnamen fuer denselben Zweck.
- Drift zwischen `Makefile`, README und CI.

---

## Abgrenzung zu anderen Modulen

- `ci.md` regelt Pipeline-Gates und Workflow-Policy.
- `docker.md` regelt Compose- und Runtime-Konventionen.
- `testing.md` regelt Testinhalte; `makefile.md` nur deren Aufruf-Fassade.
