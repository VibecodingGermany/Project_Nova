# Sprint-2-Bericht – Game Design

**Version:** 1.0.0 | **Status:** Sprint abgeschlossen | **Verantwortungsbereich:** Executive Producer | **Sprint:** 2

## Zweck

Verbindlicher Abschlussbericht von Sprint 2 (Game Design) gemäß Sprint-Ritual ([../SprintPlanning.md](../SprintPlanning.md)): Dokumentationsstand, Entscheidungen, Konsistenzreview, Self Review, Architecture Review, Risikoanalyse, Qualitätsbewertung, offene Punkte, Entscheidung über den nächsten Sprint.

## Abhängigkeiten

- Alle GDD-Dokumente unter [../../vision/](../../vision/) und [../../gamedesign/](../../gamedesign/)
- [../DecisionLog.md](../DecisionLog.md) (D-007–D-032), [../OpenQuestions.md](../OpenQuestions.md), [../RiskAnalysis.md](../RiskAnalysis.md)
- [Sprint01_Report.md](Sprint01_Report.md) (Sprint-2-Scope-Definition)

## 1. Ergebnisse des Sprints

**25 Dokumente erstellt** (alle im Dokumentstandard, alle mindestens im Korrekturlauf-Stand 0.2.0):

| Bereich | Dokumente |
|---|---|
| Vision | Vision.md, USP.md, TargetAudience.md, CoreGameplay.md, GameLoop.md |
| Fraktionen & Einheiten | Factions.md, Buildings.md, Infantry.md, Vehicles.md, Aircraft.md |
| Wirtschaft & Forschung | Resources.md, Economy.md, ResearchTree.md |
| Kampfsystem | Weapons.md, DamageSystem.md, ArmorSystem.md |
| Welt | Maps.md, Biomes.md, NeutralUnits.md, FogOfWar.md |
| Meta & Regeln | CommanderSystem.md, MultiplayerModes.md, VictoryConditions.md, Balancing.md, Campaign.md |

**26 Entscheidungen getroffen und dokumentiert** (DecisionLog v1.3.2):
- **D-007–D-019 (Grundlagen, vorab):** Geschäftsmodell Premium SP-first, 12 Gebäudetypen, Commander als Identität, Aetherium-Hybridwirtschaft, Evolvierte-Wachstumsbau, gezielte Zerstörbarkeit, Marine-Streichung, Drohnen, Elite-Regel, Neutrale, Biome/Karten, Modi-Staffelung, Kamera.
- **D-020–D-030 (Review Runde 1, ~60 eskalierte Detailfragen):** Kampagne Phase 3, kein Supply-System, Capture-System (Tunnelgräber-Lücke geschlossen), Superwaffen-Limit, Silos + Raffinerie-Packaging, Alpha-FFA lokal, Konter-Lücken (Kristallmagier-AA u. a.), Fraktions-Sonderregeln, Karten/Biome, Modi/Komfort, Forschungsregeln.
- **D-031–D-032 (Feinschliff Runde 2):** HQ-Neuaufbau-Mechanik (Builder-basiert), Detektor-Regel + Burrow-Sonderregel, Alpha-Koop = 1 Spieler + KI-Verbündeter, Survival-/Vernichtungs-Harmonisierung, Regen-Kompensation über Rate, Plattform-Aggressions-Modi, HQ-Grundenergie +30.

**Exit-Kriterien:** vollständiges GDD ✓ | Konsistenzcheck ohne offene Widersprüche ✓ | alle P0/P1-Designfragen entschieden (Q-001–Q-017) ✓ | keine Implementierung ✓

## 2. Konsistenzreview (Zusammenfassung)

Dreistufig durchgeführt:
1. **Runde 1 (13 Review-Agentenmeldungen):** ~60 eskalierte Fragen, keine Verletzungen verbindlicher Entscheidungen; Befundklassen: Regel-Lücken (Capture, Detektoren), Zahlen-Abgleich (HQ-Energie, Bauzeiten), Scope-Fragen (Kampagne, Supply), Phasen-Widerspruch (Alpha-FFA vs. MP-Technik). Alle durch D-020–D-030 aufgelöst und von 13 Korrektur-Agenten eingearbeitet.
2. **Runde 2 (Feinschliff):** 8 neue Querschnitts-Befunde aus der Korrektur (u. a. HQ-Neuaufbau-Logiklücke, Detektor-Widerspruch, tote Links `Units.md`/`MapDesign.md`/`TechTree.md`). Aufgelöst durch D-031/D-032 und gezielte Fixes; Link-Grep über `docs/vision` + `docs/gamedesign` final sauber.
3. **Zahlenanker-Verifikation:** 1.000 AE Start / 300 AE Ladung / Low-Power-Regel / 20–35 min / Fraktionsfaktoren (Allianz ×1,15–1,25, Legion ×0,8–0,85) durchgehend konsistent; Economy↔Maps-Reserven und Buildings↔Economy-Energie abgeglichen.

**Verbleibende, bewusst offene Design-Details** (keine Widersprüche, terminierte Folge-Entscheidungen): Tor-Modul (Beta-Evaluierung), Parasiten-Königin (Beta), Flak-DPS-Korridor (Balancing-Pass v0.2), Footprints/Grid-Tile-Größe (Sprint 3), Streuen-Befehl (Alpha-Playtests), Disconnect-Regel/Host-Migration (Sprint 3, Q-013), Doktrinen (Beta), Rendersequenzen (Sprint 6).

## 3. Self Review

**Stärken:** Die Entscheidungs-First-Methodik (D-007–D-019 vor dem Schreiben) hat die Kohärenz von 25 parallel erstellten Dokumenten gesichert; Subagenten eskalierten diszipliniert statt eigenmächtig zu entscheiden; jede Review-Frage ist mit D-ID beantwortet und nachvollziehbar.

**Schwächen:**
- Zwei Korrektur-Wellen waren nötig – die erste Welle erzeugte selbst neue Querschnitts-Konflikte (z. B. führende-Regel-Fragen bei Vernichtung, Regen-Kompensation). Prozess-Learnings: Bei Querverweisen immer das *führende* Dokument benennen (jetzt Standard: "führend: X.md").
- Einzelne Zahlen (Flak-DPS-Korridor Aircraft vs. Weapons) zeigen, dass der Balancing-Pass v0.2 Pflicht ist, bevor Werte als stabil gelten.
- Vision-/USP-Abhängigkeit von Kampagne wurde erst im Review sichtbar (D-020) – hätte in die Grundlagendefinition gehört.

## 4. Architecture Review (Dokument-Architektur)

- **Modularität:** 25 Dokumente mit klaren Hoheiten (Einheiten-, Wirtschafts-, Kampf-, Welt-, Meta-Cluster); Querverweise bidirektional auflösbar, keine Zyklen-Probleme (Master: Factions.md; Zahlenanker: Economy.md/Resources.md).
- **Datengetriebenheit:** Alle Wertedokumente spezifizieren flache SO-taugliche Datensätze – direkte Eingabe für Sprint 3 (Datenmodelle) und Sprint 7 (ScriptableObjects).
- **Befund:** Keine strukturellen Mängel. Die verbleibenden Abhängigkeiten (Grid-Tile-Größe, Footprints, Sim-Tick-Parameter) sind korrekt an Sprint 3 delegiert.
- **Schnittstellen-Input für Sprint 3:** FoW-Grid (1-m-Raster), Flow-Field-Grid, Biome-Effekt-Grid teilen sich laut Design ein gemeinsames Tile-Raster – Architektur muss das als *eine* Grid-Infrastruktur abbilden.

## 5. Risikoanalyse (Update)

Vollständig in [../RiskAnalysis.md](../RiskAnalysis.md) v1.2.0:
- **R-01 (Scope-Explosion) teilentschärft:** Scope ist jetzt entschieden und beziffert (36 Gebäude-Assets statt 54, 9 Elite statt 15, Marine/Drohnen-Inflation gestrichen); Restrisiko: Umsetzungs-Disziplin.
- **R-05 (Zerstörbarkeit) entschärft:** D-012 begrenzt auf gezielte Zerstörbarkeit ohne Terrain-Deformation.
- **Neu (klein):** Kristallsturm-Aetherium-Kopplung (D-027.1) als Balancing-Beobachtungspunkt registriert.

## 6. Qualitätsbewertung

| Kriterium | Bewertung | Anmerkung |
|---|---|---|
| Vollständigkeit (geforderte GDD-Liste) | gut | alle 20 GDD- + 5 Vision-Dokumente, keine Lücken |
| Konsistenz | gut | 3 Review-Wellen, finaler Link-/Zahlen-Check sauber |
| Entscheidungsdisziplin | sehr gut | 26 Entscheidungen mit Alternativen und Verwerfungsgründen |
| Spielbarkeits-Spezifikation | gut | Werte als v0.1-Richtwerte, SO-tauglich, Balancing-Methodik definiert |
| Umsetzungsreife für Sprint 3 | gut | klare technische Schnittstellen-Anforderungen (Grid, Tick, SO-Datenmodelle) |

## 7. Offene Punkte

- **Q-013, Q-014, Q-015:** Entscheidung in Sprint 3 (Research-Vorlagen vorhanden).
- **Q-018** Preispunkt (Sprint 6), **Q-019** Telemetrie-Infrastruktur (Sprint 3/6), **Q-020** Headless-KI-Runner (Sprint 3).
- Q-001–Q-012, Q-016, Q-017: entschieden (D-007–D-032) und hiermit **formal geschlossen** (Umsetzung in allen Dokumenten verifiziert).
- Terminierte Folge-Entscheidungen: siehe §2 (Beta-/Sprint-3-/Sprint-6-Fenster).

## 8. Entscheidung über den nächsten Sprint

**GO für Sprint 3 – Technical Design.**

Begründung: Alle Exit-Kriterien erfüllt; das GDD liefert vollständige, konsistente und datengetrieben spezifizierte Anforderungen; die drei P0-Architekturfragen (Q-013–Q-015) sind research-seitig entscheidungsreif.

**Sprint-3-Scope (festgelegt):**
1. Verbindliche Architektur-Entscheidungen: Q-013 (Sim-/MP-Modell), Q-014 (Pathfinding), Q-015 (ECS/DOTS), Q-020 (Headless-KI-Runner) – als D-033 ff.
2. Kern-Dokumente: Architecture.md, ModuleOverview.md, DependencyGraph.md, FolderStructure.md, CodingGuidelines.md, NamingConvention.md
3. Simulations-Dokumente: GameState.md, Serialization.md, Savegames.md, Networking.md, Replication.md, Pathfinding.md, AIArchitecture.md
4. Präsentations-/Plattform-Dokumente: Rendering.md, Lighting.md, AnimationSystem.md, InputSystem.md, AudioArchitecture.md
5. Budgets & Betrieb: PerformanceBudget.md, MemoryBudget.md, AssetBudget.md, Testing.md, Deployment.md
6. Verbindliche Prämissen: Vier-Säulen-Architektur, Unity-freier `Nova.Simulation`-Kern, Unity 6.3 LTS/URP (D-006), Grid-Infrastruktur für FoW/Pathfinding/Biome/Aetherium, SO-Datenmodelle aus GDD, 5 Determinismus-Regeln, 4 Phase-0-Spike-Validierungen (OpenQuestions).

## Offene Punkte

- Keine zusätzlich zu §7.

## Nächste Schritte

- Sprint 3 starten: Architektur-Entscheidungen treffen, TDD-Dokumente parallel über Subagenten erstellen, danach TDD-Konsistenzreview.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Sprint 2 abgeschlossen, GO für Sprint 3 | Executive Producer |
