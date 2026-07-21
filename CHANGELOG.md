# Changelog

Alle nennenswerten Änderungen an *Project Nova* werden in dieser Datei dokumentiert.

Das Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
die Versionierung folgt (in der aktuellen Doku-Phase) dem Dokumentationsstand des Wikis
([docs/README.md](docs/README.md)). Kategorien: `Hinzugefügt`, `Geändert`, `Behoben`,
`Entfernt`, `Entschieden` (projektspezifisch für DecisionLog-Einträge).

> **Pflege-Regel:** Jede inhaltliche Änderung ergänzt einen Eintrag unter `[Unreleased]`.
> Beim Abschluss eines Sprints wird `[Unreleased]` in eine datierte Version überführt.
> Details siehe [AGENTS.md](AGENTS.md).

## [Unreleased]

## [0.5.0] – 2026-07-21 · Sprint 4: Architecture Review + Governance

### Hinzugefügt
- **Team-/Beitrags-Governance:** `CONTRIBUTING.md` (Team-Ablauf, PR-Pflicht, Release-Flow),
  PR-Vorlage und `CODEOWNERS` sowie ein günstiger, abhängigkeitsfreier CI-Check
  (`docs-check`, GitHub Actions) für tote interne Doku-Links.
- **Sprint 4 – Architecture Review abgeschlossen:** sechs adversariale Review-Berichte unter
  `docs/tech/review/` (Performance, Wartbarkeit & Prozess, Architektur-Kohärenz & Korrektheit,
  Multiplayer & Netcode, Skalierung & Systemgrenzen, GDD↔TDD-Konsistenz; im Wiki-Index verlinkt)
  und der Abschlussbericht [Sprint04_Report.md](docs/production/sprints/Sprint04_Report.md).

### Geändert
- **Repository auf öffentlich umgestellt**, Community-Projekt der Organisation `VibecodingGermany`.
- **`main` ist geschützt – Änderungen nur noch über Pull Requests** (Branch Protection:
  Review + grüne CI, keine direkten Pushes). `AGENTS.md` auf 2.0.0 (PR-only).
- **Sprint-4-Findings in 22 GDD-/TDD-Dokumente eingearbeitet** (Auflösung der Review-Widersprüche):
  Angriffsreichweiten metrisch → Grid-Felder (D-047, 1 Tile = 1 m); Weapons.md/Buildings.md/
  Vehicles.md je einzige führende Wertequelle; Alpha-Mutant-Doppeldefinition aufgelöst;
  **Assembly-Topologie kanonisiert (D-043) inkl. `ModuleOverview.md` vollständig nachgezogen**
  (KI als eigene Unity-freie Assembly `Nova.AI`); Managed-first (D-045); globaler
  600-Einheiten-Deckel (D-048); GameDatabase-Sharding (D-049); Post-Match-Re-Simulation als
  MP-Trust-Anchor (D-046); Quantum-Fallback gestrichen (D-051). `DocumentationStandard.md`
  1.1.0: Grundprinzip „Single Source of Truth für Werte" (D-047).
- **Risikoregister ehrlicher (RiskAnalysis 1.4.0):** neue reale Projektrisiken R-13 Bus-Faktor
  (W=hoch), R-14 ARM↔x86-Determinismus, R-15 KI-Code-Desync, R-16 Zeit-/Kapazität (W=hoch).

### Entschieden
- **D-043–D-052** (Sprint-4-Architecture-Review-Auflösungen, DecisionLog → 1.6.1): Assembly-
  Topologie (D-043), gestuftes Sim-Tick-Modell + Pflicht-Gate V5 (D-044), Managed-first (D-045),
  MP-Trust-Anchor (D-046), Werte-Single-Source (D-047), Skalierungs-Deckel (D-048), CI-Realismus
  + DB-Sharding (D-049), gestuftes Branching (D-050), Quantum-Fallback gestrichen (D-051),
  Referenzhardware (D-052).

## [0.4.0] – 2026-07-21 · Sprint 3: Technical Design

### Hinzugefügt
- Vollständiges Technical Design (23 Dokumente) unter `docs/tech/`: Architektur-Kern
  (Architecture, ModuleOverview, DependencyGraph, FolderStructure, CodingGuidelines,
  NamingConvention), Simulation & Daten (GameState, Serialization, Savegames),
  Multiplayer (Networking, Replication), Gameplay-Systeme (Pathfinding, AIArchitecture),
  Präsentation (Rendering, Lighting, AnimationSystem, InputSystem, AudioArchitecture),
  Budgets & Betrieb (PerformanceBudget, MemoryBudget, AssetBudget, Testing, Deployment).
- Sprint-3-Abschlussbericht ([docs/production/sprints/Sprint03_Report.md](docs/production/sprints/Sprint03_Report.md)).
- Repository-Grundgerüst: Root-`README.md`, `AGENTS.md` (Arbeitsregeln für KI-Agenten),
  `CHANGELOG.md`, `.gitignore` (macOS + Unity-vorbereitet); initiale Spiegelung zu GitHub.

### Entschieden
- 10 Architektur-Entscheidungen (D-033–D-042): determinismus-fähige Command-Simulation
  mit Lockstep-Relay-Zielbild (Q-013), Flow-Field-Pathfinding (Q-014), OOP+Burst statt
  DOTS (Q-015), Nova.SimRunner (Q-020), Burst/Managed-Doppelstruktur, Disconnect-Regel,
  Audio-Backend (FMOD ab Alpha), Forward/Realtime-Licht, Sentry, Sim-Tick-Budget ≤8 ms.

### Geändert
- Detail-Angleichungen GDD↔TDD (Disconnect-Regel final, Sim-Tick-Budget) in
  VictoryConditions, MultiplayerModes, PerformanceBudget, Networking.
- AGENTS.md Regel 1: Push nach jedem Versionsbump dauerhaft freigegeben (Anordnung
  Projektinhaber).

## [0.3.0] – 2026-07-21 · Sprint 2: Game Design

### Hinzugefügt
- Vollständiges Game Design Document (25 Dokumente): Vision, USP, Zielgruppe,
  CoreGameplay, GameLoop sowie das komplette GDD (Fraktionen, Gebäude, Einheiten,
  Wirtschaft, Forschung, Kampf-/Schadens-/Rüstungssystem, Karten, Biome, neutrale
  Einheiten, Fog of War, Commander-System, Multiplayer-Modi, Siegbedingungen,
  Balancing, Kampagne).
- Sprint-2-Abschlussbericht ([docs/production/sprints/Sprint02_Report.md](docs/production/sprints/Sprint02_Report.md)).

### Entschieden
- 26 Entscheidungen (D-007–D-032): Geschäftsmodell (Premium, Singleplayer-first),
  12 Gebäudetypen, Aetherium-Hybridwirtschaft, gezielte Zerstörbarkeit, Capture-System,
  Superwaffen-Limit, Fraktions-Sonderregeln, Kampagnen-Struktur u. a.

### Geändert
- Scope reduziert und beziffert (36 statt 54 Gebäude-Assets, 9 statt 15 Elite-Einheiten;
  Marine-/Drohnen-Inflation gestrichen) – Risiko R-01 teilentschärft.

## [0.2.0] – 2026-07-21 · Sprint 1: Research

### Hinzugefügt
- 10 Research-Dokumente unter `docs/research/`: RTS-Markt/Wettbewerb,
  Multiplayer-Simulation, Unity ECS/DOTS, Pathfinding, Fog of War, Open-Source-RTS-
  Architekturen, Unity Best Practices, KI-Architektur, Animation/Audio/UI,
  Asset-Store-Landschaft – jeweils mit ≥3 verglichenen Alternativen als
  Entscheidungsvorlagen.
- Sprint-1-Abschlussbericht.

## [0.1.0] – 2026-07-21 · Sprint 0: Projektinitialisierung

### Hinzugefügt
- Wiki-Grundgerüst und verbindlicher [Dokumentationsstandard](docs/meta/DocumentationStandard.md).
- Analyse-Dokumente: Wissensbasis, Inkonsistenz-Analyse, Gap-Analyse, Prioritätenliste.
- Produktions-Basis: Sprint-Planung, DecisionLog, OpenQuestions, RiskAnalysis.
- Übernahme der historischen Quelldokumente (`RTS_Game_Design_Outline.md`,
  `RTS_Technisches_Planungsdokument.md`, `RTS_Asset_Pipeline.md`).

[Unreleased]: https://github.com/VibecodingGermany/Project_Nova/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/VibecodingGermany/Project_Nova/releases/tag/v0.5.0
[0.4.0]: https://github.com/VibecodingGermany/Project_Nova/releases/tag/v0.4.0
[0.3.0]: https://github.com/VibecodingGermany/Project_Nova/releases/tag/v0.3.0
[0.2.0]: https://github.com/VibecodingGermany/Project_Nova/releases/tag/v0.2.0
[0.1.0]: https://github.com/VibecodingGermany/Project_Nova/releases/tag/v0.1.0
