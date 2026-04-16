# Engineering: Makefile als zentrale Befehls-Fassade

Ergänzt `CLAUDE.md`. Dieses Dokument beschreibt, wie eine zentrale `Makefile` im Repository-Root genutzt und gestaltet werden soll. Es erzwingt nicht, dass eine `Makefile` existieren muss. Sobald das Projekt eine Root-`Makefile` oder `makefile` einführt, gelten diese Regeln für Menschen und Agenten.

---

## Grundsatz

- Die `Makefile` ist die bevorzugte Befehls-Fassade für wiederkehrende Entwicklungs- und Qualitätsaufgaben.
- Ziel ist eine stabile, leicht merkbare und konsistente Einstiegsschicht für lokale Entwicklung, CI und Teamprozesse.
- Die `Makefile` reduziert Drift zwischen README, lokaler Nutzung, Docker-Workflows und CI.
- Wiederkehrende Aufgaben sollen über kanonische `make`-Ziele statt über ad-hoc Shell-Ketten ausführbar sein.

---

## Zweck

Die `Makefile` dient insbesondere dazu:

- häufige Entwickleraufgaben zu standardisieren
- lokale Workflows reproduzierbar zu machen
- CI und lokale Nutzung auf dieselben Befehle auszurichten
- die Bedienung des Projekts für neue Teammitglieder und Agenten vorhersehbar zu machen
- Compose, Tests, Linting, Builds und Hilfsbefehle zentral auffindbar zu machen

---

## Ort und Dateiname

- Die zentrale `Makefile` liegt ausschließlich im Repository-Root.
- Zulässige Namen sind:
  - `Makefile`
  - `makefile`
- Verteilte Mini-Makefiles in Teilbereichen sind nicht der Standard.
- Ausnahmen sind nur zulässig, wenn sie bewusst eingeführt und über die Root-`Makefile` referenziert werden.

---

## Erwartetes Agent-Verhalten

1. Vor wiederholten Shell-Aktionen prüfen, ob eine Root-`Makefile` existiert.
2. Wenn eine `Makefile` existiert:
   - zuerst `make help` verwenden, sofern vorhanden
   - anschließend kanonische `make`-Ziele für die Aufgabe nutzen
3. Wenn keine `Makefile` existiert:
   - dokumentierte Befehle aus README, `docker.md`, `testing.md` oder anderen Engineering-Dokumenten verwenden
4. Keine fiktive `Makefile` annehmen oder erzeugen, nur weil dieses Dokument existiert.
5. Neue wiederkehrende Befehle sollen, wenn das Projekt bereits eine `Makefile` nutzt, bevorzugt dort integriert werden.

---

## Pflichtziel `help`

- `make help` ist das bevorzugte Einstiegstor.
- Das Ziel `help` soll öffentliche Targets mit kurzer Beschreibung anzeigen.
- Optional kann das Default-Target `make` direkt auf `help` zeigen.
- Die Hilfe soll kurz, lesbar und aktuell sein.

### Ziel der Hilfe

- neue Teammitglieder und Agenten sollen sofort erkennen, welche Befehle kanonisch sind
- Zielnamen und Zweck sollen transparent sein
- die `Makefile` soll als dokumentierte Bedienoberfläche funktionieren

---

## Empfohlene Standard-Targets

Die exakten Namen können projektspezifisch angepasst werden, müssen dann aber klar dokumentiert und in `help` sichtbar sein.

| Ziel | Typische Bedeutung |
|------|---------------------|
| `help` | Ziele und Kurzbeschreibung ausgeben |
| `up` | lokalen Stack starten |
| `down` | lokalen Stack stoppen |
| `build` | Container oder Artefakte neu bauen |
| `logs` | relevante Logs anzeigen oder folgen |
| `shell` | Shell im Backend-Container oder Projektkontext öffnen |
| `migrate` | Django-Migrationen anwenden |
| `test` | gesamte relevante Tests ausführen |
| `test-be` | Backend-Tests |
| `test-fe` | Frontend-Tests |
| `lint` | Linting ausführen |
| `fmt` | Formatierung ausführen |
| `ci` | lokaler CI-ähnlicher Durchlauf |

Compose-Details: `docker.md`  
Tests: `testing.md`  
Pipeline: `ci.md`

---

## Regeln für Zielgestaltung

- Zielnamen sollen kurz, klar und vorhersehbar sein.
- Namen sollen sich an verbreiteten Teamkonventionen orientieren.
- Öffentliche Ziele sollen stabil bleiben, sobald sie etabliert sind.
- Stark ähnliche Aufgaben sollen nicht unter verwirrend unterschiedlichen Namen auftreten.
- Zielnamen sollen eher fachlich und nutzungsorientiert als implementierungsorientiert sein.

### Beispiele guter Zielnamen

- `up`
- `down`
- `build`
- `lint`
- `test`
- `ci`

### Zu vermeiden

- kryptische Abkürzungen
- mehrere konkurrierende Namen für dieselbe Aufgabe
- interne Hilfsziele als öffentliche Standards

---

## Inhaltliche Regeln für die Makefile

- Ziele sollen vorzugsweise vorhandene Projektbefehle aufrufen:
  - `docker compose`
  - Python- oder Node-Befehle
  - bestehende Projekt-Skripte
- Keine Secrets, Tokens oder sensible Werte in der `Makefile` hardcodieren.
- Wiederkehrende Aufgaben sollen nicht nur in README-Textform existieren, wenn sie zuverlässig in `make` kapselbar sind.
- Die `Makefile` soll keine unnötige versteckte Komplexität enthalten.
- Lange oder komplexe Befehle sind zulässig, wenn sie den Bedienkomfort erhöhen und sauber strukturiert bleiben.

---

## Determinismus und Wiederholbarkeit

- `make`-Ziele sollen deterministisch und wiederholbar sein.
- Ziele dürfen keine unerwarteten, versteckten Seiteneffekte enthalten.
- Exit-Codes müssen korrekt propagiert werden.
- Ein Ziel soll unter denselben Voraussetzungen konsistente Ergebnisse liefern.
- Wiederholtes Ausführen darf keine unnötigen Schäden oder inkonsistenten Zustände erzeugen.

### Wo sinnvoll anzustreben

- `up` soll mehrfach ausführbar sein, ohne Chaos zu erzeugen
- `build` soll wiederholbar und nachvollziehbar bleiben
- `migrate` soll bewusst und kontrolliert ausgeführt werden
- `test` und `ci` sollen reproduzierbar sein

---

## Technische Konventionen

- `.PHONY` soll für nicht-dateibasierte Ziele gesetzt werden.
- Die Shell-Konfiguration soll nur angepasst werden, wenn es einen klaren technischen Grund gibt.
- POSIX-Kompatibilität ist anzustreben, soweit projektpraktisch sinnvoll.
- Wenn auf Windows besondere Anforderungen bestehen, sollen diese dokumentiert werden, z. B. Nutzung über WSL oder Git Bash.
- Komplexe Zielabhängigkeiten sollen nachvollziehbar bleiben.

---

## Beziehung zu Docker und lokaler Infrastruktur

- Wenn das Projekt Docker Compose als Standard nutzt, sollen zentrale lokale Ziele darauf aufbauen.
- Typische Compose-gekoppelte Ziele sind:
  - `up`
  - `down`
  - `build`
  - `logs`
  - `shell`
- Compose-Details bleiben in `docker.md`; die `Makefile` dient als Bedienoberfläche, nicht als Ersatz für die Infrastruktur-Dokumentation.

---

## Beziehung zu Tests

- Wiederkehrende Testabläufe sollen über kanonische Ziele erreichbar sein.
- Wenn Backend- und Frontend-Tests getrennt sinnvoll sind, sollen separate Ziele wie `test-be` und `test-fe` angeboten werden.
- Ein aggregiertes Ziel wie `test` oder `ci` soll die relevante Standardsicht für lokale Qualitätssicherung abbilden.
- Testziele sollen mit `testing.md` konsistent bleiben.

---

## Beziehung zu CI

- Sobald eine Root-`Makefile` existiert, soll CI nach Möglichkeit deren Ziele verwenden.
- Bevorzugt:
  - `make ci`
  - oder klar getrennte Ziele wie `make lint`, `make test`
- Die `Makefile` ist die lokale und pipelinefähige Befehls-Fassade.
- Ziel ist, dass CI und lokale Entwicklung dieselben Einstiegspunkte verwenden, um Drift zu minimieren.

---

## Dokumentation und Pflege

- Änderungen an wiederkehrenden Projektbefehlen sollen die `Makefile` mitberücksichtigen, sofern sie existiert.
- Änderungen an öffentlichen Targets sollen in `help` sichtbar sein.
- README, `docker.md`, `testing.md` und `ci.md` sollen nicht dauerhaft von der `Makefile` abweichen.
- Die `Makefile` ist wie produktiver Projektcode zu behandeln:
  - reviewbar
  - wartbar
  - konsistent
  - nachvollziehbar

---

## Wann keine Makefile-Regel erzwungen wird

- Dieses Dokument erzwingt nicht, dass jedes Projekt zwingend eine `Makefile` haben muss.
- Fehlt eine Root-`Makefile`, bleiben README und Engineering-Dokumente maßgeblich.
- Eine `Makefile` soll bewusst eingeführt werden, nicht reflexartig oder rein symbolisch.
- Eine schlechte oder ungenutzte `Makefile` ist schlechter als keine.

---

## Verbotene Muster

- Hardcodierte Secrets oder Tokens
- nicht dokumentierte öffentliche Targets
- inkonsistente oder irreführende Zielnamen
- versteckte Seiteneffekte in Standardzielen
- Drift zwischen `Makefile`, README und CI
- mehrere konkurrierende Root-Einstiegspunkte ohne klaren Standard
- Einführung einer `Makefile` ohne tatsächlichen Nutzen für den Workflow