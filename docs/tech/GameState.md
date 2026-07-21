# GameState – Zustandsmodell der Simulation

**Version:** 0.2.1 | **Status:** Entwurf (Korrekturlauf Sprint 4) | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 4

## Zweck

Definiert das vollständige, serialisierbare Zustandsmodell der `Nova.Simulation`-Assembly: welche Daten den Simulationszustand eines Matches ausmachen, wie sie strukturiert und adressiert sind und welche Invarianten gelten. Verbindlich für alle Sim-Systeme (Sprint 7), für [./Serialization.md](./Serialization.md) und [./Savegames.md](./Savegames.md). Erfüllt D-033 Regel 5 (vollständig serialisierbarer State) und ist die Grundlage für Replays, Desync-Jagd (State-Hash) und den `Nova.SimRunner` (D-036).

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (5 Sim-Regeln), D-034 (Integer-Grid 1 m, geteilte Grid-Infrastruktur), D-035 (Unity-freie Assembly `Nova.Simulation`), D-036 (SimRunner), D-010/D-012 (Aetherium, Zerstörbarkeit), D-011 (Keim/Reifung/Regeneration), D-015 (Elite-Limit), D-016 (Neutrale), D-022 (Capture-Kanal), D-023 (Superwaffen-Limit), D-029 (Artefakt-Sonde nur SP/Koop), D-047 (1 Tile = 1 m), D-048 (Einheiten-Deckel 600, Density ≤ 1,5)
- [../research/Multiplayer_Simulation.md](../research/Multiplayer_Simulation.md) – Desync-Quellen, State-Hash, Iterationsreihenfolge-Regeln
- [../gamedesign/Resources.md](../gamedesign/Resources.md) – Aetherium-Feld-Datenmodell (führend für Feld-State)
- [../gamedesign/FogOfWar.md](../gamedesign/FogOfWar.md) – drei Sichtzustände, Radar-Regeln
- [../gamedesign/DamageSystem.md](../gamedesign/DamageSystem.md) / [../gamedesign/Weapons.md](../gamedesign/Weapons.md) – Status-Effekte und Fähigkeiten (führend für Effect-/Channel-/Cooldown-State)
- [../gamedesign/Biomes.md](../gamedesign/Biomes.md) – Biom-Modifikatoren, Wetter-/Hazard-System (führend für Environment-State)
- [../gamedesign/MultiplayerModes.md](../gamedesign/MultiplayerModes.md) – MatchSettings (11 Felder, §2)
- [../gamedesign/Aircraft.md](../gamedesign/Aircraft.md) – Munition, Landebuchten, Transport-Regeln
- [../gamedesign/NeutralUnits.md](../gamedesign/NeutralUnits.md) – Lager-/Critter-Regeln (D-016)
- [../gamedesign/Economy.md](../gamedesign/Economy.md) / [../gamedesign/ResearchTree.md](../gamedesign/ResearchTree.md) – Ressourcen-/Tech-State (führend)
- [./Serialization.md](./Serialization.md) – Format der Serialisierung
- [./Savegames.md](./Savegames.md) – Snapshot-Verwendung
- [./Pathfinding.md](./Pathfinding.md) – Grid-Nutzung für Wegfindung; [./Rendering.md](./Rendering.md) – FoW-Darstellung (parallel, Sprint 3)

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
    public EnvironmentState Environment;      // Biom-Modifikatoren + Hazard-Zeitplan (Biomes.md)
    public NeutralCampState[] NeutralCamps;   // feindliche neutrale Lager als Objectives (D-016)
    public CritterSpawnState[] CritterSpawns; // Ambient-Fauna mit Respawn (D-016)
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
                             public int AmmoCount;           // Bomber/Spezial (Aircraft.md); −1 = unbegrenzt
                             public float RearmTimerSec;     // ~10 s Nachladen an eigener Bucht
                             public EntityId[] Passengers;   // Transport-Ladung (8 Inf./1 leichtes Fzg Luft; APC 6 Sitze)
                             public EntityId HomeAirfield;   // Heimat-Flugfeld (FixedWing), 0 = keins/VTOL
                             public byte BayIndex;           // belegte Landebucht 0–3
                             public EntityId MoveTarget; /* … */ }
public struct BuildingState{ public EntityCore Core; public int BuildProgressPct; public bool Powered;
                             public ushort RallyTile; public DefId[] ProductionQueue;
                             public EntityId[] Bays;          // 4 Landebuchten (Flugfeld, Aircraft.md); Belegung = Bau-Limit
                             public GrowthPhase Growth;       // Keim / Reifung / Reif (Evolvierte, D-011)
                             public byte MaturityPct;         // Reifungsgrad 0–100 % (Keim startet mit 25 % Ziel-TP)
                             public float RegenDelaySec; }    // 5 s kampffrei → 2 % TP/s Regeneration (D-011, statt Reparatur)
public struct ProjectileState { public EntityCore Core; public SimVec3 Velocity; public EntityId Target;
                                public float FuseTime; }   // nur sim-relevante Projektile (s. Offene Punkte)
```

- **Orders vs. Commands:** Commands (Spielereingaben, serialisierbar, Replay-relevant) erzeugen Orders (interne Ausführungszustände, Teil des State, nicht des Replays).
- Selektion, Kamera, Hover, UI-Highlight sind **View-State** und gehören nicht in den `WorldState`.
- Trümmer (D-012) sind eigene Entity-Kategorie mit Verfalls-Timer (Fade-out 60 s mit hartem Cap, D-042.2); Vegetations-Brände als `FirePatch`-Liste im `GridState` (s. Offene Punkte).
- **Landebuchten (Aircraft.md):** Jedes FixedWing-Luftfahrzeug belegt dauerhaft eine der 4 Buchten seines Heimat-Flugfelds (`HomeAirfield`/`BayIndex`); ohne freie Bucht keine Produktion. Bei Verlust des Heimat-Flugfelds weicht das Flugzeug auf eine freie Bucht des nächsten eigenen Flugfelds aus – gibt es keine, kann es nicht nachladen (kein Absturz).
- **Transport-Ladung:** `Passengers` referenziert geladene Entitäten; deren eigener Slot bleibt bestehen, sie sind aber bewegungs-/feuerunfähig (Flag) und werden bei Abschuss des Transporters mitzerstört (Aircraft.md/Vehicles.md).

### Effekt-/Fähigkeiten-State (Abilities/Effects-Modul)

Das GDD definiert ~40 aktive Fähigkeiten ([../gamedesign/Weapons.md](../gamedesign/Weapons.md), Infantry/Vehicles/Aircraft) und 4 Status-Effekte ([../gamedesign/DamageSystem.md](../gamedesign/DamageSystem.md): `Burning`, `Contamination` inkl. Regenerations-Blockade, `Slow`, `EMP`). Alle sind serialisierbarer, hashbarer State – flache, slot-basierte Stores, adressiert über `EntityId`:

```csharp
public struct EffectState   // laufende Status-Effekte/DoTs auf einem Ziel
{
    public EntityId Target; public DefId EffectDef; public EntityId Source;
    public ushort RemainingTicks;   // DoT tickt 1×/s (DamageSystem.md); Refresh statt Stacking
    public int    ShieldAbsorb;     // restliche Absorption (Schild-Fähigkeiten), 0 = kein Schild
}

public struct CooldownState { public EntityId Owner; public DefId AbilityDef; public uint ReadyTick; }

public struct ChannelState  // generische Kanal-Mechanik: Capture (5 s, D-022), Sprengsatz-Setup, Brückenreparatur
{
    public EntityId Channeler; public EntityId Target; public DefId ChannelDef;
    public ushort ProgressTicks; public ushort DurationTicks; // Abbruch bei Schaden → Fortschritt verworfen
}

public struct AuraState     // quell-zentrierte Dauer-Effekte (z. B. Befehlsaura +15 %)
{
    public EntityId Source; public DefId AuraDef; public bool Active;
}
```

- Effekte werden bei erneutem Treffer **aufgefrischt, nicht gestapelt** (DamageSystem.md-Regel). Immunitäten (Gebäude vs. `Slow`, Evolvierte vs. `EMP`, D-027.2) wertet das Abilities/Effects-Modul aus, nicht der State.
- Der Capture-Kanal (D-022) ist **kein** Sonderfall des NeutralUnits-Moduls, sondern eine Ausprägung der generischen Kanal-Mechanik (`ChannelDef` trägt Dauer, Reichweite ≤ 3 m, Verbrauchs-Regel).

### Spieler-/Team-State

```csharp
public struct PlayerState
{
    public PlayerId Id; public TeamId Team;
    public FactionId Faction;           // Allianz / Legion / Evolvierte
    public int Aetherium;               // einzige Währung (Start 1.000 AE, Economy.md)
    public int EnergyProduced, EnergyConsumed;  // Low-Power-Regel
    // Kein Supply-/Pop-System (D-021): Begrenzung läuft ausschließlich über Ökonomie,
    // Produktionszeit und den globalen Deckel `MatchState.GlobalUnitCount` (600/Match, D-048)
    // sowie das Elite-Limit unten – kein Supply-Feld hier.
    public ushort[] EliteCounts;        // Zähler je Elite-DefId; Limit aus MatchSettings.EliteUnitLimit (D-015)
    public PlayerStatus Status;         // Active / Defeated / Disconnected (deterministische KI-Übernahme, D-038/D-046)
    public DefId CommanderDef;          // CommanderSystem.md
    public SuperweaponState Superweapon; // Ladung/Cooldown/Gebäude-Referenz (D-023, s. u.)
}

public struct TeamState { public TeamId Id; public bool SharedVision; public DiplomacyFlags Diplomacy; }

public struct SuperweaponState      // Limit 1 Gebäude pro Spieler, globale Bau-Ansage (D-023)
{
    public EntityId Building;       // Superwaffen-Gebäude; 0 = keine gebaut
    public float ChargeSec;         // 0–180 s Ladezeit nach Fertigstellung (Buildings.md §5)
    public float CooldownSec;       // 300 s nach jedem Einsatz
    public bool  Ready;             // geladen & abklingzeitfrei; Ladung pausiert bei Low Power ohne Reset (D-030)
}
```

Der 25-%-Rückschlag bei Zerstörung eines **geladenen** Superwaffen-Gebäudes (D-023) wird vom Combat-Modul aus `SuperweaponState` + `BuildingState` ausgewertet; der Zählerstand selbst lebt ausschließlich hier.

### Aetherium-Feld-State (führend: Resources.md)

```csharp
public struct AetheriumFieldState
{
    public EntityId MotherId;        // Mutterkristall als Entität (HP 3.000, zerstörbar, D-012)
    public int  ReserveAE;           // Restreserve, Nachwuchs zieht 1:1 ab
    public FieldPhase Phase;         // Wachsend / Reif / Erschöpft
    public byte UpgradeLevel;        // Mutterkristall-Ausbaustufe 1–3 (Resources.md); Überernte-Stufe 2 senkt sie um 1
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

Ein 1-m-Integer-Grid (Karten S/M/L = 128/192/256 Tiles pro Achse, 1 Tile = 1 m – D-034/D-047), mehrere Schichten:

```csharp
public sealed class GridState
{
    public int Width, Height;
    public byte[]  Terrain;        // Geländetyp + Klippen-Blocker-Flag (FoW-Regel)
    public byte[]  HeightLevel;    // Höhenstufen (Klippen-Bonus +20 % Sicht)
    public uint[]  Occupancy;      // belegt durch EntityId (Bau-/Bewegungs-Blocking, Clearance-Radien via Lookup)
    public int[]   Contamination;  // TileIndex → Feld-Index (oder -1); inert-Flag über Feld-Phase
    public byte[]  Debris;         // Trümmer-Aufbau je Tile (D-012)
    public byte[]  BiomeZone;      // Effekt-Zone je Tile (Slow-Zonen, Nebel-/Smog-Zonen – Biomes.md)
    public byte[]  SpeedModifier;  // Tempo-Malus je Tile, nur 25-%-Schritte (Biomes.md); Zielklasse in BiomeZone kodiert
    public byte[]  RadiationShelter; // Mond: gebackene Schutz-Zone (Krater-Schatten, Bauwerke) als Sim-Flag –
                                     // KEIN Render-Schatten (Review GDD↔TDD F-07); Strahlung trifft nur ungeschützte Tiles
}
```

Pathfinding-Clearance-Layer und Flow-Field-Caches sind **abgeleitete** Daten (Dirty-Flagging, D-034) und nicht Teil des serialisierten State – sie werden nach dem Laden neu aufgebaut.

### Environment-State (Biom-Modifikatoren & Hazards, Biomes.md)

Kartenweite Modifikatoren und der deterministische Wetter-/Hazard-Zeitplan; zonale Effekte liegen als Layer im `GridState` (s. o.). Vorwarnung und aktive Phase sind State, damit Savegames/Hash auch mitten in einem Sandsturm konsistent sind:

```csharp
public struct EnvironmentState
{
    public DefId  BiomeDef;         // Biom der Karte (Biomes.md)
    public float  SightMultiplier;  // 1,0 / 0,75 / 0,5 während Wetter/Hazard (FoW wertet aus)
    public float  RadarMultiplier;  // Mars-Staubsturm: Radar-Reichweite −25 %
    public HazardPhase Phase;       // Idle / Warning / Active
    public float  PhaseTimerSec;    // Restdauer der laufenden Phase (Vorwarnung 15 s Wetter / 20 s Hazard)
    public float  NextEventSec;     // deterministischer Zeitplan (Intervall 4–6 Min Wetter / 5–7 Min Hazard)
    public float  SpreadModifier;   // Biom-Multiplikator Aetherium-Ausbreitung (−25 % … +50 %, Eingang an Economy)
}
```

Schaden über Zeit (Mond-Strahlungsfront) läuft als DoT über das Combat-Modul nur auf Tiles ohne `RadiationShelter`-Flag. Wetter verändert darüber hinaus **keine** Produktions-, Energie- oder Schadenswerte (Regel aus Biomes.md); `WeatherEnabled` aus den MatchSettings schaltet den Zeitplan ab (Phase bleibt `Idle`).

### FoW-State pro Team (drei Zustände, FogOfWar.md)

```csharp
public sealed class FogOfWarState
{
    public TeamId Team;
    public BitArray Explored;      // 1 bit/Tile: unerforscht → erforscht (monoton)
    public BitArray Visible;       // 1 bit/Tile: aktuell sichtbar (Sicht-Tick 5–10 Hz)
    public GhostBuilding[] Ghosts; // zuletzt gesehene feindliche Gebäude (DefId, Tile, HP-Snapshot)
    public RadarPing[] RadarPings; // Signatur-Pings, 1-Hz-Sweep, ~4 s Verfall (keine Vollsicht)
    public TemporaryReveal[] Reveals; // zeitlich begrenzte Aufdeckung (Artefakt-Sonde, nur SP/Koop – D-029)
}

public struct TemporaryReveal { public int TileIndex; public byte RadiusTiles; public uint UntilTick; }
```

`Visible` ist transient rekonstruierbar, wird aber serialisiert, damit Savegames/Hash ohne Re-Sight sofort konsistent sind. Sicht-Caches (pro-Quelle-Rasterung) sind abgeleitet und nicht Teil des State. Die globale Sicht beeinflussenden Wetter-Effekte laufen über `EnvironmentState.SightMultiplier`, nicht über eigene FoW-Felder.

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
    public MatchSettings Settings;   // Laufzeit-Kopie aller 11 Lobby-Felder (MultiplayerModes.md §2)
    public float ElapsedSeconds;     // = Tick / 10
    public float TimeLimitSec;       // Countdown aus Settings.TimeLimitMin; 0 = deaktiviert
    public ushort GlobalUnitCount;   // Deckel 600/Match (D-048): bei Erreichen Produktionsstopp + UI-Hinweis
    public VictoryCondition Victory; // VictoryConditions.md
    public EntityId Winner;          // TeamId-kodiert, 0 = offen
}

public struct MatchSettings         // 11 Felder gemäß MultiplayerModes.md §2 (Review GDD↔TDD F-08)
{
    public int   StartingResourcesAE;   // 500–10.000, Default 1.000
    public byte  StartingUnits;         // HarvesterOnly / HarvesterPlusDefense
    public float AetheriumDensity;      // 0,5–2,0; ≤ 1,5 bei 5–6 Spielern erzwungen (D-048)
    public float AetheriumSpreadRate;   // 0,5–2,0
    public bool  WeatherEnabled;        // Biom-Wetter/Hazards an/aus (D-017)
    public byte  FogOfWarMode;          // Standard / Explored / Off
    public bool  SuperweaponsEnabled;   // Superwaffen-Tier an/aus
    public byte  EliteUnitLimit;        // 1 (MVP/Alpha) / 2 (Release), D-015
    public float GameSpeed;             // fest 1,0 – siehe Hinweis unten
    public int   TimeLimitMin;          // 0 = aus / 20–60
    public byte  AIDifficulty;          // pro KI-Slot; wird beim Setup in die KI-Slot-Konfiguration überführt
}
```

**GameSpeed fest 1,0:** Die Option `Fast` (+15 % Sim-Tempo) aus MultiplayerModes.md §2 ist mit der festen 10-Hz-Sim-Clock (D-033) und dem Lockstep-Modell nicht deterministisch abbildbar und widerspricht zudem CoreGameplay.md („Spielgeschwindigkeit 1,0 fest im Skirmish"). Sim-seitig ist `GameSpeed` daher konstant 1,0 (kein Eingriff in Tick-Rate oder Zeitfaktor); die GDD-seitige Streichung bzw. Einschränkung der Option ist als Offener Punkt an den Lead Gameplay Designer eskaliert (Review GDD↔TDD F-08).

Der frühere `EventTimers`-Platzhalter entfällt: der Hazard-/Wetter-Zeitplan lebt jetzt in `EnvironmentState` (s. o.).

### Neutrale-State (D-016, NeutralUnits.md)

```csharp
public struct NeutralCampState   // feindliche neutrale Lager (Bonus-Aetherium-Feld / Artefakt-Cache)
{
    public EntityId CampId;      // Lager-Hauptobjekt (Cache bzw. zentrales Lager-Objekt)
    public int   HpPool;         // verbleibende Summen-HP der Lager-Besatzung
    public bool  Cleared;        // geräumt = final, kein Respawn (NeutralUnits.md)
    public bool  RewardPaid;     // AE-Belohnung/Cache-Effekt ausgezahlt (an Economy)
}

public struct CritterSpawnState  // Ambient-Fauna
{
    public int   TileIndex;      // Spawn-Punkt (Respawn am Spawn-Punkt, nicht am Todesort)
    public DefId CritterDef;
    public float RespawnTimerSec;// 90–180 s nach Tod; 0 = lebend
}
```

Leash-Verhalten und Aggro-Radien sind Definitionsdaten; im State verbleiben nur fortschrittsrelevante Werte (Zerstört-/Belohnungs-Status, Respawn-Timer). Bonus-Aetherium-Felder der Lager sind reguläre `AetheriumFieldState`-Einträge mit kleinerer Reserve (NeutralUnits.md).

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
- **GameSpeed-Option (GDD-seitig, neu):** MultiplayerModes.md §2 führt `GameSpeed Fast` (+15 %); Sim-seitig ist der Wert fest 1,0 (s. Match-State). Streichung der Option oder eine auf unranked beschränkte, deterministisch definierte Tick-Skalierung ist durch den Lead Gameplay Designer zu entscheiden (Review GDD↔TDD F-08) – kein Sim-seitiger Entscheidungsspielraum.

*Entschieden im Korrekturlauf Sprint 4 (D-043–D-052, Review-Findings F-2/F-02/F-07/F-08/F-09): Effekt-/Fähigkeiten-State (`EffectState`/`CooldownState`/`ChannelState`/`AuraState`, Capture als generischer Kanal); Environment-State inkl. gebackener Strahlungs-Schutz-Zone statt Render-Schatten; `MatchSettings`-Laufzeit-Struct (11 Felder); Munition/Landebuchten/Transport-Ladung; Elite-Zähler je DefId und globaler `GlobalUnitCount` (Deckel 600, D-048); `SuperweaponState` mit Gebäude-Referenz (D-023 – löst den bisherigen Offenen Punkt „globale Ladung vs. Gebäudeinstanz": Gebäude-Referenz, da Limit 1/Spieler); Neutrale-Lager-/Critter-State (D-016); Mutterkristall-Ausbaustufe 1–3 und Keim-Reifungsgrad (Abgleich Resources.md/Buildings.md).*

## Nächste Schritte

- Review mit den Parallel-TDDs (Pathfinding, FoW, Networking) zur Grid- und FoW-State-Schnittmenge (Sprint-3-Konsistenzreview).
- Vollständigkeitsprüfung „GDD-Mechanik ↔ State-Feld" durch einen zweiten Reviewer nach diesem Korrekturlauf gegen alle GDD-Dokumente wiederholen (Empfehlung aus Review Architektur-Kohärenz F-2).
- Sprint 7: `EntityStore`-Slots und `WorldState` als erste Implementierung im Sim-Kern-Modul, inkl. Roundtrip-/Hash-Test im SimRunner (D-036).
- Klärung der Offenen Punkte Projektile/Feuer/Ghosts/GameSpeed mit Lead Gameplay Designer vor Sprint-4-Abschluss.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Technical Director |
| 0.2.0 | 2026-07-21 | Korrekturlauf Sprint 4 (D-043–D-052, Review-Findings): Effekt-/Fähigkeiten-State, Environment-State, MatchSettings, Munition/Buchten/Transport, Elite-/Unit-Counter, SuperweaponState, Neutrale-State, Ausbaustufe 1–3, Keim-Reifung | Lead Technical Director |
| 0.2.1 | 2026-07-21 | Fix F-18 (GDD↔TDD): `SupplyUsed`/`SupplyCap` aus `PlayerState` entfernt (D-021 verbietet Supply-/Pop-System); Begrenzung läuft über `MatchState.GlobalUnitCount` (Deckel 600, D-048) und `EliteCounts` (D-015) | Lead Technical Director |
