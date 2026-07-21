# Folder Structure – Verbindliche Unity-Projektstruktur

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 3

## Zweck

Dieses Dokument legt die verbindliche Verzeichnis- und Assembly-Struktur des Unity-Projekts fest. Es konkretisiert den TPD-§10-Vorschlag und die Assembly-Empfehlung aus dem Sprint-1-Research (Unity_BestPractices.md §4) unter den Bedingungen von D-033–D-036: Unity-freier Simulationskern (`Nova.Simulation`), Assembly-Trennung mit erzwungener Referenzrichtung, getrennter Third-Party-Bereich, SO-Registry-Ordner und der headless Konsolen-Runner `Nova.SimRunner` (D-036). Verbindlich für alle Implementierungs-Sprints ab Sprint 7; Abweichungen nur per ADR/Eintrag im DecisionLog.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-006 (Unity 6.3 LTS + URP), D-033 (Sim/View-Trennung, 5 Regeln), D-034 (Pathfinding Grid/Jobs), D-035 (OOP+SO-Gerüst, Unity-freie `Nova.Simulation`), D-036 (`Nova.SimRunner`)
- [../research/Unity_BestPractices.md](../research/Unity_BestPractices.md) – §4 (Assembly Definitions), §3 (SO-Datenmodell)
- [../research/Multiplayer_Simulation.md](../research/Multiplayer_Simulation.md) – §7 (Architekturregeln)
- [../../RTS_Technisches_Planungsdokument.md](../../RTS_Technisches_Planungsdokument.md) – §10 (Ausgangsstruktur), §11 (datengetrieben)
- [./CodingGuidelines.md](./CodingGuidelines.md) – Layer-Regeln, die diese Struktur durchsetzt
- [./NamingConvention.md](./NamingConvention.md) – Namespaces, die der Ordnerstruktur entsprechen
- [./Testing.md](./Testing.md) – CI-/Test-Integration (SimRunner, EditMode-Tests)

## 1. Repository-Grundstruktur

Der Repository-Root **ist** gleichzeitig die Unity-Projekt-Wurzel. Dadurch liegen `docs/` und `tools/` als normale Geschwister neben `Assets/`, ohne vom Unity-Import erfasst zu werden.

```text
<Repo-Root>/
├── Assets/                  # Unity-Projektinhalt (siehe §2)
├── Packages/                # manifest.json, packages-lock.json (URP, Burst, Jobs, Test Framework)
├── ProjectSettings/         # Unity-Projektsettings (Unity-Version gepinnt, D-006)
├── tools/
│   └── Nova.SimRunner/      # .NET-Konsolen-App, headless KI-vs-KI (D-036, siehe §6)
├── docs/                    # Projektwiki (bestehend, unverändert)
└── ci/                      # Build-/CI-Skripte (BuildPipeline-API, GitHub Actions; vgl. Research §9)
```

## 2. Assets-Struktur

Erstanbieter-Code und -Content liegen vollständig unter `Assets/_Project/` (führender Unterstrich sortiert den Ordner im Project-Window nach oben und grenzt ihn sichtbar von `ThirdParty/` ab). Gekaufte Assets werden ausschließlich unverändert unter `Assets/ThirdParty/` abgelegt (TPD §7.1).

```text
Assets/
├── _Project/
│   ├── Art/                         # Modelle, Texturen, Materialien, VFX, Shader Graphs
│   │   ├── Characters/  Vehicles/  Buildings/  Environment/  Resources/  VFX/  UI/
│   │   └── Materials/  Textures/  Shaders/
│   ├── Audio/
│   │   ├── Music/  SFX/  UI/  Voice/
│   ├── Data/                        # SO-Assets (Definitionsdaten) + zentrale Registry (§4)
│   │   ├── GameDatabase.asset       # EINZIGE Registry-Instanz (D-035, Research §3)
│   │   ├── Units/  Buildings/  Weapons/  Tech/  Factions/  AI/  Maps/  Biomes/
│   ├── Prefabs/
│   │   ├── Units/  Buildings/  Projectiles/  Environment/  UI/
│   ├── Scenes/
│   │   ├── Boot/  Menu/  Gameplay/  Test/
│   ├── Scripts/                     # Laufzeit-Code, eine Assembly pro Ordner (§3)
│   │   ├── Core/                    # → Nova.Core.asmdef
│   │   ├── Data/                    # → Nova.Data.asmdef (SO-Schemas)
│   │   ├── Simulation/              # → Nova.Simulation.asmdef (Unity-frei)
│   │   │   ├── Commands/  State/  Definitions/
│   │   │   └── Systems/  Economy/  Combat/  Movement/  Pathfinding/  FogOfWar/  AI/
│   │   ├── Simulation.Burst/        # → Nova.Simulation.Burst.asmdef (Jobs/Burst-Varianten)
│   │   ├── Gameplay/                # → Nova.Gameplay.asmdef (MonoBehaviours, Sim-Brücke)
│   │   │   ├── Match/  Commands/  Spawning/  Pools/
│   │   └── Presentation/            # → Nova.Presentation.asmdef (View, VFX, Audio, UI)
│   │       ├── Rendering/  Units/  UI/  Audio/  Camera/
│   ├── Editor/                      # → Nova.Editor.asmdef (EINZIGER Editor-Ordner, §5)
│   │   ├── Inspectors/  Validators/  DataTools/
│   └── Settings/                    # URP Pipeline Assets, Renderer, Quality-/Graphics-Profiles
├── ThirdParty/                      # gekaufte Pakete, 1 Unterordner pro Paket, read-only
└── Tests/                           # Unity Test Framework (§5)
    ├── EditMode/
    │   ├── Simulation/              # → Nova.Simulation.Tests.asmdef
    │   └── Gameplay/                # → Nova.Gameplay.Tests.asmdef
    └── PlayMode/                    # → Nova.PlayMode.Tests.asmdef
```

Regeln:

1. **Keine Quelldateien außerhalb der genannten Ordner** – insbesondere keine Skripte in `ThirdParty/`, `Art/`, `Prefabs/` oder Szenenordnern.
2. **Kein `Resources/`-Ordner** – Definitionsdaten werden per direktem Asset-Link referenziert, nicht per `Resources.Load`/Pfad-Strings (Research §3).
3. `ThirdParty/` wird nie editiert; Anpassungen an gekauften Assets erfolgen über eigene Prefab-Varianten/Materialien in `_Project/`.
4. Ordner werden nur mit Inhalt angelegt (keine leeren Struktur-Leichen, analog D-004).

## 3. Assembly-Definitionen und Referenzrichtung

| Assembly | Pfad | Engine-Referenzen | Referenziert | Inhalt |
|---|---|---|---|---|
| `Nova.Core` | `Scripts/Core/` | **keine** (`noEngineReferences`) | – | Basistypen (`EntityId`, `Tick`), `INovaLogger`, Result-Typen, Pools/Puffer |
| `Nova.Simulation` | `Scripts/Simulation/` | **keine** (`noEngineReferences`) | `Nova.Core` | Commands, State-Structs, Sim-Definitionen, ISimSystem, Sim-Logik (D-033/D-035) |
| `Nova.Simulation.Burst` | `Scripts/Simulation.Burst/` | Unity.Collections, Unity.Burst, Unity.Jobs, Unity.Mathematics | `Nova.Core`, `Nova.Simulation` | Burst/Jobs-Varianten der Hotspots (Pathfinding, FoW, Sicht; D-034/D-035) |
| `Nova.Data` | `Scripts/Data/` | UnityEngine | `Nova.Core` | SO-Schemas, `GameDatabaseSO` (Definitions-only) |
| `Nova.Gameplay` | `Scripts/Gameplay/` | UnityEngine + Collections/Burst | Core, Simulation, Simulation.Burst, Data | MonoBehaviours, Match-Runner, SO→Sim-Überführung, Pools |
| `Nova.Presentation` | `Scripts/Presentation/` | UnityEngine, URP, UI Toolkit | Core, Gameplay | View-Layer, Render Features, Audio, UI |
| `Nova.Editor` | `Editor/` | UnityEngine + UnityEditor | Core, Data, Gameplay | Custom Inspectors, SO-Validatoren, Datenbank-Tools |
| `Nova.*.Tests` | `Tests/` | Test Framework | nur die getesteten Assemblies | EditMode-/PlayMode-Tests |

**Referenzgesetze:**

- Referenzrichtung strikt: `Presentation → Gameplay → Simulation → Core` und `Gameplay → Data → Core`. Rückwärtsreferenzen sind durch die asmdef-Konfiguration **unmöglich** zu machen, nicht nur konventionell verboten.
- `Nova.Simulation` und `Nova.Core` werden mit `noEngineReferences = true` konfiguriert – ein `using UnityEngine;` im Sim-Pfad ist damit ein **Kompilierfehler** (Durchsetzung von D-033 Regel 2 per Werkzeug statt per Disziplin).
- `Nova.Simulation` kennt `Nova.Data` nicht: SOs sind Unity-typisiert. Die Überführung der Definitionsdaten in Unity-freie Sim-Definitionen (immutable Snapshots beim Match-Start) ist Aufgabe von `Nova.Gameplay` (Detaildesign in GameState.md).
- `Nova.Simulation.Burst` ist die einzige Assembly mit Burst/Jobs-Abhängigkeiten nahe am Sim-Kern (Begründung und Paritäts-Risiko in [./CodingGuidelines.md](./CodingGuidelines.md) §3 und Offene Punkte).

## 4. SO-Registry-Ordner (`Data/`)

- Alle Definitions-SOs liegen unter `_Project/Data/<Typ>/`, gruppiert nach Fraktion (`Units/Allianz/UNIT_Allianz_Rifleman.asset`, Dateikonvention siehe [./NamingConvention.md](./NamingConvention.md)).
- `GameDatabase.asset` ist die einzige Registry-Instanz und indiziert alle Definitionen per stabiler ID (Datenbank-Pattern, Research §3 – Pflicht ab ~150+ Definitionen).
- Laufzeit-Status wird **nie** in diesen Assets gespeichert (Definitions-only, D-035; Durchsetzung in CodingGuidelines §4).

## 5. Editor vs. Runtime vs. Tests

- **Runtime-Code:** ausschließlich unter `Scripts/` (Assembly-Trennung §3). Keine `#if UNITY_EDITOR`-Blöcke für substanzielle Logik – Editor-Funktionalität gehört in `Nova.Editor`.
- **Editor-Code:** ausschließlich unter `_Project/Editor/` mit `Nova.Editor.asmdef` (Include Platforms: Editor). Eine einzige Editor-Assembly statt verstreuter `Editor/`-Unterordner pro Modul – hält die Kompilierzeiten flach und die Grenze sichtbar.
- **Tests:** getrennt unter `Assets/Tests/`, gespiegelt nach Layer. `Nova.Simulation.Tests` referenziert nur `Nova.Simulation` + `Nova.Core` und läuft als EditMode-Suite ohne Szene – dieselbe Suite ist die Referenz für den SimRunner (§6). Test-Assemblies referenzieren niemals `Presentation` oder `Editor`.

## 6. Nova.SimRunner (`tools/`, D-036)

- `tools/Nova.SimRunner/` ist eine eigenständige .NET-Lösung **außerhalb** von `Assets/` (Unity importiert sie nicht, CI baut sie mit `dotnet build`).
- `Nova.Simulation.csproj` in `tools/` kompiliert **dieselben Quelldateien** wie `Assets/_Project/Scripts/Simulation/` per `<Compile Include="..\..\..\Assets\_Project\Scripts\**\*.cs" Link="..." />` (Core und Simulation, nicht Simulation.Burst). Es gibt genau eine Quelle der Wahrheit; die Doppel-Projektion (asmdef + csproj) ist der vereinbarte Mechanismus.
- Möglich ist das nur, weil `Nova.Simulation`/`Nova.Core` `noEngineReferences` haben – die Ordnerstruktur erzwingt also direkt die D-036-Voraussetzung.
- Ausgaben (Match-Result-Datensätze, Replay-/Seed-Fixtures) werden unter `tools/Nova.SimRunner/out/` geschrieben und sind nicht Teil des Unity-Projekts.

## 7. Verhältnis zum TPD-§10-Vorschlag

Übernommen: Art/Audio/Prefabs/Scenes-Einteilung, `ScriptableObjects`-Konzept (als `Data/`), `ThirdParty/`. Geändert: (a) First-Party unter `_Project/` gruppiert; (b) `Scripts/` nach **Assemblies/Schichten** statt nach Fachdomänen (`Units/`, `Combat/` …) gegliedert – Fachdomänen leben als Unterordner innerhalb der Schicht, weil die Schichtgrenze (D-033/D-035) die härtere Anforderung ist; (c) Assembly-Definitions-, Tests-, Editor- und SimRunner-Struktur ergänzt; (d) `Resources/`-Mechanik entfernt.

## Offene Punkte

- **Burst/Managed-Doppelstruktur:** Ob `Nova.Simulation.Burst` und die Managed-Sim dauerhaft als zwei Implementierungen derselben Hotspots koexistieren (Parität per Hash-Tests) oder Burst-Code Teile der Managed-Pfade ersetzt, ist an die Phase-0-Messung gekoppelt (CPU-Budget ≤2–4 ms, D-034) und dort zu entscheiden.
- **Repo-Root = Unity-Root:** Falls die spätere Backend-/Server-Entwicklung (TPD §9, ab Beta) ein eigenes Repo oder Monorepo-Layout erfordert, ist diese Grundstruktur erneut zu prüfen.
- **Odin Inspector o. ä.** für die SO-Datenbank wurde nicht bewertet (Budget-Frage, Research-Offener-Punkt) – bei Zukauf ändert sich nur `ThirdParty/`, nicht diese Struktur.
- **Addressables** (Content-Updates ab Phase 2) sind unentschieden (TPD §16) und würden einen eigenen Content-Ordner erfordern.

## Nächste Schritte

1. Konsistenzreview mit Architecture.md, Testing.md und GameState.md (Schnittstelle SO→Sim-Definitionen).
2. Sprint 7: Struktur beim Projekt-Setup anlegen, asmdefs mit Referenzmatrix und `noEngineReferences` konfigurieren, Leerprojekt + Hello-Tick gegen CI verifizieren.
3. `Nova.SimRunner`-Skeleton (csproj-Linking) mit einem minimalen Tick-Lauf aufsetzen (D-036, Pflicht in Sprint 7).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Technical Director |
