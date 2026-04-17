# Engineering: API & OpenAPI (drf-spectacular)

Ergänzt `CLAUDE.md`. Pflichtstruktur und Dateinamen bleiben in `CLAUDE.md` (Non-negotiables).

---

## Geltungsbereich

- Dieses Dokument gilt für API-Design, API-Änderungen und OpenAPI-Pflege.
- Es betrifft insbesondere DRF-Views, Serializer, Permissions und Schema-Definitionen.

---

## Verbindliche Regeln

- Das OpenAPI-Schema ist Teil des API-Vertrags, nicht optionale Doku.
- Bei geändertem Endpoint-Verhalten müssen Schema und Beispiele mitgepflegt werden.
- Schema-Definitionen pro Domäne liegen unter `api/v1/schema/` innerhalb der jeweiligen App.
- Benennung zwischen Serializer, View, Route und Schema-Modul bleibt konsistent.
- Custom Actions werden explizit dokumentiert.
- Collection-Endpunkte dokumentieren Pagination, Filter, Sortierung und Auth.
- Für Audit-bezogene Endpunkte sind die kanonischen Schnittstellen aus `docs/backend/common/audit-interfaces.md` zu verwenden und zu dokumentieren.

---

## Breaking Changes & Versionierung

- Breaking Changes sind vor Merge explizit zu kennzeichnen (PR-Beschreibung und Review-Hinweis).
- Änderungen an Statuscodes, Pflichtfeldern, Feldtypen oder Semantik gelten als potenziell breaking.
- Potenziell breaking Änderungen benötigen:
  - dokumentierte Migration oder Rollout-Strategie
  - aktualisierte API-Beispiele
  - aktualisierte Tests gemäß `testing.md`
- Unbeabsichtigte Breaking Changes sind durch Schema- und API-Tests zu verhindern.

---

## drf-spectacular — Nutzung

- Sinnvoll einsetzen: `extend_schema`, `extend_schema_view`, `OpenApiParameter`, `OpenApiResponse`, verwandte Primitive.
- Große oder wiederholte Schema-Blöcke nicht dauerhaft inline in Views halten; bei Bedarf auslagern.
- Pagination, Filter, Sortierung und Auth für Collection-Endpunkte beschreiben.

### Kanonische Doku-Endpoints

- OpenAPI-Schema (JSON/YAML je Konfiguration): `/api/schema/`
- Swagger UI: `/api/docs/swagger/`
- ReDoc UI: `/api/docs/redoc/`

Diese Endpunkte sind der verbindliche Einstieg für den API-Vertrag im laufenden System.

---

## OpenAPI-Tags (verbindliches Format)

- **Standard-Endpunkte:** `Domain - Funktion`  
- **Custom Actions:** `Domain - Funktion - Funktionsgruppe`

**Beispiele:** `Kunden - Stammdaten`, `Kunden - Verträge`, `Kunden - Verträge - Kündigung`, `Rechnungen - Export - DATEV`

**Tagging-Standards**

- Projektweit konsistent; Tags domänenorientiert, nicht implementierungslastig.
- Keine willkürliche Mischung aus Groß-/Kleinschreibung, Singular/Plural oder Ad-hoc-Abkürzungen.
- Verwandte Endpunkte unter demselben Tag gruppieren, sofern es fachlich Sinn ergibt.  
- Für Custom Actions ist die Funktionsgruppe im Tag Pflicht.

---

## Dokumentationsqualität

- Standard-Erfolgs- und Fehlerantworten; bei Nutzen Validierungsfehler beschreiben.
- Authentifizierung und Autorisierung klar angeben.
- Beispiele realistisch und an realer Nutzung orientiert.  
- Keine undokumentierten Custom Actions; keine «stillen» Sonder-Response-Shapes.

---

## Checkliste

Vor Abschluss einer API-Änderung:

- Endpoint-Verhalten und OpenAPI-Schema sind synchron
- Tagging folgt dem verbindlichen Format
- Erfolgs- und Fehlerfälle sind dokumentiert
- Auth-/Permission-Verhalten ist beschrieben
- API-Tests für Statuscodes, Struktur und Fehlerfälle sind aktualisiert
- bei Audit- oder Operations-Endpunkten ist die Dokumentation mit `docs/backend/common/audit-interfaces.md` und `docs/backend/common/audit-basics.md` konsistent
- bei Breaking-Änderungen ist der Rollout dokumentiert

---

## Querverweise

- Service-/View-Grenzen: `backend.md`
- Testanforderungen: `testing.md`
- CI-Durchsetzung: `ci.md`
- Sicherheitsregeln: `security.md`
- Audit-Bausteine (`apps/common`): `../backend/common/README.md`
- Audit-Basics und Event-Konventionen: `../backend/common/audit-basics.md`
- Audit-Schnittstellen (Commands/API): `../backend/common/audit-interfaces.md`

---

## Verbotene Muster

- API-Verhaltensänderungen ohne Schema-Update
- undokumentierte Custom Actions
- inkonsistente OpenAPI-Tags
- implizite Breaking Changes ohne Kennzeichnung
- Sonder-Response-Formate ohne Dokumentation
