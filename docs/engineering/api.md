# Engineering: API & OpenAPI (drf-spectacular)

Ergaenzt `CLAUDE.md`. Dieses Dokument ist der Owner fuer API-Vertrag, Schema-Pflege und Tagging-Konventionen.

---

## Zweck und Scope

- Verbindliche Regeln fuer OpenAPI als API-Vertrag.
- Konsistente Schema-Struktur in `api/v1/schema/`.
- Einheitliche Dokumentationsqualitaet und Tagging.

---

## Verbindliche Regeln

### API-Vertrag

- OpenAPI ist verpflichtender Teil des API-Vertrags.
- Aenderungen am Endpoint-Verhalten erfordern Schema-Update im selben Change.
- Request/Response, Fehlerfaelle, Auth, Parameter und Pagination sauber dokumentieren.

### Struktur und Pflege

- Schema-Definitionen domaenenspezifisch unter `api/v1/schema/` ablegen.
- Grosse Schemabloecke nicht unstrukturiert inline in Views halten.
- Benennung zwischen Serializer, View, Route und Schema konsistent halten.

### Tagging

- Standard-Endpunkte: `Domain - Funktion`.
- Custom Actions: `Domain - Funktion - Funktionsgruppe`.
- Tags projektweit konsistent, domaenenorientiert und ohne Ad-hoc-Abweichungen.

---

## Verbotene Muster

- Endpunktverhalten aendern ohne Schema-Anpassung.
- Undokumentierte Custom Actions.
- Inkonsistente oder technisch statt fachlich benannte Tags.

---

## Abgrenzung zu anderen Modulen

- Backend-Schichttrennung liegt in `backend-rules.md`.
- Testanforderungen fuer API-Tests liegen in `testing.md`.
- CI-Checks fuer Schema/Contract laufen ueber `ci.md`.
