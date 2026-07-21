# Coding Guidelines – C#-Regeln für Project Nova

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 3

## Zweck

Diese Richtlinien operationalisieren die Architektur-Entscheidungen D-033–D-035 als verbindliche C#-Regeln. Ziel: ein determinismusfähiger, GC-armer Simulationskern neben einem frei Unity-nutzenden Präsentationslayer – überprüfbar in Code Reviews und (perspektivisch) per Analyzer. Verbindlich für allen Projektcode ab Sprint 7; wo Regeln nicht maschinell geprüft werden können, sind sie Review-Pflicht.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (5 Sim-Regeln, Float im MVP), D-034 (Jobs/Burst-Hotspots, Budget), D-035 (OOP+SO, Unity-freie `Nova.Simulation`), D-036 (SimRunner)
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
| `Nova.Presentation` | UnityEngine, URP, UI Toolkit, Audio | Sim-State mutieren (nur lesen + Commands absetzen) |

Grundsatz: **Die View fragt nie die Sim nach Erlaubnis, sie stellt Commands.** Direkte State-Mutationen außerhalb des Command-Pfads sind ein Architekturverstoß (D-033 Regel 1).

## 2. Sim-Core-Regeln (`Nova.Simulation`)

Diese Regeln setzen die fünf D-033-Regeln in Code um. Verstöße sind Desync- und GC-Quellen.

### 2.1 Unity-Unabhängigkeit

- Kein `using UnityEngine;` und keine Unity-Package-Typen in `Nova.Simulation`/`Nova.Core` – technisch erzwungen über `noEngineReferences` (vgl. FolderStructure §3), zusätzlich Review-Punkt.
- Verboten im gesamten Sim-Pfad: `Time.*`, `UnityEngine.Random`, `System.Random`, `DateTime.Now`, `Environment.TickCount`, `Task`/`Thread` (nicht-deterministische Parallelität), Physik-APIs.
- Zufall ausschließlich über den injizierten seedbaren PRNG (`ISimRandom`, D-033 Regel 4); jeder Systemzugriff auf Zufall erfolgt in fester, dokumentierter Reihenfolge.

### 2.2 Commands als einzige Mutation

- Jede Zustandsänderung entsteht durch ein Command (Struct, `ICommand`), das validiert und dann im Tick ausgeführt wird. Systeme lesen den State direkt, schreiben nur innerhalb der Command-Ausführung bzw. ihres Tick-Durchlaufs.
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

## 3. Burst/Jobs-Richtlinien (D-035, D-034)

- Burst/Jobs **nur** für die benannten Hotspots: Flow-Field-Berechnung, Separation/lokale Vermeidung, FoW-/Sicht-Raster, Projektil-Sweeps. Kein präventiver Burst-Einsatz außerhalb der Hotspots – Optimierung nur gegen Profiler-Befund (Budget: Sim-Pathfinding ≤2–4 ms, D-034).
- Jobs arbeiten ausschließlich auf `NativeArray<T>`/NativeContainern von Structs; keine Managed-Referenzen im Job-Struct. Ownership und Dispose-Pflicht liegen beim schedulenden System (`Allocator.TempJob` für Tick-Arbeitsdaten, `Allocator.Persistent` nur für Match-Lebensdauer).
- Determinismus: Jobs werden innerhalb eines Ticks in fester Reihenfolge gescheduled und vollständig (`JobHandle.Complete()`) abgeschlossen, bevor der nächste Sim-Schritt liest. Kein Frame-übergreifendes Job-Scheduling im Sim-Pfad.
- `[BurstCompile]` auf allen Hotspot-Jobs; Burst Safety Checks und Leak-Detection in Development-Builds aktiv.
- **Parität:** Jede Burst-Variante muss dieselben Ergebnisse wie der Managed-Referenzpfad liefern (Hash-Vergleich in `Nova.Simulation.Tests`), weil `Nova.SimRunner` (D-036) die Managed-Variante ausführt. Abweichungen sind Desync-Vorstufen und blockieren den Merge.

## 4. ScriptableObject-Regeln (D-035, Research §3)

- SOs sind **Definitions-only**: keine zur Laufzeit veränderten Felder. Runtime-Zustand (HP, Produktionsfortschritt, Cooldowns) lebt ausschließlich im Sim-State. Verstoß-Beispiel, das im Review abzulehnen ist: ein SO, das "aktuelle Anzahl gebauter Einheiten" zählt.
- Vererbungshierarchien flach (max. 2 Ebenen); **Komposition vor Vererbung** (Unit-SO referenziert Weapon-SO, Ability-SO).
- Stabile IDs als Feld (`string`, Konvention in NamingConvention §8), Referenzen zwischen SOs per direktem Asset-Link (GUID-stabil), nie per Pfad-String.
- Zugriff zur Laufzeit ausschließlich über die `GameDatabase`-Registry, nicht über Szenen-Suchlauf.
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
| `Resources.Load` für Definitionsdaten | Pfad-Strings statt GUID-Referenzen (Research §3) | GameDatabase-Registry |
| LINQ, Closures mit Capture, Boxing in Hot Paths | GC im Tick (§2.4) | Vorallokierte Puffer, generische Constraints |
| `UnityEngine.Random` / `System.Random` im Sim-Pfad | Nicht seedbar/nicht deterministisch (D-033 Regel 4) | `ISimRandom` |
| `Time.deltaTime` / `Time.time` im Sim-Pfad | Frame-abhängig, bricht festen Tick (D-033 Regel 3) | Tick-Zähler, Tick-Dauer-Konstante |
| Coroutinen für Sim-Logik | Frame-getrieben, nicht tick-getrieben | Tick-basierte Zustandsmaschinen; Coroutinen nur für View-Choreografie |
| `public`-Felder in MonoBehaviours | Kapselungsbruch | `[SerializeField] private` + Property |

## Offene Punkte

- **Fixed-Point-Umstellung (Beta, D-033):** Bibliothekswahl und die konkrete Migrationsstrategie hinter dem Sim-Mathe-Typ sind Teil der Beta-MP-Arbeiten; die jetzige Regel (§2.3) sichert nur den Umsetzpunkt.
- **Paritäts-Nachweis Managed↔Burst:** Umfang der Hash-Tests (welche Systeme, welche Match-Fixtures) ist mit Testing.md abzustimmen; bis dahin gilt "jede Burst-Variante" als Review-Regel.
- **Analyzer-Enforcement:** `.editorconfig`, ggf. Roslyn-Analyzer (z. B. UnityEngine-Verbot im Sim-Projekt als Diagnose statt nur Kompilierfehler, Allokations-Warnungen) sind noch nicht beschafft/konfiguriert – Ziel Sprint 7.
- **Transzendentale im MVP:** Ob `Math.Sqrt` in Distanzberechnungen des MVP-Sim toleriert wird (Performance vs. Umstellungsaufwand), soll der Phase-0-Spike anhand echter Profile klären.

## Nächste Schritte

1. Konsistenzreview mit Architecture.md und Testing.md (Paritäts-Hash-Tests, Desync-Logging-Format).
2. Sprint 7: `.editorconfig` + Referenz-Beispieldateien (ein Command, ein SimSystem, ein SO-Schema) als Muster anlegen.
3. Analyzer-Bedarf bewerten (Roslyn vs. Review-Checkliste) und in Sprint-7-Backlog aufnehmen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Technical Director |
