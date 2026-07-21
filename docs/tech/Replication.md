# Replication – Command-Replikation, Desync-Detektion, Reconnect, Replays

**Version:** 0.2.0 | **Status:** Entwurf (Korrekturlauf Sprint 4) | **Verantwortungsbereich:** Lead Multiplayer Engineer | **Sprint:** 4

## Zweck

Definiert, **was** zwischen den Teilnehmern eines Nova-Matches repliziert wird und **wie** Konsistenz überwacht wird: ausschließlich Commands plus Tick-Hashes (kein State-Sync), Desync-Detektion über State-Hashes mit Server-Vergleich und Report-Format, Reconnect via Snapshot + Fast-Forward, Beobachter-Modell (60–120 s Delay) und Replays als Replikations-Nebenprodukt. Abschließend der Migrationspfad vom lokalen MVP-Singleplayer zum Beta-Relay. Transport, Server-Rollen und Disconnect-Regel: [./Networking.md](./Networking.md).

Grundprinzip (D-033, Regel 1): **Commands sind die einzige State-Mutation.** Daraus folgt: Wer Seed, Initialzustand und den kanonischen Command-Strom besitzt, besitzt das gesamte Match – Replikation, Replay, Beobachter und Reconnect sind vier Ausprägungen desselben Stroms.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (5 Architekturregeln, Float im MVP, Fixed-Point in Beta), D-035 (Nova.Simulation-Assembly), D-036 (SimRunner), D-046 (MP-Trust-Anchor: Post-Match-Re-Sim, Hash-Kette, deterministische KI-Übernahme), D-049 (xxHash64 verbindlich)
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

- Nach **jedem Tick** bildet jeder Client einen Hash über den vollständigen Simulationszustand (Entities, Ressourcen, Grid-Layer inkl. Aetherium/FoW-Sim-Anteil, PRNG-State, Tick-Zähler). Hash-Funktion: **xxHash64 (verbindlich, D-049)** – schneller Nicht-Krypto-Hash mit stabiler Spezifikation; deterministische Iterationsreihenfolge über ID-indizierte Strukturen (Research §3.3). Die Breite von 64 bit ist einheitlich für alle State-Hashes im Projekt (u. a. [./Serialization.md](./Serialization.md)).
- **Übertragung gedrosselt:** `StateHash` wird alle **N = 10 Ticks (1 s)** an den Server gesendet (unreliable – Redundanz eingebaut, siehe [./Networking.md](./Networking.md) §2.1). Lokal wird der Hash jedes Ticks ins Hash-Ringlog geschrieben (Desync-Lokalisierung).

### 2.2 Vergleich und Reaktion

Der Server führt pro Tick-Intervall die Hashes aller Slots zusammen:

1. **Alle gleich:** weiter.
2. **Minderheit abweichend (nur bei ≥3 Clients anwendbar):** Desync-Bescheid (`HashMismatch`) an alle; das Match **läuft weiter** (kein harter Abbruch – Koop/KI-Kontext, D-007), der abweichende Slot wird markiert. Server fordert vom abweichenden Client automatisch einen **Desync-Report** an (§2.3).
3. **1v1 (2 Clients – kein Mehrheitsvotum möglich, Review F-03):** Bei divergenten Hashes ist aus dem Live-Vergleich kein Schuldspruch ableitbar. Beide Clients liefern Desync-Reports, das Match läuft weiter, wird aber als **strittig** markiert; bis zum Schiedsspruch gilt es als ungültig/Remis. Die **Arbitration erfolgt per Post-Match-Re-Simulation des Command-Logs** (Trust-Anchor, D-046): Eine serverseitige, on-demand gestartete `Nova.SimRunner`-Instanz (D-036) re-simuliert das Match aus dem kanonischen Command-Log und bestimmt Ergebnis-Wahrheit und divergierenden Client – Sekunden CPU pro strittigem Match, nicht im Echtzeitpfad, keine laufenden Server-Sim-Kosten (Server-Rolle: [./Networking.md](./Networking.md) §1.1).
4. **Hash des Desync-Clients + Command-Log** erlauben die exakte Reproduktion im `Nova.SimRunner` (D-036): Match bis Tick T fast-forwarden, Divergenz per Bisektion tickgenau eingrenzen. Hinweis: `FirstMismatchTick` im Report (§2.3) ist der vom Server ermittelte erste abweichende 10-Tick-Block, keine tickgenaue Client-Angabe – der Client kennt die Hashes der anderen Teilnehmer nicht (Review F-03).

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

1. **Periodische Snapshots:** Jeder Client erzeugt alle **60 s** einen vollständigen Sim-Snapshot inkl. Hash. Der Server fordert von einem designierten Slot (round-robin, oder vom stabilsten Client) die aktuellen Snapshots an und hält den neuesten hash-validierten vor. **Kompression: LZ4 als Standard** (schnell genug für den 60-s-Rhythmus); Zielgröße **1–2 MB komprimiert** (hängt am Umfang der zerstörbaren Umgebung, R-05 → Messung im Alpha). Das Format ist identisch zu Savegames ([./Savegames.md](./Savegames.md), D-033 Regel 5).
   - **Integritätsprüfung (D-046):** Ein Client-Upload-Snapshot ist per se ein Manipulationsvektor – der liefernde Client kontrolliert Snapshot *und* Hash. Der Server akzeptiert einen Reconnect-Snapshot daher nur, wenn sein Hash in der **lückenlosen Pre-Disconnect-Hash-Kette des reconnectenden Clients** verankert ist (die Tick-Hashes, die dieser Client selbst vor seinem Disconnect gemeldet hat – fälschungssicher, weil sie vom Betroffenen stammen und der Server sie bereits hält). Uploads ohne lückenlose Hash-Kette werden verworfen.
2. **Reconnect-Ablauf** (innerhalb der 60-s-Grace-Period, [./Networking.md](./Networking.md) §5):
   - Client baut neue Session auf (`Hello` mit `MatchId` + Resume-Token aus dem ursprünglichen Handshake).
   - Server sendet neuesten Snapshot (`SnapshotChunk`-Sequenz, reliable) **plus** das Command-Log aller Ticks seit Snapshot.
   - Client lädt den Snapshot in `Nova.Simulation`, dann **Fast-Forward**: Simulation der aufgelaufenen Ticks so schnell wie möglich (headless, kein Rendering – erwartete Dauer für 60 s Rückstand: wenige Sekunden bei 10 Hz; Ziel < 10 s, Messung offen). **Upload-Ziel für den Snapshot: < 10 s bei 1 Mbit/s** (≈ 1 MB LZ4-komprimierter Snapshot; Zielgröße 1–2 MB, §3).
   - Hash-Abgleich am Live-Tick; bei Match → nahtloser Wiedereinstieg, bei Mismatch → Desync-Report, Slot gilt als verloren (KI-Übernahme als deterministisches Sim-Ereignis, D-038/D-046, [./Networking.md](./Networking.md) §5).
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
- **Besiegte Spieler (Ghosting-Schutz, Review F-09):** Ausgeschiedene Spieler werden **nicht** sofort zur Vollsicht freigeschaltet – sie erhalten die Beobachter-Sicht **erst nach 120 s Delay**; bis dahin behalten sie ihre bisherige Team-Sicht. Damit gilt die Delay-Barriere auch gegen Ghosting zugunsten des eigenen Teams (externe Voice-Tools, D-029).
- **Sicht:** Observer-/Replay-Clients nutzen die FoW-Maske "alle" ([../gamedesign/FogOfWar.md](../gamedesign/FogOfWar.md)) – reine View-Einstellung, kein Einfluss auf die Sim.
- **Skalierung:** Bis zu 2 Beobachter-Slots pro Lobby (Richtwert, MultiplayerModes §6); der Server puffert den Command-Strom ringförmig (bei <5 kB/s trivial: 120 s × 6 Slots ≈ <4 MB).

## 5. Replay als Replikations-Nebenprodukt

Ein Replay ist **kein eigenes System**, sondern die Persistenz des Replikationsstroms:

```
Replay-Datei = Header (Version, MatchId, Map-Seed)
             + MatchConfig/Initialzustand (Tick-0-Batch)
             + Command-Log (alle TickBatches, chronologisch)
             + Meta-Records (serverseitig, z. B. `SetInputDelay` ab Tick T)
             + Hash-Trail (zur Integritätsprüfung beim Abspielen)
```

- **Größe:** Kilobyte bis wenige MB für 20–35 min (Research §4) – teilbar, auto-aufgezeichnet (letzte 20 Matches lokal, MultiplayerModes §6).
- **Versionsbindung:** Replays laufen nur auf der exakten Spielversion (Determinismus, MultiplayerModes §6); der `ProtocolVersion`-Header erzwingt das hart.
- **Meta-Records im Strom (Review F-11):** Serverseitige Änderungen des adaptiven Input-Delays werden als `SetInputDelay`-Meta-Record (wirksam ab Tick T) in das kanonische Command-Log geschrieben ([./Networking.md](./Networking.md) §2.3) – Replays und Desync-Forensik reproduzieren den Delay-Verlauf damit exakt.
- **Abspielen:** Replay-Client = Simulation + freie Kamera, Zeitleiste 0,5×–8× (View-seitig; Fast-Forward nutzt denselben Pfad wie Reconnect §3).
- **Nebennutzen (ab Alpha):** KI-Test-Fixtures, Balancing-Läufe im SimRunner (D-036), Desync-Debugging (§2.3) und Savegame-Grundlage im SP – dasselbe `ISnapshotStore`-Format.

## 6. Migrationspfad MVP (SP lokal) → Beta (Relay)

| Phase | Replikations-Realität | Was sich ändert |
|---|---|---|
| **MVP (SP)** | `LocalRelay` im Prozess: Commands → Queue → Ausführung bei T+2. Hash-Ringlog und Command-Log laufen **produktiv mit** (Desync-/Replay-Tooling ab Tag 1). Sim in Float erlaubt (D-033). | – |
| **Alpha** | Koop/FFA lokal = mehrere Command-Quellen (Mensch + KI) über denselben LocalRelay. Snapshot-Format finalisiert (Savegames). Desync-Report-Pfad gegen SimRunner erprobt. | Erste echte Mehrquellen-Replikation, noch ohne Netz. |
| **Beta** | Transport-Wechsel: `LocalRelay` → UDP-Relay ([./Networking.md](./Networking.md)). **Fixed-Point-Umstellung** der Sim (fester Bestandteil der Beta-MP-Arbeiten, D-033) – ab hier Cross-Platform-Bitgenauigkeit, Hash-Vergleich live, Reconnect/Observer/Replay-Persistenz serverseitig. | Transport + **Fixed-Point-Migration als eigenes Arbeitspaket** (Review F-04: Steering-Mathe, Call-Sites, Fixture-Neuaufzeichnung – kein bloßer Typ-Tausch); Sim-/Command-Modell unverändert. |

**Phase-0-Spike-Scope (erweitert, Review F-04 / DecisionLog, Offene Punkte):** Der Spike validiert nicht nur den Rechenkern (Add/Mul/Div), sondern zusätzlich:

1. den **Fixed-Point-Pfad für ORCA-/Flow-Field-Steering** (geometrische Float-Algorithmen, D-034 – bitgenauer Port ist ein Eigenprojekt),
2. die **Bibliothekswahl** für Fixed-Point-Mathe inkl. deterministischer Ersatzfunktionen für `sqrt`, `sin/cos`, `atan2`,
3. die Regel **„keine nackten floats im GameState"** – State-Felder nur als SimVec/SimFixed-Typen; float-Direktfelder in [./GameState.md](./GameState.md) sind zu beseitigen und per Review/CI verboten.

Zusätzlich ist die **Neuaufzeichnung aller Golden-Master-Fixtures und SimRunner-Baselines** nach der Umstellung als eigenes Beta-Arbeitspaket einzuplanen.

Kritisch: Der MVP darf **keine** Codepfade etablieren, die State direkt manipulieren oder UnityEngine-APIs im Tick nutzen (D-033 Regeln 1–2) – jede solche Stelle wird in Beta zur Desync-Quelle. Reviews und SimRunner-CI (D-036) sichern das ab.

## Offene Punkte

- **Hash-Intervall N:** 10 Ticks (1 s) als Startwert; Abwägung Bandbreite (trivial) vs. Desync-Lokalisierungsgüte nach Alpha-Messung.
- **Snapshot-Größe und Fast-Forward-Dauer** bei 500 Einheiten + zerstörbarer Umgebung (R-05): ungemessen; Zielwerte (< 10 s Fast-Forward für 60 s Rückstand; Snapshot-Upload **< 10 s bei 1 Mbit/s** bei Zielgröße 1–2 MB LZ4-komprimiert, §3) sind im Alpha zu verifizieren.
- **Desync-UX in PvP:** Die Arbitration ist entschieden (Post-Match-Re-Simulation, D-046, §2.2); offen bleibt nur die UX-Seite – Anzeige des „strittig"-Status und Remis-/Wertungs-Handling bis zum Re-Sim-Bescheid. Übergabe an Game Design vor Beta.
- **Snapshot-Quelle (Last-Frage):** Die Integritätsfrage ist entschieden (Prüfung gegen die Pre-Disconnect-Hash-Kette, D-046, §3). Offen bleibt, wer die Upload-Last trägt: round-robin über Clients vs. stabilstester Client – mit Relay-Hosting-Entscheidung klären ([./Networking.md](./Networking.md), Offene Punkte).

## Nächste Schritte

1. [./GameState.md](./GameState.md): Command-Schema (`ICommand`, `CommandKind`-Katalog), Snapshot-Layout und Hash-Berechnungsreihenfolge definieren – direkte Vorlage für dieses Dokument.
2. Phase-0-Spike: Hash-Vergleich über 10.000 Ticks ARM↔x86 als Determinismus-Nachweis – Scope um ORCA-/Flow-Field-Steering-Mathe und Bibliothekswahl erweitert (§6, Review F-04).
3. Alpha: Snapshot-/Fast-Forward-Messung unter Volllast (500 Einheiten) gegen die Zielwerte in §3.
4. Game Design: PvP-Desync-Reaktion und Observer-UX (Dashboard, MultiplayerModes §6) spezifizieren lassen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Multiplayer Engineer |
| 0.2.0 | 2026-07-21 | Korrekturlauf Sprint 4 (D-043–D-052, Review-Findings) | Lead Multiplayer Engineer |
