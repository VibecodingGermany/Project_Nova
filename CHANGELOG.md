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

### Hinzugefügt
- Repository-Grundgerüst: Root-`README.md`, `AGENTS.md` (Arbeitsregeln für KI-Agenten),
  `CHANGELOG.md`, `.gitignore` (macOS + Unity-vorbereitet).
- Technical-Design-Dokumente (Sprint 3, Entwurfsstand v0.1.0) unter `docs/tech/`:
  Architektur, Modul-Übersicht, Dependency-Graph, Folder-Struktur, Coding-Guidelines,
  GameState, Serialization, Savegames, Networking, Replication, Pathfinding,
  AIArchitecture, Rendering, Lighting, AnimationSystem, InputSystem, AudioArchitecture,
  Performance-/Memory-/Asset-Budget, Testing, Deployment.

### Geändert
- Projekt erstmals unter Git-Versionskontrolle genommen und nach GitHub gespiegelt.

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

[Unreleased]: https://github.com/VibecodingGermany/Project_Nova/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/VibecodingGermany/Project_Nova/releases/tag/v0.3.0
[0.2.0]: https://github.com/VibecodingGermany/Project_Nova/releases/tag/v0.2.0
[0.1.0]: https://github.com/VibecodingGermany/Project_Nova/releases/tag/v0.1.0
