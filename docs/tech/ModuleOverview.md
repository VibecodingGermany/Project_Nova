# Modulübersicht

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 3

## Zweck

Vollständige Auflistung aller Module von Project Nova mit Zweck, Abhängigkeiten und Datenhoheit. Verbindliche Arbeitsteilung für die Sprint-7-Implementierung; jedes Modul erhält später ein eigenes Detail-TDD. Schichtenzuordnung und erlaubte Abhängigkeitsrichtungen: [./Architecture.md](./Architecture.md) und [./DependencyGraph.md](./DependencyGraph.md).

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-006, D-008, D-010–D-016, D-021–D-024, D-033–D-036
- [./Architecture.md](./Architecture.md)
- [../gamedesign/Economy.md](../gamedesign/Economy.md), [../gamedesign/Resources.md](../gamedesign/Resources.md), [../gamedesign/Buildings.md](../gamedesign/Buildings.md), [../gamedesign/ResearchTree.md](../gamedesign/ResearchTree.md), [../gamedesign/Weapons.md](../gamedesign/Weapons.md), [../gamedesign/DamageSystem.md](../gamedesign/DamageSystem.md), [../gamedesign/NeutralUnits.md](../gamedesign/NeutralUnits.md), [../gamedesign/FogOfWar.md](../gamedesign/FogOfWar.md), [../gamedesign/VictoryConditions.md](../gamedesign/VictoryConditions.md)
- [../research/Pathfinding.md](../research/Pathfinding.md), [../research/FogOfWar.md](../research/FogOfWar.md), [../research/KI_Architektur.md](../research/KI_Architektur.md), [../research/Animation_Audio_UI.md](../research/Animation_Audio_UI.md)

## 1. Simulations-Module (Assembly `Nova.Simulation`, Unity-frei)

Alle Sim-Module implementieren `ISimulationModule` (Tick in fester Reihenfolge, siehe Architecture.md §3), halten ihren State vollständig serialisierbar (D-033 Regel 5) und mutieren ausschließlich command-/tick-getrieben.

### 1.1 SimulationCore

- **Zweck:** Tick-Kernel (`SimulationKernel`, `SimulationClock` 10 Hz), Command-Pufferung/-Sortierung/-Anwendung, `DeterministicRandom`, State-Container (`SimState`), View-Event-Sammler, Modul-Orchestrierung.
- **Abhängigkeiten:** keine fachlichen (Basis aller Sim-Module); keine Unity-Referenzen.
- **Datenhoheit:** Tick-Zähler, Command-Queue, PRNG-Seed/-Zustand, Entity-Registry (IDs, Allokation), Event-Puffer.

### 1.2 Grid

- **Zweck:** Uniformes Integer-Grid, 1-m-Tiles (D-034), Kartengrößen S/M/L = 128/192/256. Geteilte Infrastruktur für Pathfinding (Cost-/Clearance-Layer), FoW (Bitmask), Aetherium-Ausbreitung, Bauplatzierung und Biom-Effekte – eine Grid-Basis statt Einzelsysteme.
- **Abhängigkeiten:** SimulationCore.
- **Datenhoheit:** statisches Terrain-Layer (Höhenklasse, Passierbarkeit), dynamische Belegung (Dirty-Flagging), Tile-Metadaten (Biom, Hazard-Flags).

### 1.3 Pathfinding

- **Zweck:** Gruppen-Flow-Fields (Dijkstra-Maps) für globale Wegfindung, lokale Separation im MVP (ORCA ab Alpha), 3 Clearance-Radien, Dirty-Flagging bei dynamischen Hindernissen (Mauern, Trümmer), separates Luft-Steering (D-034). CPU-Budget ≤ 2–4 ms.
- **Abhängigkeiten:** SimulationCore, Grid; Burst-Fast-Path optional über `Nova.Simulation.Jobs`.
- **Datenhoheit:** Flow-Field-Cache, Clearance-Layer, Bewegungsaufträge/Steering-State der Einheiten.

### 1.4 FogOfWar (Sim-Seite)

- **Zweck:** Sicht-Berechnung auf dem 1-m-Grid als Bitmask, 3 Zustände (unsichtbar/erkundet/sichtbar), Sicht-Tick 5–10 Hz (GDD), Detektor-/Tarnungs-Regeln (D-031.2, D-032.1). Sim-autoritativ, weil Sicht Gameplay-Regeln steuert (Targeting, Tarnung).
- **Abhängigkeiten:** SimulationCore, Grid.
- **Datenhoheit:** Sicht-Bitmasken pro Spieler, Detektor-Status, FoW-Deltas für die View.

### 1.5 Economy

- **Zweck:** Aetherium-Wirtschaft: Mutterkristall-Reserve, nachwachsende Ausläufer, Überernte-Stufen, Ausbreitung auf dem Grid (D-010); Harvester-Logik (300 AE/Ladung, Raffinerie mit 1 Harvester, D-024), Lager-Kapazität (+2.000 AE/Lager, anteiliger Verlust), Energie/Low-Power (−50 %, D-030), Startkapital 1.000 AE.
- **Abhängigkeiten:** SimulationCore, Grid (Ausbreitung), Pathfinding (Harvester-Routen).
- **Datenhoheit:** Ressourcenkonten, Feld-Zustände (Reserve, Wachstumsstufe, Überernte), Energiebilanz.

### 1.6 Combat

- **Zweck:** Waffen, Projektile (deterministisch simuliert), Schaden/Rüstung ([DamageSystem/ArmorSystem](../gamedesign/DamageSystem.md)), Zielerfassung unter FoW-Regeln, Aggressions-Modi (Halten/Abwehren/Freies Feuer, D-031.6), gezielte Zerstörbarkeit (Trümmer, Vegetations-Brände, Brücken, D-012), Superwaffen-Schadensanwendung.
- **Abhängigkeiten:** SimulationCore, Grid, FogOfWar, Pathfinding (Trümmer → Dirty-Flags).
- **Datenhoheit:** Trefferpunkte/Rüstungs-State aller Entities, Projektil-State, Feuer-Cooldowns, Zerstörungs-/Trümmer-State.

### 1.7 Production

- **Zweck:** Bau-Queues und Einheitenproduktion (12 Gebäudetypen, D-008), Bauplatzierung auf dem Grid, Evolvierte-Wachstumsbauweise (Keim/Reifung/Regeneration statt Reparatur, D-011), HQ-Neuaufbau SPC_REBASE (D-031.1), Elite-Limits (D-015), Verteidigungsplattform-Module.
- **Abhängigkeiten:** SimulationCore, Grid, Economy (Kosten/Energie), Research (Freischaltungen).
- **Datenhoheit:** Queue-State, Baustellen-/Reife-State, Platzierungs-Belegung, Elite-Zähler.

### 1.8 Research

- **Zweck:** Tech-Bäume (12–16 Techs/Fraktion, Tier 1–3), max. 1 Ausschluss-Paar pro Fraktion, Low-Power-Interaktion (D-030), Freischaltung von Einheiten/Upgrades/Eliten/Superwaffen.
- **Abhängigkeiten:** SimulationCore, Economy (Kosten, Low-Power), Production (Gate für Freischaltungen).
- **Datenhoheit:** geforschte Techs, laufende Forschung, Ausschluss-Status.

### 1.9 AI

- **Zweck:** 3-Schichten-KI: Utility-Director (strategisch) + HTN-light (taktisch) + Squad-Behaviour-Trees ([KI_Architektur](../research/KI_Architektur.md)); Schwierigkeit über `DifficultyProfileSO`-Daten; gibt ausschließlich Commands ab (Command-only, D-033-konform), versteht Feldbewirtschaftung (D-010).
- **Abhängigkeiten:** SimulationCore, Economy, Production, Research, Combat, FogOfWar (nur eigene Sicht), Pathfinding.
- **Datenhoheit:** KI-Planungs-State (pro KI-Spieler), Squad-Zuordnungen, Utility-Scores.

### 1.10 NeutralUnits

- **Zweck:** Neutrale Map-Elemente: Critters, feindliche Lager als Objectives (Aetherium-Belohnung), capturebare Geschütztürme (Kanal-Capture 5 s, D-016/D-022), einfache Reaktionslogik.
- **Abhängigkeiten:** SimulationCore, Combat, Grid.
- **Datenhoheit:** neutrale Entities, Lager-/Turm-State (Besitzer, Capture-Fortschritt), Belohnungs-Auszahlung (an Economy).

### 1.11 Superweapons

- **Zweck:** Superwaffen-Ladung/-Abfeuerung, Limit 1 pro Spieler mit globaler Bau-Ansage, 25-%-Rückschlag bei Zerstörung im geladenen Zustand (D-023); fraktionsspezifische Effekte inkl. Kristallsturm-Aetherium-Interaktion (D-027.1).
- **Abhängigkeiten:** SimulationCore, Combat (Schadensanwendung), Economy/Resources (Feld-Interaktion), Production (Limit/Bau).
- **Datenhoheit:** Lade-State, Cooldown, globale Ansage-Events.

### 1.12 Match/Session (Sim-Seite)

- **Zweck:** Sieg-/Niederlagen-Auswertung ([VictoryConditions](../gamedesign/VictoryConditions.md), Vernichtungsregel D-031.4), Match-Timer, `MatchResult`-Datensatz (für SimRunner-Auswertung, D-036), Modus-Parameter (Skirmish, FFA, Survival-Regeln).
- **Abhängigkeiten:** SimulationCore, Combat/Economy (Auswertungsgrundlagen).
- **Datenhoheit:** Match-Status, Siegbedingungs-State, Ergebnisdatensatz.

### 1.13 Replay

- **Zweck:** Aufzeichnung (Start-Seed, Map-/Slot-Konfiguration, DefinitionSnapshot-Version, vollständiger Command-Stream, periodische Checksums) und deterministische Wiedergabe über den Kernel; Beobachter-Fähigkeit ab Beta (D-033).
- **Abhängigkeiten:** SimulationCore (Kernel, Serializer), Match/Session.
- **Datenhoheit:** Replay-Dateiformat/-Stream, Wiedergabe-State.

### 1.14 Savegame

- **Zweck:** Vollständige State-Serialisierung/Deserialisierung (D-033 Regel 5) über `IStateSerializer`, versioniertes Binärformat, Tick-exaktes Wiederaufsetzen.
- **Abhängigkeiten:** SimulationCore (alle Modul-States).
- **Datenhoheit:** Savegame-Format/-Versionierung.

## 2. Bridge-Module (Assembly `Nova.Game`)

### 2.1 Session/Bridge

- **Zweck:** `MatchSession`-Orchestrierung (Map-Load, Slots, Start-Seed), `IMatchTransport` inkl. `LocalLoopbackTransport` (SP = lokaler Server, D-033), Input→Command-Übersetzung, Tick-Antrieb des Kernels, Event-Dispatch an Präsentation/UI.
- **Abhängigkeiten:** Nova.Simulation, Nova.Data.
- **Datenhoheit:** Unity-seitiger Session-State (kein Spielzustand!).

### 2.2 GameDatabase/Datenbindung (Assembly `Nova.Data`)

- **Zweck:** SO-Registry `GameDatabase` (Definitions-only-SOs, kein Runtime-State), Laden/Validieren aller Definitionen, Erzeugung des reinen `DefinitionSnapshot` für die Simulation.
- **Abhängigkeiten:** Nova.Simulation (nur Definitions-Datentypen).
- **Datenhoheit:** alle statischen Spieldaten (Einheiten, Gebäude, Waffen, Tech, Karten-Metadaten, DifficultyProfile).

## 3. Präsentations-Module (Assembly `Nova.Presentation`)

### 3.1 Camera

- **Zweck:** RTS-Standardkamera: Pitch 50–60°, Zoom-Stufen, Rotation optional/ab Beta (D-019, D-029.5), Edge-Scrolling, Minimap-Navigation.
- **Abhängigkeiten:** Bridge (Karten-Dimensionen), Nova.UI (Minimap-Klicks).

### 3.2 Selection

- **Zweck:** Einheiten-/Gebäude-Selektion (Klick, Box-Select, Gruppen), Kontext-Intents an die Bridge (`ICommandSink`), Selektions-Visualisierung.
- **Abhängigkeiten:** Bridge (Commands, Sichtbarkeits-Filter über FoW-Events), Camera.

### 3.3 UnitsView / BuildingsView

- **Zweck:** Instanziierung/Abbau von View-Repräsentationen aus View-Events, Bewegungs-Interpolation zwischen Ticks, Animations-Steuerung (Mecanim nur Infanterie, Code-Animation Fahrzeuge, 3-stufiges LOD – [Animation_Audio_UI](../research/Animation_Audio_UI.md)), gebatchtes Healthbar-Mesh-Overlay.
- **Abhängigkeiten:** Bridge (View-Events, Snapshots), Nova.Data (visuelle Definitionen).

### 3.4 VFX

- **Zweck:** Effekte aus View-Events (Mündungsfeuer, Treffer, Brände, Wetter/Hazards pro Biom, D-017), Zerstörungs-/Trümmer-Visualisierung (D-012).
- **Abhängigkeiten:** Bridge (Events), UnitsView.

### 3.5 FoW-Rendering

- **Zweck:** Darstellung der Sim-FoW-Bitmask als URP Full Screen Pass (RenderGraph-konform), Übergänge der 3 Zustände, Minimap-FoW-Textur für Nova.UI.
- **Abhängigkeiten:** Bridge (FoW-Deltas), URP/RenderGraph.

### 3.6 Audio

- **Zweck:** AudioService-Abstraktion; MVP Unity Audio dahinter, FMOD ab Alpha (Austausch ohne Callsite-Änderungen); Event-getriebene Sound-Auslösung, Commander-Voice (D-009).
- **Abhängigkeiten:** Bridge (Events), Nova.Data (Audio-Definitionen).

## 4. UI-Module (Assembly `Nova.UI`)

### 4.1 HUD/Menüs

- **Zweck:** UI-Toolkit-basiert: Ressourcenanzeige, Produktions-Queues, Bau-Menü, Forschungsübersicht, Superwaffen-Status/Ansagen, Match-Ende-Dialoge; uGUI ausschließlich World-Space-Elemente.
- **Abhängigkeiten:** Bridge (abgeleitete Anzeige-Daten, `ICommandSink`), Nova.Data.

### 4.2 Minimap

- **Zweck:** Kartenübersicht inkl. FoW-Textur (von FoW-Rendering), Radar-Pings (Team-geteilt, D-029.4), Kamera-Viewport-Anzeige und Navigation.
- **Abhängigkeiten:** FoW-Rendering (Textur), Camera, Bridge (Ping-Events).

## 5. Tools & Headless

### 5.1 Nova.Tools (Editor-only)

- **Zweck:** Karten-Authoring/Validierung (Startpositionen, Felder, Engstellen-Anforderung Survival D-028.7), SO-Daten-Validierung, Bake-Helfer (Grid aus Szene).
- **Abhängigkeiten:** Nova.Data, UnityEditor.

### 5.2 Nova.SimRunner (reine .NET-Konsole, D-036)

- **Zweck:** Headless KI-vs-KI-Läufe für die Balancing-Pipeline (CI-Nachtläufe), Match-Result-Auswertung, reproduzierbare Match-Fixtures, Desync-Jagd via Checksums.
- **Abhängigkeiten:** ausschließlich `Nova.Simulation` (+ ggf. serialisierte DefinitionSnapshots); **kein Unity**.
- **Datenhoheit:** Run-Konfiguration, Ergebnis-Aggregation (CSV/JSON).

## Offene Punkte

1. Feinzerlegung: Ob Economy/Resources, UnitsView/BuildingsView und HUD-Menüs als jeweils ein Modul oder zwei Assemblies/Namespaces geführt werden, wird im Sprint-7-Setup anhand der Dateigrößen entschieden (Modulgrenzen oben sind fachlich verbindlich, physische Aufteilung nicht).
2. NeutralUnits: Reaktions-KI der neutralen Lager – eigene Mini-BT-Schicht oder Teil des AI-Moduls? → Detail-TDD `NeutralUnits` (Sprint 7).
3. Wetter/Hazards: sim-seitige Effekte (Schaden, Sicht-Malus) sind noch keinem Sim-Modul zugeordnet – Zuordnung (Grid vs. eigenes Environment-Modul) offen → `GameState.md`/Detail-TDD.
4. Replay- und Beobachter-Fähigkeit der UI (Spectator-HUD) ist Beta-Scope; Schnittstellen-Vorkehrung unklar → `Networking.md`.

## Nächste Schritte

- Detail-TDDs je Sim-Modul priorisiert nach Sprint-7-Scope (SimulationCore, Grid, Pathfinding, Economy zuerst).
- `DependencyGraph.md` als Review-Checkliste in die Sprint-7-Definition-of-Done aufnehmen.
- Datenhoheiten mit `GameState.md` (Serialisierungs-Design) abgleichen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Technical Director |
