# Multiplayer-Simulationsmodelle für RTS (Q-013)

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Multiplayer Engineer | **Sprint:** 1

## Zweck

Dieses Dokument beantwortet die Open Question **Q-013** (Simulations- & Multiplayer-Modell) als Entscheidungsvorlage für Sprint 3. Es vergleicht deterministisches Lockstep, server-autoritativen State-Sync und Hybrid-/Rollback-Ansätze projektbezogen: 100–500+ Einheiten, 60 FPS auf Desktop (Windows/macOS), Entwicklung auf macOS Apple Silicon, Datengetriebenheit via ScriptableObjects, MVP-Disziplin (SP-Kern zuerst) bei langfristig autoritativer Serverarchitektur (TPD §9). Kernfrage: Wie muss die Simulationsarchitektur **jetzt** gelegt werden, damit Multiplayer später **ohne Rewrite** möglich ist?

## Abhängigkeiten

- [KnowledgeBase.md](../analysis/KnowledgeBase.md) – projektweiter Faktenraum (TPD §9, §15; Zielplattformen; Einheitengrößenordnung)
- [OpenQuestions.md](../production/OpenQuestions.md) – Q-013 (diese Frage), Q-014 (Pathfinding), Q-015 (ECS/DOTS)
- TPD §9 (Multiplayer-Architektur: langfristig autoritativer Server), TPD §15 („deterministische oder kontrollierte Simulation")
- Risiko R-02 („Multiplayer-Architektur zu spät entschieden") in [RiskAnalysis.md](../production/RiskAnalysis.md)

## 1. Ausgangslage und Projektzwänge

- **Skalierung:** 100–500+ gleichzeitige Einheiten schließen naive State-Replikation aus – der RTS-Genrestandard ist seit *Age of Empires* aus genau diesem Grund die synchrone Simulation mit Befehlssynchronisation ([1500 Archers on a 28.8 – Terrano/Bettner](https://www.gamedeveloper.com/programming/1500-archers-on-a-28-8-network-programming-in-age-of-empires-and-beyond)).
- **Sequenz:** MP kommt erst nach stabilem SP-Kern. Die Simulationsarchitektur wird aber **jetzt** geschrieben; ein nicht-determinismusfähiger Gameplay-Kern würde MP später einen kompletten Rewrite des Gameplay-Codes kosten (R-02).
- **TPD-Spannung:** TPD §9 empfiehlt „autoritative Server", meint damit aber Befehlsvalidierung, Positionen, Schaden, Match-Zustand – das ist mit Lockstep vereinbar, wenn der **Server autoritativ über den Input-Stream** waltet (siehe §6).
- **Plattformfalle:** Entwicklung auf macOS **ARM** (Apple Silicon), Zielgruppe überwiegend Windows **x86**. Cross-Architektur-Gleitkomma-Determinismus ist der härteste Fallstrick des Projekts (§3).

## 2. Die drei Modelle im Vergleich

### 2.1 Deterministisches Lockstep (Input-Sync)

Alle Clients simulieren identisch; über das Netz wandern nur **Spielerbefehle** (plus Seed und Initialzustand). Befehle werden pro Simulations-Tick mit kurzem Input-Delay (typisch 2–6 Ticks ≈ 67–200 ms) synchron ausgeführt. Referenzen: *Age of Empires I/II*, *StarCraft I/II*, *Warcraft III*, *Total War* ([samu.space – Age of Empires and Networking](https://samu.space/Age-of-Empires-and-networking/), [Lockstep als RTS-Standard](https://www.socratopia.app/library/math-for-game-devs-en/chapter-30)).

### 2.2 Server-autoritativer State-Sync

Der Server simuliert und repliziert Zustand (Positionen, HP, Ressourcen) an Clients; Clients senden Befehle und interpolieren. Standard bei Shootern/MMOs; in Unity die Domäne von Netcode for GameObjects, Mirror, Photon Fusion und Netcode for Entities ([Framework-Überblick 2025](https://uversedigital.com/blog/multiplayer-framework-for-your-game/)).

### 2.3 Hybrid / Rollback

Deterministische Simulation, aber Clients **prognostizieren** fremde Inputs sofort und rollen bei Abweichung zurück (GGPO-Prinzip, Fighting-Game-Standard). *Stormgate* (Frost Giant) ist der erste nennenswerte RTS mit Rollback-Netcode ([PC Gamer, 2022](https://www.pcgamer.com/an-upcoming-rts-will-incorporate-the-rollback-tech-that-took-fighting-games-by-storm/)); kommerziell verfügbar als fertige Engine via **Photon Quantum 3** (deterministische ECS-Engine mit Input-Prediction/Rollback, Unity Verified Solution, bis 100 CCU frei) ([Photon-Blog, 2024](https://blog.photonengine.com/the-evolution-of-deterministic-multiplayer-photon-quantum-now-a-unity-verified-solution/)).

### 2.4 Vergleichstabelle (projektbezogen)

| Kriterium | Lockstep | State-Sync (server-autoritativ) | Hybrid/Rollback |
|---|---|---|---|
| Bandbreite bei 500 Einheiten | **Sehr gering:** nur Befehle; AoE lief mit 1500 Einheiten auf 28,8-kbit/s-Modems. Einschätzung: <5 kB/s pro Spieler | **Hoch:** 500 Einheiten × ~20–30 B × 20 Hz ≈ 200–300 kB/s pro Client (Einschätzung); Interest Management hilft kaum, da RTS-Spieler die ganze Karte sehen können | Wie Lockstep (nur Inputs), plus etwas Overhead |
| Unity-Support out-of-the-box | **Keiner** – Unity bietet laut Unity-Mitarbeiter (Juli 2025) keine Lockstep-Bibliothek; Eigenbau oder Quantum nötig ([Unity Discussions](https://discussions.unity.com/t/netcode-for-entities-for-rts/1660672)) | **Sehr gut:** NGO, Mirror, Fusion, Netcode for Entities (>5.000 Entities mit Relevancy getestet – aber eben mit Sichtbarkeits-Culling, das ein RTS nicht will) ([Unity Discussions](https://discussions.unity.com/t/netcode-for-entities-for-rts/1660672)) | Gut via Photon Quantum; sonst Eigenbau |
| Determinismus-Zwang | **Absolut, bitgenau, cross-platform** – härteste Anforderung | Keiner – großer praktischer Vorteil | Absolut, wie Lockstep, zusätzlich muss Resimulation (Rollback) in ms-Budget passen |
| Cheating-Resistenz | Schwach gegen Informations-Cheats (Map-Hacks: jeder Client kennt den vollen State); stark gegen Manipulation (Desync = sofort erkennbar, Validierung möglich) | **Stark:** Server kann Fog-of-War-Daten vorenthalten und Befehle validieren | Wie Lockstep |
| Replays / Beobachter | **Natürlich:** Seed + Befehlsstrom = Replay; winzige Dateien, Observer = verzögerter Client | Aufwendig: Snapshots oder Event-Log nötig | Natürlich (wie Lockstep) |
| Reconnect | **Schwer:** Snapshot + Fast-Forward oder komplette Re-Simulation ab Tick 0 nötig | **Einfach:** Server sendet aktuellen Snapshot | Schwer (wie Lockstep) |
| Input-Gefühl | Spürbares Befehls-Delay (67–200 ms, RTS-üblich und akzeptiert) | Minimal (Client-Prediction) | Minimal, aber Risiko sichtbarer „Jitter"-Korrekturen bei vielen Einheiten – genau dafür wurde Stormgate früh kritisiert ([TL.net-Community-Berichte](https://tl.net/forum/games/594282-stormgate-frost-giant-megathread?page=101)) |
| MVP-Tauglichkeit (SP zuerst) | Sehr gut: SP = Lockstep mit einem lokalen Client | Gut, aber Versuchung, Unity-Physik/Floats direkt zu nutzen → MP-Falle | Überdimensioniert für MVP |

### 2.5 Bandbreiten-Beispielrechnung bei 500 Einheiten (Einschätzung)

Zahlen sind Größenordnungen zur Einordnung, keine Messwerte:

- **Lockstep / Rollback:** Ein Befehl (z. B. „Einheitengruppe {IDs} → Angriff auf {Ziel}") kostet typisch 10–40 Byte. Selbst bei 300 APM (5 Befehle/s) und 20 Ticks/s mit Takt-Overhead bleibt der Strom pro Spieler im Bereich **weniger kB/s**; ein 8-Spieler-Match liegt in Summe unterhalb dessen, was ein 28,8-kbit/s-Modem der AoE-Ära schon trug ([1500 Archers](https://www.gamedeveloper.com/programming/1500-archers-on-a-28-8-network-programming-in-age-of-empires-and-beyond)). Entscheidend: Das Volumen skaliert mit **Spielerzahl und APM**, nicht mit Einheitenzahl.
- **State-Sync:** 500 Einheiten × (Position 12 B + Rotation/Status ~8–18 B) × 20 Hz ≈ **200–300 kB/s Downstream pro Client** – vor Delta-Kompression, aber auch bevor Projektile, VFX-Events, Gebäude und Fog-of-War-Updates dazukommen. Da ein RTS-Spieler jederzeit die ganze Karte einsehen kann, ist das klassische Gegenmittel (Relevancy/Interest Management, mit dem Netcode for Entities >5.000 Entities testet) hier weitgehend wirkungslos ([Unity Discussions](https://discussions.unity.com/t/netcode-for-entities-for-rts/1660672)). Bei 8 Spielern muss der Server ~1,6–2,4 MB/s aggregiert ausliefern – machbar, aber teuer und ohne jede Not, wenn das Spiel dieselbe Information als Befehlsstrom in Promille der Größe liefern kann.

## 3. Determinismus in Unity: Anforderungen und Fallstricke

Lockstep/Rollback steht und fällt mit bitgenauer Deterministik über **Windows-x86-Clients und macOS-ARM-Entwicklungsmaschinen** hinweg. Konkrete Fallstricke für Project Nova:

1. **Floating-Point:** IEEE-754-Operationen sind pro Operation definiert, aber Compiler-Optimierungen, FMA-Kontraktion, SIMD-Pfade und Transzendentale (`Mathf.Sin`, `Pow`) unterscheiden sich zwischen Plattformen und sogar Mono vs. IL2CPP. Faustregel der Praxis: floats in der synchronisierten Simulation vermeiden; **Fixed-Point** (z. B. Q32.32) oder Soft-Floats verwenden ([State of Determinism in Unity](https://discussions.unity.com/t/state-of-determinism-in-unity/867770), [Kimbatt/unity-deterministic-physics](https://github.com/Kimbatt/unity-deterministic-physics)).
2. **Unity-Physik (PhysX) und DOTS-Physik:** nicht bitgenau cross-platform. Unity selbst: DOTS Physics ist „deterministic enough for state syncing", **nicht** bit-by-bit cross-platform ([Unity Discussions](https://discussions.unity.com/t/netcode-for-entities-for-rts/1660672)). Konsequenz: Gameplay-relevante Kollision/Bewegung gehört in eigenen, kontrollierten Code – Unity-Physik nur visuell/dekorativ.
3. **Iterationsreihenfolge:** `Dictionary<TKey,TValue>`-Enumeration, `GetHashCode()`, parallele Jobs ohne feste Reihenfolge, `FindObjectsOfType`-Reihenfolge → Desync-Quellen. Im Tick-Pfad nur sortierte/ID-indizierte Datenstrukturen.
4. **RNG:** ein eigener seedbarer PRNG (z. B. xorshift); niemals `UnityEngine.Random` oder `System.Random` in der Simulation.
5. **Zeit:** fester Simulations-Timestep (z. B. 10–20 Ticks/s, entkoppelt vom Rendering); `Time.deltaTime`/`Time.time` im Simulationspfad verboten.
6. **Desync-Früherkennung:** State-Hash (Checksum) pro N Ticks über alle Clients vergleichen; Logging, das den ersten divergierenden Tick und Entity findet, ist Pflicht-Tooling, kein Nice-to-have ([Bugnet – State Desync in Deterministic Lockstep](https://bugnet.io/blog/how-to-fix-state-desync-in-deterministic-lockstep)).

**Projektkritisch:** Q-013 hängt direkt an Q-014 (Pathfinding muss deterministisch sein – Flow-Fields sind dafür gut geeignet) und Q-015 (bei ECS/DOTS: Job-Scheduling-Reihenfolge kontrollieren; DOTS ersetzt die Determinismus-Disziplin nicht).

## 4. Replay-System, Beobachtermodus, Reconnect

- **Replays:** Bei Lockstep/Rollback ist ein Replay = Map-Seed + Initialzustand + zeitgestempelter Befehlsstrom. Das ergibt Kilobyte-kleine Replay-Dateien, deterministisch abspielbar, frei kameraführbar – praktisch gratis, sobald die Simulation befehlsgetrieben ist (AoE/SC2-Modell). **Nebenutzen fürs Studio:** Replays sind gleichzeitig Savegames-Grundlage, KI-Test-Fixtures und Desync-Debugging-Werkzeug – die SP-Phase profitiert sofort.
- **Beobachtermodus:** Observer sind verzögerte Lockstep-Clients (Sekunden bis Minuten Delay), ggf. über den Relay-Server verteilt. Trivial im Lockstep-Modell; im State-Sync-Modell ein eigenes Snapshot-Streaming-System.
- **Reconnect:** Der teuerste Nachteil des Lockstep. Optionen: (a) periodische, hash-validierte **Snapshots** der Simulation (alle ~30–60 s), Reconnect = Snapshot laden + Fast-Forward bis Live-Tick; (b) vollständige Re-Simulation ab Tick 0 (nur für kurze Matches tragbar). Voraussetzung für beides: vollständig serialisierbarer Simulationszustand – wieder eine Anforderung, die der SP-Kern (Savegames) ohnehin braucht. State-Sync hat hier strukturell den kürzesten Weg.

## 5. Cheating-Resistenz

- **Lockstep:** Jeder Client besitzt den kompletten Spielzustand → Map-Hacks (Fog-of-War-Aufhebung) sind clientseitig nicht verhinderbar. Manipulations-Cheats (Einheiten-Buffs etc.) erzeugen dagegen sofort Desyncs und sind durch Server-Validierung des Befehlsstroms plus Hash-Vergleich nachweisbar. Für MVP/Koop vertretbar; für Ranked PvP langfristig ein offenes Risiko (SC2 hatte jahrelang Map-Hacks).
- **State-Sync:** Der Server kann Sichtbarkeit serverseitig filtern – die strukturell beste Cheating-Resistenz, aber um den Preis der Bandbreiten- und Skalierungsprobleme aus §2.4.
- **Realistische Mittelfrist-Linie für Nova:** autoritativer Input-Relay-Server (validiert Befehle, waltet über Tick-Takt und Hash-Vergleiche), Fog-of-War-Datenfilterung erst, wenn Ranked relevant wird.

## 6. Unity-Umsetzungsoptionen im Einzelnen

| Option | Modell | Bewertung für Project Nova |
|---|---|---|
| **Eigenbau-Lockstep** über schlankem Transport (UDP/RUDP, Relay) | Lockstep | Volle Kontrolle, keine Lizenzkosten, genau auf RTS zugeschnitten; der Simulationskern (commands + fixed tick + deterministische Mathe) ist ohnehin Pflicht. Aufwand liegt in Determinismus-Disziplin und Relay/Backend, nicht im Transport. Referenz, dass es in Unity geht: [LockstepRTSEngine (GitHub)](https://github.com/mrdav30/LockstepRTSEngine). **Favorit.** |
| **Photon Quantum 3** | Deterministisch, Prediction/Rollback | Fertige deterministische ECS-Engine inkl. Physik, Mathe, Navigation, Bots, Profiler; Unity Verified Solution; Einstieg bis 100 CCU frei, danach CCU-basierte Kosten ([Photon-Blog](https://blog.photonengine.com/the-evolution-of-deterministic-multiplayer-photon-quantum-now-a-unity-verified-solution/)). Stark, aber: Gameplay-Code wird in Quantums DSL/ECS-Modell geschrieben → Vendor-Lock-in, Konflikt mit eigener ScriptableObject-Datenarchitektur und Q-015-Entscheidung. **Fallback/Evaluierungskandidat**, wenn Eigenbau-Determinismus in Phase 0 scheitert. |
| **Netcode for GameObjects (NGO)** | State-Sync | Unity-nativ, Open Source, gut für Lobbys/Relay-Services – aber State-Sync-Modell, laut Unity-Mitarbeiter für RTS mit allen sichtbaren Einheiten ungeeignet; „still maturing" bei hoher Konkurrenz ([Uverse 2025](https://uversedigital.com/blog/multiplayer-framework-for-your-game/)). Für die **Simulation: verworfen**. Optional für Lobby/Account-Peripherie wiederverwendbar. |
| **Mirror / Fish-Net** | State-Sync | Bewährt, kostenfrei, flexibel ([appwill 2025](https://appwill.co/multiplayer-in-unity-best-networking-solutions-2025/)) – aber gleiches Grundmodell wie NGO, gleiche Verwerfungsbegründung. |
| **Netcode for Entities** | State-Sync (DOTS) | Skaliert >5.000 Entities – **aber nur** über Relevancy/Importance-Culling, was einem RTS mit Gesamtsicht widerspricht; Unity selbst verweist RTS-Fragesteller auf deterministisches Input-Syncing ([Unity Discussions, Juli 2025](https://discussions.unity.com/t/netcode-for-entities-for-rts/1660672)). Verworfen. |
| **Photon Fusion/PUN** | State-Sync | Für schnelle Action-Spiele stark; CCU-Kostenmodell; kein RTS-Determinismus. Verworfen. |

**Wichtig:** Keine dieser Optionen muss **jetzt** final gewählt werden – vorausgesetzt, der Simulationskern wird ab Sprint 3 determinismusfähig gebaut (§7). Die Framework-Entscheidung ist dann eine Integrations-, keine Architekturentscheidung mehr.

## 7. Auflösung der TPD-Spannung (SP zuerst vs. MP ohne Rewrite)

Die Lösung ist eine **Architekturregel, kein Framework-Kauf**:

1. **Befehlsgetriebene Simulation:** Gameplay ändert Zustand ausschließlich über serialisierbare Befehle („Command-Queue pro Tick"). Mausklicks erzeugen Befehle, nie direkte Zustandsänderungen. Das ist im SP unsichtbar (lokale Queue) und macht MP später zum reinen Transportproblem.
2. **Strikte Simulation/View-Trennung:** Der Simulationskern referenziert keine UnityEngine-APIs im Tick-Pfad (keine Transforms, keine Physik, kein `Time`, kein `UnityEngine.Random`); die View liest Simulationszustand und interpoliert. ScriptableObjects liefern die **statischen Definitionsdaten** (Einheiten-/Gebäudetypen) – zustandslos und damit determinismusfreundlich.
3. **Fester Simulations-Takt** (Vorschlag: 10–20 Ticks/s) + eigener PRNG + deterministische IDs für alle Entities.
4. **Mathe-Strategie früh festlegen:** Fixed-Point-Bibliothek (oder disziplinierte Floats nur, falls Phase-0-Spike Cross-Platform-Bitgenauigkeit beweist – unwahrscheinlich bei ARM↔x86). Zu validieren im TPD-Phase-0-Spike.
5. **State-Serialisierung von Anfang an** (Savegames) → deckt später Reconnect-Snapshots ab.

Diese fünf Regeln kosten im SP nahezu nichts, verbessern Testbarkeit (Replays als Test-Fixtures) und halten **alle drei** MP-Modelle offen: Lockstep, Quantum-Rollback und – falls Determinismus wider Erwarten nicht haltbar ist – sogar State-Sync.

## Empfehlung

**Entscheidungsvorschlag für den DecisionLog (Sprint 3):**

1. **Simulationsmodell: deterministisches Lockstep über einem autoritativen Input-Relay-Server** als Zielarchitektur für Multiplayer. Der Server verteilt und validiert Befehle, gibt den Tick-Takt vor, vergleicht State-Hashes und hostet Replays/Observer. Damit ist die TPD-Forderung „autoritativer Server" erfüllt (Autorität über Befehle, Takt und Match-Ergebnis), ohne die bei 500 Einheiten unbezahlbare volle serverseitige State-Replikation. Bandbreite bleibt trivial, Replays/Observer/Spectator sind im Modell enthalten.
2. **Jetzt (Sprint 3, vor allem Gameplay-Code):** die fünf Architekturregeln aus §7 verbindlich machen – befehlsgetriebene, tickbasierte, von Unity-APIs entkoppelte Simulation mit serialisierbarem State und eigener Mathe/RNG. Das ist die eigentliche Q-013-Antwort: Das **Modell** wird jetzt festgelegt, das **Netzwerk-Framework** erst, wenn MP ansteht.
3. **Framework-Strategie:** Eigenbau-Lockstep auf schlankem UDP-Transport als Primärpfad; **Photon Quantum 3** als kostenpflichtiger Fallback, falls der Phase-0-Determinismus-Spike zeigt, dass Eigenbau-Determinismus (insb. cross-platform ARM↔x86, Pathfinding Q-014) das Budget sprengt.
4. **Geprüfte und verworfene Alternativen:**
   - *Reiner server-autoritativer State-Sync (NGO, Mirror, Fusion, Netcode for Entities):* verworfen – Synchronisationsvolumen bei 500 voll sichtbaren Einheiten nicht darstellbar (Interest Management greift bei RTS-Gesamtsicht nicht); Unity selbst empfiehlt RTS-Fragestellern deterministisches Input-Syncing; zusätzlich Lock-in des Gameplay-Codes ans Replikationsmodell.
   - *Rollback (GGPO-artig, Eigenbau):* verworfen als Primärpfad – Resimulation von 500 Einheiten über mehrere Ticks sprengt das 60-FPS-Budget; Jitter-Korrekturen sind bei Formationen sichtbar (Stormgate-Erfahrung); Mehrwert gegenüber 2–6 Ticks Input-Delay im RTS gering.
   - *„Erst SP ohne Rücksicht, MP später dranflanschen":* verworfen – bedeutet faktisch Rewrite des Gameplay-Kerns (R-02), genau das vom TPD benannte Risiko.

## Offene Punkte

- **Fixed-Point vs. disziplinierte Floats:** Entscheidung erst nach Phase-0-Spike mit echten Cross-Platform-Builds (Windows-x86 vs. macOS-ARM) und Hash-Vergleich möglich. → Übergabe an Sprint 3 / Q-015.
- **Tick-Rate und Input-Delay:** 10, 15 oder 20 Ticks/s? Abhängig von Simulationskosten bei 500 Einheiten (Kopplung an Q-014/Q-015 und Performance-Budget).
- **Aetherium-Nachwachsen & Umweltveränderung:** müssen vollständig in der deterministischen Simulation laufen (kein „ambientes" Verhalten außerhalb des Ticks) – Designregel für Sprint 2.
- **Zerstörbare Umgebung:** Umfang entscheidet über Snapshot-Größe (Reconnect) und Desync-Angriffsfläche – Abhängigkeit zu R-05.
- **Map-Hack-Risiko für Ranked PvP:** akzeptiert für MVP/Koop; ob später ein serverseitiges Fog-of-War-Filtering (Hybrid Richtung State-Authority nur für Sichtbarkeit) nötig wird, bleibt offen.
- **Backend-Dienst (Lobby, Matchmaking, Accounts):** orthogonal; NGO/Relay, Photon Cloud oder Eigenbau-Backend (TPD §9 Option A/B) – nicht Teil dieser Entscheidung.

## Nächste Schritte

1. Sprint 3: Empfehlung §7 als DecisionLog-Eintrag (D-006 ff.) verabschieden; die fünf Architekturregeln in Architecture.md/CodingGuidelines.md gießen.
2. TPD Phase 0: **Determinismus-Spike** definieren – minimaler Tick-Loop mit Fixed-Point-Mathe, Build für Windows + macOS, Hash-Vergleich über 10.000 Ticks; Ergebnis entscheidet Fixed-Point-Strategie und Quantum-Fallback.
3. Abstimmung mit Q-014-Research: Pathfinding-Ansatz muss deterministisch umsetzbar sein (Flow-Fields prüfen).
4. Abstimmung mit Q-015-Research: falls ECS/DOTS für die Simulation, Determinismus-Constraints (Job-Reihenfolge, `Unity.Mathematics`) in die Entscheidungsmatrix aufnehmen.
5. Sprint 2 (Game Design): Regel „alles Simulation-relevante läuft im Tick" in die GDD-Dokumente aufnehmen (Aetherium, Wetter, Umgebungszerstörung).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Research-Erstfassung | Lead Multiplayer Engineer |
