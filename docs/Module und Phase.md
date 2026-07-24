# Module und Phasen-Übersicht (*Project Nova*)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                    PROJECT NOVA                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
     │
     ├── Phase 0: MS-0 Spike & Vertical Slice (ABGESCHLOSSEN ✅)
     ├── Phase 1: MS-1 MVP (Minimum Viable Product / Spielbarer Kern)
     ├── Phase 2: MS-2 Alpha (3 Fraktionen, Doktrinen, MP-Relay)
     ├── Phase 3: MS-3 Beta (Karten-Skalierung, Superwaffen, Polish)
     └── Phase 4: MS-4 Release v1.0 (Kampagne & Launch)
```

---

## 🟢 Phase 0: MS-0 Spike & Foundation Setup (ABGESCHLOSSEN ✅)
> **Fokus:** Nachweis des deterministischen Simulationskerns, Flow-Field Pathfinding, Entitätsverwaltung & View-Brücke.

| Modul | Name / Bereich | Inhalt & Hauptkomponenten | Status |
|---|---|---|---|
| **Modul 1** | **Sim Core & Lockstep Kernel** (`Nova.Core`, `Nova.Simulation`) | `SimMath`, `EntityId`, `Tick`, `SimRandom` (PRNG), `CommandEnvelope`, `SimulationKernel` | ✅ **Fertiggestellt** |
| **Modul 2** | **Flow-Field Pathfinding** (`Nova.Simulation.Pathfinding`) | `GridPos2D`, `Direction2D`, `CostField`, `IntegrationField` (Dijkstra), `FlowField`, `PathfindingSystem` | ✅ **Fertiggestellt** |
| **Modul 3** | **Entity Storage & Movement** (`Nova.Simulation.State`, `Movement`) | `Transform2D`, `UnitState`, `EntityManager` (0-GC Free-List), `MovementSystem` ($O(N)$ Spatial Binning) | ✅ **Fertiggestellt** |
| **Modul 4** | **Unity Gameplay Bridge** (`Nova.Gameplay`) | `MatchRunner` (20-Hz-Akkumulator), `UnitViewManager` (60-FPS-Interpolation), `PathfindingTestBootstrap` | ✅ **Fertiggestellt** |
| **Modul 5** | **GameDatabase Sharding** (`Nova.Data`, `Nova.Editor`) | Sub-Registries (`UnitRegistrySO`), `GameDatabaseMasterSO`, `GameDatabaseGenerator.cs`, `UnitDefinition` Structs | ✅ **Fertiggestellt** |
| **Modul 6** | **Command Bus & Orders** (`Nova.Simulation.Commands`) | `CommandProcessorSystem` (`ISimSystem` für `Move`, `Stop`, `AttackTarget`) | ✅ **Fertiggestellt** |
| **Modul 7** | **Combat & Damage Pipeline** (`Nova.Simulation.Combat`) | `WeaponDefinition`, `CombatSystem` (Reichweiten, Waffenfrequenzen, Schadensberechnungen, Zerstörung) | ✅ **Fertiggestellt** |
| **Modul 8** | **Lockstep Hashing & Replays** (`Nova.Simulation.State`, `Replays`, `Nova.Presentation`) | `StateHashUtility` (FNV-1a 64-Bit), `ReplayBuffer`, `FlowFieldDebugView` (Scene View Gizmos) | ✅ **Fertiggestellt** |

---

## 🟡 Phase 1: MS-1 MVP – Minimum Viable Product (In Arbeit 🚀)
> **Fokus:** Spielbarer 1v1-Skirmish-Kern mit 2 Fraktionen (Allianz vs. Legion) gegen die KI auf 1 Karte / Biom.

| Modul | Name / Bereich | Geplante Features & Aufgaben | Status |
|---|---|---|---|
| **Modul 9** | **Wirtschafts- & Ressourcen-System** (`Nova.Simulation.Economy`) | Aetherium-Raffinerien, Mutterkristall-Sammler, Energienetz-Berechnung & Low-Power-Mali (-50 %) | ✅ **Fertiggestellt** |
| **Modul 10** | **Basisbau- & Bauplatz-System** (`Nova.Simulation.Construction`) | HQ-Bau-Queues, Bauzonen-Grid, Gebäudebau-Zustände, Grid-Platzierung & Kollision | ✅ **Fertiggestellt** |
| **Modul 11** | **Einheiten-Produktion & Tech-Tree** (`Nova.Simulation.Production`) | Kasernen-/Fabrik-Bau-Queues, Tier-1/2-Forschungs-Entsperrung (`ResearchTreeSystem`) | ✅ **Fertiggestellt** |
| **Modul 12** | **Fog of War & Sichtweiten-Grid** (`Nova.Simulation.Vision`) | 2D-Sichtraster, Nebel des Krieges (unbekannt / erkundet / sichtbar), Tarnungs- & Detektor-Mechanik | 🚀 **In Arbeit** |
| **Modul 13** | **Skirmish-KI (Allianz & Legion)** (`Nova.AI`) | Nutzenbasierte KI-Entscheidungsschleife (Wirtschaftsaufbau, Basisverteidigung, Angriffs-Squad-Formierung) | ⏳ Geplant |
| **Modul 14** | **RTS-UI & Command-Card** (`Nova.Presentation.UI`) | Minimap-Rendering, Ressourcenanzeige, Einheiten-Mehrfachauswahl (Selection Box), Command-Card (Icons/Hotkeys) | ⏳ Geplant |
| **Modul 15** | **Asset-Integration MS-1** (`Nova.Data`) | Einbindung der CC0-Asset-Bibliotheken (Kenney/Quaternius) für 27 Einheiten & 24 Gebäude | ⏳ Geplant |

---

## 🔵 Phase 2: MS-2 Alpha (Geplant)
> **Fokus:** 3. Fraktion (Evolvierte), Doktrinen-System, 3 Maps/Biome und 2–4 Spieler Multiplayer-Relay.

| Modul | Name / Bereich | Geplante Features & Aufgaben |
|---|---|---|
| **Modul 16** | **3. Fraktion: Die Evolvierten** (`Nova.Simulation.Factions`) | Biologisch-organische Baumechanik (Burrow, Regeneration, Biomasse-Nutzung) |
| **Modul 17** | **Commander- & Doktrinen-System** (`Nova.Simulation.Commanders`) | Passive & aktive Commander-Fähigkeiten (z. B. Artillerie-Schlag, Sensor-Overdrive) |
| **Modul 18** | **Multiplayer Command-Relay** (`Nova.Networking`) | UDP-Relay-Server-Client-Anbindung, Synchronisations-Buffer & Desync-Erkennung |
| **Modul 19** | **Map- & Biom-Erweiterung** (`Nova.Presentation.Maps`) | 3 verifizierte Karten (1v1, 2v2) in 3 Biomen (Wüste, Schnee, Dschungel/Industrie) |
| **Modul 20** | **VFX- & Teamfarben-Shader Pass** (`Nova.Presentation.Shaders`) | URP-Shader für Fraktions-Teamfarben, Treffereffekte & Aetherium-Glow (B-14) |

---

## 🟣 Phase 3: MS-3 Beta (Geplant)
> **Fokus:** Content-Skalierung (12 Maps, 10 Biome), Superwaffen, Sound-Mix & Telemetrie.

| Modul | Name / Bereich | Geplante Features & Aufgaben |
|---|---|---|
| **Modul 21** | **Superwaffen-System** (`Nova.Simulation.Superweapons`) | Orbital-Kanone, Nuke & Bio-Katalysator mit Lade-Zählern und globalen Warnungen |
| **Modul 22** | **Karten- & Biom-Skalierung** (`Nova.Data.Maps`) | Fertigstellung aller 12 Karten & 10 Biome gemäß GDD |
| **Modul 23** | **Audio-Engine & Sound-Mix** (`Nova.Audio`) | Einbindung Sonniss GDC Sound-Bibliotheken, Sprachausgabe, Kampf- & Umgebungsmusik |
| **Modul 24** | **Opt-in Telemetrie & Crash-Reporting** (`Nova.Services`) | Anonymisierte Match-Balancing-Telemetrie & automatisiertes Crash-Dump-Handling |

---

## 🔴 Phase 4: MS-4 Release v1.0 (Geplant)
> **Fokus:** Singleplayer-Kampagne, Steamworks-Integration, Golden Master.

| Modul | Name / Bereich | Geplante Features & Aufgaben |
|---|---|---|
| **Modul 25** | **Singleplayer-Kampagne** (`Nova.Campaign`) | Story-Missionen mit Skript-Events, Zwischensequenzen und Missionszielen |
| **Modul 26** | **Steamworks- & Platform-Integration** (`Nova.Platform`) | Achievements, Cloud-Saves, Matchmaking-Lobby-Verknüpfung & Golden Master Build |
