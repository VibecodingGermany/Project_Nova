# Replication – Command-Replikation, Desync-Detektion, Reconnect, Replays

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Multiplayer Engineer | **Sprint:** 3

## Zweck

Definiert, **was** zwischen den Teilnehmern eines Nova-Matches repliziert wird und **wie** Konsistenz überwacht wird: ausschließlich Commands plus Tick-Hashes (kein State-Sync), Desync-Detektion über State-Hashes mit Server-Vergleich und Report-Format, Reconnect via Snapshot + Fast-Forward, Beobachter-Modell (60–120 s Delay) und Replays als Replikations-Nebenprodukt. Abschließend der Migrationspfad vom lokalen MVP-Singleplayer zum Beta-Relay. Transport, Server-Rollen und Disconnect-Regel: [./Networking.md](./Networking.md).

Grundprinzip (D-033, Regel 1): **Commands sind die einzige State-Mutation.** Daraus folgt: Wer Seed, Initialzustand und den kanonischen Command-Strom besitzt, besitzt das gesamte Match – Replikation, Replay, Beobachter und Reconnect sind vier Ausprägungen desselben Stroms.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (5 Architekturregeln, Float im MVP, Fixed-Point in Beta), D-035 (Nova.Simulation-Assembly), D-036 (SimRunner)
- [../research/Multiplayer_Simulation.md](../research/Multiplayer_Simulation.md) – §2 Modellvergleich, §4 Replay/Observer/Reconnect, §3 Determinismus-Fallstricke
- [./Networking.md](./Networking.md) – Protokoll (`TickBatch`, `StateHash`, `Snapshot*`), Server-Rollen, Disconnect-Regel
- [./GameState.md](./GameState.md) – geplant: Command-Modell, State-Serialisierung, Snapshot-Layout (D-033 Regel 5)
- [../gamedesign/MultiplayerModes.md](../gamedesign/MultiplayerModes.md) – §6 Beobachter-/Replay-Anforderungen (Delay 60–120 s, Auto-Replay, Versionsbindung)
- [../gamedesign/FogOfWar.md](../gamedesign/FogOfWar.md) – Spectator/Replay sehen alles (Maske "alle")

## 1. Replikationsumfang

| Datenklasse | Repliziert? | Weg | Begründung |
|---|---|---|---|
| **Player-Commands** | Ja | Client → Server (`CommandSubmit`), Server → alle (`TickBatch`) | Einzige State-Mutation (D-033 Regel 1); Volumen skaliert mit APM, nicht Einheitenzahl (Research §2.5: <5 kB/s) |
| **Tick-Hashes** | Ja | Client → Server (`StateHash`, unreliable) | Desync-Detektion (§2) |
| **Initialzustand / MatchConfig** | Ja | Einmalig bei Matchstart (Tick-0-Batch) | Map-Seed, Slots, Settings, InputDelay – Determinismus-Anker |
| **Snapshots** | Nur auf Anforderung | Server → Reconnecting Client (chunked) | Reconnect (§3); im Normalbetrieb **kein** State-Transfer |
| **Einheiten-State (Positionen, HP, …)** | **Nein** | – | State-Sync bei 500 sichtbaren Einheiten ~200–300 kB/s/Client, strukturell ungeeignet (D-033, Research §2.5) |
| **FoW-/Sichtdaten** | Nein (bis Ranked-Re-Eval) | – | Jeder Client simuliert alles; FoW ist View-Filter. Maphack-Lage: [./Networking.md](./Networking.md) §8 |
| **View-Effekte (VFX, Audio, Kamera)** | Nein | – | View-Schicht, nie Teil der Sim (D-033 Regel 2) |

**Konsequenz für das Command-Schema:** Commands müssen vollständig, kompakt und versionsstabil serialisierbar sein. Skizze:

```csharp
namespace Nova.Simulation.Commands
{
    // Alle Commands sind flache, allocation-freie Datensätze; IDs deterministisch.
    public interface ICommand
    {
        byte PlayerSlot { get; }        // Ausführender Slot (vom Server gegen Session geprüft)
        CommandKind Kind { get; }       // Move, Attack, Build, Research, Capture, Superweapon, ...
    }

    public static class CommandSerializer
    {
        // Binär, little-endian, manuell versioniert; KEIN Reflection-/JSON-Serializer
        // im Tick-Pfad (GC + Versionierungsrisiko). Ziel: 10–40 Byte/Command (Research §2.5).
        public static int Write(in ICommand cmd, Span<byte> dst);
        public static bool TryRead(ReadOnlySpan<byte> src, out ICommand cmd);
    }
}
```

## 2. Desync-Detektion

### 2.1 State-Hash

- Nach **jedem Tick** bildet jeder Client einen Hash über den vollständigen Simulationszustand (Entities, Ressourcen, Grid-Layer inkl. Aetherium/FoW-Sim-Anteil, PRNG-State, Tick-Zähler). Hash-Funktion: schneller Nicht-Krypto-Hash mit stabiler Spezifikation (Vorschlag xxHash64), deterministische Iterationsreihenfolge über ID-indizierte Strukturen (Research §3.3).
- **Übertragung gedrosselt:** `StateHash` wird alle **N = 10 Ticks (1 s)** an den Server gesendet (unreliable – Redundanz eingebaut, siehe [./Networking.md](./Networking.md) §2.1). Lokal wird der Hash jedes Ticks ins Hash-Ringlog geschrieben (Desync-Lokalisierung).

### 2.2 Vergleich und Reaktion

Der Server führt pro Tick-Intervall die Hashes aller Slots zusammen:

1. **Alle gleich:** weiter.
2. **Minderheit abweichend:** Desync-Bescheid (`HashMismatch`) an alle; das Match **läuft weiter** (kein harter Abbruch – Koop/KI-Kontext, D-007), der abweichende Slot wird markiert. Server fordert vom abweichenden Client automatisch einen **Desync-Report** an (§2.3). In PvP (Beta) ist die weitere Behandlung (Fortsetzung vs. Remis-Angebot) eine Balancing-/UX-Frage → Offener Punkt.
3. **Hash des Desync-Clients + Command-Log** erlauben die exakte Reproduktion im `Nova.SimRunner` (D-036): Match bis Tick T fast-forwarden, Divergenz tickgenau eingrenzen.

### 2.3 Desync-Report-Format

Automatisch erzeugt, an den Server hochgeladen, serverseitig mit dem Match-Record verknüpft:

```csharp
namespace Nova.Net.Diagnostics
{
    public readonly record struct DesyncReport(
        uint MatchId,
        byte PlayerSlot,
        uint FirstMismatchTick,         // erster Tick mit abweichendem Hash
        ulong LocalHash,
        ulong MajorityHash,             // Referenz-Hash der Mehrheit
        string BuildVersion,            // exakte Spielversion + Plattform (ARM/x86, Mono/IL2CPP)
        string[] HashRingTail,          // letzte 64 Tick-Hashes (Lokalisierung der Divergenz)
        byte[] CommandLogDelta,         // eigene Command-Eingaben seit letztem Hash-Match
        byte[] EntityDumpFirstDiverging // optional: Binärdump der ersten divergierenden Entity
                                        // (nur Dev-/Beta-Builds; Release: deaktiviert, Größenbegrenzung)
    );
}
```

Pflicht-Tooling, kein Nice-to-have (Research §3.6): Ohne tickgenaue Lokalisierung ist Desync-Jagd bei 10 Hz × 20–35 min praktisch unmöglich. Der SimRunner-Replay des Reports ist der Standard-Debug-Pfad (D-036).

## 3. Reconnect: Snapshot + Fast-Forward

Lockstep-Reconnect ist der teuerste Nachteil des Modells (Research §4) – Lösung über zwei Mechanismen, die beide auf D-033 Regel 5 (vollständig serialisierbarer State) aufbauen:

1. **Periodische Snapshots:** Jeder Client erzeugt alle **60 s** einen vollständigen Sim-Snapshot inkl. Hash. Der Server fordert von einem designierten Slot (round-robin, oder vom stabilsten Client) die aktuellen Snapshots an und hält den neuesten hash-validierten vor. Snapshot-Größe hängt am Umfang der zerstörbaren Umgebung (R-05, Research Offene Punkte) → Messung im Alpha.
2. **Reconnect-Ablauf** (innerhalb der 60-s-Grace-Period, [./Networking.md](./Networking.md) §5):
   - Client baut neue Session auf (`Hello` mit `MatchId` + Resume-Token aus dem ursprünglichen Handshake).
   - Server sendet neuesten Snapshot (`SnapshotChunk`-Sequenz, reliable) **plus** das Command-Log aller Ticks seit Snapshot.
   - Client lädt den Snapshot in `Nova.Simulation`, dann **Fast-Forward**: Simulation der aufgelaufenen Ticks so schnell wie möglich (headless, kein Rendering – erwartete Dauer für 60 s Rückstand: wenige Sekunden bei 10 Hz; Ziel < 10 s, Messung offen).
   - Hash-Abgleich am Live-Tick; bei Match → nahtloser Wiedereinstieg, bei Mismatch → Desync-Report, Slot gilt als verloren (KI-Übernahme).
3. **Fallback:** Ist kein gültiger Snapshot verfügbar (frühe Matchphase), Re-Simulation ab Tick 0 – bei Matchdauer < ~2 min tragbar, danach nur mit Snapshot (Research §4).

```csharp
namespace Nova.Simulation.Persistence
{
    public interface ISnapshotStore
    {
        // Vollständig serialisierbarer State (D-033 Regel 5); identisches Format für
        // Savegames (SP), Reconnect-Snapshots und SimRunner-Fixtures (D-036).
        ulong WriteSnapshot(in SimState state, IBufferWriter<byte> dst);
        bool TryLoadSnapshot(ReadOnlySpan<byte> src, out SimState state, out ulong hash);
    }
}
```

## 4. Beobachter (Spectator)

- **Modell:** Beobachter sind verzögerte Lockstep-Clients (Research §4). Der Server spiegelt den kanonischen Command-Strom mit **60–120 s Delay** (Design-Vorgabe, [../gamedesign/MultiplayerModes.md](../gamedesign/MultiplayerModes.md) §6) über `ObserverFeed`; der Beobachter-Client initialisiert aus dem Matchstart-Snapshot (Tick-0-Batch bzw. erstem periodischen Snapshot) und simuliert normal hinterher.
- **Kein Anti-Cheat-Kanal:** Das Delay ist die einzige Informationsbarriere; Beobachter erhalten **keine** Live-Daten (Coach-Exploit-Ausschluss).
- **Sicht:** Observer-/Replay-Clients nutzen die FoW-Maske "alle" ([../gamedesign/FogOfWar.md](../gamedesign/FogOfWar.md)) – reine View-Einstellung, kein Einfluss auf die Sim.
- **Skalierung:** Bis zu 2 Beobachter-Slots pro Lobby (Richtwert, MultiplayerModes §6); der Server puffert den Command-Strom ringförmig (bei <5 kB/s trivial: 120 s × 6 Slots ≈ <4 MB).

## 5. Replay als Replikations-Nebenprodukt

Ein Replay ist **kein eigenes System**, sondern die Persistenz des Replikationsstroms:

```
Replay-Datei = Header (Version, MatchId, Map-Seed)
             + MatchConfig/Initialzustand (Tick-0-Batch)
             + Command-Log (alle TickBatches, chronologisch)
             + Hash-Trail (zur Integritätsprüfung beim Abspielen)
```

- **Größe:** Kilobyte bis wenige MB für 20–35 min (Research §4) – teilbar, auto-aufgezeichnet (letzte 20 Matches lokal, MultiplayerModes §6).
- **Versionsbindung:** Replays laufen nur auf der exakten Spielversion (Determinismus, MultiplayerModes §6); der `ProtocolVersion`-Header erzwingt das hart.
- **Abspielen:** Replay-Client = Simulation + freie Kamera, Zeitleiste 0,5×–8× (View-seitig; Fast-Forward nutzt denselben Pfad wie Reconnect §3).
- **Nebennutzen (ab Alpha):** KI-Test-Fixtures, Balancing-Läufe im SimRunner (D-036), Desync-Debugging (§2.3) und Savegame-Grundlage im SP – dasselbe `ISnapshotStore`-Format.

## 6. Migrationspfad MVP (SP lokal) → Beta (Relay)

| Phase | Replikations-Realität | Was sich ändert |
|---|---|---|
| **MVP (SP)** | `LocalRelay` im Prozess: Commands → Queue → Ausführung bei T+2. Hash-Ringlog und Command-Log laufen **produktiv mit** (Desync-/Replay-Tooling ab Tag 1). Sim in Float erlaubt (D-033). | – |
| **Alpha** | Koop/FFA lokal = mehrere Command-Quellen (Mensch + KI) über denselben LocalRelay. Snapshot-Format finalisiert (Savegames). Desync-Report-Pfad gegen SimRunner erprobt. | Erste echte Mehrquellen-Replikation, noch ohne Netz. |
| **Beta** | Transport-Wechsel: `LocalRelay` → UDP-Relay ([./Networking.md](./Networking.md)). **Fixed-Point-Umstellung** der Sim (fester Bestandteil der Beta-MP-Arbeiten, D-033) – ab hier Cross-Platform-Bitgenauigkeit, Hash-Vergleich live, Reconnect/Observer/Replay-Persistenz serverseitig. | Nur Transport + Mathe-Disziplin; Sim-/Command-Modell unverändert. |

Kritisch: Der MVP darf **keine** Codepfade etablieren, die State direkt manipulieren oder UnityEngine-APIs im Tick nutzen (D-033 Regeln 1–2) – jede solche Stelle wird in Beta zur Desync-Quelle. Reviews und SimRunner-CI (D-036) sichern das ab.

## Offene Punkte

- **Hash-Intervall N:** 10 Ticks (1 s) als Startwert; Abwägung Bandbreite (trivial) vs. Desync-Lokalisierungsgüte nach Alpha-Messung.
- **Snapshot-Größe und Fast-Forward-Dauer** bei 500 Einheiten + zerstörbarer Umgebung (R-05): ungemessen; Zielwerte (<10 s Fast-Forward für 60 s Rückstand, Snapshot-Upload < 5 s bei 1 Mbit/s) sind im Alpha zu verifizieren.
- **Desync-Reaktion in PvP:** Weiterspielen mit markiertem Slot vs. Remis-Angebot vs. Abbruch – UX-/Balancing-Entscheidung, Übergabe an Game Design vor Beta.
- **Snapshot-Quelle:** Round-robin über Clients erzeugt Upload-Last bei Spielern; Alternative "stabilstester Client" oder serverseitige Simulations-Instanz nur für Snapshots (Kosten!) – mit Relay-Hosting-Entscheidung klären ([./Networking.md](./Networking.md), Offene Punkte).
- **Hash-Funktion final:** xxHash64 als Vorschlag; verbindliche Festlegung erst mit Fixed-Point-Entscheidung (Phase-0-Spike), da Hash über den State-Dump die Serialisierungs-Bitfolge berührt.

## Nächste Schritte

1. [./GameState.md](./GameState.md): Command-Schema (`ICommand`, `CommandKind`-Katalog), Snapshot-Layout und Hash-Berechnungsreihenfolge definieren – direkte Vorlage für dieses Dokument.
2. Phase-0-Spike: Hash-Vergleich über 10.000 Ticks ARM↔x86 als Determinismus-Nachweis (DecisionLog, Offene Punkte).
3. Alpha: Snapshot-/Fast-Forward-Messung unter Volllast (500 Einheiten) gegen die Zielwerte in §3.
4. Game Design: PvP-Desync-Reaktion und Observer-UX (Dashboard, MultiplayerModes §6) spezifizieren lassen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Multiplayer Engineer |
