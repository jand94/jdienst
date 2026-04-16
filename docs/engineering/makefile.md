# Engineering: Makefile als zentrale Befehls-Fassade (Konvention)

Ergänzt `CLAUDE.md`. Dieses Dokument beschreibt **wie** eine Wurzel-`Makefile` gedacht und genutzt werden soll — **nicht**, dass sie zwingend existiert. Sobald das Projekt eine `Makefile` (oder `makefile`) im **Repository-Root** einführt, gelten die folgenden Regeln für Menschen und Agenten.

---

## Zweck

- **Eine** stabile Einstiegsschicht für wiederkehrende Aufgaben: Compose, Tests, Lint, Migrationen, Hilfe.  
- **Weniger Drift:** dieselben Ziele lokal, in Doku und idealerweise in CI (`ci.md`).  
- **Vorhersagbarkeit für Agenten:** Zuerst prüfen, ob `Makefile` existiert; dann **`make <ziel>`** statt langer, einmalig zusammengeklickter Shell-Ketten.

---

## Ort und Namen

- **Pfad:** nur die zentrale Datei im Root: `Makefile` (üblich) oder `makefile`.  
- **Keine** verteilten «Mini-Makefiles» pro App als Standard — Ausnahmen nur mit Team-Abstimmung und Verweis in der Root-`Makefile` (`include` o. ä.).

---

## Pflichtziel `help` (empfohlen)

- **`make help`** (oder Default-Target `make` → `help`) listet alle öffentlichen Targets mit **kurzer** Zeile Beschreibung.  
- So ist für Agenten und neue Teammitglieder sofort sichtbar, welche Befehle kanonisch sind.

---

## Empfohlene Standard-Targets (Orientierung)

Namen sind **Vorschläge**; das Projekt kann abweichen, muss es dann in `help` klar führen.

| Ziel | Typische Bedeutung |
|------|---------------------|
| `help` | Targets + Kurzbeschreibung ausgeben |
| `up` / `down` | Stack starten / stoppen (meist Compose) |
| `build` | Images neu bauen |
| `logs` | relevante Service-Logs folgen |
| `shell` | Shell im Backend-Container (o. ä.) |
| `migrate` | Django-Migrationen anwenden |
| `test` / `test-be` / `test-fe` | Tests (gesplittet nur wenn nötig) |
| `lint` / `fmt` | Lint bzw. Format (read-only vs. schreibend trennen) |
| `ci` | lokaler «CI-ähnlicher» Durchlauf (Lint + Tests, optional Frontend) |

Compose-Details: `docker.md`. Tests: `testing.md`. Pipeline: `ci.md`.

---

## Inhaltliche Regeln für die `Makefile`

- Targets rufen vorzugsweise **`docker compose`** oder vorhandene Projekt-Skripte auf — **keine** Secrets oder Tokens in der `Makefile` hardcoden.  
- **POSIX-kompatibel** anstreben, wo möglich (`SHELL` nur setzen, wenn nötig); auf Windows: dokumentieren, ob `make` über Git Bash/WSL erwartet wird.  
- Lange Befehle in **`.PHONY:`** markieren; Zwischenziele nachvollziehbar benennen.  
- Änderungen an wiederkehrenden Befehlen: **Makefile +** Verweise in README/`docker.md` **konsistent** halten.

---

## Erwartetes Agent-Verhalten

1. Vor wiederholten Shell-Aktionen: **Existiert `Makefile` im Root?**  
2. Wenn **ja:** `make help` nutzen und anschließend **`make <ziel>`** für die Aufgabe (z. B. Tests, Stack, Lint).  
3. Wenn **nein:** weiterhin kanonische Befehle aus README und `docker.md` / `testing.md` verwenden — **keine** fiktive `Makefile` anlegen, nur weil dieses Dokument existiert (Anlage ist eine bewusste Projektentscheidung).

---

## Beziehung zu CI

GitHub Actions soll, sobald eine `Makefile` existiert, wo sinnvoll **`make ci`** oder einzelne `make`-Ziele aufrufen, damit lokal und in der Pipeline dieselbe Fassade genutzt wird (`ci.md`).
