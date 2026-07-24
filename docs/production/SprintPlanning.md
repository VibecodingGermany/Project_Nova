# Sprint-Planung

**Version:** 1.6.0 | **Status:** aktiv | **Verantwortungsbereich:** Executive Producer / Producer / Project Owner | **Sprint:** 6

## Zweck

Definiert alle Sprints, ihre Ziele, Deliverables und Exit-Kriterien. Kein Sprint gilt als abgeschlossen, ohne dass alle Exit-Kriterien erfüllt und ein Sprint-Bericht unter [sprints/](sprints/) vorliegt.

## Abhängigkeiten

- [../analysis/PriorityList.md](../analysis/PriorityList.md)
- [../analysis/GapAnalysis.md](../analysis/GapAnalysis.md)
- [DecisionLog.md](DecisionLog.md)

## Sprint-Definitionen

| Sprint | Thema | Ziel / Deliverables | Exit-Kriterien | Status |
|---|---|---|---|---|
| 0 | Projektinitialisierung | Quellenanalyse, Wissensbasis, Inkonsistenz- und Gap-Analyse, Prioritätenliste, Wiki-Grundgerüst | Alle Analyse-Dokumente vorliegend; Wiki-Standard verabschiedet; Sprint-Bericht | **abgeschlossen** |
| 1 | Research | Research-Dokumente zu: RTS-Markt/Wettbewerb, moderne RTS-Architekturen, Unity-Best-Practices, Open-Source-RTS, Multiplayer-Simulationsmodelle, ECS/DOTS, Pathfinding, Fog of War, KI, Animation, Audio, UI, Asset-Stores | Jedes kritische Thema (P0/P1) mit ≥3 verglichenen Alternativen; Empfehlungen als Entscheidungsvorlagen; Sprint-Bericht | **abgeschlossen** |
| 2 | Game Design | Alle GDD-Dokumente (Vision, Factions, Buildings, Units, Economy, ResearchTree, Damage/Armor, Maps, Biomes, NeutralUnits, Campaign, MultiplayerModes, Balancing, CommanderSystem, VictoryConditions, FogOfWar u. a.); Auflösung Q-001–Q-012 | Konsistenzcheck ohne offene Widersprüche; alle P0/P1-Designfragen entschieden; keine Implementierung; Sprint-Bericht | **abgeschlossen** |
| 3 | Technical Design | Vollständige Architektur: Module, Schnittstellen, Datenmodelle, Projektstruktur, Build-Prozess, alle TDD-Dokumente gemäß Gap-Analyse §3 | Alle P0-Architekturfragen (Q-013–Q-015, Q-020) entschieden; Schnittstellen dokumentiert; Sprint-Bericht | **abgeschlossen** |
| 4 | Architecture Review | Unabhängige Review-Agenten prüfen Architektur auf Fehler, Performance, Skalierung, Wartbarkeit, Multiplayer | Alle Findings dokumentiert und klassifiziert; kritische Findings in Architektur eingearbeitet; Sprint-Bericht | **abgeschlossen** |
| 5 | Asset Audit | Pro benötigtem Asset: Recherche, Lizenz, Kosten, Qualität, Anpassungsaufwand; Klassifikation BUY / MODIFY / BUILD | Vollständiges Asset-Register inkl. Licenses.md; Sprint-Bericht | **abgeschlossen** |
| 6 | Produktionsplanung | MVP / Alpha / Beta / Release mit Features, Risiken, Abhängigkeiten, Aufwand, Priorität; Roadmap.md, Milestones.md | Plan deckt sich mit Scope-Entscheidungen aus Sprint 2; Sprint-Bericht | **abgeschlossen** |
| 7 | Implementierung | Modulare Umsetzung, ein Modul nach dem anderen | Pro Modul: Unit Tests, Integration Tests, Performance Tests, Dokumentation, Code Review, Refactoring | **bereit (GO)** |

## Sprint-Abschluss-Ritual (verbindlich für jeden Sprint)

1. Vollständige Dokumentation des Sprint-Ergebnisses
2. Self Review
3. Architecture Review (dokument-/architekturbezogen)
4. Risikoanalyse (Update [RiskAnalysis.md](RiskAnalysis.md))
5. Qualitätsbewertung
6. Offene Punkte (Update [OpenQuestions.md](OpenQuestions.md))
7. Begründete Entscheidung über den nächsten Sprint (GO / NO-GO / Anpassung)
8. Sprint-Bericht in [sprints/](sprints/), Index [../README.md](../README.md) aktualisieren

## Offene Punkte

- Sprint-Längen sind ergebnisorientiert, nicht zeitorientiert ("Qualität vor Geschwindigkeit").

## Nächste Schritte

- **Sprint 7 starten (Implementierung / Phase 0 Spike / MS-0):** Modulare Umsetzung des Simulations- & Lockstep-Kerns, Fixed-Point-Determinismus (ARM↔x86) und Flow-Field-Pathfinding im echten Code.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Sprint-Definitionen 0–7 verabschiedet (Sprint 0) | Executive Producer |
| 1.1.0 | 2026-07-21 | Sprints 1–2 als abgeschlossen markiert, Sprint 3 GO; Exit-Kriterium Sprint 3 um Q-020 ergänzt | Executive Producer |
| 1.2.0 | 2026-07-21 | Sprint 3 als abgeschlossen markiert, Sprint 4 GO | Executive Producer |
| 1.3.0 | 2026-07-21 | Sprint 4 als abgeschlossen markiert, Sprint 5 (Asset Audit) GO | Executive Producer |
| 1.4.0 | 2026-07-22 | Sprint 5 (Asset Audit) als abgeschlossen markiert, Sprint 6 (Produktionsplanung) GO | Executive Producer |
| 1.5.0 | 2026-07-24 | Inhaberentscheidung D-054 (0 € Open-Source & KI-Pipeline, Q-035 geschlossen) in Sprint-6-Vorbereitung eingetragen | Executive Producer |
| 1.6.0 | 2026-07-24 | Sprint 6 (Produktionsplanung) als abgeschlossen markiert, Sprint 7 (Implementierung) GO | Executive Producer |
