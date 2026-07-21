# Memory-Budget

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Performance Engineer | **Sprint:** 3

## Zweck

Dieses Dokument legt das verbindliche RAM-Budget für Project Nova (Desktop-Release ≤ 4 GB) fest, zerlegt es in Speicherbereiche (Assets, Sim-State, Grid-Layer, FoW-Bitmasken, Engine-Overhead) und definiert die GC-Politik (0 B pro Sim-Tick) inklusive Pool-Strategien sowie die Bewertung von Streaming/Addressables. Es operationalisiert die TPD-§15-Ziele „kontrollierter Speicherverbrauch" und „geringe Garbage-Collection-Spitzen" und ist Eingabe für die Sprint-7-Implementierung und die Asset-Prüfung in [AssetBudget.md](AssetBudget.md).

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (vollständig serialisierbarer State), D-034 (Integer-Grid 1-m-Tiles, 3 Clearance-Radien, Flow Fields), D-035 (kein GC im Tick, UnityEngine.Pool), D-036 (SimRunner)
- [../research/Pathfinding.md](../research/Pathfinding.md) – Grid-Layer-Modell, Flow-Field-Speicherabschätzung
- [../research/FogOfWar.md](../research/FogOfWar.md) – Bitmask-Datenstruktur (`values`/`visited` pro Team)
- [./PerformanceBudget.md](PerformanceBudget.md) – Frame-/Tick-Budgets, Mess-Methodik
- [./AssetBudget.md](AssetBudget.md) – Asset-seitige Speicherbudgets (Texturen, Meshes, Audio)
- [./Pathfinding.md](Pathfinding.md), [./Architecture.md](Architecture.md) – Schwester-TDDs aus Sprint 3 (FoW als Subsystem von `Nova.Simulation`)

## 1. Gesamtbudget

| Kennzahl | Budget | Bemerkung |
|---|---|---|
| RAM gesamt (Desktop-Release, Match auf L-Karte, 500 Einheiten) | ≤ 4 GB | P95 während 35-min-Match (längstes Szenario laut GDD: 20–35 min) |
| Managed Heap (C# Objekte, View + Services) | ≤ 512 MB | ohne native Unity-Engine-Objekte |
| Native/Engine (Unity-Runtime, URP, RenderTargets, Physik) | ≤ 1,0 GB | Messbasis Phase-0-Spike |
| Assets im Speicher (Texturen, Meshes, Audio, Animation) | ≤ 1,8 GB | Detailbudget: [AssetBudget.md](AssetBudget.md) |
| Sim-State + Grid-Infrastruktur + FoW | ≤ 100 MB | §2–§4 |
| Reserve (Fragmentierung, OS-Seitiges, Wachstum Beta-MP) | ≥ 0,6 GB | Lockstep-Ringpuffer, Replay-Aufzeichnung |

## 2. Sim-State (Nova.Simulation, D-033/D-035)

Vollständig serialisierbarer State, Unity-frei, Array-of-Structs-Layout:

| Bestandteil | Abschätzung | Rechnung |
|---|---|---|
| Einheiten (500 aktiv) | ≤ 1 MB | 500 × ~1–2 KB (Position, Bewegung, Kampf, Orders, Statusflags, Fixed-Point-Felder ab Beta) |
| Gebäude (12 Typen × ≤ 8 Spieler, inkl. Module/Trümmer-Zustand) | ≤ 0,5 MB | ≤ 500 Instanzen × ~1 KB |
| Projektile, Effekte, Aetherium-Feldzustand, Commander/Elite-Metadaten | ≤ 1 MB | gepoolte feste Kapazitäten |
| Command-Ringpuffer + Replay-Aufzeichnung (35 min × 10 Hz) | ≤ 20 MB | 21.000 Ticks × ≤ 1 KB Commands/Tick (Obergrenze, typisch weit darunter) |
| **Summe Sim-State** | **≤ 25 MB** | inkl. Sicherheitszuschlag |

Savegame-/Serialisierungs-Puffer (Snapshot des Gesamt-State) doppelt vorhalten: ≤ 50 MB transient, nur während Save/Load.

## 3. Grid-Layer (D-034, Abschätzung bis zur Finalisierung von tech/Pathfinding.md)

Basis: uniformes Integer-Grid, 1-m-Tiles. Worst Case = L-Karte 256 × 256 m = 65.536 Zellen (M: 192² = 36.864; S: 128² = 16.384).

| Layer | Datentyp/Zelle | L-Karte | Anmerkung |
|---|---|---|---|
| Statische Begehbarkeit/Terrainkosten | u8 | 64 KB | einmal geladen |
| Höhenlevel (für Höhen-LoS-FoW ab Phase 2) | u8 | 64 KB | |
| Clearance (3 Radienklassen, D-034) | 3 × u8 | 192 KB | max. passierbarer Radius pro Zelle |
| Dynamische Belegung (Einheiten, Dirty-Flags) | u8 + Dirty-Bitset | 72 KB | pro Tick aktualisiert |
| Aetherium-Feld (Typ, Wachstumsstufe, Überernte) | u8 | 64 KB | |
| Aktive Flow Fields (Kosten + Richtung) | 2 Byte + 1 Byte/Zelle | ~200 KB **pro Feld** | Begrenzung über Feld-Cache nötig |
| **Flow-Field-Cache, gedeckelt ≤ 32 aktive Felder** | | **≤ 6,5 MB** | LRU-Eviction; Ziel-Clustering reduziert Feldzahl (research/Pathfinding.md §2.2) |
| **Summe Grid** | | **≤ 8 MB** | |

Falls tech/Pathfinding.md eine höhere Zellauflösung oder zusätzliche Layer (z. B. Dichtefelder, Einflusskarten für den KI-Director) festlegt, wird diese Tabelle aktualisiert – die 100-MB-Gesamtkappappe bleibt verbindlich.

## 4. FoW-Bitmasken (research/FogOfWar.md §B)

Grid-Auflösung 1 m (D-034-Doppelnutzung), 3 Zustände über zwei Bitmasken-Arrays (`values` = aktuell sichtbar, `visited` = erforscht) als Team-Bitmask (bis 8 Spieler = 1 Byte/Zelle/Array):

| Bestandteil | L-Karte (256²) | Anmerkung |
|---|---|---|
| `values` + `visited` | 2 × 64 KB = 128 KB | 8-Spieler-Bitmask |
| Radar-/Stealth-Zusatzplanes | ≤ 128 KB | GDD-Radar-Mechanik |
| GPU-Sicht-Textur (R8/RG8, upsampled) | ≤ 0,5 MB VRAM | Upload ~65 KB/Sicht-Tick, vernachlässigbar |
| **Summe FoW (CPU-Seite)** | **≤ 0,5 MB** | |

## 5. GC-Politik (D-035)

**Verbindliche Regeln:**

1. **0 B Managed-Allokation pro Sim-Tick** in `Nova.Simulation` und allen Hotspots – enforced über CI-Messung (SimRunner meldet `GC.GetAllocatedBytesForCurrentThread()`-Delta pro Tick; >0 = Build-Fehler) und Code-Review.
2. **Kein UnityEngine im Sim-Pfad** (D-033) ⇒ Sim-Allokationen sind rein managed; native Unity-Allokationen entstehen nur in der View-Schicht.
3. **Pools statt new:** Commands, Projektile, Schadensereignisse, Pfad-Anfragen und Flow-Field-Puffer kommen aus festkapazitisierten Pools (`UnityEngine.Pool.ObjectPool<T>` in der View, eigene ringbasierende Pools in der Sim). Pool-Kapazitäten sind Budget-Zahlen (z. B. Projektile ≤ 2.000, Pfad-Anfragen ≤ 256 in Flight).
4. **Structs & Arrays in Hotpaths:** keine LINQ-Queries, keine Closures/Lambdas mit Capture, keine `foreach` über `IEnumerable`-Interfaces, keine String-Erzeugung im Tick (Logging im Sim-Pfad nur ringgepuffert als Enum-/ID-Einträge).
5. **Event-Bus/Puffer:** Sim→View-Kommunikation über vorgepufferte Struct-Listen (double-buffered), keine Delegates mit Allokation pro Event.
6. **View-Schicht:** GC freundlich, aber diszipliniert – Ziel ≤ 1 KB/Frame transient, damit Gen-0-Collections selten und <0,5 ms bleiben (Deckel im Frame-Budget, siehe PerformanceBudget.md).
7. **GC-Modus:** Incremental GC aktiv (Unity-Standard), damit Sammlungen über Frames amortisiert werden; `GC.Collect()`-Aufrufe außerhalb von Ladebildschirmen sind verboten.

## 6. Streaming & Addressables – Bewertung

- **Match-Loading statt Streaming:** RTS-Matches laden ihr gesamtes Asset-Set im Ladebildschirm (3 Fraktionen komplett, Karte, VFX, Audio). Echtes Runtime-Streaming (wie in Open-World-Titeln) ist nicht erforderlich und würde die View-Schicht unnötig komplizieren – **kein Runtime-Streaming im MVP/Alpha**.
- **Addressables: empfohlen, aber zurückgestuft.** Vorteile (Fraktions-/Karten-Bundles, saubere Lade/Entlade-Grenzen zwischen Matches, Grundlage für spätere DLCs/Biome-Roadmap 1/4/8/12) sprechen dafür; der Overhead (Build-Pipeline, Lernkurve) spricht für Einführung **ab Phase 2 (Alpha)**, nicht im MVP. MVP lädt klassisch per Szenen-/Ressourcenstruktur, die Referenzierung erfolgt aber bereits über die GameDatabase-Registry (Vier-Säulen-Prämisse), sodass der Addressables-Umstieg keine API-Änderung erzwingt.
- **Texture Streaming (Unity Texture Mipmap Streaming):** nur bei Überschreitung des VRAM-Budgets evaluieren; auf Desktop mit ≤1,8 GB Asset-Budget voraussichtlich unnötig.
- **Audio:** Musik gestreamt (Streaming-LoadType), SFX dekomprimiert im Speicher oder komprimiert-in-memory nach Größenklasse (Details: [AssetBudget.md](AssetBudget.md) §Audio).
- **Entladen zwischen Matches:** Match-Ende ⇒ vollständiges Unload aller Match-Assets + `Resources.UnloadUnusedAssets()` im Menü-Übergang (einzige erlaubte Stelle für teure Cleanup-Calls); verhindert RAM-Kriech über Match-Folgen.

## 7. Schnittstellen-Skizze (API-Design, keine Implementierung)

```csharp
namespace Nova.Performance
{
    // Kapazitäten & Speicherbudgets, datengetrieben (GameDatabase).
    public sealed class MemoryBudgetSO : ScriptableObject
    {
        public PoolCapacity[] Pools;      // z. B. { "Projectile", 2000 }, { "PathRequest", 256 }
        public int MaxActiveFlowFields;   // 32 (Deckel §3)
        public long ManagedHeapBudgetBytes;
    }

    public struct PoolCapacity { public string PoolId; public int Capacity; }

    // CI-/Laufzeit-Prüfung: Allokationsdelta pro Tick (SimRunner, D-036).
    public interface IAllocationProbe
    {
        long BytesAllocatedLastTick { get; }   // Muss 0 sein (Regel 1, §5)
    }
}
```

## Offene Punkte

- **Grid-Layer-Finalliste** (Dichtefelder, KI-Einflusskarten, Bauplatzierungs-Maske) hängt von tech/Pathfinding.md und dem KI-TDD ab; obige Abschätzung ist der Deckel, nicht die Finalliste.
- **Flow-Field-Cache-Größe (32 Felder)** ist eine Annahme; der Phase-0-Spike (V4, siehe PerformanceBudget.md) muss zeigen, ob 32 aktive Ziele für reale Match-Situationen (8 Spieler × mehrere Angriffsgruppen) ausreichen.
- **Fixed-Point-Umstellung (D-033, Beta)** kann Struct-Größen im Sim-State ändern; Abschätzung §2 muss dann neu vermessen werden.
- **Replay/Spectator-Vollaufzeichnung** (research/FogOfWar.md empfiehlt serverseitige Vollaufzeichnung) würde den FoW-Verlauf zusätzlich puffern (~128 KB/Sicht-Tick × 21.000 Ticks ≈ 2,7 GB unkomprimiert) – nur mit Kompression/Delta-Kodierung machbar; Umfang der Replay-Funktion ist noch nicht entschieden (kein D-Eintrag).
- **macOS-RAM-Verhalten** (Unified Memory, Swap-Aggressivität) auf 8-GB-Macs ist ungemessen; Mindest-RAM-Anforderung des Spiels (8 vs. 16 GB) muss nach Phase-0-Messung festgelegt werden.

## Nächste Schritte

1. Phase 0: Native/Engine-Baselines messen (leere Szene, dann Massenschlacht-Szenario) → Tabelle §1 mit Ist-Werten versehen.
2. Sprint 7: Pool-Kapazitäten und `MemoryBudgetSO`-Einträge beim ersten vertikalen System-Durchstich anlegen; CI-Allokationsprobe (Regel 1) aktivieren.
3. Alpha (Phase 2): Addressables-Einführung mit Fraktions-Bundles; Entscheidung zu tech/Pathfinding.md-Layerliste hier nachziehen.
4. Beta: Fixed-Point-Umstellung und Lockstep-Ringpuffer neu vermessen; Replay-Kompressionskonzept (falls Replay-Feature beschlossen).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Performance Engineer |
