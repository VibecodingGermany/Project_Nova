# Networking – Zielarchitektur Lockstep über autoritativem Command-Relay

**Version:** 0.1.1 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Multiplayer Engineer | **Sprint:** 3

## Zweck

Definiert die Netzwerk-Zielarchitektur von Project Nova gemäß **D-033**: deterministisches Lockstep über einem autoritativen Command-Relay-Server (Eigenbau-UDP primär, Photon Quantum 3 als dokumentierter Fallback). Festgelegt werden Server-Rollen, Protokoll-Design, Lobby-/Match-Flow, Disconnect-Regel (final), Host-Migration-Bewertung, NAT/Traversal, Regions-/Ping-Anforderungen und die Maphack-Lage. Was konkret über die Leitung wandert (Commands, Hashes, Snapshots), spezifiziert [./Replication.md](./Replication.md); das Simulationsmodell selbst liegt in [./GameState.md](./GameState.md) (geplant, D-033/D-035).

Geltungsbereich: **MVP = Singleplayer als "lokaler Server"** (kein Netzwerk, aber identische Command-Pipeline); **Beta = online PvP/Koop über Relay** (D-018, D-025). Dieses Dokument beschreibt die Beta-Zielarchitektur so, dass der MVP-Codepfad strukturell identisch bleibt – MP wird ein Transport-Thema, kein Rewrite (D-033, Begründung).

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (Sim-/MP-Modell), D-006 (Unity 6.3), D-018/D-025 (Modus-Phasen), D-029 (kein Voice-Chat), D-035 (Nova.Simulation-Assembly)
- [../research/Multiplayer_Simulation.md](../research/Multiplayer_Simulation.md) – Modellvergleich, Bandbreitenrechnung, Determinismus-Fallstricke, §6 Umsetzungsoptionen
- [../gamedesign/MultiplayerModes.md](../gamedesign/MultiplayerModes.md) – Lobby-/Teamregeln (§4), Beobachter/Replays (§6), MatchSettings
- [../gamedesign/VictoryConditions.md](../gamedesign/VictoryConditions.md) – Match-Ergebnis-Regeln, technischer Abbruch (§ Konflikt, siehe Offene Punkte)
- [./Replication.md](./Replication.md) – Replikationsumfang, Desync-Detektion, Reconnect, Replays
- [./GameState.md](./GameState.md) – geplant: Command-Modell, Tick-Loop, Serialisierung (D-033-Regeln 1–5)

## 1. Zielarchitektur (ab Beta)

```
┌─────────┐  Commands (zu Tick T+2)   ┌──────────────────┐   Commands (zu Tick T+2)  ┌─────────┐
│ Client A│ ────────────────────────▶ │  Command-Relay   │ ◀──────────────────────── │ Client B│
│ (Sim)   │ ◀──────────────────────── │     -Server      │ ────────────────────────▶ │ (Sim)   │
└─────────┘  Tick-Batches + Hash-Acks └──────────────────┘   Tick-Batches + Hash-Acks └─────────┘
                                            │
                                     ┌──────┴──────┐
                                     │ Match-Record│ (Command-Log → Replay,
                                     │ + Hash-Log  │  Desync-Reports, Observer-Feed)
                                     └─────────────┘
```

**Jeder Client simuliert das komplette Match lokal und deterministisch.** Über das Netz wandern ausschließlich Spieler-Commands und Validierungs-Hashes – kein State-Sync (D-033; Bandbreitenbegründung Research §2.5: <5 kB/s pro Spieler statt 200–300 kB/s).

### 1.1 Server-Rollen (Autorität)

Der Relay-Server ist **autoritativ über Befehle, Takt und Ergebnis** (TPD §9, aufgelöst in Research §6/§7):

| Rolle | Beschreibung |
|---|---|
| Befehls-Autorität | Nimmt Commands entgegen, validiert (Slot-Zugehörigkeit, Tick-Fenster, Format, Rate-Limits), verwirft Ungültiges, reiht sie in das kanonische Tick-Batch ein. Clients können keine gegenseitigen Commands fälschen. |
| Taktgeber | Vergibt die globale Tick-Nummerierung und das Verarbeitungsfenster; das Tick-Batch des Servers ist die einzige Wahrheit darüber, welche Commands in welchem Tick ausgeführt werden. |
| Hash-Validierung | Sammelt State-Hashes pro Client und Tick-Intervall, vergleicht, erkennt Desyncs (Details: [./Replication.md](./Replication.md) §2). |
| Match-Ergebnis | Führt das Command-Log als Beweismittel; bestätigt das per Simulation ermittelte Ergebnis und schließt das Match ab (Replay-Persistenz). |
| Observer-/Replay-Verteilung | Verteilt den verzögerten Command-Strom an Beobachter ([../gamedesign/MultiplayerModes.md](../gamedesign/MultiplayerModes.md) §6). |

Der Server simuliert **nicht** selbst (kein Gameplay-State) – das hält Hosting-Kosten minimal (D-007: MP ist Feature, nicht Fundament) und vermeidet eine zweite Sim-Implementierung als Desync-Quelle.

### 1.2 MVP-Ausprägung: lokaler Server

Im Singleplayer läuft dieselbe Pipeline gegen einen in-prozess `LocalRelay` (Loopback-Implementierung von `IRelayClient`/`IRelayServer`): Commands werden in eine Queue gestellt, 2 Ticks später ausgeführt. Damit sind Input-Delay-Verhalten, Command-Serialisierung und Hash-Logging ab MVP produktiv – die Online-Infrastruktur ersetzt später nur den Transport.

## 2. Eigenbau-UDP-Relay (Primärpfad)

### 2.1 Transport: Reliable-Ordered-Layer über UDP

Begründung Eigenbau: Das Nachrichtenvolumen ist winzig und homogen (Command-Batches, Hashes), die Anforderungen speziell (Tick-Takt, keine Head-of-Line-Blockade bei Positions-unabhängigen Acks), und der Sim-Kern ist ohnehin Pflicht (Research §6, "Favorit"). TCP ist ausgeschlossen (Head-of-Line-Blocking würde Tick-Batches stauen). Auf UDP wird ein schmaler Zuverlässigkeits-Layer gelegt:

- **Reliable-Ordered nur für Command- und Kontroll-Kanäle** (Sequenznummer + Ack-Bitmap, Retransmit nach 2×RTT oder spätestens 150 ms).
- **Unreliable für Hash-/Heartbeat-Kanal** (Hashes sind redundant, alle N Ticks neu – Verlust egal).
- Paketgröße ≤ 1.200 Byte (unter typischer MTU, kein IP-Fragmenting).
- Verbindung: session-tokenbasiert, keep-alive 1 Hz, Timeout 10 s ohne Paket = "verloren-Verdacht", 30 s = Disconnect-Ereignis (§5).

### 2.2 Protokoll-Design (Skizze)

```csharp
namespace Nova.Net
{
    // Wire-Header: klein, versioniert, little-endian
    public enum PacketType : byte
    {
        Hello, HelloAck,            // Handshake
        CommandSubmit,              // Client → Server: eigene Commands für Tick T+InputDelay
        TickBatch,                  // Server → Clients: kanonische Commands eines Ticks
        StateHash,                  // Client → Server: Hash nach Tick T (unreliable)
        HashMismatch,               // Server → Clients: Desync-Bescheid
        Heartbeat,                  // beidseitig, 1 Hz
        SnapshotRequest, SnapshotChunk, SnapshotDone, // Reconnect (siehe Replication.md §3)
        MatchEnd,                   // Server → Clients: finales Ergebnis + Replay-Ref
        ObserverJoin, ObserverFeed  // verzögerter Strom für Beobachter
    }

    public readonly record struct PacketHeader(
        byte ProtocolVersion,       // hart an Spielversion gebunden (Replay-Kompatibilität)
        PacketType Type,
        uint SessionId,             // serverseitig beim Handshake vergeben
        ushort Sequence,            // pro Richtung, für Reliable-Layer
        ushort AckBits);            // Bitmap der letzten 16 empfangenen Sequenzen

    public readonly record struct TickBatch(
        uint Tick,                  // absolute Sim-Tick-Nummer (10 Hz, D-033)
        byte PlayerMask,            // welche Slots in diesem Batch Commands haben
        byte[] CommandPayload);     // serialisierte Nova.Simulation-Commands, leer = Leertick
}
```

### 2.3 Tick-Vorausplanung (Input-Delay)

- **Sim-Tick: 10 Hz** (D-033). Commands werden **2 Ticks vorausgeplant** (`InputDelay = 2`): Ein Command, den der Spieler während Tick T eingibt, wird im Tick-Batch **T+2** ausgeführt → 200 ms Befehls-Delay, RTS-üblich und akzeptiert (Research §2.4).
- Clients senden ihre Commands für T+2 laufend; der Server schließt das Fenster für T+2, wenn seine Uhr T erreicht, und broadcastet das Batch (fehlende Spieler = Leertick). Spieler, deren Commands verspätet eintreffen (Ping > Fenster), erzeugen **Stall**: Das Match wartet bis zu `MaxStallTicks` (Vorschlag 5 Ticks = 500 ms), dann gilt der Slot für diesen Tick als leer und der Vorfall zählt in die Disconnect-Schwelle (§5).
- **Adaptiver Input-Delay:** Der Server darf `InputDelay` sitzungsweit auf 3–6 Ticks erhöhen, wenn ein Teilnehmer dauerhaft >100 ms RTT hat (einheitlich für alle, Determinismus bleibt gewahrt, da Delay Teil des Initialzustands ist).

## 3. Fallback: Photon Quantum 3

Primärpfad bleibt Eigenbau (D-033). Quantum 3 wird **genau dann** aktiviert, wenn eines dieser Kriterien eintritt:

1. **Phase-0-Spike scheitert:** Fixed-Point-Determinismus ARM↔x86 nicht bitgenau erreichbar und nicht mit vertretbarem Aufwand behebbar (DecisionLog, Offene Punkte).
2. **Budget-Bruch:** Abgeschätzter Fertigstellungsaufwand Eigenbau-Relay + Determinismus-Tooling > 1,5× der Quantum-Integration in der Beta-Planung.
3. **Zeitplan:** Beta-MP-Meilenstein wäre durch Eigenbau-Transport um mehr als einen Sprint gefährdet.

Hürden beachten: Gameplay-Code in Quantum-DSL/ECS, Vendor-Lock-in, Konflikt mit der SO-Datenarchitektur (D-035) und CCU-Kosten ab 100 CCU (Research §6). Die 5 Architekturregeln aus D-033 bleiben in jedem Fall gültig – sie halten den Quantum-Umstieg möglich, ohne den Sim-Kern wegzuwerfen.

## 4. Lobby- und Match-Flow

Fachliche Regeln: [../gamedesign/MultiplayerModes.md](../gamedesign/MultiplayerModes.md) §4 (Host-Lobby, max. 6 Slots, Slot-Optionen, Ready-Check, Text-Chat; kein Voice-Chat, D-029). Technischer Ablauf:

1. **Lobby (serverseitig, nicht im Lockstep):** Der Relay-Server hostet die Lobby-Rooms; der "Host" der Design-Dokumente ist nur eine **UI-Rolle** (erster Beitretender) mit Rechten für Slot-/Map-/MatchSettings-Wahl – keine technische Autorität. `MatchSettings`-SO wird bei Matchstart in den serialisierten Initialzustand überführt.
2. **Matchstart:** Server friert Slots + Settings ein, erzeugt `MatchConfig` (Map-Seed, Slot→Fraktion/Team, Doktrinenwahl vgl. [../gamedesign/CommanderSystem.md](../gamedesign/CommanderSystem.md), InputDelay), broadcastet sie als Tick-0-Batch. Alle Clients initialisieren `Nova.Simulation` identisch daraus.
3. **Lauf:** §2.3. KI-Slots laufen **auf dem Server? Nein** – KI ist command-erzeugend wie ein Spieler; im Relay-Modell läuft jede KI-Instanz auf genau einem fest zugewiesenen Client/Prozess (bei reinem PvP-Mix: beim Slot-Inhaber bzw. round-robin verteilt). Ihre Commands durchlaufen dieselbe Validierung. (Zuordnungsregel: Offener Punkt §8.)
4. **Ende:** Ergebnis aus der lokalen Simulation; Clients melden Ergebnis-Hash, Server bestätigt und persistiert Match-Record (Replay, [./Replication.md](./Replication.md) §5).

## 5. Disconnect-Regel (FINAL)

**Entscheidung: KI-Übernahme nach Grace-Period – kein Pause-Vote, keine sofortige Auto-Niederlage.**

- **Grace-Period 60 s:** Ab Disconnect-Ereignis (§2.1) sendet der Slot Leerticks; das Match läuft **unpausiert** weiter. Der getrennte Spieler kann per Reconnect (Snapshot + Fast-Forward, [./Replication.md](./Replication.md) §3) wieder einsteigen. UI zeigt den Ausfall allen Spielern an.
- **Nach 60 s ohne Reconnect:** Eine KI-Instanz (Difficulty = Normal, fest, kein Vote) übernimmt den Slot vollständig und spielt zu Ende. Der ursprüngliche Spieler kann danach **nicht** mehr zurückkehren (Snapshot-Auslieferung an "Fremde" wäre ein Maphack-Vektor).
- **Wertung:** Wird die übernommene Fraktion vernichtet, gilt der getrennte Spieler als besiegt; gewinnt sie, wird das Match für ihn als "unvollständig" ohne Sieg gewertet (kein Farming über Disconnect).

**Begründung (Alternativabwägung):**
- *Pause-Vote verworfen:* missbrauchbar (Taktik-Pausen, Griefing-Verweigerung), friert 20–35-min-Matches ein, benachteiligt disziplinierte Spieler; im Lockstep trivial als DoS nutzbar.
- *Auto-Niederlage verworfen:* bestraft flüchtige Netzprobleme mit Matchverlust und ruiniert 2v2-/Koop-Matches für den Mitspieler (Team-Asymmetrie); Wiedereinstieg wäre unmöglich, obwohl die Reconnect-Technik ohnehin gebaut wird.
- *KI-Übernahme* hält das Match für alle verbleibenden Spieler spielbar, nutzt die ohnehin existierende KI-Schicht (Command-only, erzeugt ausschließlich Commands wie ein menschlicher Slot) und das Reconnect-System, und kostet keinen zusätzlichen Netzwerk-Pfad.

**Konflikt (aufgelöst):** [../gamedesign/VictoryConditions.md](../gamedesign/VictoryConditions.md) definierte ursprünglich "Verbindungsverlust > 120 s = Niederlage". Diese Regel ist durch die finale Festlegung **ersetzt** (KI-Übernahme statt Auto-Niederlage, D-038); die Angleichung von VictoryConditions.md und MultiplayerModes.md §3.2 ist erfolgt (beide verweisen auf dieses Dokument als führend).

## 6. Host-Migration-Bewertung

**Im Relay-Modell entfällt klassische Host-Migration.** Der autoritative Knoten ist der dedizierte Relay-Server, kein Spieler-Client; ein Client-Ausfall (auch des Lobby-"Hosts") berührt weder Takt noch Command-Kanonizität. Verbleibende Fälle:

- **Lobby-Host-Wechsel (pre-match):** UI-Rolle, wird vom Server einfach dem nächsten Client zugewiesen – keine Migration von Spielzustand nötig. Der in MultiplayerModes.md §4 offene Punkt "techn. Machbarkeit im Lockstep-Relay" ist damit beantwortet: trivial, da kein Host-State existiert.
- **Server-Ausfall mid-match:** nicht abgedeckt (Match bricht ab, Command-Log bis zum Ausfall liegt serverseitig vor → technisch wäre Fortsetzung via Snapshot + neuer Session denkbar, wird **nicht** verplant; akzeptiertes Restrisiko, Dokumentation in Offene Punkte).

## 7. NAT/Traversal, Regionen, Ping

- **NAT/Traversal:** Im Relay-Modell bauen alle Clients nur **ausgehende** UDP-Verbindungen zum Server auf – kein P2P, kein STUN/TURN, keine Port-Forwarding-Problematik. Symmetrische NATs sind unproblematisch. Firewall-Fallback: Relay zusätzlich auf Port 443/UDP erreichbar machen (Beta-Ops-Entscheidung).
- **Regionen (Beta):** Start mit **EU-Zentral** (Primärzielgruppe H1, D-007); Region wird der Session als Matchmaking-/Lobby-Parameter mitgegeben. US-East als zweite Region erst nach Beta-Telemetry.
- **Ping-Anforderungen:** Weiches Limit **RTT ≤ 150 ms** für gutes Spielgefühl (2-Tick-Fenster = 200 ms); darüber greift der adaptive Input-Delay (§2.3) bis max. 6 Ticks (600 ms), darüber gilt der Spieler als stall-gefährdet (Disconnect-Schwelle). Lobby zeigt RTT pro Slot an.

## 8. Maphack-Lage

Gemäß D-033 **akzeptiert bis Ranked-Re-Evaluierung**: Jeder Client besitzt den vollständigen Simulationszustand (Lockstep-Struktur), Fog-of-War ist rein clientseitig – clientseitige FoW-Aufhebung ist nicht verhinderbar (SC2-Präzedenz). Gegenmaßnahmen heute: Manipulations-Cheats erzeugen Desyncs und sind per Hash-Validierung + Replay nachweisbar (§1.1, [./Replication.md](./Replication.md) §2). Für Ranked (unter Vorbehalt, D-018) bleibt serverseitiges Sichtgrid-Filtering als Re-Evaluationspunkt offen (Research §5).

## Offene Punkte

- **Konflikt VictoryConditions.md (aufgelöst, D-038):** Die frühere Regel "Verbindungsverlust > 120 s = Niederlage" widersprach der finalen KI-Übernahme-Regel (§5) – Angleichung erfolgt (VictoryConditions.md 0.3.1, MultiplayerModes.md 0.3.2; dieses Dokument führend).
- **KI-Slot-Ausführungsort im Relay-Match** (§4.3): feste Zuordnung pro Slot vs. Server-seitige KI-Prozesse (erhöht Hosting-Kosten). Zu entscheiden mit Beta-Infrastrukturplanung.
- **Server-Ausfall mid-match:** Fortsetzungs-Szenario bewusst nicht verplant; Restrisiko für lange Matches (20–35 min) dokumentieren.
- **Relay-Backend-Technologie:** Implementierungssprache/-Hosting des Relay-Servers (z. B. .NET auf Basis von `Nova.Simulation`-nahen Serializern) ist Sprint-6-/Beta-Thema; Research nennt Backend-Dienst explizit orthogonal.
- **Tick-Rate 10 Hz unter Last:** Endbestätigung hängt am Phase-0-Spike (Sim-Kosten bei 500 Einheiten); bei Überschreitung ist 8 Hz mit Input-Delay 2 zu prüfen – Abhängigkeit zu [./GameState.md](./GameState.md).
- **Verschlüsselung/Integrität des UDP-Stroms** (DTLS vs. eigenes HMAC-Tagging): vor Beta-Extern-Tests festzulegen.

## Nächste Schritte

1. ~~Angleichung von [../gamedesign/VictoryConditions.md](../gamedesign/VictoryConditions.md) (technischer Abbruch) und [../gamedesign/MultiplayerModes.md](../gamedesign/MultiplayerModes.md) §3.2~~ – **erledigt (D-038, 2026-07-21)**; die Host-Migration-Frage aus MultiplayerModes.md §4 ist oben (§6) beantwortet.
2. Phase-0-Spike: Fixed-Point-Determinismus ARM↔x86 validieren (Fallback-Kriterium §3, DecisionLog Offene Punkte).
3. [./GameState.md](./GameState.md): Command-Schema und Tick-Loop so definieren, dass `TickBatch`/Input-Delay direkt darauf aufsetzen.
4. Sprint 6 (Produktionsplanung): Relay-Server-Hosting, Regionen und Kostenrahmen für Beta schätzen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Multiplayer Engineer |
| 0.1.1 | 2026-07-21 | Konflikt-Verweise auf VictoryConditions.md/MultiplayerModes.md als aufgelöst markiert (D-038-Angleichung erfolgt) | Lead Technical Director |
