# Engineering: Docker & lokale Infrastruktur

Ergänzt `CLAUDE.md`. Docker Compose ist der Standard-Einstieg für den vollständigen lokalen Stack, insbesondere für Backend, Frontend, Datenbank, Cache, Worker und – falls genutzt – Ollama.

---

## Zielbild

- Lokale Entwicklung soll primär über Docker Compose erfolgen.
- Der Compose-Stack soll reproduzierbar, teamfähig und möglichst produktionsnah sein.
- Änderungen an infra-relevanten Features müssen Compose, Umgebungsvariablen und Projektdokumentation gemeinsam berücksichtigen.
- Neue Services oder Abhängigkeiten, die für normale Entwicklung, Integrationstests oder zentrale Features erforderlich sind, sind in Compose zu integrieren.

---

## Grundprinzipien

- Ein klar dokumentierter Compose-Workflow schlägt fragmentierte Host-Installationen.
- Lokale Setups sollen einfach startbar, nachvollziehbar und wartbar sein.
- Dev-Optimierungen sind erlaubt, solange sie produktionsrelevantes Verhalten nicht unnötig verfälschen.
- Umgebungsvariablen sind konsistent und explizit zu verwalten.
- Pflichtvariablen für lokales bzw. dev-nahes Betreiben sind zu dokumentieren.
- Container-Setups müssen review-freundlich und betrieblich nachvollziehbar bleiben.

---

## Compose-Konventionen

- Bevorzugte Service-Namen: `backend`, `frontend`, `db`, `redis`, `worker`, `beat`, `ollama`, soweit im Projekt genutzt.
- Service-Kommunikation erfolgt bevorzugt über Compose-Service-Namen, nicht über hartcodierte Host-Adressen.
- Nur erforderliche Ports sollen nach außen veröffentlicht werden.
- Interne Services sollen nicht unnötig exponiert werden.
- Benannte Volumes sind gegenüber unstrukturierten ad-hoc-Mounts zu bevorzugen, wenn Persistenz erforderlich ist.
- Bind-Mounts sind nur zu verwenden, wenn sie den Entwickler-Workflow spürbar verbessern.
- Compose-Konfiguration soll lesbar, modular und review-freundlich bleiben.
- Unnötige Container-Komplexität ist zu vermeiden.

---

## Startverhalten und Verfügbarkeit

- Healthchecks sind für relevante Services zu definieren, insbesondere für Datenbank, Cache und weitere kritische Abhängigkeiten.
- Start-Abhängigkeiten sind explizit zu modellieren.
- Service-Verfügbarkeit ist nach Möglichkeit über Healthchecks abzusichern, nicht über fragile Sleep-Workarounds.
- Entrypoints und Startskripte dürfen keine versteckte Business-Logik enthalten.
- Datenbankmigrationen dürfen nicht unbeabsichtigt oder unkontrolliert ausgeführt werden; projektspezifische Migrationsregeln sind einzuhalten.

---

## Umgebungsvariablen

- Konfiguration erfolgt über Umgebungsvariablen mit konsistenter Benennung.
- Erforderliche Variablen für lokale Entwicklung müssen dokumentiert sein.
- Defaults dürfen lokale Entwicklung erleichtern, aber keine sicherheitskritischen Fehlannahmen erzeugen.
- Secrets dürfen nicht hartcodiert in Compose-Dateien oder Dockerfiles abgelegt werden.
- Modellnamen, API-Endpunkte, Feature-Flags und optionale Service-Konfigurationen sollen über Umgebungsvariablen steuerbar sein.

---

## Dockerfiles und Images

- Dockerfiles sollen klar, minimal und wartbar sein.
- Images sollen nur die tatsächlich benötigten Abhängigkeiten enthalten.
- Unnötige Build-Komplexität ist zu vermeiden.
- Build-Schritte sollen nachvollziehbar und möglichst cache-freundlich sein.
- Runtime-Container sollen keine offensichtlichen Dev-Only-Abhängigkeiten enthalten, sofern diese nicht bewusst für lokale Entwicklung erforderlich sind.

---

## Ollama und optionale Services

- Ollama wird nur dann in Compose integriert, wenn das Projekt lokale LLM-Funktionalität tatsächlich nutzt.
- LLM-bezogene Services sollen den restlichen Stack nicht unnötig blockieren, wenn sie optional sind.
- Optionale Services sollen, wenn sinnvoll, separat aktivierbar sein.
- Persistenz für Modelle und LLM-Daten ist bewusst zu planen.
- Ressourcenbedarf für lokale LLM-Ausführung ist zu berücksichtigen.

---

## Dokumentation im Projekt

Wenn eine **Root-`Makefile`** existiert, sollen kanonische Dev-/Stack-Befehle dort als **`make`-Ziele** gebündelt und über `make help` auffindbar sein — siehe `makefile.md`. Zusätzlich oder bis dahin: README bzw. `docs/`.

Kanonische Befehle für das Team sind im README oder in `docs/` gemäß Projektstandard zu dokumentieren, mindestens für:

- Stack starten
- Stack stoppen
- Services neu bauen
- Logs einsehen
- Shell im Backend-Container öffnen
- Migrationen anwenden
- Tests ausführen
- Statische Assets sammeln, falls relevant

Zusätzlich sollen dokumentiert sein:

- erforderliche Umgebungsvariablen
- optionale Services wie Ollama
- typische Fehlerbilder und lokale Recovery-Schritte, wenn dies betrieblich sinnvoll ist

---

## Erwartetes Agent-Verhalten

Bei infra-relevanten Änderungen gilt:

- Compose-Dateien, Dockerfiles und Dokumentation konsistent mitändern
- neue Pflicht-Services in den Compose-Workflow integrieren
- Healthchecks und Abhängigkeiten prüfen
- unnötige Portfreigaben vermeiden
- bestehende lokale Workflows nicht ohne klaren Grund brechen