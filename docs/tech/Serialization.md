# Serialization – Sim-State- und Replay-Serialisierung

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 3

## Zweck

Legt das Serialisierungsformat für den `WorldState` ([./GameState.md](./GameState.md)), das Schema-Versionierungsmodell und das Command-Log-Format (Replays) fest. Verbindlich für `Nova.Simulation` (Unity-frei, D-035), `Nova.SimRunner` (D-036) und [./Savegames.md](./Savegames.md). Erfüllt D-033 Regel 5 und liefert die Hash-Grundlage für Desync-Erkennung.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (serialisierbarer State, Lockstep-Ziel), D-035 (Unity-freie Assembly), D-036 (SimRunner/CI)
- [../research/Multiplayer_Simulation.md](../research/Multiplayer_Simulation.md) – Replay = Seed + Befehlsstrom, State-Hash-Vergleich, Desync-Tooling
- [./GameState.md](./GameState.md) – zu serialisierendes Zustandsmodell
- [./Savegames.md](./Savegames.md) – Dateiformat-Verbraucher (Slots, Header, Checksummen)
- [./Networking.md](./Networking.md) – Hash-Austausch im Lockstep (parallel, Sprint 3)

## Format-Vergleich

Kriterien: Dateigröße, Schema-Versionierung, Determinismus (bit-exakter Roundtrip, plattformstabil), Menschenlesbarkeit/Debuggbarkeit, Unity-Freiheit des Kerns, Wartungsaufwand.

| Kriterium | Eigener BinaryWriter | MessagePack-C# | Unity JsonUtility |
|---|---|---|---|
| Größe (Snapshot ~500 Entities) | sehr klein (~50–150 kB, flache Structs) | klein (~1,2–2× Binär) | groß (~5–10× Binär, Text) |
| Versionierung | explizit, voll kontrolliert (Feldreihenfolge = Kontrakt) | gut (Key-/Index-Schema), aber Magie im Attribut-Layer | schwach (still fehlende Felder, keine Migration) |
| Determinismus | voll kontrollierbar (Endianness, Feldreihenfolge, Float-Rohbits) | grundsätzlich stabil, aber Map-/Enum-Verhalten versionssensitiv | Float-Text-Rundung, keine Bit-Stabilität garantiert |
| Menschenlesbarkeit (Debug) | nein (Hexdump) → separater JSON-Debug-Export nötig | nein (msgpack-Tools vorhanden) | ja |
| Unity-Freiheit `Nova.Simulation` | ja (reines .NET) | ja (NuGet, AOT-fähig) | **nein** (UnityEngine-API → verletzt D-033/D-035) |
| Wartung / Tooling | Handarbeit pro Typ, dafür explizit und codegen-fähig | gering, Attribut-getrieben | gering, aber funktional zu schwach |

**Empfehlung: Eigener BinaryWriter (handgeschriebene, explizite `Write`/`Read` pro State-Struct), ergänzt um einen optionalen JSON-Debug-Export.**

Begründung:
1. **Determinismus ist das harte Kriterium.** Replays, State-Hashes und Lockstep (D-033) verlangen bit-exakte, plattformstabile Bytes (feste Endianness Little-Endian, Floats als Rohbits). Nur ein eigenes Format macht das zum expliziten, testbaren Kontrakt statt zur Framework-Annahme.
2. **D-035-Ausschluss:** JsonUtility ist eine UnityEngine-API und darf im Sim-Kern nicht verwendet werden – es scheidet strukturell aus, nicht nur qualitativ.
3. **Abhängigkeitsdisziplin:** MessagePack-C# wäre technisch tragfähig (reines .NET), zieht aber eine Third-Party-Abhängigkeit in den Determinismus-kritischen Kern; der Wartungsvorteil ist bei flachen Structs (kein Objektgraph, GameState.md) klein. Als dokumentierter Fallback festgehalten (Analogie D-034-Fallback).
4. **Debuggbarkeit** wird über einen separaten, nicht determinismuskritischen JSON-Export (System.Text.Json, nur Tooling/SimRunner, nie im Tick) gelöst – nicht über das Primärformat.

## Serialisierungs-Skizze

```csharp
namespace Nova.Simulation.Serialization
{
    // Binärer Kontrakt: Little-Endian, Feldreihenfolge = Schema, keine Selbstbeschreibung.
    public interface ISimSerializable
    {
        void Write(SimBinaryWriter w, SchemaVersion v);
        void Read (SimBinaryReader r, SchemaVersion v);   // v steuert Migrations-Lesen
    }

    public static class WorldStateSerializer
    {
        public static byte[] Serialize(WorldState state);          // → identischer Hash bei Roundtrip
        public static WorldState Deserialize(ReadOnlySpan<byte> data);
        public static uint ComputeStateHash(WorldState state);     // xxHash32 über kanonische Bytes
    }

    // Debug-Export (außerhalb des Determinismus-Pfads, SimRunner/Editor-Tooling)
    public static class WorldStateDebugDump { public static string ToJson(WorldState state); }
}
```

Regeln:
- Floats werden als Rohbits (`BitConverter.SingleToInt32Bits`) geschrieben – kein Text, kein Runden.
- Längen-Präfixe als `ushort`/`int` explizit; `BitArray` als gepackte `uint`-Blöcke mit Längenfeld.
- Der Serializer ist die **einzige** Stelle, die Feldreihenfolge kennt – er ist damit automatisch die Migrations-Stelle.

## Schema-Versionierung

```csharp
public readonly struct SchemaVersion { public readonly ushort Major; public readonly ushort Minor; }
```

- Jede Datei (Savegame, Replay, Netzwerk-Snapshot) beginnt mit einem Header: Magic `"NOVA"`, `SchemaVersion`, `ContentKind` (Savegame/Replay/Snapshot), Erstell-Tick, `GameVersion` (Build), `DefinitionsHash` (Hash der GameDatabase-Version).
- **Major** = brechende Strukturänderung des State (Feld hinzugefügt/entfernt/umtypisiert). **Minor** = rückwärtskompatible Ergänzung (neuer optionaler Block am Ende).
- **Migrations-Strategie:** lineare Migratoren-Kette `v(n) → v(n+1)`; der Reader lädt in das älteste passende Schema und migriert schrittweise auf `Current`. Keine Sprung-Migrationen, keine Schema-Verzweigungen. Migratoren leben im Sim-Kern und sind durch Roundtrip-Tests je Version abgesichert (SimRunner-Fixtures, D-036).
- **Definitions-Änderungen (Balance-Patches) sind keine Schema-Migration:** geänderte GameDatabase-Werte werden nicht migriert, sondern über `DefinitionsHash`-Vergleich als inkompatibel erkannt (Policy in [./Savegames.md](./Savegames.md)).

## Command-Log-Format (Replay = Seed + Command-Strom)

Grundlage: Research – bei befehlsgetriebener Simulation ist ein Replay = Map-Setup + Seed + zeitgestempelter Befehlsstrom (Kilobyte-klein, deterministisch abspielbar).

```csharp
public struct ReplayHeader
{
    public SchemaVersion Version;
    public string   GameVersion;      // Build-Nummer
    public string   MapId;            // Map + Layout-Seed
    public int      RandomSeed;       // WorldState.RandomSeed
    public ReplayPlayer[] Players;    // Slot → Faction/Team/Commander (Meta, nicht im Hash)
    public uint     DefinitionsHash;
    public DateTime RecordedUtc;      // Meta
}

public struct CommandRecord              // 12–32 Byte je nach Payload
{
    public uint     Tick;              // Ziel-Tick (10 Hz, D-033)
    public PlayerId Issuer;
    public CommandType Type;           // Move, Attack, Build, Research, Harvest, …
    public ushort   PayloadLength;
    // Payload: typabhängige, ISimSerializable-Daten (IDs, Tiles, DefIds)
}

public struct HashCheckpoint { public uint Tick; public uint StateHash; }
```

- Datei = `ReplayHeader` + sequentieller `CommandRecord`-Strom + periodische `HashCheckpoint`s (Vorschlag: alle 100 Ticks = 10 s) für Desync-Lokalisierung und Schnellvorlauf.
- Wiedergabe = Setup aus Header + Commands tickgenau einspielen; bei Checkpoint-Abweichung: Desync-Report (erster divergierender Tick/Entity, Pflicht-Tooling laut Research §3.6).
- Das Format dient dreifach: Replays/Observer (Beta), Savegame-Grundlage, KI-Test-Fixtures und Desync-Debugging im SimRunner (D-036).

## Offene Punkte

- **Kompression:** LZ4/Deflate über Snapshot- und Replay-Payload noch nicht entschieden; Snapshots sind unkomprimiert bereits klein, Langzeit-Replays (35 min × N Commands) und Reconnect-Snapshots (Beta) könnten Kompression rechtfertigen. Entscheidung mit ersten Größenmessungen in Sprint 7.
- **MessagePack-C# als Fallback:** Falls der Pflegeaufwand der handgeschriebenen Serializer bei wachsendem State unverhältnismäßig wird, ist MessagePack-C# der dokumentierte Ersatzkandidat – erfordert dann erneute Determinismus-Validierung (Phase-0-Spike-Methodik, ARM↔x86).
- **Hash-Algorithmus:** xxHash32 vorgeschlagen (schnell, ausreichend für Desync-Erkennung); kryptografische Stärke ist nicht gefordert, aber Kollisionsresistenz bei 500-Entity-State ungeprüft – Messung im SimRunner.
- **Endianness ARM↔x86:** Little-Endian als Kontrakt festgelegt; Big-Endian-Hosts werden derzeit nicht unterstützt (Win/macOS primär, D-006) – Bestätigung im Phase-0-Determinismus-Spike.
- **CommandRecord-Payload-Größenobergrenze:** Offen, ob variable Payloads oder feste 32-Byte-Records (einfacherer Parser, etwas größer); nach Command-Inventar aus GDD entscheiden.

## Nächste Schritte

- Sprint 7: `SimBinaryWriter/Reader` + Serializer für `WorldState`-Kern implementieren; Roundtrip- und Hash-Tests in den SimRunner-CI-Lauf aufnehmen (D-036).
- Größenmessung: Referenz-Snapshot (500 Entities, L-Karte) serialisieren und Zahlen für Größe/Schreibdauer hier dokumentieren (Version 0.2).
- Hash-Checkpoint-Intervall mit Networking.md (Lockstep-Bandbreite) abstimmen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Technical Director |
