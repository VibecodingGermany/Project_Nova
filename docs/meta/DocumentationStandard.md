# Dokumentationsstandard

**Version:** 1.1.0 | **Status:** verbindlich | **Verantwortungsbereich:** Technical Writer | **Sprint:** 0

## Zweck

Definiert den verbindlichen Standard für alle Dokumente im Project-Nova-Wiki. Ziel: dauerhaft synchron gepflegte, verlinkbare, reviewbare Living Documents statt veralteter Monolithen.

## Grundprinzipien

1. **Klein und fokussiert:** Ein Dokument behandelt genau ein Thema. Wächst ein Dokument über seinen Zweck hinaus, wird es aufgeteilt.
2. **Living Documents:** Jedes Dokument wird bei jeder relevanten Erkenntnis, Entscheidung oder Architekturänderung sofort aktualisiert und die Version erhöht. Dokumentation ist nie "fertig".
3. **Verlinkung:** Dokumente verlinken ihre Abhängigkeiten und verwandte Dokumente relativ (`../production/DecisionLog.md`), damit das Wiki navigierbar bleibt.
4. **Sprache:** Deutsch für alle Projektdokumente. Code, Identifier und Dateipfade bleiben englisch/technisch.
5. **Keine Platzhalter:** Es werden keine leeren Dokumente für zukünftige Sprints angelegt (verhindert veraltete Leichen). Der Index ([../README.md](../README.md)) führt geplante Bereiche als "geplant".
6. **Single Source of Truth für Werte:** Jeder Zahlenwert (Kosten, HP, DPS, Reichweiten, Raten, Energie u. ä.) existiert **genau einmal** im Wiki – im jeweils führenden Dokument. Alle anderen Dokumente **verweisen** auf das führende Dokument, statt den Wert zu wiederholen (Grundsatzregel gemäß [../production/DecisionLog.md](../production/DecisionLog.md), D-047). Bei Konflikten gilt das führende Dokument; doppelt gepflegte Werte gelten als Review-Befund und sind zu beseitigen.

## Pflichtabschnitte jedes Dokuments

Jedes Dokument enthält in dieser Reihenfolge:

1. **Titel** (`# ...`)
2. **Kopfzeile:** Version, Status, Verantwortungsbereich (Studio-Rolle), Sprint
3. **Zweck** – wozu existiert dieses Dokument, für wen ist es verbindlich
4. **Abhängigkeiten** – verlinkte Dokumente/Entscheidungen, auf denen der Inhalt aufbaut
5. **Inhalt** – themenspezifisch
6. **Offene Punkte** – mit Verweis auf [../production/OpenQuestions.md](../production/OpenQuestions.md), falls übertragen
7. **Nächste Schritte**
8. **Änderungsverlauf** – Tabelle: Version, Datum, Änderung, Autor (Studio-Rolle)

## Versionierung

- `0.x` – Entwurf, im jeweiligen Sprint in Arbeit
- `1.0` – sprint-freigegeben (Inhalt des zugehörigen Sprint-Abschlussberichts)
- Erhöhung der Minor-Version bei jeder inhaltlichen Änderung, Patch bei Korrekturen
- Der Änderungsverlauf ist Pflicht; undokumentierte Änderungen gelten als nicht erfolgt

## Entscheidungen

- Jede Architektur- oder Design-Entscheidung wird mit mindestens **drei geprüften Alternativen** und Begründung in [../production/DecisionLog.md](../production/DecisionLog.md) eingetragen.
- Entscheidungen erhalten fortlaufende IDs (`D-001`, `D-002`, …) und werden in Fachdokumenten per ID referenziert.
- Wird eine Entscheidung revidiert, bleibt der alte Eintrag stehen (Status: "ersetzt durch D-xxx") – keine stillen Umschreibungen.

## Review-Rhythmus

- Am Ende jedes Sprints: Self Review + Architecture Review des Dokumentbestands, dokumentiert im Sprint-Bericht unter [../production/sprints/](../production/sprints/).
- Inkonsistenzen zwischen Dokumenten werden in [../analysis/Inconsistencies.md](../analysis/Inconsistencies.md) bzw. nach Sprint 0 direkt in den betroffenen Dokumenten plus OpenQuestions erfasst.

## Abhängigkeiten

- Keine (Basisdokument des Wikis).

## Offene Punkte

- Keine.

## Nächste Schritte

- Standard in Sprint 1 auf Research-Dokumente anwenden und ggf. nachschärfen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Initialer verbindlicher Standard (Sprint 0) | Technical Writer |
| 1.1.0 | 2026-07-21 | Korrekturlauf Sprint 4 (D-043–D-052, Review-Findings): Grundprinzip 6 „Single Source of Truth für Werte" ergänzt (D-047) | Technical Writer |
