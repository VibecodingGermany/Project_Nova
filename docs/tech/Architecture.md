# Gesamtarchitektur

**Version:** 0.2.0 | **Status:** Entwurf (Korrekturlauf Sprint 4) | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 4

## Zweck

Verbindliche Gesamtarchitektur für Project Nova: Schichtenmodell, Command-Pipeline, Tick-Modell und der Erweiterungspfad von lokalem Singleplayer zu Online-Multiplayer. Grundlage für alle weiteren TDD-Dokumente in `docs/tech/` und für die Implementierung ab Sprint 7. Verbindlich für alle Engineering-Rollen.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – insb. D-006 (Unity 6.3 LTS + URP), D-033 (Sim-/MP-Modell), D-034 (Pathfinding), D-035 (OOP+SO+Burst, kein DOTS), D-036 (SimRunner), D-037 (Burst-Trennung), D-039 (Sim-Budgets), D-043 (kanonische Assembly-Topologie), D-044 (Tick-Ausführungsmodell), D-045 (Managed-first), D-046 (MP-Trust-Anchor), D-051 (Quantum-Fallback gestrichen)
- [../research/Multiplayer_Simulation.md](../research/Multiplayer_Simulation.md)
- [../research/Unity_ECS_DOTS.md](../research/Unity_ECS_DOTS.md)
- [../research/Unity_BestPractices.md](../research/Unity_BestPractices.md)
- [../vision/CoreGameplay.md](../vision/CoreGameplay.md) (Zielwerte: 500 Einheiten, 60 FPS, 20–35 min Matches)
- [./ModuleOverview.md](./ModuleOverview.md), [./DependencyGraph.md](./DependencyGraph.md)

## 1. Architektur-Leitplanken (Vier Säulen + 5 Sim-Regeln)

Die Architektur steht auf vier Säulen (Research-Konsens, D-033/D-035):

1. **Strikte Simulation/View-Trennung.** Der gesamte Spielzustand lebt in der Unity-freien Assembly `Nova.Simulation`. Im Sim-Pfad sind **keine UnityEngine-APIs** erlaubt (D-033 Regel 2, D-035). Die Präsentation liest Zustand nur über Snapshots/Events, schreibt nie.
2. **Commands als einzige State-Mutation.** Jede Änderung am Spielzustand (Bewegen, Bauen, Forschen, Feuern-Entscheidungen von Spielern und KI) geht als Command durch die Command-Pipeline (D-033 Regel 1). Direkte Zugriffe auf den Sim-State von außerhalb sind verboten.
3. **Fester Sim-Tick, entkoppeltes Rendering.** Die Simulation läuft mit festen 10 Hz (100 ms/Tick, D-033 Regel 3). Das Rendering läuft mit Display-Framerate (Ziel 60 FPS) und interpoliert zwischen Tick-Snapshots. Framezeit hat keinen Einfluss auf Sim-Ergebnisse.
4. **Vollständig datengetrieben.** Alle statischen Definitionen (Einheiten, Gebäude, Waffen, Tech, Karten) kommen aus der SO-Registry `GameDatabase` (Sub-Registries pro Kategorie + generierter Master-Index, D-049; Definitions-only-SOs, **kein Runtime-State in SOs**). Beim Matchstart wird ein reiner Daten-Snapshot (`DefinitionSnapshot`) erzeugt, den die Simulation ohne Unity-Referenzen nutzt.

Zusätzlich gelten aus D-033: **(4)** eigener seedbarer PRNG im Sim-Kern (kein `System.Random`, kein `UnityEngine.Random`), **(5)** vollständig serialisierbarer State (Savegame, Replay, Desync-Debugging, später Lockstep-Checksums). **Singleplayer ist ein "lokaler Server"**: SP und (später) MP benutzen denselben Codepfad, nur der Transport unterscheidet sich.

Float-Arithmetik ist im MVP erlaubt; die Umstellung auf Fixed-Point ist fester Bestandteil der Beta-MP-Arbeiten (D-033).

## 2. Schichtenmodell

Kanonische Assembly-Topologie gemäß D-043 (FolderStructure-Lager führend, ergänzt um `Nova.AI`/`Nova.AI.Data`):

| Schicht | Assembly | Unity-Bezug | Inhalt |
|---|---|---|---|
| Basis | `Nova.Core` | **keine** (`noEngineReferences`) | Basistypen (`EntityId`, `Tick`), Logging, Result-Typen, Pools/Puffer – von allen Assemblies referenziert |
| Simulation | `Nova.Simulation` | **keine** (`noEngineReferences`, reines .NET) | Spielregeln, State, Commands, Grid, Pathfinding, FoW, Economy, Combat, Production, Research, NeutralUnits, Superweapons, Match/Session, Replay, Savegame |
| Sim-Beschleunigung | `Nova.Simulation.Burst` | Unity.Collections/Burst/Jobs, **kein UnityEngine** | Burst-Varianten der Hotspots (Flow Fields, FoW-Scan, Separation) hinter identischen Interfaces auf NativeArray-Spiegeln (D-037). **Managed-first (D-045):** Auslieferungspfad ist Managed; Burst nur hinter Feature-Flag mit Toleranz-Parität |
| KI | `Nova.AI` | **keine** (reines .NET) | KI-Entscheidungslogik (Utility-Director, HTN-light, Squad-BT) als Client der Simulation über `IAiWorldView`/`ICommandSink`; SimRunner-tauglich ([./AIArchitecture.md](./AIArchitecture.md)) |
| KI-Daten | `Nova.AI.Data` | UnityEngine (ScriptableObjects) | `DifficultyProfileSO`/`StrategyOptionSO`/`TaskPlanSO`/`SquadBehaviorSO`; Übersetzung in Unity-freie Records beim Match-Start |
| Daten | `Nova.Data` | UnityEngine (ScriptableObjects) | Definitions-only-SOs, `GameDatabase` als Sub-Registries pro Kategorie + generierter Master-Index (D-049), Validierung |
| Bridge | `Nova.Gameplay` | UnityEngine | Session-/Match-Orchestrierung, SO→`DefinitionSnapshot`-Überführung, Input→Command, lokaler Server (Loopback-Transport), Event-Dispatch an View |
| Präsentation | `Nova.Presentation` | UnityEngine + URP | Kamera, Selektion, Units-/Buildings-View, Interpolation, VFX, FoW-Rendering (Full Screen Pass), Healthbars, Audio-Service |
| UI | `Nova.UI` | UnityEngine (UI Toolkit) | HUD, Menüs, Minimap; uGUI nur World-Space; Minimap-Navigation über `UINavigationEvent` (dokumentierte Ausnahme, [./DependencyGraph.md](./DependencyGraph.md) §1) |
| Editor | `Nova.Editor` | Unity Editor only | Karten-/Daten-Validierung, Custom Inspectors, Bake-Tools |
| Build | `Nova.BuildTools` | Unity Editor only | Build-Pipeline-/CI-Werkzeuge (BuildPipeline-API, Skripte unter `ci/`) |
| Headless | `Nova.SimRunner` | **keine** (reines .NET, außerhalb von `Assets/` unter `tools/`) | Konsolen-Runner auf `Nova.Core` + `Nova.Simulation` + `Nova.AI` für CI-Balancing-Läufe (D-036) |

Regeln: Abhängigkeiten zeigen nur nach unten in dieser Tabelle (Details und Verbotsliste: [./DependencyGraph.md](./DependencyGraph.md); Referenzmatrix verbindlich in [./FolderStructure.md](./FolderStructure.md) §3). `Nova.Simulation` kennt keine der anderen Schichten. Die Präsentation darf Unity-APIs voll nutzen (D-035), aber niemals Sim-Interna.

## 3. Command-Pipeline

Fluss: **Eingabe → Command → Tick-Ausführung → State-Mutation → View-Events → Präsentation.**

1. **Eingabe (Bridge):** UI/Selektion/Hotkeys erzeugen Intent-Aufrufe auf `ICommandSink`. Auch die KI (Unity-freie Assembly `Nova.AI`, Client der Sim) und später Netzwerk-Peers speisen ausschließlich über Commands ein.
2. **Pufferung:** Commands werden dem nächsten Tick zugeordnet (`TargetTick = CurrentTick + InputDelay`, MVP: 2 Ticks = 200 ms, Lockstep-kompatibel). Pro Tick entsteht ein deterministisch sortierter `CommandBatch` (Sortierschlüssel: `PlayerId`, dann `Sequence`).
3. **Tick-Ausführung:** Der `SimulationKernel` führt pro Tick nacheinander aus: Command-Anwendung → Modul-Ticks in fester Reihenfolge (Economy → Production → Research → Combat → Movement/Pathfinding → FoW → AI-Strategie → Match/Victory) → View-Event-Sammlung.
4. **State-Mutation:** Nur Commands und die daraus folgenden Modul-Ticks ändern State (Regel 1/2). Der PRNG wird ausschließlich aus dem Sim-Pfad bedient, pro Tick deterministisch weitergeschaltet.
5. **View-Events:** Die Simulation emittiert pro Tick eine Liste von View-Events (Spawn, Move, Damage, Death, ResourceChanged, FoWDelta, …). Die Bridge verteilt sie an die Präsentation; Bewegung wird zusätzlich über Positions-Snapshots interpoliert.

Schnittstellen-Skizze (API-Design, keine Implementierung):

```csharp
namespace Nova.Simulation.Core
{
    public interface ICommand { int PlayerId { get; } }

    public readonly record struct CommandEnvelope(int TargetTick, int PlayerId, int Sequence, ICommand Command);

    public interface ICommandSink
    {
        void Submit(ICommand command);        // Bridge/UI/KI-Einstieg
    }

    public sealed class SimulationClock
    {
        public const int TicksPerSecond = 10; // D-033, fester Tick
        public int CurrentTick { get; }
    }

    public sealed class DeterministicRandom  // D-033 Regel 4 (z. B. XorShift)
    {
        public DeterministicRandom(ulong seed);
        public int NextInt(int minInclusive, int maxExclusive);
        public float NextFloat01();
    }

    public interface ISimulationModule
    {
        void Tick(SimContext ctx);            // feste Aufrufreihenfolge, siehe §3.3
    }

    public interface IStateSerializer         // D-033 Regel 5
    {
        byte[] Serialize(in SimState state);
        SimState Deserialize(ReadOnlySpan<byte> data);
        int ComputeChecksum(in SimState state); // Desync-Erkennung / Lockstep
    }
}

namespace Nova.Simulation.Events
{
    public interface IViewEvent { }           // marker; konkrete Records je Modul
    public interface IViewEventCollector
    {
        void Emit(IViewEvent e);
        IReadOnlyList<IViewEvent> DrainTick(int tick); // Bridge holt pro Tick ab
    }
}
```

## 4. Singleplayer als lokaler Server (D-033)

Die Bridge kapselt den Transport hinter `IMatchTransport`. Im MVP existiert genau eine Implementierung: `LocalLoopbackTransport`, die Command-Batches verzögert (Input-Delay) an den eigenen Kernel zurückliefert. Session-Aufbau, Slot-Verwaltung (Mensch + KI), Start-Seed und Match-Konfiguration laufen über `MatchSession` in der Bridge – identisch zum späteren Online-Pfad.

```csharp
namespace Nova.Gameplay.Session
{
    public interface IMatchTransport
    {
        void SendCommands(in CommandEnvelope[] batch);   // eigene Befehle "zum Server"
        event Action<CommandEnvelope[]> OnTickCommands;  // autoritative Batches "vom Server"
    }

    public sealed class LocalLoopbackTransport : IMatchTransport { /* MVP: lokaler Server */ }
    // Beta: LockstepRelayTransport (Eigenbau-UDP; Fallback = reduzierter MP-Scope, D-051) – D-033

    public sealed class MatchSession
    {
        // Orchestriert: GameDatabase → DefinitionSnapshot, Map-Load, Slot-Belegung,
        // Start-Seed, Kernel-Start, Transport-Bindung, Match-Ende (MatchResult)
    }
}
```

Konsequenz: Es gibt keinen separaten "Singleplayer-Code". Alle Modi (Skirmish vs. KI, Koop lokal, später PvP) laufen über `MatchSession` + Transport-Abstraktion.

## 5. Erweiterungspfad: deterministisches Lockstep-Relay ab Beta (D-033)

Zielarchitektur ab Beta: deterministisches Lockstep über einem **autoritativen Command-Relay-Server** (Eigenbau-UDP; der früher erwähnte Photon-Quantum-3-Fallback ist gestrichen – Ersatz-Fallback bei Scheitern des Eigenbau-Relay ist ein reduzierter MP-Scope, D-051). Der Relay validiert und sortiert Command-Batches pro Tick und verteilt sie an alle Clients; das Match-Ergebnis validiert der Server per Post-Match-Re-Simulation des Command-Logs (SimRunner-basiert, on-demand, D-046). Clients simulieren identisch.

Vorbereitung in der MVP-Architektur (keine Beta-Funktionalität, aber keine Sackgassen):

- Input-Delay und deterministische Batch-Sortierung (§3) sind von Anfang an aktiv.
- `IMatchTransport` ist die einzige Stelle, an der Netzcode eingehängt wird.
- `ComputeChecksum` pro Tick wird im MVP bereits für Replay-Verifikation und Desync-Jagd genutzt; im Lockstep derselbe Mechanismus für Sync-Vergleich.
- Fixed-Point-Umstellung (MVP: float) ist Beta-Pflichtarbeit; Phase-0-Spike validiert ARM↔x86-Determinismus (DecisionLog, Offene Punkte).
- Replays (Command-Stream + Seed + DefinitionSnapshot-Version) und Beobachter fallen aus dem Modell gratis (D-033).
- Maphack-Risiko (voller State auf jedem Client) bis Ranked-Re-Evaluierung akzeptiert (D-033); serverseitiges Sichtgrid ist dann eigene Entscheidung.

## 6. Serialisierung, Savegame, Replay

- **Savegame:** vollständige `SimState`-Serialisierung (Regel 5) über `IStateSerializer`, binär, versioniert (Format-Version im Header). Speichern erzeugt einen konsistenten Tick-Schnappschuss; Laden setzt Kernel in exakt diesen Tick.
- **Replay:** Start-State-Referenz (Map, Slots, DefinitionSnapshot-Version) + Start-Seed + vollständiger Command-Stream; Verifikation über periodische State-Checksums. Replay-Abspielung = Kernel im Replay-Modus (Commands aus Datei statt Transport).
- Beides liegt in `Nova.Simulation` und ist damit auch im `Nova.SimRunner` nutzbar (D-036).

## 7. Performance- und Ressourcen-Budgets (Zielvorgaben)

- Sim-Tick gesamt: ≤ 8 ms auf Zielhardware (10 Hz → ausreichend Reserve für View); Pathfinding-Anteil ≤ 2–4 ms (D-034, Phase-0-Messung).
- Rendering: 60 FPS bei 500 Einheiten (URP, GPU Resident Drawer, SRP Batcher – Phase-0-Validierung laut DecisionLog).
- Kein GC-Allokation im Tick (D-035-Konsequenz; Details in `CodingGuidelines.md`, Sprint 7).
- FoW-Sicht-Tick 5–10 Hz (GDD) gekoppelt an Sim-Tick-Raster (Standard: jeder 2. Tick = 5 Hz; Feinjustage offen, siehe Offene Punkte).

## Offene Punkte

1. **Burst/Jobs vs. SimRunner-Portabilität (gelöst):** D-035 fordert Burst/Jobs auf Sim-Hotspots, D-033/D-036 fordern eine Unity-freie `Nova.Simulation`, die im reinen .NET-SimRunner läuft. Gelöst durch D-043 (eigene Assembly `Nova.Simulation.Burst`, nicht `.Jobs`) und D-045 (Managed-first: Auslieferungspfad ist Managed, Burst nur hinter Feature-Flag mit Toleranz-Parität ≤1e-4 statt Bit-Identität; Pflicht-Paritätstests Managed↔Burst sind CI-Pflicht, D-037). Kein offener Klärungsbedarf mehr vor Sprint 7.
2. **Sim-Threading:** MVP-Vorschlag: Sim läuft synchron auf dem Main-Thread (10 Hz, Budget §7). Auslagerung auf Worker-Thread erst nach Messung; Auswirkung auf Event-Dispatch klären (Sprint 7).
3. **FoW-Sicht-Tick-Frequenz:** GDD-Spanne 5–10 Hz; exakte Kopplung (jeder Tick vs. jeder 2. Tick) und Interaktion mit Sicht-basiertem Targeting offen → `FogOfWar.md` (tech).
4. **Savegame-Format-Versionierung und Kompatibilitätsstrategie** über Patches hinweg → `GameState.md`/`Savegame`-Spezifikation.
5. **Disconnect-Regel (KI-Übernahme) und Host-Migration:** laut D-033 in `Networking.md` final zu definieren (Beta-Scope, hier nur Schnittstellen-Vorkehrung).
6. **Input-Delay-Wert:** 2 Ticks als MVP-Startwert; Feinjustage nach Spielgefühl/Lockstep-Anforderungen.

## Nächste Schritte

- Modul-Detail-TDDs auf dieser Basis: `GameState.md`, `Networking.md`, `Replication.md`, `Pathfinding.md`, `FogOfWar.md`, `Testing.md` (D-033/D-036-Konsequenzen).
- `CodingGuidelines.md` (Hotspot-Regeln, Assembly-Regeln) vorbereiten (Sprint 7).
- Phase-0-Spike: vier Pflicht-Validierungen lt. DecisionLog (Fixed-Point ARM↔x86, GPU Resident Drawer, Animator vs. Playables, Pathfinding-Budget).
- TDD-Konsistenzreview, danach formale Schließung von Q-013/Q-014/Q-015/Q-020.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Technical Director |
| 0.2.0 | 2026-07-21 | Korrekturlauf Sprint 4 (D-043-Topologie): kanonische Assembly-Topologie (§2) inkl. `Nova.AI`/`Nova.AI.Data`; Offene Punkte bereinigt (Burst/Jobs-Frage via D-043/D-045/D-037 gelöst, `GameDatabase`-Sharding nach D-049 nachgetragen) | Lead Technical Director |
