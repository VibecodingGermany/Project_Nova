# Abhängigkeitsgraph

**Version:** 0.2.0 | **Status:** Entwurf (Korrekturlauf Sprint 4) | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 3

## Zweck

Verbindliche Festlegung der erlaubten Abhängigkeitsrichtungen zwischen Schichten und Assemblies von Project Nova, inklusive Verbotsliste und Assembly-Definition-Abbildung (.asmdef). Grundlage für Code-Reviews und Architektur-Checks ab Sprint 7. Schichtenbeschreibung: [./Architecture.md](./Architecture.md), Moduldetails: [./ModuleOverview.md](./ModuleOverview.md).

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (Sim-Regeln), D-035 (Assembly-Struktur, kein DOTS), D-036 (SimRunner), D-037 (Burst-Trennung), D-043 (kanonische Assembly-Topologie), D-045 (Managed-first)
- [./Architecture.md](./Architecture.md), [./ModuleOverview.md](./ModuleOverview.md)
- [../research/Unity_BestPractices.md](../research/Unity_BestPractices.md)

## 1. Erlaubte Abhängigkeitsrichtungen

Grundsatz: Abhängigkeiten zeigen ausschließlich **nach unten** Richtung Simulation. Die Simulation kennt niemanden; alle kennen (höchstens) die Simulation. Querverbindungen innerhalb der Präsentation sind erlaubt, solange kein Rückgriff in Bridge/Sim-Interna erfolgt.

```
┌─────────────────────────────────────────────────────────────┐
│ Nova.Editor · Nova.BuildTools (Editor-only)                 │
└──────────────┬──────────────────────────────────────────────┘
               │ (Editor)
┌──────────────▼──────────────────────────────────────────────┐
│ Nova.UI (HUD, Minimap) · Nova.Presentation (Camera, View,   │
│ VFX, FoW, Audio) – KEINE Direktreferenz UI↔Presentation:    │
│ Minimap-Navigation nur über UINavigationEvent (Ausnahme §1) │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│ Nova.Gameplay (Bridge)                                      │
│ MatchSession, IMatchTransport/LocalLoopback,                │
│ Input→Command, SO→DefinitionSnapshot, Event-Dispatch        │
└───┬─────────┬──────────┬───────────────┬────────────────────┘
    │         │          │               │
┌───▼───────┐ ┌▼─────────┐ ┌▼────────────▼──────┐ ┌▼───────────┐
│ Nova.Data │ │Nova.AI.  │ │Nova.Simulation.    │ │ Nova.AI    │
│ (SOs,     │ │Data (SOs,│ │Burst (Burst-       │ │ (Unity-frei│
│ Sub-Regis-│ │Difficulty│ │Varianten, Feature- │ │ Director/  │
│ tries)    │ │Profile)  │ │Flag, D-045)        │ │ HTN/BT)    │
└───┬───────┘ └┬─────────┘ └┬───────────────────┘ └┬───────────┘
    │          │            │                      │
┌───▼──────────▼────────────▼──────────────────────▼───────────┐
│ Nova.Simulation (Unity-frei, reines .NET)                   │
│ Core-Loop, Commands, Grid, Pathfinding, FoW, Economy,       │
│ Combat, Production, Research, NeutralUnits, Superweapons,   │
│ Match/Session, Replay, Savegame                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│ Nova.Core (Unity-frei): Basistypen (EntityId, Tick),        │
│ Logging, Puffer – von allen Assemblies referenziert         │
└──────────────────────────▲──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │ Nova.SimRunner          │
              │ (reine .NET-Konsole:    │
              │  Core + Simulation + AI │
              │  CI-Balancing, D-036)   │
              └─────────────────────────┘
```

Erlaubt (zusammengefasst; verbindliche Referenzmatrix in [./FolderStructure.md](./FolderStructure.md) §3):

- `Nova.Simulation → Nova.Core` (sonst nichts); `Nova.Simulation.Burst → Nova.Core, Nova.Simulation` (nur öffentliche State-Datentypen; Spiegelung in NativeArrays)
- `Nova.AI → Nova.Core, Nova.Simulation` (nur die Client-Verträge `IAiWorldView`/`ICommandSink` und Snapshot-Typen, [./AIArchitecture.md](./AIArchitecture.md))
- `Nova.Data → Nova.Core`; `Nova.AI.Data → Nova.Core` – SOs kennen die Simulation nicht; die Überführung in Unity-freie `DefinitionSnapshot`-/KI-Records ist Aufgabe von `Nova.Gameplay`
- `Nova.Gameplay → Nova.Core, Nova.Simulation, Nova.Simulation.Burst, Nova.Data, Nova.AI, Nova.AI.Data` (öffentliche Verträge: Events, Snapshots, `ICommandSink`)
- `Nova.Presentation → Nova.Core, Nova.Gameplay`; `Nova.UI → Nova.Core, Nova.Gameplay`
- **Dokumentierte Ausnahme UI↔Presentation (Minimap-Klick→Kamera):** Es gibt **keine direkte Assembly-Referenz** zwischen `Nova.UI` und `Nova.Presentation`. Die Minimap-Navigation läuft über den Vertragstyp `UINavigationEvent` (in `Nova.Core`, damit für beide Seiten referenzierbar): Die Minimap publiziert Navigations-Intents (Klick → Weltposition), die Kamera in `Nova.Presentation` abonniert sie; umgekehrt publiziert die Kamera ihren Viewport-State für die Minimap-Viewport-Anzeige über denselben Kanal. Die Verdrahtung (Kanal-Instanz, Übergabe der Minimap-FoW-Textur) erfolgt durch `Nova.Gameplay` als Composition Root beim Match-Setup.
- `Nova.Editor → Nova.Core, Nova.Data, Nova.Gameplay` (+ UnityEditor); `Nova.BuildTools → Nova.Core, Nova.Data, Nova.Gameplay` (+ UnityEditor)
- `Nova.SimRunner → Nova.Core, Nova.Simulation, Nova.AI` (Quelltext-Sharing per csproj-Compile-Include, [./FolderStructure.md](./FolderStructure.md) §6)
- Sim-Module untereinander entlang der in [./ModuleOverview.md](./ModuleOverview.md) gelisteten Abhängigkeiten (z. B. Combat → FogOfWar, Economy → Grid); Richtung: fachlich höhere Module → Basis-Module, niemals zyklisch. Production ↔ Research ist entkoppelt (siehe Verbotsliste Nr. 7).

## 2. Verbotsliste

Verboten (Verstoß = Review-Blocker):

1. **`Nova.Core`/`Nova.Simulation`/`Nova.AI` → UnityEngine** / UnityEditor / URP (D-033 Regel 2, D-035, D-043). Kein `using UnityEngine;`, kein `UnityEngine.Random`, kein `Time.*`, kein `Physics.*` in diesen Pfaden. Durchgesetzt über `noEngineReferences = true` und fehlende Assembly-Referenzen (technisch unmöglich, nicht nur Konvention; FolderStructure.md §3).
2. **`Nova.Simulation`/`Nova.AI` → Nova.Gameplay/Data/AI.Data/Presentation/UI** – Simulation und KI kennen keine höheren Schichten; Rückmeldung ausschließlich über View-Events/Snapshots bzw. die Client-Verträge.
3. **`Nova.Presentation`/`Nova.UI → Nova.Simulation` direkt** – Zugriff nur über die Bridge-Verträge in `Nova.Gameplay`; keine Sim-Interna (keine `internal`-Umgehung via `InternalsVisibleTo`, außer für Test-Assemblies). Ebenso verboten: **direkte Referenz `Nova.UI ↔ Nova.Presentation`** – einzige erlaubte Interaktion ist der `UINavigationEvent`-Kanal (§1).
4. **Direkte State-Mutation von außen** – niemand außer Commands/Modul-Ticks schreibt Sim-State (D-033 Regel 1); Bridge/View erhalten Nur-Lese-Snapshots.
5. **Runtime-State in ScriptableObjects** – SOs sind Definitions-only; Laufzeitdaten gehören in den Sim-State (D-033 Regel 5; Vier-Säulen-Regel).
6. **`Nova.SimRunner → Unity-*`** – der Runner referenziert ausschließlich `Nova.Core`, `Nova.Simulation` und `Nova.AI` (D-036, D-043); Unity-Paket-Referenzen würden die reine .NET-Lauffähigkeit brechen. Runner und Golden-Master-Tests fahren grundsätzlich den Managed-Pfad (D-045).
7. **Zyklen zwischen Sim-Modulen** – Kommunikation über Core-Mediatoren (Command/Event im selben Tick-Raster), nicht über gegenseitige Referenzen. Der früher dokumentierte Graubereich **Production ↔ Research** ist aufgelöst (Review F-3): Research schreibt den `TechState` alleinig und publiziert `TechUnlockedEvent`; Production greift ausschließlich lesend auf `TechState.UnlockedDefs` zu – eine gegenseitige Modul-Referenz existiert nicht.
8. **Kein Unity Entities/DOTS-Package** in irgendeiner Assembly (D-035; Re-Evaluierung nach Unity 6.4).

## 3. Assembly-Definition-Abbildung

Physische Umsetzung im Unity-Projekt (`Assets/`). Test-Assemblies (`*.Tests`, EditMode/PlayMode) spiegeln die Referenzen ihrer Ziel-Assembly und dürfen zusätzlich `InternalsVisibleTo`-Ziele referenzieren.

| .asmdef | Referenzen (asmdef) | Unity-Referenzen | Plattform | Bemerkung |
|---|---|---|---|---|
| `Nova.Core` | – | **keine** (`noEngineReferences`) | alle (auch Standalone-.NET) | Basistypen (`EntityId`, `Tick`), Logging, Puffer |
| `Nova.Simulation` | `Nova.Core` | **keine** (`noEngineReferences`) | alle (auch Standalone-.NET) | Kern aller Regeln (D-033/D-035) |
| `Nova.Simulation.Burst` | `Nova.Core`, `Nova.Simulation` | Unity.Collections, Unity.Burst, Unity.Jobs, Unity.Mathematics (Packages) | alle | **kein UnityEngine-API-Aufruf**; Managed-first: Auslieferung Managed, Burst nur hinter Feature-Flag mit Toleranz-Parität ≤1e-4 (D-037/D-045) |
| `Nova.AI` | `Nova.Core`, `Nova.Simulation` | **keine** (`noEngineReferences`) | alle (auch Standalone-.NET) | KI-Entscheidungslogik, SimRunner-tauglich ([./AIArchitecture.md](./AIArchitecture.md)) |
| `Nova.AI.Data` | `Nova.Core` | UnityEngine (ScriptableObject) | alle | Difficulty-/Plan-/Squad-SOs → Unity-freie Records |
| `Nova.Data` | `Nova.Core` | UnityEngine (ScriptableObject) | alle | Definitions-only-SOs, Sub-Registries + Master-Index (D-049) |
| `Nova.Gameplay` | `Nova.Core`, `Nova.Simulation`, `Nova.Simulation.Burst`, `Nova.Data`, `Nova.AI`, `Nova.AI.Data` | UnityEngine | alle | Bridge/Session/Transport, SO→`DefinitionSnapshot` |
| `Nova.Presentation` | `Nova.Core`, `Nova.Gameplay` | UnityEngine, URP, RenderGraph | alle | volle Unity-Nutzung erlaubt (D-035) |
| `Nova.UI` | `Nova.Core`, `Nova.Gameplay` | UnityEngine, UI Toolkit (uGUI nur World-Space) | alle | Minimap-Navigation via `UINavigationEvent` (Ausnahme §1) |
| `Nova.Editor` | `Nova.Core`, `Nova.Data`, `Nova.Gameplay` | UnityEngine, UnityEditor | **Editor only** | kein Runtime-Code |
| `Nova.BuildTools` | `Nova.Core`, `Nova.Data`, `Nova.Gameplay` | UnityEngine, UnityEditor | **Editor only** | Build-Pipeline-/CI-Werkzeuge (D-043) |
| `Nova.Simulation.Tests` / `Nova.AI.Tests` | jeweilige Ziel-Assemblies | – | Editor (EditMode) + .NET-Testprojekt | Paritäts-/Determinismus-Tests |
| `Nova.Gameplay.Tests` / `Nova.Presentation.Tests` | jeweilige Ziel-Assemblies | UnityEngine Test Framework | Editor | |
| `Nova.SimRunner` (eigenes .NET-Projekt unter `tools/`, außerhalb von `Assets/`) | `Nova.Core`, `Nova.Simulation`, `Nova.AI` (csproj-Compile-Include derselben Quellen, FolderStructure.md §6) | **keine** | Standalone .NET | CI-Balancing (D-036) |

Durchsetzung: Die Trennung wird primär über fehlende Referenzen erzwungen (Regeln 1, 3, 6 sind so technisch unmöglich). Zusätzlich werden in `Testing.md` (Sprint 7) statische Architektur-Checks definiert (Namespace-/Referenz-Scan in CI: kein `UnityEngine`-Using in `Nova.Simulation`-Quellen, keine Direktreferenz Presentation→Simulation).

## Offene Punkte

1. **Burst-Brücke:** Ob `Nova.Simulation.Jobs` Ergebnisse bit-identisch zum reinen C#-Pfad liefern muss (SimRunner-Parität, D-036) oder ob der Runner bewusst den C#-Pfad nutzt, ist unentschieden → Offener Punkt 1 in [./Architecture.md](./Architecture.md), Entscheidung nach Phase-0-Spike im DecisionLog.
2. **SimRunner-Bezug der Sim-Assembly:** Quelltext-Sharing (Shared Project/Linked Files) vs. DLL-Referenz aus dem Unity-Build – CI-Detail, Festlegung im Sprint-7-Setup (`Testing.md`).
3. **UI→Presentation-Referenz** (Minimap braucht FoW-Textur/Camera) erzeugt eine Kante, die bei wachsender UI zur Schichten-Unschärfe führen kann; ggf. später über Bridge-Mediatoren ersetzen – Beobachtung im Architecture Review.
4. Test-Assembly-Strategie für `Nova.Simulation` außerhalb von Unity (reines .NET-Testprojekt vs. Unity Test Framework EditMode) offen → `Testing.md`.

## Nächste Schritte

- .asmdef-Gerüst gemäß §3 im Sprint-7-Projekt-Setup anlegen und Referenzmatrix 1:1 umsetzen.
- CI-Architektur-Check (Namespace-Scan) in `Testing.md` spezifizieren.
- Verbotsliste als Review-Checkliste in `CodingGuidelines.md` übernehmen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Technical Director |
