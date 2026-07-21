# GameState – Zustandsmodell der Simulation

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 3

## Zweck

Definiert das vollständige, serialisierbare Zustandsmodell der `Nova.Simulation`-Assembly: welche Daten den Simulationszustand eines Matches ausmachen, wie sie strukturiert und adressiert sind und welche Invarianten gelten. Verbindlich für alle Sim-Systeme (Sprint 7), für [./Serialization.md](./Serialization.md) und [./Savegames.md](./Savegames.md). Erfüllt D-033 Regel 5 (vollständig serialisierbarer State) und ist die Grundlage für Replays, Desync-Jagd (State-Hash) und den `Nova.SimRunner` (D-036).

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (5 Sim-Regeln), D-034 (Integer-Grid 1 m, geteilte Grid-Infrastruktur), D-035 (Unity-freie Assembly `Nova.Simulation`), D-036 (SimRunner), D-010/D-012 (Aetherium, Zerstörbarkeit)
- [../research/Multiplayer_Simulation.md](../research/Multiplayer_Simulation.md) – Desync-Quellen, State-Hash, Iterationsreihenfolge-Regeln
- [../gamedesign/Resources.md](../gamedesign/Resources.md) – Aetherium-Feld-Datenmodell (führend für Feld-State)
- [../gamedesign/FogOfWar.md](../gamedesign/FogOfWar.md) – drei Sichtzustände, Radar-Regeln
- [../gamedesign/Economy.md](../gamedesign/Economy.md) / [../gamedesign/ResearchTree.md](../gamedesign/ResearchTree.md) – Ressourcen-/Tech-State (führend)
- [./Serialization.md](./Serialization.md) – Format der Serialisierung
- [./Savegames.md](./Savegames.md) – Snapshot-Verwendung
- [./Pathfinding.md](./Pathfinding.md), [./FogOfWar.md](./FogOfWar.md) – Grid- und Sichtsysteme (parallel, Sprint 3)

## Grundprinzipien (aus D-033)

1. Der `WorldState` ist der **einzige** Simulationszustand. Alles, was das Match-Ergebnis beeinflusst, steht darin – nichts davon in MonoBehaviours, ScriptableObjects (Definitions-only) oder Unity-Objekten.
2. Commands sind die einzige State-Mutation; der State selbst ist ein flacher, serialisierbarer Schnappschuss ohne Objektgraph-Referenzen (nur IDs, keine Zeiger).
3. Keine UnityEngine-Typen im State (kein `Vector3`, kein `Transform`): eigene `SimVec2`/`SimVec3`-Structs (MVP: `float`, Beta: Fixed-Point, D-033).
4. Tick-stabile Iteration: Entitäten liegen in **ID-indizierten Arrays/Slots**, nicht in `Dictionary` mit undefinierter Enumerationsreihenfolge (Desync-Quelle laut Research §3).
5. Der State ist hashbar: `ComputeStateHash()` über den gesamten serialisierten State liefert die Grundlage für Desync-Erkennung (ab Beta Pflicht im MP, ab sofort im SimRunner).

## ID-Modell

- Stabile `uint`-IDs pro Entität, vergeben aus einem **monotonen Zähler im `WorldState`** (deterministisch, serialisiert). Keine GUIDs, keine `GetHashCode()`-Ableitungen, keine Unity-`GetInstanceID()` im Tick.
- IDs werden nicht wiederverwendet (Zähler läuft durch); bei 10 Hz und 500 Einheiten ist 32 bit über Matchdauern unkritisch, Überlauf-Guard beim Serialisieren.
- Definitions-Verweise (Einheitentyp, Waffe, Tech) sind `ushort`-Definitions-IDs aus der GameDatabase-Registry – niemals SO-Referenzen oder Strings im Tick-Pfad.

```csharp
namespace Nova.Simulation.State
{
    public readonly struct EntityId   { public readonly uint Value; }  // 0 = ungültig
    public readonly struct DefId      { public readonly ushort Value; } // GameDatabase-Registry
    public readonly struct PlayerId   { public readonly byte Value; }
    public readonly struct TeamId     { public readonly byte Value; }
}
```

## Zustandsmodell

### Wurzel: `WorldState`

```csharp
public sealed class WorldState
{
    public uint   Tick;                 // fester Sim-Tick, 10 Hz (D-033)
    public int    RandomSeed;           // Basis-Seed (Match-Setup)
    public SimRng Rng;                  // seedbarer PRNG-State (D-033 Regel 4), kein System.Random-Shared
    public MatchState  Match;
    public PlayerState[] Players;       // Index = PlayerId, max. 8 (Maps laut gamedesign)
    public TeamState[]   Teams;         // Index = TeamId
    public EntityStore   Entities;      // Einheiten, Gebäude, Projektile, Neutrale/Trümmer
    public AetheriumFieldState[] Fields;
    public GridState     Grid;          // geteiltes 1-m-Grid (D-034)
    public FogOfWarState[] FogPerTeam;  // Index = TeamId
    public TechState[]   TechPerPlayer;
    public uint NextEntityId;           // ID-Zähler (s. o.)
}
```

### Entitäten (`EntityStore`)

Flache, slot-basierte Speicher pro Kategorie; Entität = Datensatz, kein Verhaltens-Objektgraph. Gemeinsamer Kern + kategoriespezifische Erweiterung:

```csharp
public struct EntityCore
{
    public EntityId Id;
    public DefId    Definition;     // UnitDef/BuildingDef/ProjectileDef
    public PlayerId Owner;          // 0xFF = neutral
    public SimVec3  Position;
    public float    Heading;        // Yaw, rad
    public int      Hp;
    public int      MaxHp;          // gecacht aus Def + Tech-Modifikatoren
    public EntityFlags Flags;       // Stealthed, Burrowed, Disabled(LowPower), Selected-frei (View!)
    public ushort   OrderQueueHead; // Index in Order-Puffer; Orders ≠ Commands (s. u.)
}

public struct UnitState    { public EntityCore Core; public int CargoAE; public float ReloadTimer;
                             public EntityId MoveTarget; /* … */ }
public struct BuildingState{ public EntityCore Core; public int BuildProgressPct; public bool Powered;
                             public ushort RallyTile; public DefId[] ProductionQueue; }
public struct ProjectileState { public EntityCore Core; public SimVec3 Velocity; public EntityId Target;
                                public float FuseTime; }   // nur sim-relevante Projektile (s. Offene Punkte)
```

- **Orders vs. Commands:** Commands (Spielereingaben, serialisierbar, Replay-relevant) erzeugen Orders (interne Ausführungszustände, Teil des State, nicht des Replays).
- Selektion, Kamera, Hover, UI-Highlight sind **View-State** und gehören nicht in den `WorldState`.
- Trümmer (D-012) sind eigene Entity-Kategorie mit Verfalls-Timer; Vegetations-Brände als `FirePatch`-Liste im `GridState` (s. Offene Punkte).

### Spieler-/Team-State

```csharp
public struct PlayerState
{
    public PlayerId Id; public TeamId Team;
    public FactionId Faction;           // Allianz / Legion / Evolvierte
    public int Aetherium;               // einzige Währung (Start 1.000 AE, Economy.md)
    public int EnergyProduced, EnergyConsumed;  // Low-Power-Regel
    public int SupplyUsed, SupplyCap;   // inkl. Elite-Limits (Zähler je Elite-DefId)
    public PlayerStatus Status;         // Active / Defeated / Disconnected(KI-Übernahme, D-033)
    public DefId CommanderDef;          // CommanderSystem.md
    public int SuperweaponChargePct;    // oder je Superwaffen-Instanz im BuildingState
}

public struct TeamState { public TeamId Id; public bool SharedVision; public DiplomacyFlags Diplomacy; }
```

### Aetherium-Feld-State (führend: Resources.md)

```csharp
public struct AetheriumFieldState
{
    public EntityId MotherId;        // Mutterkristall als Entität (HP 3.000, zerstörbar, D-012)
    public int  ReserveAE;           // Restreserve, Nachwuchs zieht 1:1 ab
    public FieldPhase Phase;         // Wachsend / Reif / Erschöpft
    public byte OverharvestStage;    // 0–3, permanent, kein Zurücksinken
    public float OverharvestMeterSec;// kumulative Überentnahme-Zeit (Stufen-Auslöser)
    public float SpreadTimerSec;     // Intervall 90–120 s
    public SproutState[] Sprouts;    // max. maxSprouts je Feldtyp
    public int[] ContaminatedTiles;  // Indizes ins Grid; inert ab Phase Erschöpft (D-027)
}

public struct SproutState { public int TileIndex; public int ContentAE; /* ≤300 */ public byte MaturityPct;
                            public int Hp; }  // einzeln ernt-/zerstörbar (150 HP)
```

### Grid-State (geteilte Infrastruktur, D-034)

Ein 1-m-Integer-Grid (Karten S/M/L = 128/192/256 Tiles pro Achse), mehrere Schichten:

```csharp
public sealed class GridState
{
    public int Width, Height;
    public byte[]  Terrain;        // Geländetyp + Klippen-Blocker-Flag (FoW-Regel)
    public byte[]  HeightLevel;    // Höhenstufen (Klippen-Bonus +20 % Sicht)
    public uint[]  Occupancy;      // belegt durch EntityId (Bau-/Bewegungs-Blocking, Clearance-Radien via Lookup)
    public int[]   Contamination;  // TileIndex → Feld-Index (oder -1); inert-Flag über Feld-Phase
    public byte[]  Debris;         // Trümmer-Aufbau je Tile (D-012)
}
```

Pathfinding-Clearance-Layer und Flow-Field-Caches sind **abgeleitete** Daten (Dirty-Flagging, D-034) und nicht Teil des serialisierten State – sie werden nach dem Laden neu aufgebaut.

### FoW-State pro Team (drei Zustände, FogOfWar.md)

```csharp
public sealed class FogOfWarState
{
    public TeamId Team;
    public BitArray Explored;      // 1 bit/Tile: unerforscht → erforscht (monoton)
    public BitArray Visible;       // 1 bit/Tile: aktuell sichtbar (Sicht-Tick 5–10 Hz)
    public GhostBuilding[] Ghosts; // zuletzt gesehene feindliche Gebäude (DefId, Tile, HP-Snapshot)
    public RadarPing[] RadarPings; // Signatur-Pings, 1-Hz-Sweep, ~4 s Verfall (keine Vollsicht)
}
```

`Visible` ist transient rekonstruierbar, wird aber serialisiert, damit Savegames/Hash ohne Re-Sight sofort konsistent sind. Sicht-Caches (pro-Quelle-Rasterung) sind abgeleitet und nicht Teil des State.

### Tech-State

```csharp
public struct TechState
{
    public PlayerId Player;
    public BitArray CompletedTechs;   // Bit je TechDefId (ResearchTree.md)
    public DefId   ActiveResearch;    // laufende Forschung, 0 = keine
    public float   ResearchProgress;  // Sekunden
    public BitArray UnlockedDefs;     // gecachte Freischaltungen (Units/Gebäude/Upgrades)
}
```

### Match-State

```csharp
public struct MatchState
{
    public MatchPhase Phase;         // Setup / Running / Ended
    public MatchType Type;           // lokal (MVP) / online (Beta)
    public string MapId;             // Map-Definition + Layout-Seed
    public float ElapsedSeconds;     // = Tick / 10
    public VictoryCondition Victory; // VictoryConditions.md
    public EntityId Winner;          // TeamId-kodiert, 0 = offen
    public int[]  EventTimers;       // Hazard-/Wetter-Zeitpläne (Biomes.md, deterministisch geplant)
}
```

## Serialisierbarkeits-Regeln (D-033 Regel 5)

- `WorldState` ist vollständig über [./Serialization.md](./Serialization.md) schreib-/lesbar; Roundtrip liefert identischen State-Hash (CI-Test im SimRunner, D-036).
- Verboten im State: Objektreferenzen/Zyklen, Delegates/Events, `Dictionary`-Iteration im Tick, Unity-Typen, String-Keys (nur im `MapId`-Meta-Feld, außerhalb des Hash-Kerns).
- Abgeleitete Caches (Flow Fields, Clearance, Sicht-Raster) werden nach Deserialisierung deterministisch neu aufgebaut und sind als `RebuildDerivedState()`-Vertrag dokumentiert.

## Offene Punkte

- **Projektil-Granularität:** Welche Projektile sind sim-relevant (Zielverfolgung, AoE-Fuse) vs. rein visuell (Hitscan-Tracer)? Betrifft State-Größe und Hash-Fläche; Abstimmung mit DamageSystem.md nötig.
- **Feuer/Vegetation (D-012):** Ausbreitungsmodell der Brände (pro Tile Intensität + Timer?) ist gamedesign-seitig nicht final spezifiziert; `FirePatch`-Struktur ist Platzhalter-Entwurf.
- **FoW-Ghost-Umfang:** Speichern Ghost-Gebäude den HP-Snapshot des letzten Sichtzeitpunkts (SC2-Modell) oder nur DefId+Tile? UX- und Hash-Auswirkung, Klärung mit Game Design.
- **Fixed-Point-Umstellung (Beta):** `SimVec3`/`float`-Felder müssen bei der Beta-Umstellung (D-033) schema-versioniert migriert werden; frühe Finalisierung der Feldtypen reduziert Migrationsaufwand.
- **ID-Wiederverwendung:** Monotoner Zähler ohne Reuse ist gewählt; falls Speicherdruck in Langzeit-Survival-Matches (Survival-Modus) auftritt, Generations-Indizes re-evaluieren.
- **Superwaffen-State:** Eine globale Ladung pro Spieler vs. je Superwaffen-Gebäudeinstanz – hängt von der finalen Gebäude-/Superwaffen-Regel in Buildings.md ab.

## Nächste Schritte

- Review mit den Parallel-TDDs (Pathfinding, FoW, Networking) zur Grid- und FoW-State-Schnittmenge (Sprint-3-Konsistenzreview).
- Sprint 7: `EntityStore`-Slots und `WorldState` als erste Implementierung im Sim-Kern-Modul, inkl. Roundtrip-/Hash-Test im SimRunner (D-036).
- Klärung der Offenen Punkte Projektile/Feuer/Ghosts mit Lead Gameplay Designer vor Sprint-3-Abschluss.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Technical Director |
