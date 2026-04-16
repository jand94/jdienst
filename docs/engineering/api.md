# Engineering: API & OpenAPI (drf-spectacular)

Ergänzt `CLAUDE.md`. Pflichtstruktur und Dateinamen bleiben in `CLAUDE.md` (Non-negotiables).

---

## Grundsatz

- Das OpenAPI-Schema ist **Teil des API-Vertrags**, nicht optionale Doku.  
- Bei geändertem Endpoint-Verhalten **Schema und Beispiele** mitpflegen.

---

## Ablage & Struktur

- Schema-Definitionen pro Domäne unter `api/v1/schema/` innerhalb der jeweiligen App.  
- Große oder wiederholte Schema-Blöcke **nicht** ungebremst inline in Views — auslagern, wenn es die Wartbarkeit verbessert.  
- Benennung zwischen Serializer, View, Route und Schema-Modul **aligned** halten.

---

## drf-spectacular — Nutzung

- Sinnvoll einsetzen: `extend_schema`, `extend_schema_view`, `OpenApiParameter`, `OpenApiResponse`, verwandte Primitive.  
- Custom Actions **explizit** dokumentieren.  
- Pagination, Filter, Sortierung und Auth für Collection-Endpunkte beschreiben.

---

## OpenAPI-Tags (verbindliches Format)

- **Standard-Endpunkte:** `Domain - Funktion`  
- **Custom Actions:** `Domain - Funktion - Funktionsgruppe`

**Beispiele:** `Kunden - Stammdaten`, `Kunden - Verträge`, `Kunden - Verträge - Kündigung`, `Rechnungen - Export - DATEV`

**Tagging-Standards**

- Projektweit **konsistent**; Tags **domänenorientiert**, nicht implementierungslastig.  
- Keine willkürliche Mischung aus Groß-/Kleinschreibung, Singular/Plural oder Ad-hoc-Abkürzungen.  
- Verwandte Endpunkte unter demselben Tag gruppieren, sofern es fachlich Sinn ergibt.  
- Für Custom Actions ist die **Funktionsgruppe** im Tag **Pflicht**.

---

## Dokumentationsqualität

- Standard-Erfolgs- und Fehlerantworten; bei Nutzen Validierungsfehler beschreiben.  
- Authentifizierung und Autorisierung klar angeben.  
- Beispiele realistisch und an realer Nutzung orientiert.  
- Keine undokumentierten Custom Actions; keine «stillen» Sonder-Response-Shapes.
