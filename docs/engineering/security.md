# Engineering: Security

Ergänzt `CLAUDE.md`. LLM-spezifische Grenzen zusätzlich in `llm.md`.

---

## Grundsatz

- Security ist ein Default-Verhalten, kein optionaler Schritt.
- Alle Eingaben und Ausgaben sind potenziell unsicher.
- Sicherheitsrelevante Entscheidungen dürfen nicht implizit getroffen werden.

---

## Input- und Output-Validierung

- Alle externen Eingaben müssen validiert werden:
  - API-Requests
  - Query-Parameter
  - Form-Daten
  - LLM-Outputs
- Validierung erfolgt primär über:
  - DRF-Serializer (Backend)
  - explizite Checks im Service-Layer bei komplexer Logik

### Verboten

- Vertrauen auf ungeprüfte Eingaben
- Nutzung von LLM-Output ohne Validierung
- Weitergabe von unvalidierten Daten an Datenbank oder externe Systeme

---

## Autorisierung (verbindlich)

- Jede geschützte Operation benötigt eine explizite Berechtigungsprüfung.
- Keine impliziten Default-Zugriffe.

### Regeln

- Permissions liegen in `api/v1/permissions/`
- Zugriff wird nicht nur auf Endpoint-, sondern bei Bedarf auch auf Objekt-Ebene geprüft
- Sensitive Aktionen benötigen explizite Prüfung

### Verboten

- Zugriff basierend auf Annahmen (z. B. „User gehört wahrscheinlich dazu“)
- fehlende Objekt-Level-Checks bei sensiblen Daten

---

## Geheimnisse & Datenlecks

- Secrets dürfen niemals im Code, Logs oder Responses erscheinen.
- Verwendung von:
  - Environment Variables
  - Secret Stores (falls vorhanden)

### Verboten

- Hardcodierte API-Keys
- Logging von Tokens, Passwörtern oder sensiblen Payloads

---

## Fehlerhandling

- Fehlermeldungen dürfen keine internen Details preisgeben.
- Keine Stacktraces oder Debug-Informationen im API-Response.
- Fehler müssen konsistent und kontrolliert ausgegeben werden.

---

## Logging & Audit

- Sicherheitsrelevante Aktionen müssen nachvollziehbar sein.
- Logs müssen ausreichend Kontext enthalten, ohne sensible Daten zu leaken.

### Beispiele für Audit-relevante Events

- Login / Auth-Versuche
- Datenänderungen
- Berechtigungsverletzungen
- kritische API-Aufrufe

---

## Web-Risiken (OWASP)

Typische Risiken aktiv vermeiden:

- Broken Access Control
- Injection (SQL, Command, Template)
- XSS
- CSRF
- IDOR

### Regeln

- ORM statt Raw SQL bevorzugen
- Template-Ausgaben escapen
- CSRF-Schutz nutzen, wenn relevant

---

## Sessions, Cookies, CORS, Auth

- Sichere Defaults verwenden:
  - HttpOnly
  - Secure
  - SameSite
- CORS restriktiv konfigurieren

### Verboten

- Wildcard-CORS ohne Grund
- unsichere Cookie-Konfiguration

---

## Rate Limiting & Abuse Protection

- Öffentliche oder sensible Endpunkte müssen vor Missbrauch geschützt werden.
- Rate Limiting ist zu berücksichtigen, insbesondere für:
  - Auth-Endpunkte
  - API-Endpunkte mit hoher Last
  - LLM-Integrationen

---

## Datenminimierung

- Nur notwendige Daten speichern und übertragen.
- API-Responses enthalten nur benötigte Felder.
- Sensible Daten besonders schützen.

---

## Dependencies & Supply Chain

- Nur vertrauenswürdige Libraries verwenden.
- Abhängigkeiten regelmäßig aktualisieren.
- Keine unnötigen Dependencies einführen.

---

## LLM / KI-Grenzen

- LLM-Ein- und Ausgaben sind sicherheitsrelevant.
- LLM darf keine sicherheitskritischen Entscheidungen allein treffen.
- Prompt Injection berücksichtigen und mitigieren.

---

## Proaktivität

- Sicherheitsprobleme müssen aktiv angesprochen werden.
- Unsichere Implementierungen sind zu korrigieren, nicht zu tolerieren.

---

## Verbotene Muster

- Unvalidierte Eingaben
- Fehlende Permissions
- Hardcodierte Secrets
- Sensible Daten in Logs
- Offene CORS-Konfiguration
- Stacktraces im Response
- Vertrauen auf LLM-Output