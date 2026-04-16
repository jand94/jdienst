# Engineering: CI (GitHub Actions)

Ergaenzt `CLAUDE.md`. Dieses Dokument ist der Owner fuer Pipeline-Policy und Qualitaetsgates im Repository.

---

## Zweck und Scope

- Definiert, wie Qualitaet in CI verifiziert wird.
- Sichert Reproduzierbarkeit zwischen lokalem Workflow und Pipeline.
- Legt Regeln fuer Workflow-Aenderungen und Merge-Readiness fest.

---

## Verbindliche Regeln

### Ort und Nachvollziehbarkeit

- Workflow-Dateien liegen unter `.github/workflows/*.yml` (oder `.yaml`).
- CI-relevante Regeln muessen im Repo nachvollziehbar sein, nicht nur lokal bekannt.

### Pipeline-Prinzipien

- Schnelle Checks moeglichst frueh ausfuehren.
- Toolchain-Versionen und Laufumgebung reproduzierbar halten.
- Pipeline-Befehle mit dokumentierten lokalen Befehlen abstimmen.

### Qualitaetsgates

- Lint/Format/Tests als verbindliche Gates definieren, passend zum Projektstand.
- Aenderungen an zentralen Regeln muessen die relevanten CI-Checks beruecksichtigen.
- Rote Pipeline wird behoben oder bewusst durch Scope-Anpassung aufgeloest, nicht ignoriert.

### Workflow-Aenderungen

- Aenderungen an Workflows im selben PR oder mit klar referenziertem Folge-PR ausliefern.
- Geheimnisse ueber GitHub Secrets/Environments verwalten.

---

## Verbotene Muster

- Pipeline-Regeln implizit ohne Workflow-Datei.
- Greenwashing durch Auslassen relevanter Checks.
- CI- und Lokalbefehle dauerhaft auseinanderlaufen lassen.

---

## Abgrenzung zu anderen Modulen

- `docker.md` regelt lokale Runtime/Compose, nicht Pipeline-Policy.
- `makefile.md` regelt Befehls-Fassade, nicht CI-Governance.
- `testing.md` definiert Testinhalte; `ci.md` definiert deren Ausfuehrung als Gate.
