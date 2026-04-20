# Engineering: Notifications

Ergaenzt `CLAUDE.md`. Bei Widerspruch gilt die Regel-Prioritaet aus `CLAUDE.md`.

---

## Geltungsbereich

- Dieses Dokument gilt fuer alle Aenderungen an der Notification-Domaene in Backend und Frontend.
- Es betrifft insbesondere:
  - `backend/apps/notification/*`
  - Benachrichtigungs-Ausloeser in anderen Apps
  - User-Praeferenzen fuer Kanaele (In-App, Mail, Realtime, Digest)
  - Celery-/Channels-Integration fuer Zustellung

---

## Verbindliche Regeln

- Notification-Workflows muessen ueber den Service-Layer orchestriert werden, nicht in Views, Serializern oder Tasks selbst.
- User-Praeferenzen fuer Kanaele sind pro Notification-Typ explizit zu beruecksichtigen.
- Kanal-Zustellung ist idempotent zu gestalten (Dedupe-Key, eindeutige Delivery-Eintraege).
- Realtime- und Mail-Zustellung sind asynchron ausfuehrbar zu halten (Celery/Channels), ohne Request-Thread-Blockierung.
- Write-Flows (Create, Read-Status, Preference-Aenderung, Digest-Status) muessen Audit-Events ueber `apps.common` erzeugen.
- API-Vertrag fuer Notifications ist ueber OpenAPI aktuell zu halten (`docs/engineering/api.md`).

---

## Entscheidungslogik

### Kanalwahl

- In-App ist der kanonische Persistenzkanal.
- Mail und Realtime werden auf Basis effektiver Praeferenzen zusaetzlich verarbeitet.
- Digest-Kanal wird ueber Batch-/Zeitfensterlogik verarbeitet und nicht wie Sofortkanaele behandelt.

### Trigger

- Primaerer Trigger fuer neue Notifications ist die Notification-API bzw. Notification-Service.
- Direkte Kanal-Implementierungen ausserhalb der Notification-Domaene sind nicht zulaessig.

### Fehler- und Retry-Verhalten

- Kanalfehler duerfen den persistierten Notification-Status nicht inkonsistent machen.
- Retries werden ueber Delivery-Status und naechsten Versuchstermin gesteuert.
- Fehlertexte duerfen keine sensiblen Inhalte enthalten.

---

## Checkliste

Vor Abschluss einer Notification-Aenderung:

- Service-Layer trennt klar zwischen Erstellung, Praeferenzauflosung und Kanalzustellung
- User-Praeferenzen pro Typ/Kanal werden korrekt respektiert
- Delivery-Status und Retry-Verhalten sind nachvollziehbar
- Audit-Events fuer Mutationen sind vorhanden und getestet
- Realtime/Mail laufen asynchron und blockieren keine API-Requests
- API-Schema und Frontend-Annahmen sind synchron
- Tests decken Happy Path, Fehlerfaelle und Praeferenz-Varianten ab

---

## Querverweise

- Backend-Schichten: `backend.md`
- API-Vertrag/OpenAPI: `api.md`
- Sicherheitsregeln: `security.md`
- Testpflichten: `testing.md`
- CI-Durchsetzung: `ci.md`
- Audit-Konventionen: `../backend/common/audit-basics.md`

---

## Verbotene Muster

- Notification-Logik direkt in Views oder Serializern
- Direkter Mail-/Realtime-Versand aus fachfremden Apps ohne Notification-Service
- Umgehen von User-Praeferenzen bei Kanalzustellung
- Write-Flows ohne Audit-Event
- Blockierende Kanalzustellung im Request-Pfad
- Stille API-Aenderungen ohne OpenAPI-Update
