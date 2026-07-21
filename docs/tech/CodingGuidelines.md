# Coding Guidelines – C#-Regeln für Project Nova

**Version:** 0.2.0 | **Status:** Entwurf (Korrekturlauf Sprint 4) | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 3–4

## Zweck

Diese Richtlinien operationalisieren die Architektur-Entscheidungen D-033–D-035 als verbindliche C#-Regeln. Ziel: ein determinismusfähiger, GC-armer Simulationskern neben einem frei Unity-nutzenden Präsentationslayer – überprüfbar in Code Reviews und (perspektivisch) per Analyzer. Verbindlich für allen Projektcode ab Sprint 7; wo Regeln nicht maschinell geprüft werden können, sind sie Review-Pflicht.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (5 Sim-Regeln, Float im MVP), D-034 (Jobs/Burst-Hotspots, Budget), D-035 (OOP+SO, Unity-freie `Nova.Simulation`), D-036 (SimRunner), D-043 (Assembly-Topologie inkl. `Nova.AI`/`Nova.AI.Data`), D-045 (Managed-first, Toleranz-Parität), D-049 (Registry-Sharding)
- [../research/Unity_BestPractices.md](../research/Unity_BestPractices.md) – §3 (SO-Grenzen), §5 (Pooling), §6 (GC-Vermeidung)
- [../research/Multiplayer_Simulation.md](../research/Multiplayer_Simulation.md) – §3 (Determinismus-Fallstricke)
- [./FolderStructure.md](./FolderStructure.md) – Layer-/Assembly-Struktur, auf die sich diese Regeln beziehen
- [./NamingConvention.md](./NamingConvention.md) – Benennung der hier referenzierten Rollen

## 1. Geltungsbereich und Layer-Regeln

| Layer (Assembly) | Darf | Darf nicht |
|---|---|---|
| `Nova.Simulation` (+ `Nova.Core`) | `System.*`, `System.Collections.Generic`, eigene Typen | UnityEngine-APIs, Unity-Packages, Engine-State (durch `noEngineReferences` erzwungen) |
| `Nova.Simulation.Burst` | Unity.Collections/Burst/Jobs/Mathematics | Managed-Referenztypen in Jobs, Sim-State außerhalb der übergebenen Container |
| `Nova.Data` | ScriptableObject-Schemas, Editor-Validierung | Runtime-State, Sim-Logik |
| `Nova.Gameplay` | UnityEngine voll, Brücke SO→Sim, Pools, Tick-Antrieb | Gameplay-Regeln, die in den Sim-Kern gehören |
| `Nova.AI` (Unity-frei, D-043) | `System.*`, eigene Typen, Sim-Tick als Zeit, Zufall via `ISimRandom` | UnityEngine-APIs, Engine-State (durch `noEngineReferences` erzwungen), direkter Zugriff auf den vollen Sim-State – nur `IAiWorldView`/`ICommandSink` |
| `Nova.AI.Data` | ScriptableObject-Schemas (KI-Profile), Editor-Validierung | Runtime-State, KI-Logik; SOs betreten nie den Sim-/KI-Pfad (Überführung in Unity-freie Records beim Match-Setup) |
| `Nova.Presentation` | UnityEngine, URP, UI Toolkit, Audio | Sim-State mutieren (nur lesen + Commands absetzen) |

Grundsatz: **Die View fragt nie die Sim nach Erlaubnis, sie stellt Commands.** Direkte State-Mutationen außerhalb des Command-Pfads sind ein Architekturverstoß (D-033 Regel 1).

## 2. Sim-Core-Regeln (`Nova.Simulation`)

Diese Regeln setzen die fünf D-033-Regeln in Code um. Verstöße sind Desync- und GC-Quellen.

### 2.1 Unity-Unabhängigkeit

- Kein `using UnityEngine;` und keine Unity-Package-Typen in `Nova.Simulation`/`Nova.Core` – technisch erzwungen über `noEngineReferences` (vgl. FolderStructure §3), zusätzlich Review-Punkt.
- Verboten im gesamten Sim-Pfad: `Time.*`, `UnityEngine.Random`, `System.Random`, `DateTime.Now`, `Environment.TickCount`, `Task`/`Thread` (nicht-deterministische Parallelität), Physik-APIs.
- Zufall ausschließlich über den injizierten seedbaren PRNG (`ISimRandom`, D-033 Regel 4); jeder Systemzugriff auf Zufall erfolgt in fester, dokumentierter Reihenfolge.

### 2.2 Commands als einzige Mutation

- Jede Zustandsänderung entsteht durch ein Command (Struct), das validiert und dann im Tick ausgeführt wird. Systeme lesen den State direkt, schreiben nur innerhalb der Command-Ausführung bzw. ihres Tick-Durchlaufs.
- **Boxfreier Transport (Review F-5):** Commands werden als Structs im `CommandEnvelope`-Struct transportiert: `CommandType`-Enum plus fixed-size Payload – **kein `ICommand`-Interface-Feld im Envelope** (ein Struct in einem Interface-Feld wäre geboxt, Verstoß gegen §2.4). `ICommand` existiert höchstens als Marker-Interface und wird ausschließlich über generische Constraints (`where T : struct, ICommand`) verwendet, nie als Feld-, Parameter- oder Rückgabetyp im Tick-Pfad.
- **Tick-/Sequenzvergabe (Review F-5):** Der Client **schlägt** `TargetTick` vor (`CurrentTick + InputDelay`); der Server (Lockstep-Kernel hinter `ICommandSink`) vergibt `TargetTick` und `Sequence` **final bei `Submit`** – einzige Vergabestelle, niemals der Aufrufer. `Sequence` ist pro Spieler streng monoton; die finale Vergabe ist konsens-relevant und gehört nicht in den Client.
- **Issuer-Regel (Review F-7, Entscheidung Lead Technical Director):** Das Envelope führt eine Issuer-Kategorie (`Human`, `Peer`, `AI`). Die KI ist ein **interner Issuer**: Ihre Commands sind Teil des aufgezeichneten Command-Stroms (Replay = Start-Seed + vollständiger Strom inklusive KI-Commands); bei der Replay-Wiedergabe läuft die KI **nicht** erneut – kein Re-Tick, keine Doppelanwendung. KI-Input-Delay = 0: KI-Commands entstehen tick-intern und unterliegen nicht dem externen Input-Delay (Balancing- und SimRunner-relevant).
- Ungültige Commands werden verworfen und protokolliert – niemals als Exception im Tick (§5).

### 2.3 Deterministische Iteration und IDs

- Keine Enumeration über `Dictionary<>`/`HashSet<>` im Tick-Pfad (undefinierte Reihenfolge). Bestand: **ID-indizierte, vorallokierte Arrays/Listen**; freie Slots über explizite Free-Lists.
- `GetHashCode()` von Strings/`object` ist im Sim-Pfad verboten (plattformabhängig).
- IDs sind Integer-Typen: `EntityId`/`DefinitionId`-Structs um `int`/`uint`. **Kein `float` in Tick-kritischen IDs, Indizes, Zählern oder Tick-Werten** – auch nicht als Zwischenschritt.
- `float` ist im MVP für Sim-Mathe (Positionen, Schaden) erlaubt (D-033), aber: keine Transzendentalen (`Math.Sin/Cos/Pow/Sqrt`) ohne Freigabe, weil sie die Beta-Fixed-Point-Umstellung erschweren; Mathe-Zugriffe gebündelt über einen internen Sim-Mathe-Typ halten, damit die Umstellung einen Umsetzpunkt hat.

### 2.4 Kein GC im Tick

- Kein `new` von Referenztypen im Tick (Ausnahme: nichts). Sim-State besteht aus Structs in vorallokierten Arrays; Kapazitätsänderungen nur beim Match-Setup.
- Wiederverwendbare Puffer als Felder des Systems, nie lokale Allokation pro Tick.
- Verboten im Tick-Pfad: LINQ, String-Konkatenation/Interpolation, Closures/Lambdas mit Capture, Boxing (`object`-Parameter, nicht-generische Collections), `foreach` über Interfaces (Boxing) – stattdessen generische Constraints.
- Pools (`Nova.Core`, Unity-frei) für Match-Setup- und Event-Puffer; `UnityEngine.Pool` (`ObjectPool<T>`, `ListPool<T>`) nur in Gameplay/Presentation (Research §5).

### 2.5 Events ohne Allokation

- Die Sim feuert **keine C#-Events/Delegates im Tick** (Allokation durch Multicast-Listen, Captures, Boxing; außerdem Desync-Gefahr durch Abonnenten-Reihenfolge).
- State-Änderungen für die View werden als Struct-Records in einen vorallokierten, append-only **Event-Puffer** pro Tick geschrieben (z. B. `DamageEvent`, `UnitDiedEvent`); die View konsumiert den Puffer nach Tick-Ende und löscht ihn. Keine String-Payloads, keine Referenztypen in Event-Records.
- C#-`event Action<T>` mit Struct-Payload ist im Gameplay-/Presentation-Layer erlaubt (Benennung: [./NamingConvention.md](./NamingConvention.md) §7).

## 3. Burst/Jobs-Richtlinien (D-035, D-034, D-045)

- **Managed-first (D-045):** Der einzige Auslieferungs- und CI-Messpfad bis zur Fixed-Point-Beta ist die **Managed-Simulation**. Burst-Code wird ausschließlich hinter einem **Feature-Flag** (Define `NOVA_BURST`, standardmäßig aus) kompiliert und aktiviert – nie als Default-Pfad. CI, Golden-Master und Auslieferung messen damit denselben Pfad; eine grüne CI gegen Burst bei Managed-Auslieferung (Messblindheit) ist damit strukturell ausgeschlossen.
- Burst/Jobs **nur** für die benannten Hotspots: Flow-Field-Berechnung, Separation/lokale Vermeidung, FoW-/Sicht-Raster, Projektil-Sweeps. Kein präventiver Burst-Einsatz außerhalb der Hotspots – Optimierung nur gegen Profiler-Befund (Budget: Sim-Pathfinding ≤2–4 ms, D-034).
- Jobs arbeiten ausschließlich auf `NativeArray<T>`/NativeContainern von Structs; keine Managed-Referenzen im Job-Struct. Ownership und Dispose-Pflicht liegen beim schedulenden System (`Allocator.TempJob` für Tick-Arbeitsdaten, `Allocator.Persistent` nur für Match-Lebensdauer).
- Determinismus: Jobs werden innerhalb eines Ticks in fester Reihenfolge gescheduled und vollständig (`JobHandle.Complete()`) abgeschlossen, bevor der nächste Sim-Schritt liest. Kein Frame-übergreifendes Job-Scheduling im Sim-Pfad.
- `[BurstCompile]` auf allen Hotspot-Jobs; Burst Safety Checks und Leak-Detection in Development-Builds aktiv.
- **Parität (D-045):** Es gilt **Toleranz-Parität** statt Bit-Parität: Jede Burst-Variante wird per Hash-Vergleich gegen den Managed-Referenzpfad geprüft (`Nova.Simulation.Tests`); eine relative Abweichung >1e-4 löst **Alarm** aus (CI-Report + Ticket), blockiert den Merge aber **nicht**. Bit-Parität ist im Float-Regime nicht garantierbar und wird erst mit der Fixed-Point-Umstellung (Beta) relevant – dann neu bewertet. Der SimRunner (D-036) führt grundsätzlich die Managed-Variante aus.

## 4. ScriptableObject-Regeln (D-035, Research §3)

- SOs sind **Definitions-only**: keine zur Laufzeit veränderten Felder. Runtime-Zustand (HP, Produktionsfortschritt, Cooldowns) lebt ausschließlich im Sim-State. Verstoß-Beispiel, das im Review abzulehnen ist: ein SO, das "aktuelle Anzahl gebauter Einheiten" zählt.
- Vererbungshierarchien flach (max. 2 Ebenen); **Komposition vor Vererbung** (Unit-SO referenziert Weapon-SO, Ability-SO).
- Stabile IDs als Feld (`string`, Konvention in NamingConvention §8), Referenzen zwischen SOs per direktem Asset-Link (GUID-stabil), nie per Pfad-String.
- Zugriff zur Laufzeit ausschließlich über die Sub-Registries bzw. den generierten Master-Index der GameDatabase (Sharding nach D-049, Struktur in [./FolderStructure.md](./FolderStructure.md) §4), nicht über Szenen-Suchlauf. Der Master-Index wird nie händisch editiert.
- Validierung in `OnValidate()` und Editor-Validatoren (`Nova.Editor`): Pflichtfelder, Wertebereiche, Kosten-Konsistenz. Laufzeit-Validierung der SOs selbst entfällt – die Sim vertraut den überführten Definitionen.
- `[SerializeReference]` nur nach Freigabe durch den Lead Technical Director (Refactoring-Brüchigkeit, Research §3).

## 5. Error-Handling

- **Fail-fast beim Setup** (Match-Start, Datenüberführung, Prefab-Wiring): Exceptions sind hier erlaubt und erwünscht – Fehler müssen laut sein, bevor der erste Tick läuft.
- **Im Tick: keine Exceptions.** Erwartbare Fehlerfälle (ungültiges Command, ungültige Baufläche) sind normale Ergebnisse: verwerfen + Log-Eintrag. Programmierfehler/Invarianten über `Debug.Assert` (Debug-Builds laut, Release still).
- Keine leeren `catch`-Blöcke; `catch` immer mit Log oder Re-Throw. Kein `catch (Exception)` ohne konkreten Grund.
- Fehlerfälle, die ein Design-Ergebnis sind ("nicht genug Aetherium"), sind keine Fehler im Code-Sinn und laufen über reguläre Command-Ergebnisse.

## 6. Logging

- Einzige Logging-Schnittstelle: `INovaLogger` (`Nova.Core`), Level `Trace/Debug/Info/Warn/Error`. Die Sim erhält den Logger injiziert – kein statischer Logger-Zugriff (D-033-Testbarkeit, SimRunner-Kompatibilität).
- `UnityEngine.Debug.Log*` nur in Adapterklassen des Gameplay-/Presentation-Layers, die `INovaLogger` implementieren; nirgends sonst.
- Kein Logging im Tick-Hotpath (String-Allokation = GC-Verstoß §2.4). Ausnahmen: `Error`-Einträge und das Pflicht-Desync-Logging (erster divergierender Tick + Entity, Research Multiplayer_Simulation §3.6) – dieses Logging ist Werkzeug, nicht Deko.
- Log-Meldungen knapp, englisch, ohne Interpolation in Hot Paths (Guard: `if (logger.IsEnabled(LogLevel.Debug))`).

## 7. Dokumentation, Regions, Formatierung

- **XML-Doc-Pflicht** (`/// <summary>`) für alle `public`/`internal`-Schnittstellen: Interfaces, Commands, Sim-Systeme, SO-Schemas, Services. Private Member nur dort, wo nicht offensichtlich. Kommentare erklären das *Warum*, nicht das *Was*.
- Sprache von Code-Kommentaren/XML-Docs: Englisch (Code-Artefakt; vgl. DocumentationStandard §Sprache "Code bleibt englisch/technisch").
- **Keine `#region`** in handgeschriebenem Code – große Dateien werden geteilt statt gefaltet. Ausnahme: generierter Code.
- Eine öffentliche Type pro Datei, Dateiname = Typname; Datei-Header nach [./NamingConvention.md](./NamingConvention.md) §9.
- Formatierung: 4 Leerzeichen, `var` nur bei offensichtlichem Typ, K&R-Bracing; Details perspektivisch per `.editorconfig` erzwungen (Offene Punkte).

## 8. Verbotsliste (gesamtes Projekt)

| Verbot | Grund | Erlaubte Alternative |
|---|---|---|
| `Object.FindObjectOfType` / `FindFirstObjectByType` außerhalb Bootstrap/Tests | Reihenfolge- und Performance-Falle; versteckte Abhängigkeiten | Explizite Referenzen, GameDatabase, Wiring im Match-Setup |
| Statische Singletons / Service-Locator in der Simulation | Zerstört Determinismus, Testbarkeit und SimRunner-Fähigkeit (D-033/D-036) | Konstruktor-Injektion von Services (`ISimRandom`, `INovaLogger`) |
| Statischer Mutable State generell | Gleiche Begründung; erschwert Savegames/Replays | Sim-State-Container, serialisierbar (D-033 Regel 5) |
| `Update()`-Polling, wo Events/Callbacks möglich | Frame-Kosten, Reihenfolge-Unklarheit | Event-Puffer-Konsum, `Action<T>`-Events im View-Layer |
| `SendMessage` / `BroadcastMessage` | String-basiert, refaktorierungsunsicher, Allokation | Interfaces, generische Events |
| `Resources.Load` für Definitionsdaten | Pfad-Strings statt GUID-Referenzen (Research §3) | GameDatabase-Sub-Registries/Master-Index (D-049) |
| LINQ, Closures mit Capture, Boxing in Hot Paths | GC im Tick (§2.4) | Vorallokierte Puffer, generische Constraints |
| `UnityEngine.Random` / `System.Random` im Sim-Pfad | Nicht seedbar/nicht deterministisch (D-033 Regel 4) | `ISimRandom` |
| `Time.deltaTime` / `Time.time` im Sim-Pfad | Frame-abhängig, bricht festen Tick (D-033 Regel 3) | Tick-Zähler, Tick-Dauer-Konstante |
| Coroutinen für Sim-Logik | Frame-getrieben, nicht tick-getrieben | Tick-basierte Zustandsmaschinen; Coroutinen nur für View-Choreografie |
| `public`-Felder in MonoBehaviours | Kapselungsbruch | `[SerializeField] private` + Property |

## Offene Punkte

- **Fixed-Point-Umstellung (Beta, D-033):** Bibliothekswahl und die konkrete Migrationsstrategie hinter dem Sim-Mathe-Typ sind Teil der Beta-MP-Arbeiten; die jetzige Regel (§2.3) sichert nur den Umsetzpunkt.
- **Paritäts-Fixtures:** Die Regel steht mit D-045 (Toleranz-Parität ≤1e-4, alarmierend statt blockierend); offen ist nur der Umfang der Hash-Test-Fixtures (welche Systeme, welche Match-Fixtures) – mit Testing.md abzustimmen.
- **Transzendentale im MVP:** Ob `Math.Sqrt` in Distanzberechnungen des MVP-Sim toleriert wird (Performance vs. Umstellungsaufwand), soll der Phase-0-Spike anhand echter Profile klären.

## Nächste Schritte

1. Konsistenzreview mit Architecture.md und Testing.md (Paritäts-Hash-Tests, Desync-Logging-Format).
2. **Sprint 7 (Pflicht-Backlog, Analyzer-Enforcement):** `.editorconfig` + Roslyn-Analyzer verbindlich einführen. Mindestregeln: (a) **kein LINQ im Tick-Namespace** (`Nova.Simulation.*`) als Fehler; (b) **kein `System.Random`** im Sim-/KI-Pfad (`Nova.Simulation`, `Nova.AI`); (c) **kein `UnityEngine`-Using** in `Nova.Simulation`/`Nova.Core`/`Nova.AI` – bereits per `noEngineReferences` als Kompilierfehler erzwungen (FolderStructure §3), der Analyzer liefert die frühe IDE-Diagnose statt erst beim Build. Dazu Referenz-Beispieldateien (Command + `CommandEnvelope`, SimSystem, SO-Schema) als Muster anlegen.
3. Weitere Analyzer-Regeln (Allokations-Warnungen im Tick-Pfad) nach den ersten Sprint-7-Erfahrungen bewerten und nachschärfen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Technical Director |
| 0.2.0 | 2026-07-21 | Korrekturlauf Sprint 4 (D-043–D-052, Review-Findings): CommandEnvelope boxfrei + Tick-/Sequenzvergabe + Issuer-Regel (Review F-5/F-7), Managed-first & Toleranz-Parität ≤1e-4 (D-045), Nova.AI/Nova.AI.Data in Layer-Tabelle (D-043), Registry-Sharding-Zugriff (D-049), Analyzer-Enforcement als Sprint-7-Pflicht-Backlog konkretisiert | Lead Technical Director |
