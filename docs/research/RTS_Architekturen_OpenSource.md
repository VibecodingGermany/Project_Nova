# Moderne RTS-Architekturen & Open-Source-Referenzprojekte

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 1

## Zweck

Dieses Dokument analysiert real existierende RTS-Referenzprojekte (Open Source und öffentlich dokumentierte kommerzielle Architekturen) und extrahiert übertragbare Architekturmuster für Project Nova: Trennung Simulation/Präsentation, Command-/Order-Modell, Tick-/Update-Modell, Datenmodelle für Einheiten sowie Savegame-/Replay-Ansätze. Es liefert die Referenz-Grundlage für die Architekturentscheidungen in Sprint 3 (v. a. Q-013 Simulations-/Multiplayer-Modell, Q-015 ECS/DOTS vs. OOP) und validiert, ob die festgelegten Leitplanken (Unity + URP, Datengetriebenheit via ScriptableObjects, Desktop-first, spätere MP-Autorität) mit der Praxis erfolgreicher RTS-Projekte vereinbar sind.

## Abhängigkeiten

- [../analysis/KnowledgeBase.md](../analysis/KnowledgeBase.md) – Projektkontext, verbindliche Leitplanken (Stack, MVP-Disziplin, 100–500+ Einheiten @ 60 FPS)
- [../production/OpenQuestions.md](../production/OpenQuestions.md) – Q-013 (Simulations-/Multiplayer-Modell), Q-014 (Pathfinding), Q-015 (ECS/DOTS vs. OOP); Q-013/Q-015 werden durch dieses Dokument vorbereitet, Q-014 nur am Rand (→ eigenes Research-Dokument Pathfinding)
- [../production/RiskAnalysis.md](../production/RiskAnalysis.md) – R-02 (MP-Architektur zu spät), R-03 (Pathfinding-Skalierung)

## Untersuchte Referenzen im Überblick

| Referenz | Typ / Sprache | Skalierung (belegt) | Netzwerkmodell | Datenmodell | Lizenz/Quelle |
|---|---|---|---|---|---|
| OpenRA | Open Source, C# (.NET) | klassische C&C-Maps, typ. < 1.000 Actors | deterministisches Lockstep (Orders only) | YAML (MiniYaml) + Trait-Komposition in C# | GPL-3.0, [github.com/OpenRA/OpenRA](https://github.com/OpenRA/OpenRA) |
| Spring / Recoil (BAR, Zero-K) | Open Source, C++ + Lua | Stress-Tests 2025: 100 Spieler, > 10.000 Einheiten | deterministisches Lockstep (Commands only) | Lua-Gadgets (synced/unsynced) + UnitDefs | GPL-2.0, [recoilengine.org](https://recoilengine.org/) |
| Age of Empires I/II (Ensemble) | kommerziell, dokumentiert | ~1.500 bewegte Einheiten, 8 Spieler (2001!) | deterministisches Lockstep, Turn-System 200 ms | propritäre Datendateien (GENIE Engine), datengetrieben | [GDC-Paper „1500 Archers on a 28.8"](https://zoo.cs.yale.edu/classes/cs538/readings/papers/terrano_1500arch.pdf) |
| Planetary Annihilation (Uber) | kommerziell, teilw. dokumentiert | tausende Einheiten, mehrere Planeten | Server-autoritativer State-Sync (Client/Server) | JSON-Unit-Spezifikationen | [palobby.com-Wiki](https://wiki.palobby.com/wiki/Planetary_Annihilation_Timeline), [PA Support](https://planetaryannihilation.com/support/server-performance/) |

Stand der Recherche: Juli 2026, Quellen siehe Inline-Links. Zahlen, die nicht direkt aus den Quellen stammen, sind als Einschätzung gekennzeichnet.

## Referenz 1: OpenRA

**Was es ist:** Re-Implementation der klassischen Westwood-C&C-Spiele (Tiberian Dawn, Red Alert, Dune 2000) als moderne, modding-fähige Engine in C#. Aktiv gepflegt, Releases bis in die Gegenwart. Architektur ist komplett offen einsehbar.

**Architektur-Kernpunkte:**

- **Trait-System statt Vererbung:** Jeder Actor ist eine flache Komposition von Traits (z. B. `Mobile`, `AttackFrontal`, `Health`, `Transforms`). Traits werden in C# implementiert und deklarativ in YAML-Dateien pro Einheit zusammengestellt und parametriert. Die gesamte Trait-Palette inkl. aller Properties ist maschinell dokumentiert: [docs.openra.net/en/release/traits](https://docs.openra.net/en/release/traits/). Vererbung erfolgt über YAML-Template-Vererbung (`^Vehicle` etc.), nicht über C#-Klassenhierarchien.
- **Order-Modell:** Alle Spielereingaben werden zu serialisierbaren `Order`-Objekten (OrderString + Target + Parameter). Nur Orders gehen übers Netz; sie werden beim Senden **und** Empfangen validiert. Die Simulation konsumiert Orders tickweise.
- **Tick-Modell:** Fixe Simulationsschritte (Default-Timestep 40 ms = 25 Ticks/s, Einschätzung aus Konfigurations-Defaults), Rendering entkoppelt und interpoliert.
- **Determinismus:** Die Engine verwendet für die Simulation eigene Fixed-Point-/Integer-Typen (`WVec`, `WDist`, `WAngle`) statt Floats, um Lockstep-Determinismus plattformübergreifend zu sichern. Replays sind nichts anderes als aufgezeichnete Order-Streams – praktisch kostenlos.
- **Savegames:** OpenRA hat historisch lange **keine** Mid-Game-Savegames unterstützt, weil der World-State nicht serialisierbar war (Traits halten beliebige Objektgraphen). Savegames kamen erst spät und eingeschränkt – ein direktes Symptom der Architekturentscheidung „State lebt im Code".

**Übernehmen für Project Nova:**

1. **Trait-/Kompositions-Gedanke → ScriptableObjects:** OpenRA beweist seit 15+ Jahren, dass RTS-Einheiten als flache Komposition kleiner, datengetriebener Verhaltensbausteine modelliert werden sollten – exakt die Leitplanke von Project Nova. Die YAML-Traits entsprechen 1:1 Unity-ScriptableObject-Definitions + Komponenten-Komposition.
2. **Order-Abstraktion von Tag 1:** Eingaben nie direkt auf GameObjects wirken lassen, sondern als validierbare, serialisierbare Command-Objekte in eine Queue – das ist die Voraussetzung für Replays, MP und KI gleichermaßen und kostet im Singleplayer fast nichts.
3. **Feste Simulations-Tickrate entkoppelt vom Rendering.**

**Nicht übernehmen:**

1. **Fixed-Point-Zwang überall:** OpenRAs volle Lockstep-Determinismus-Disziplin (eigene Zahlentypen, kein `float` in der Simulation) ist für einen autoritativen Server später nicht nötig und würde Unity-Physik, NavMesh und Mathf praktisch aussperren. Project Nova sollte determinismus-*fähig* strukturieren (Sim/Präsentation getrennt, fester Tick, gezähmter RNG), aber Float bleiben.
2. **Kein Savegame-Konzept von Anfang an:** Der OpenRA-Schmerz (Savegames als Nachrüstproblem) ist eine Warnung, kein Vorbild. Project Nova braucht von Anfang an serialisierbaren Sim-State (MVP: skaliert das Savegame überhaupt mit? → Offene Punkte).

## Referenz 2: Spring / Recoil (Beyond All Reason, Zero-K)

**Was es ist:** Spring ist die älteste aktive Open-Source-RTS-Engine (seit ~2005, ursprünglich Total-Annihilation-Nachbau); Recoil ist ein aktiver Hard-Fork des Spring-105-Zweigs, der u. a. Beyond All Reason (BAR) und Zero-K antreibt ([recoilengine.org](https://recoilengine.org/)). BAR demonstriert aktuell die Skalierungsobergrenze des Genres im Open-Source-Bereich: Community-Stress-Tests Anfang 2025 mit über 100 Spielern und mehr als 10.000 Einheiten, nach Backend-Optimierungen im „Season 2"-Update März 2025 ([Notebookcheck, 2025-05-13](https://www.notebookcheck.net/Open-source-RTS-Beyond-All-Reason-showcases-large-scale-engine-update-as-player-interest-climbs.1014152.0.html)).

**Architektur-Kernpunkte:**

- **Synced/Unsynced-Trennung als Sprachkonstrukt:** Spiellogik läuft in Lua. Gadgets (Gameplay) haben einen *synced* Teil (läuft identisch auf allen Maschinen, darf Sim-State ändern) und einen *unsynced* Teil (lokale Darstellung, UI, darf Sim-State nur lesen). Die Engine erzwingt die Informationsbarriere ([Spring Wiki: Lua Callins](https://springrts.com/wiki/Lua:Callins), [Recoil Docs: Widgets and Gadgets](https://recoilengine.org/docs/guides/getting-started/widgets-and-gadgets/)). Das ist die konsequenteste real existierende Ausprägung der Trennung Simulation/Präsentation.
- **Command-Modell:** Jede Einheit besitzt eine explizite, inspizierbare Command-Queue (CMD.MOVE, CMD.FIGHT, …), die über `GiveOrderToUnit` manipuliert wird. Spieler-Eingaben werden zu Commands, die als einzige Daten über das Netz gehen (Lockstep).
- **Skalierung:** Die Engine ist C++, hot paths (Kollision, Pathfinding, Projektile) nativ; Lua ist nur Orchestrierung. Ergebnis: 10.000+ Einheiten. Zero-K zeigt zudem, dass komplexe Verhaltenslogik (Unit-AI-Micro, Terraforming) auf diesem Modell möglich ist.
- **Replays:** Demos sind Command-Aufzeichnungen, deterministisch abspielbar, inkl. Zeitraffer – Standard-Feature seit Jahren.

**Übernehmen für Project Nova:**

1. **Die synced/unsynced-Barriere als Coding-Regel:** In Unity gibt es keinen Sprachschutz – Project Nova sollte die Regel architektonisch nachbauen: Sim-Assembly darf nie Render-State lesen, Präsentation darf Sim-State nur lesen. Das ist die billigste MP-Versicherung (adressiert R-02 direkt).
2. **Explizite Command-Queue pro Einheit** als zentrales Datenmodell (statt verstreuter Zustandsautomaten in MonoBehaviours): unterstützt Shift-Queueing, KI, Replays und Debugging gleichermaßen.
3. **Hot Paths nativ halten:** In Unity-Übersetzung heißt das: Bewegung/Kollision/Target-Acquisition sind die Kandidaten für Burst/Jobs bzw. später DOTS – nicht das gesamte Gameplay (speist Q-015).

**Nicht übernehmen:**

1. **Lua als Gameplay-Schicht:** Eine eigene Scripting-VM einzubinden wäre für Project Nova reiner Overhead; C# + ScriptableObjects decken denselben Zweck (datengetriebene, hot-reloadbare Logik-Parameter) ohne zweite Sprache.
2. **Volldeterministisches Lockstep als Zielarchitektur:** Spring/Recoil zahlen dafür seit Jahren mit Desync-Jagd und eingeschränkter Physik (vgl. auch die AoE-Erfahrung unten). Project Novas Zielbild (autoritativer Server) braucht diese Disziplin nicht – State-Sync ist toleranter gegenüber Nichtdeterminismus.
3. **Engine-Größe als Blaupause:** Recoil ist eine generische Engine für 100-Spieler-Schlachten. Project Novas MVP (1 Fraktion, 1 Karte) braucht einen Bruchteil davon; Skalierungsziel 500+ Einheiten ist um Faktor 20 unter dem BAR-Stress-Test – die Skalierung ist belegt machbar, darf aber kein Gold-Plating rechtfertigen.

## Referenz 3: Age of Empires I/II – „1500 Archers on a 28.8" (Bettner/Terrano, GDC 2001)

**Was es ist:** Der Referenzvortrag der RTS-Netzwerkarchitektur schlechthin ([PDF via Yale](https://zoo.cs.yale.edu/classes/cs538/readings/papers/terrano_1500arch.pdf), [Gamasutra-Feature](https://www.gamasutra.com/view/feature/3094/1500_archers_on_a_288_network_.php)). Trotz des Alters beschreibt er Muster, die bis heute (AoE II: Definitive Edition läuft 2025 noch mit tausenden concurrent Spielern) tragen.

**Architektur-Kernpunkte:**

- **Simultane Simulation statt State-Transfer:** Nur Commands werden übertragen; jede Maschine simuliert identisch. Grund: Schon 2001 wäre State-Sync von X/Y/Status/Facing pro Einheit auf ~250 Einheiten begrenzt gewesen – Command-Only skaliert mit der *Anzahl der Befehle*, nicht der Einheiten.
- **Turn-System:** Simulation läuft in 200-ms-Turns, entkoppelt vom Rendering. Commands werden zwei Communication-Turns in die Zukunft geplant (aus Turn 1000 → Ausführung in Turn 1002), damit Empfang/ACK im Hintergrund laufen kann, während die Animation weiterläuft.
- **Speed Control:** Turn-Länge wird dynamisch an langsamste Maschine + Ping angepasst – Glättung statt Ruckeln, „konsistente 500 ms Latenz sind spielbar, schwankende 80–500 ms nicht".
- **Metering & Command-Filter:** Messdaten immer an; triviale Filter (Doppelklicks auf gleiche Position verwerfen) reduzierten Netzspitzen massiv. Spieler feuern im Schnitt 1 Befehl pro 1,5–2 s, Spitzen 3–4/s.
- **Determinismus-Schmerz:** Out-of-Sync-Bugs waren der härteste Dauerbrenner des Projekts („goes all the way to the wire"); minimale Abweichungen (RNG-Aufrufzählung!) kaskadierten über Minuten.
- **Recorded Games als Nebenprodukt:** Weil die Simulation deterministisch ist, sind Aufzeichnungen = Command-Streams; zuerst Debug-Feature, dann Community-Killerfeature.
- **Datengetriebenheit:** AoE II ist berühmt dafür, dass Einheiten/Zivilisationen/Techs vollständig aus Datendateien (GENIE/.dat) definiert sind – die Modding-Szene lebt bis heute davon.

**Übernehmen für Project Nova:**

1. **Command-Latenz-Budget als Designgröße:** 250 ms Command-Latenz sind in RTS unsichtbar, bis 500 ms spielbar – das gibt Project Novas späterem Server-Modell massiv Luft (kein Frame-Perfect-Netcode nötig) und legitimiert ein Tick-Modell mit 100–250 ms Command-Fenstern.
2. **Metering von Tag 1:** Simulationszeit pro Tick, Commands/s, längste Einzelsysteme – als lesbares Overlay. Die AoE-Lektion „Metering ist King" ist gratis übernehmbar.
3. **Command-Filter/Dedup** gegen Input-Spitzen (Doppelklicks) – trivial, messbar wirksam.
4. **Vollständig datengetriebene Einheitendefinitionen** als nicht verhandelbar – bestätigt die ScriptableObject-Leitplanke.

**Nicht übernehmen:**

1. **Peer-to-Peer-Topologie:** AoEs Stern-Topologie bricht an NAT und skaliert schlecht; Project Nova peilt autoritativen Server an – Peer-Lockstep ist damit vom Tisch.
2. **Strikte Lockstep-Determinismus-Disziplin als Produktionsmodus:** Das Paper dokumentiert selbst die Kosten (Desync-Jagd, 50-MB-Traces, RNG-Call-Counting). Für einen Titel ohne Release-gebundenes MP ist das Risiko/Nutzen-Verhältnis schlecht.

## Referenz 4: Planetary Annihilation (Uber Entertainment)

**Was es ist:** Großskalen-RTS (mehrere Planeten, tausende Einheiten) mit explizit **abweichender** Netzwerkarchitektur: cross-platform Client/Server, die Simulation läuft auf dem Server, Clients sind Viewer/Controller ([palobby.com-Wiki](https://wiki.palobby.com/wiki/Planetary_Annihilation_Timeline), [PA Support: Sim Performance, Time Dilation and RAM Usage](https://planetaryannihilation.com/support/server-performance/)).

**Architektur-Kernpunkte:**

- **Server-autoritative Simulation:** Ein Server-Prozess (auch im „Singleplayer" lokal) simuliert; Clients erhalten Simulationsdaten verzögert und rendern ältere Zustände (Keyframe-Stream). Kein Lockstep, keine Determinismus-Anforderung an Clients.
- **Time Dilation:** Wenn die Simulation die Echtzeit nicht hält, läuft die Spielzeit bewusst langsamer statt zu ruckeln – Server-Performance wird als öffentliche Metrik kommuniziert (Sim %).
- **Konsequenz:** Beliebige Physik/Floats erlaubt, kein Desync-Risiko, Cheating strukturell erschwert; dafür Server-Bandbreite und -CPU als zentrale Kostenstelle.

**Übernehmen für Project Nova:**

1. **„Simulation läuft immer server-artig, auch lokal":** Project Nova kann den Singleplayer von Anfang an als lokalen Server + lokalen Client strukturieren (gleiche Prozessgrenze, aber getrennte Module mit klarer Schnittstelle). Der spätere Umzug auf echte MP-Server ist dann ein Transport-Thema, kein Rewrite – das ist die eleganteste Antwort auf R-02.
2. **Time Dilation als akzeptierter Degradationspfad** statt FPS-Einbruch bei 500+ Einheiten: lieber 45 Sim-FPS bei 60 Render-FPS als umgekehrt.

**Nicht übernehmen:**

1. **Vollständiger State-Stream an Clients:** PA zahlt dafür mit hohen Server-Anforderungen und Bandbreite. Project Nova sollte später einen Hybrid prüfen: Server autoritativ, aber Command-basierte Replikation + Delta-Snapshots statt Vollzustände (→ Q-013-Research-Dokument).
2. **PA spezifische Komplexität** (sphärische Planeten, Orbital-Layer) ist irrelevant für Project Nova.

## Muster-Querschnitt: Was alle Referenzen gemeinsam haben

| Muster | OpenRA | Spring/Recoil | Age of Empires | Planetary Annihilation | Übertragung auf Project Nova |
|---|---|---|---|---|---|
| Sim/Präsentation getrennt | ja (Render-Traits vs. Sim-Traits) | ja, sprachlich erzwungen (synced/unsynced) | ja (Rendering 30 % Budget, entkoppelt) | ja, prozessual (Client = Viewer) | **Pflicht:** getrennte Assemblies/Module, Präsentation read-only |
| Command-/Order-Modell | serialisierbare `Order`-Objekte, doppelt validiert | explizite CMD-Queue pro Einheit | Commands 2 Turns vorgeplant, Dedup-Filter | Commands an Server, Server validiert | **Pflicht:** Command-Pipeline als einziger Eingriffspunkt in die Simulation |
| Tick-Modell | fester Timestep (~25 Ticks/s), interpoliertes Rendering | fester Sim-Frame (30/s, Einschätzung) | 200-ms-Turns, dynamische Länge (Speed Control) | Server-Tick mit Time Dilation | **Pflicht:** fester Sim-Tick (z. B. 20–30 Hz), Rendering via Interpolation; Degradation über Dilation, nicht über Tick-Ausfall |
| Einheiten-Datenmodell | YAML-Trait-Komposition, flach | Lua UnitDefs + Gadgets | vollständig externe Datendateien | JSON-Unit-Specs | **Pflicht:** ScriptableObject-Definitionen + Komposition; **alle vier** Referenzen sind datengetrieben – kein Gegenbeispiel im Genre |
| Savegame | schwach/nachgerüstet (Warnsignal) | via Sim-Serialisierung möglich | ja (kompletter Sim-State) | Server-Snapshots | **Anforderung:** serialisierbarer Sim-State von Anfang an (MVP-Anforderung) |
| Replay | Order-Stream (quasi gratis) | Demo = Command-Stream | Recorded Games = Command-Stream | Server-Aufzeichnung | **Früh einplanen:** Replay = Command-Log + Seed; kostet fast nichts, wenn Command-Pipeline sauber ist |
| Determinismus | strikt (Fixed-Point) | strikt (Float + Sync-Checks) | strikt (mit dokumentiertem Schmerz) | nicht erforderlich (Server autoritativ) | **Bewusst NICHT strikt:** determinismus-fähig strukturieren, Float erlauben; Entscheidung final in Q-013 |

**Kernbefund:** Unabhängig von Engine, Sprache und Netzwerkmodell teilen alle erfolgreichen RTS-Architekturen dieselben vier Säulen – (1) harte Trennung Simulation/Präsentation, (2) Commands als einzige mutationsfähige Schnittstelle zur Simulation, (3) fester Sim-Tick mit entkoppeltem Rendering, (4) vollständig datengetriebene Einheitsdefinitionen. Das Netzwerkmodell (Lockstep vs. Server-autoritativ) variiert – die vier Säulen nie. Project Novas Leitplanken (Datengetriebenheit, MP-Vorbereitung) sind damit genre-konform und werden durch die Praxis bestätigt.

## Empfehlung

**Entscheidungsvorlage (für DecisionLog, D-006 ff.):**

1. **Vier-Säulen-Architektur verbindlich festschreiben:** getrennte Simulations- und Präsentations-Module (Präsentation read-only auf Sim-State), eine Command-Pipeline als einziger Eingriffspunkt in die Simulation, fester Sim-Tick (20–30 Hz) mit interpoliertem Rendering, vollständig datengetriebene Einheits-/Gebäudedefinitionen via ScriptableObjects. Begründung: Alle vier untersuchten Referenzen (OpenRA, Spring/Recoil, Age of Empires, Planetary Annihilation) – über 25 Jahre Genregeschichte und alle Netzwerkmodelle hinweg – teilen exakt dieses Muster; es ist die Voraussetzung für Replays, KI-Testbarkeit, Savegames und die spätere MP-Autorität (R-02).

2. **Singleplayer als „lokaler Server" strukturieren (Planetary-Annihilation-Muster), Determinismus nur determinismus-fähig, nicht strikt.** Begründung: Das Zielbild ist ein autorisativer Server; Server-autoritative Simulation benötigt keine strikte Lockstep-Deterministik und erlaubt Float, Unity-Physik und Standard-Tooling. Die Sim/Präsentation-Trennung plus Command-Pipeline hält den späteren Umzug auf Netz-Transport billig.

3. **Geprüfte und verworfene Alternativen:**
   - *Deterministisches Lockstep (OpenRA/AoE/Spring-Modell):* verworfen als Produktionsziel. Belegte Kosten: Desync-Jagd als Dauerbaustelle (AoE-Paper), Fixed-Point-Zwang schließt Unity-Physik/NavMesh aus, Peer-Topologie unvereinbar mit Server-Autorität. Nutzen (minimale Bandbreite) ist für Desktop-first mit Server-Zielbild nicht entscheidend. Replays erhält Project Nova auch ohne Lockstep gratis über das Command-Log.
   - *Voller State-Sync im PA-Stil:* verworfen als alleiniges Replikationsmodell für später (Server-Kosten, Bandbreite); Hybrid aus Command-Replikation + Delta-Snapshots in Q-013-Detailresearch prüfen.
   - *Generische Engine-Übernahme (Fork von OpenRA/Recoil statt Unity):* verworfen – widerspricht D-002 (Unity + URP festgelegt), Lizenz-Fragen (GPL), und die Engines lösen Probleme (100-Spieler-Skalierung, 2D-Sprite-Legacy), die Project Nova nicht hat.
   - *Lua/externe Scripting-Schicht für Gameplay:* verworfen – C# + ScriptableObjects liefern dieselbe Datengetriebenheit ohne zweite Runtime.

4. **Konsequenz für Q-015 (Vorbereitung):** Hybrider Ansatz – klassisches C#/MonoBehaviour-OOP für Gameplay-Orchestrierung, Burst/Jobs (später optional DOTS) nur für identifizierte Hot Paths (Bewegung, Kollision, Target-Acquisition). Beleg: Recoil trennt genauso (C++ hot paths, Lua-Orchestrierung) und erreicht damit 10.000+ Einheiten; Project Nova zielt auf 500+, also um Faktor 20 darunter.

## Offene Punkte

- **Savegame-Granularität im MVP:** Alle Referenzen zeigen, dass Savegames von serialisierbarem Sim-State abhängen. Ist ein kompletter Sim-State-Snapshot im MVP Umfang, oder nur skizziert? (→ Sprint 2/3, Abstimmung mit Produktionsplanung)
- **Sim-Tickrate konkret:** 20 vs. 30 Hz hat Folgen für Responsiveness und CPU-Budget; erst mit Prototyp-Messungen entscheidbar (→ TPD Phase 0 Performance-Spike).
- **Command-Log als Replay-Format:** Format, Versionierung und Kompatibilität über Builds hinweg sind noch nicht spezifiziert.
- **Abgrenzung zu Q-013/Q-014-Dokumenten:** Die Detailentscheidung Lockstep vs. State-Sync vs. Hybrid sowie das Pathfinding-Modell (Flow-Field-Kandidaten sichtbar in Spring/Recoil und AoE) gehören in die jeweiligen Research-Dokumente; dieses Dokument liefert nur die Referenz-Evidenz.
- **Zahlen zu Spring/Recoil-Tickrate und OpenRA-Default-Timestep** stammen aus Konfigurations-Defaults/Doku-Snippets und sind als Einschätzung gekennzeichnet – bei Bedarf im Code verifizieren.

## Nächste Schritte

1. Empfehlung 1–3 nach Sprint-1-Review als D-006 ff. in den [../production/DecisionLog.md](../production/DecisionLog.md) übernehmen.
2. Q-013-Research-Dokument (Multiplayer-Simulationsmodelle) gegen die hier dokumentierten Referenz-Modelle prüfen; PA-Hybrid (Command + Delta-Snapshot) als dritte Alternative konkretisieren.
3. Q-015-Research-Dokument (ECS/DOTS) um den Recoil-Beleg (native Hot Paths + Orchestrierung) ergänzen; Performance-Spike in TPD Phase 0 mit Burst/Jobs-Messung hinterlegen.
4. Q-014-Research-Dokument: Flow-Field-/HPA-Ansätze aus Spring/Recoil und AoE als Referenzkandidaten aufnehmen.
5. In Sprint 3: Vier-Säulen-Modell als verbindliche Modulstruktur ins TDD überführen (Sim-Assembly, Präsentations-Assembly, Command-Pipeline, Daten-Layer).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Research-Erstfassung | Lead Technical Director |
