# Engineering: Docker & lokale Infrastruktur

Ergaenzt `CLAUDE.md`. Dieses Dokument ist der Owner fuer Compose-Struktur, Container-Konventionen und lokalen Runtime-Stack.

---

## Zweck und Scope

- Docker Compose als Standard-Einstieg fuer den lokalen Stack.
- Reproduzierbare lokale Laufumgebung mit klaren Service-Grenzen.
- Regeln fuer Healthchecks, Exponierung und Infrastruktur-Dokumentation.

---

## Verbindliche Regeln

### Compose-Grundsaetze

- Lokale Entwicklung laeuft primaer ueber Docker Compose.
- Pflicht-Services fuer normale Entwicklung und Tests werden in Compose abgebildet.
- Service-Kommunikation ueber Compose-Service-Namen statt hartcodierter Hosts.

### Service- und Runtime-Regeln

- Bevorzugte Service-Namen: `backend`, `frontend`, `db`, `redis`, `worker`, `beat`, `ollama` (falls genutzt).
- Nur notwendige Ports nach aussen oeffnen.
- Healthchecks fuer kritische Services definieren.
- Startabhaengigkeiten explizit modellieren.

### Konfiguration

- Pflicht-Umgebungsvariablen dokumentieren.
- Keine Secrets in Compose-Dateien oder Dockerfiles.
- Optionale Services (z. B. Ollama) klar als optional kennzeichnen.

### Dokumentation

- Teamweit kanonische Befehle dokumentieren (Start, Stop, Build, Logs, Shell, Migrationen, Tests).
- Existiert eine Root-`Makefile`, sollen diese Befehle ueber `make`-Ziele sichtbar sein.

---

## Verbotene Muster

- Fragile Sleep-Workarounds statt Healthchecks.
- Unnoetige Portfreigaben.
- Infra-Aenderungen ohne begleitende Doku-Anpassung.

---

## Abgrenzung zu anderen Modulen

- Pipeline-Policy liegt in `ci.md`.
- Makefile-Regeln liegen in `makefile.md`.
- Teststrategie liegt in `testing.md`.
