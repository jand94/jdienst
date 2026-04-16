# Engineering: GitHub Actions & CI

Ergänzt `CLAUDE.md`. CI ist Teil des Qualitätsvertrags: Was im Default-Branch oder vor Merge erwartet wird, muss reproduzierbar und in den Workflows nachvollziehbar sein.

---

## Grundsatz

- CI ist der verbindliche Qualitäts- und Durchsetzungsmechanismus für projektweite Engineering-Regeln.
- Was lokal, in der Dokumentation oder in `Makefile` / Compose als kanonischer Workflow definiert ist, soll in CI konsistent abgebildet werden.
- Ein Merge ist nur dann belastbar, wenn die relevanten CI-Prüfungen erfolgreich, reproduzierbar und nachvollziehbar sind.

---

## Kanonischer Ort

- Workflow-Definitionen liegen in `.github/workflows/*.yml` oder `.github/workflows/*.yaml`.
- Was für die Pipeline relevant ist, muss im Repository sichtbar und versioniert sein.
- Keine versteckten oder nur mündlich bekannten CI-Schritte.
- Relevante Befehle sollen nach Möglichkeit über:
  - `Makefile`
  - dokumentierte Projekt-Skripte
  - definierte Compose-Setups
  abgebildet werden.

---

## Ziele der Pipeline

- Früh scheitern: schnelle Checks vor teuren Jobs ausführen.
- Determinismus: feste Runner, gepinnte Tool-Versionen und nachvollziehbare Setup-Schritte verwenden.
- Parität zu lokal: dieselben Befehle wie in README, `docker.md`, `testing.md` und — falls vorhanden — `makefile.md` verwenden.
- Reproduzierbarkeit: CI-Ergebnisse sollen lokal möglichst konsistent nachvollziehbar sein.
- Reviewbarkeit: Workflows sollen lesbar, modular und wartbar sein.

---

## Definition of Done

Ein PR oder Merge gilt nur dann als abgeschlossen, wenn:

- alle verpflichtenden CI-Jobs erfolgreich sind
- Linting- und statische Prüfungen erfolgreich sind
- relevante Tests erfolgreich sind
- Typprüfungen erfolgreich sind, falls im Projekt aktiviert
- Sicherheitsrelevante Checks erfolgreich sind, falls im Projekt aktiviert
- keine projektweiten Non-negotiables aus `CLAUDE.md` oder den Engineering-Dokumenten verletzt werden

---

## Determinismus und Versionierung

- Runner sollen bewusst gewählt und nicht unnötig wechselhaft konfiguriert werden.
- Python-, Node-, Paketmanager- und Tool-Versionen sollen gepinnt oder kontrolliert sein.
- GitHub Actions sollen, wo sinnvoll, über feste Versionen oder SHAs referenziert werden.
- Unkontrollierte „latest“-Abhängigkeiten in kritischen Workflow-Bausteinen sind zu vermeiden.
- Die Pipeline darf sich nicht auf implizites Runner-Verhalten verlassen.

---

## Job-Struktur

- Schnelle Jobs wie Lint, Format-Checks und statische Analysen sollen früh in der Pipeline ausgeführt werden.
- Unabhängige Jobs sollen parallel laufen, wenn das die Pipeline beschleunigt.
- Teure Jobs sollen nur dann blockierend sein, wenn sie für den Qualitätsvertrag relevant sind.
- Pipeline-Struktur soll nachvollziehbar und nicht unnötig verschachtelt sein.
- Wiederholte Setup-Schritte sollen nach Möglichkeit zentralisiert oder wiederverwendbar gemacht werden.

---

## Typische Jobs

Projektspezifisch ausprägen; typische Bausteine sind:

| Bereich | Typische Prüfungen |
|---------|--------------------|
| Backend | `ruff`, `flake8`, `mypy` (falls genutzt), `pytest` |
| Frontend | `eslint`, `tsc --noEmit`, Unit-Tests |
| Repo-weit | Verbotene Pfade, Namensregeln, Secret-Scans, Struktur-Checks |
| API | Schema-Checks, OpenAPI-Generierung, Breaking-Checks (falls definiert) |
| Security | Dependency-Checks, Secret-Scans, Policy-Checks |
| CI selbst | Workflow-Linting oder Validierung, wenn sinnvoll |

Details zu Tests: `testing.md`  
Lokaler Stack: `docker.md`  
Makefile-Konventionen: `makefile.md`  
API-Regeln: `api.md`

---

## Parität zu lokaler Entwicklung

- Wenn eine Root-`Makefile` existiert, sollen CI-Workflows bevorzugt `make`-Ziele aufrufen.
- Beispiel: `make lint`, `make test`, `make ci`.
- Wenn keine `Makefile` existiert, sollen dieselben dokumentierten Befehle verwendet werden, die lokal für Team und Agenten kanonisch sind.
- CI darf keine völlig andere Befehlskette verwenden, wenn dieselbe Aufgabe bereits lokal standardisiert ist.
- Ziel ist, dass „grün lokal, rot in CI“ selten und erklärbar bleibt.

---

## Caching

- Abhängigkeiten wie Python- oder Node-Pakete sollen, wo sinnvoll, gecached werden.
- Caching muss deterministisch und korrekt invalidierbar sein.
- Caches dürfen Build-Probleme nicht verschleiern.
- Caching ist ein Performance-Werkzeug, kein Ersatz für saubere Reproduzierbarkeit.

---

## Geheimnisse und Umgebungen

- Keine Secrets im Klartext im Repository.
- GitHub Secrets und GitHub Environments sind für Tokens, Credentials und Deploy-Keys zu verwenden.
- Secrets dürfen nicht in Logs, Artefakten oder Fehlermeldungen auftauchen.
- Test- oder Service-Abhängigkeiten in CI sind bewusst zu definieren, z. B.:
  - GitHub Actions Service Containers
  - Compose-basierte Testdienste
  - SQLite nur, wenn das Projekt dies explizit vorsieht
- Sicherheitskritische Umgebungen sollen klar getrennt und kontrolliert sein.

---

## Artefakte und Debugbarkeit

- Fehlgeschlagene Jobs müssen ausreichend Logs liefern, um Ursachen nachvollziehen zu können.
- Test-Reports, Coverage-Daten oder relevante Artefakte sollen bereitgestellt werden, wenn sie den Debugging- oder Review-Prozess verbessern.
- Debugging-Hilfen dürfen keine sensiblen Daten preisgeben.
- Pipeline-Fehler müssen reproduzierbar untersuchbar sein.

---

## Pull Requests und Merge-Disziplin

- Änderungen an Workflows oder an den in CI ausgeführten Befehlen sollen im selben PR wie die fachliche Änderung erfolgen oder in einem klar beschriebenen, zeitnahen Follow-up.
- Wenn die Pipeline fehlschlägt, ist die Ursache zu beheben oder der Scope des PRs anzupassen.
- CI-Regeln dürfen nicht stillschweigend umgangen werden.
- Änderungen an `CLAUDE.md` oder `docs/engineering/` dürfen nicht als Ersatz für fehlende technische Umsetzung in der Pipeline missbraucht werden.
- Branch-Protection und verpflichtende Status-Checks sind zu respektieren, wenn das Repository sie verwendet.

---

## Harte Repo-Regeln in CI spiegeln

Wo sinnvoll und wirtschaftlich, sollen projektweite Regeln automatisiert geprüft werden, insbesondere:

- verbotene generische Dateinamen
- Django-Pflichtstruktur und Paketstruktur
- `__init__.py`-Regeln
- API-Schema-Konsistenz und Generierung
- Security- oder Secret-Checks
- Namens- und Strukturregeln aus `CLAUDE.md`

Regeln, die im Engineering-System als Non-negotiable definiert sind, sollen nach Möglichkeit technisch durch CI abgesichert werden.

---

## API und Schema in CI

- Wenn OpenAPI-Schema Teil des Qualitätsvertrags ist, muss die Pipeline dessen Konsistenz prüfen.
- Schema-Generierung, Validierung oder Breaking-Checks sollen automatisiert erfolgen, wenn das Team dies festgelegt hat.
- API-Dokumentation darf nicht stillschweigend vom tatsächlichen Verhalten abweichen.
- Änderungen an API-Verhalten ohne begleitende Schema-Anpassung sollen nach Möglichkeit erkennbar gemacht werden.

---

## Beziehung zur Makefile

- Sobald eine Root-`Makefile` existiert, soll CI wo sinnvoll deren Ziele verwenden.
- `make ci` ist ein bevorzugtes Muster, wenn das Projekt einen lokalen CI-ähnlichen Ablauf definiert.
- Einzelne Jobs können gezielt `make lint`, `make test`, `make test-be`, `make test-fe` oder ähnliche kanonische Ziele nutzen.
- CI und lokale Entwickler-Workflows sollen dieselbe Befehlsfassade verwenden, um Drift zu reduzieren.

---

## Einführung oder Änderung von CI

- Existiert noch kein Workflow im Repository, sollen beim Einführen von GitHub Actions auch `CLAUDE.md` und relevante Engineering-Dokumente aktualisiert werden.
- Neue CI-Regeln müssen mit bestehender Dokumentation konsistent sein.
- Änderungen an CI sind wie produktiver Code zu behandeln:
  - reviewbar
  - nachvollziehbar
  - risikoarm
  - dokumentiert, wenn relevant

---

## Verbotene Muster

- versteckte CI-Logik außerhalb des Repositories
- ungepinnte kritische Tool- oder Action-Versionen ohne Grund
- lokale Standardbefehle und CI-Befehle driften auseinander
- Secrets im Workflow, Repo oder Log-Ausgaben
- stillschweigendes Deaktivieren relevanter Checks
- CI-Umgehung durch bloße Dokumentationsänderungen ohne technische Absicherung
- Pipeline-Schritte, die nicht reproduzierbar oder nicht erklärbar sind