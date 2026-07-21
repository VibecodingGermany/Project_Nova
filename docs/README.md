# Project Nova – Entwicklungs-Wiki

**Version:** 0.4.0 | **Status:** Living Document | **Verantwortungsbereich:** Executive Producer / Technical Writer | **Sprint:** 3

## Zweck

Zentraler Einstiegspunkt in die gesamte Projektdokumentation von *Project Nova* (Arbeitstitel), einem modernen Echtzeitstrategiespiel (Unity 6.3 LTS, C#, URP) mit Base-Building, drei Fraktionen und der Kristallressource **Aetherium**.

Dieses Wiki folgt dem Prinzip vieler kleiner, logisch getrennter und untereinander verlinkter Markdown-Dokumente statt weniger Monolithen. Regeln siehe [meta/DocumentationStandard.md](meta/DocumentationStandard.md); Arbeitsregeln für Agenten: [../AGENTS.md](../AGENTS.md). Repository: `github.com/VibecodingGermany/Project_Nova` (Push nach jedem Versionsbump).

## Quelldokumente (Projektroot)

- [RTS_Game_Design_Outline.md](../RTS_Game_Design_Outline.md) – Game-Design-Grundgerüst (historisch)
- [RTS_Technisches_Planungsdokument.md](../RTS_Technisches_Planungsdokument.md) – verbindliche technische Grundausrichtung
- [RTS_Asset_Pipeline.md](../RTS_Asset_Pipeline.md) – Asset-Bedarf und Paketstruktur (wird in Sprint 5 korrigiert)

## Dokumentbereiche

| Bereich | Ordner | Status | Sprint |
|---|---|---|---|
| Meta & Standards | [meta/](meta/DocumentationStandard.md) | aktiv | 0 |
| Analyse | [analysis/](analysis/KnowledgeBase.md) | abgeschlossen | 0 |
| Research | [research/](research/) | abgeschlossen | 1 |
| Vision | [vision/](vision/) | abgeschlossen | 2 |
| Game Design | [gamedesign/](gamedesign/) | abgeschlossen | 2 |
| Technical Design | [tech/](tech/) | abgeschlossen | 3 |
| Architecture Review | tech/review/ | bereit (GO) | 4 |
| Asset Pipeline | assets/ | geplant | 5 |
| Production | [production/](production/SprintPlanning.md) | aktiv | 0–6 |
| Sprint-Berichte | [production/sprints/](production/sprints/) | laufend | alle |

## Aktuelle Dokumente

### Meta
- [DocumentationStandard.md](meta/DocumentationStandard.md) – verbindlicher Dokumentationsstandard

### Analyse (Sprint 0)
- [KnowledgeBase.md](analysis/KnowledgeBase.md) – destillierte Wissensbasis aus den Quelldokumenten
- [Inconsistencies.md](analysis/Inconsistencies.md) – erkannte Widersprüche (alle aufgelöst, D-007–D-032)
- [GapAnalysis.md](analysis/GapAnalysis.md) – fehlende Bereiche und Dokumente
- [PriorityList.md](analysis/PriorityList.md) – priorisierte Arbeitsliste

### Research (Sprint 1)
- [RTS_Markt_Wettbewerb.md](research/RTS_Markt_Wettbewerb.md) · [Multiplayer_Simulation.md](research/Multiplayer_Simulation.md) · [Unity_ECS_DOTS.md](research/Unity_ECS_DOTS.md) · [Pathfinding.md](research/Pathfinding.md) · [FogOfWar.md](research/FogOfWar.md) · [RTS_Architekturen_OpenSource.md](research/RTS_Architekturen_OpenSource.md) · [Unity_BestPractices.md](research/Unity_BestPractices.md) · [KI_Architektur.md](research/KI_Architektur.md) · [Animation_Audio_UI.md](research/Animation_Audio_UI.md) · [AssetStore_Landschaft.md](research/AssetStore_Landschaft.md)

### Vision (Sprint 2)
- [Vision.md](vision/Vision.md) · [USP.md](vision/USP.md) · [TargetAudience.md](vision/TargetAudience.md) · [CoreGameplay.md](vision/CoreGameplay.md) · [GameLoop.md](vision/GameLoop.md)

### Game Design (Sprint 2)
- Fraktionen & Einheiten: [Factions.md](gamedesign/Factions.md) · [Buildings.md](gamedesign/Buildings.md) · [Infantry.md](gamedesign/Infantry.md) · [Vehicles.md](gamedesign/Vehicles.md) · [Aircraft.md](gamedesign/Aircraft.md)
- Wirtschaft & Forschung: [Resources.md](gamedesign/Resources.md) · [Economy.md](gamedesign/Economy.md) · [ResearchTree.md](gamedesign/ResearchTree.md)
- Kampfsystem: [Weapons.md](gamedesign/Weapons.md) · [DamageSystem.md](gamedesign/DamageSystem.md) · [ArmorSystem.md](gamedesign/ArmorSystem.md)
- Welt: [Maps.md](gamedesign/Maps.md) · [Biomes.md](gamedesign/Biomes.md) · [NeutralUnits.md](gamedesign/NeutralUnits.md) · [FogOfWar.md](gamedesign/FogOfWar.md)
- Meta & Regeln: [CommanderSystem.md](gamedesign/CommanderSystem.md) · [MultiplayerModes.md](gamedesign/MultiplayerModes.md) · [VictoryConditions.md](gamedesign/VictoryConditions.md) · [Balancing.md](gamedesign/Balancing.md) · [Campaign.md](gamedesign/Campaign.md)

### Technical Design (Sprint 3)
- Architektur-Kern: [Architecture.md](tech/Architecture.md) · [ModuleOverview.md](tech/ModuleOverview.md) · [DependencyGraph.md](tech/DependencyGraph.md) · [FolderStructure.md](tech/FolderStructure.md) · [CodingGuidelines.md](tech/CodingGuidelines.md) · [NamingConvention.md](tech/NamingConvention.md)
- Simulation & Daten: [GameState.md](tech/GameState.md) · [Serialization.md](tech/Serialization.md) · [Savegames.md](tech/Savegames.md)
- Multiplayer: [Networking.md](tech/Networking.md) · [Replication.md](tech/Replication.md)
- Gameplay-Systeme: [Pathfinding.md](tech/Pathfinding.md) · [AIArchitecture.md](tech/AIArchitecture.md)
- Präsentation: [Rendering.md](tech/Rendering.md) · [Lighting.md](tech/Lighting.md) · [AnimationSystem.md](tech/AnimationSystem.md) · [InputSystem.md](tech/InputSystem.md) · [AudioArchitecture.md](tech/AudioArchitecture.md)
- Budgets & Betrieb: [PerformanceBudget.md](tech/PerformanceBudget.md) · [MemoryBudget.md](tech/MemoryBudget.md) · [AssetBudget.md](tech/AssetBudget.md) · [Testing.md](tech/Testing.md) · [Deployment.md](tech/Deployment.md)
- Architecture Review (Sprint 4): [Performance](tech/review/Review_Performance.md) · [Wartbarkeit & Prozess](tech/review/Review_Wartbarkeit_Prozess.md) · [Architektur-Kohärenz](tech/review/Review_ArchitekturKohaerenz.md) · [Multiplayer & Netcode](tech/review/Review_Multiplayer_Netcode.md) · [Skalierung & Systemgrenzen](tech/review/Review_Skalierung_Systemgrenzen.md) · [GDD↔TDD-Konsistenz](tech/review/Review_GDD-TDD-Konsistenz.md)

### Production
- [SprintPlanning.md](production/SprintPlanning.md) – Sprint-Definitionen und Status
- [DecisionLog.md](production/DecisionLog.md) – alle Entscheidungen (D-001–D-042)
- [OpenQuestions.md](production/OpenQuestions.md) – offene Fragen (nur Q-018, Q-019)
- [RiskAnalysis.md](production/RiskAnalysis.md) – Risikoregister
- Sprint-Berichte: [Sprint 0](production/sprints/Sprint00_Report.md) · [Sprint 1](production/sprints/Sprint01_Report.md) · [Sprint 2](production/sprints/Sprint02_Report.md) · [Sprint 3](production/sprints/Sprint03_Report.md)

## Status-Board

| Sprint | Thema | Status |
|---|---|---|
| 0 | Projektinitialisierung | **abgeschlossen** |
| 1 | Research | **abgeschlossen** |
| 2 | Game Design | **abgeschlossen** |
| 3 | Technical Design | **abgeschlossen** |
| 4 | Architecture Review | bereit (GO) |
| 5 | Asset Audit | blockiert bis Sprint 4 |
| 6 | Produktionsplanung | blockiert bis Sprint 5 |
| 7 | Implementierung | blockiert bis Sprint 6 |

## Abhängigkeiten

- Alle Wiki-Dokumente folgen [meta/DocumentationStandard.md](meta/DocumentationStandard.md).
- Verbindlicher Technik-Stack: Unity 6.3 LTS, C#, URP ([DecisionLog D-006](production/DecisionLog.md)); Architektur: D-033–D-042.
- Verbindliches Design: [DecisionLog D-007–D-032](production/DecisionLog.md); führende Zahlenanker: [Economy.md](gamedesign/Economy.md), [Resources.md](gamedesign/Resources.md).

## Offene Punkte

- Q-018 (Preispunkt), Q-019 (Telemetrie): Sprint 6.
- Vier Phase-0-Spike-Validierungen als Pflicht-Checkliste für Sprint 7.

## Nächste Schritte

- Sprint 4 (Architecture Review): unabhängige Review-Agenten mit Widerspruchs-Mandat gemäß [Sprint03_Report.md](production/sprints/Sprint03_Report.md) §8.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Initiale Wiki-Struktur nach Sprint 0 | Technical Writer |
| 0.2.0 | 2026-07-21 | Research-Bereich (10 Dokumente) aufgenommen, Sprint 1 abgeschlossen | Technical Writer |
| 0.3.0 | 2026-07-21 | Vision- und GDD-Bereich (25 Dokumente) aufgenommen, Sprint 2 abgeschlossen | Technical Writer |
| 0.4.0 | 2026-07-21 | Technical-Design-Bereich (23 Dokumente) aufgenommen, Sprint 3 abgeschlossen | Technical Writer |
