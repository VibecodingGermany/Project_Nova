# Performance-Budget (Frame & Tick)

**Version:** 0.1.1 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Performance Engineer | **Sprint:** 3

## Zweck

Dieses Dokument operationalisiert die Qualitätsziele aus TPD §15 („stabile 60 FPS auf typischer Gaming-Hardware, mindestens 30 FPS auf schwächerer Hardware, mehrere hundert aktive Einheiten, geringe GC-Spitzen") in ein verbindliches, messbares Frame- und Tick-Budget. Es definiert die Aufteilung des 16,6-ms-Frames auf Simulation, Rendering (CPU/GPU), UI und Reserve, die Skalierungsziele je Meilenstein (100 / 300 / 500 Einheiten), die Mess-Methodik inklusive Windows-Referenzhardware und die vier aus den OpenQuestions übernommenen Pflicht-Validierungen am Phase-0-Spike. Verbindlich für alle Engineering-Rollen; Eingabe für [MemoryBudget.md](MemoryBudget.md), [AssetBudget.md](AssetBudget.md) und die Sprint-7-Implementierungsplanung.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-006 (Unity 6.3 LTS + URP), D-033 (fester Sim-Tick 10 Hz, Rendering entkoppelt), D-034 (Pathfinding-CPU-Budget ≤2–4 ms), D-035 (Burst/Jobs-Hotspots, keine GC-Allokationen im Tick), D-036 (Nova.SimRunner für Headless-Messungen), D-042.1 (Sim-Tick-Gesamtbudget ≤8 ms mit Unterbudgets PF ≤4 ms / FoW ≤1,0 ms / Rest-Sim ≤3 ms, führend Architecture.md)
- [../production/OpenQuestions.md](../production/OpenQuestions.md) – vier Pflicht-Validierungen am Phase-0-Spike (§ Offene Punkte)
- [../research/Pathfinding.md](../research/Pathfinding.md) – CPU-Budget-Arbeitsannahme §4.1
- [../research/Animation_Audio_UI.md](../research/Animation_Audio_UI.md) – Animator-vs.-Playables-Frage, Animations-LOD
- [../research/FogOfWar.md](../research/FogOfWar.md) – Sicht-Tick-Kostenmodell
- [./MemoryBudget.md](MemoryBudget.md), [./AssetBudget.md](AssetBudget.md) – Schwesterdokumente
- [./Pathfinding.md](Pathfinding.md), [./Architecture.md](Architecture.md) – Schwester-TDDs aus Sprint 3

## 1. Zielwerte

| Kennzahl | Ziel | Minimum | Quelle |
|---|---|---|---|
| Framerate | 60 FPS (16,6 ms/Frame) | 30 FPS (33,3 ms/Frame) | TPD §15 |
| Sim-Tick-Frequenz | 10 Hz (D-033) | – | D-033 |
| FoW-Sicht-Tick | 5–10 Hz | 5 Hz | GDD FoW |
| Aktive Einheiten | 500 (Release) | 100 (MVP) | GDD/TPD |
| GC-Allokation im Sim-Tick | 0 B | 0 B | D-035 |
| RAM (Desktop-Release) | ≤ 4 GB | – | [MemoryBudget.md](MemoryBudget.md) |

Das 30-FPS-Minimum ist ein Degradationsziel für schwächere Hardware (TPD §15: „skalierbare Grafikqualität"): Es wird primär über GPU-Qualitätsstufen und View-seitige Reduktion (Animations-LOD, Partikel-LOD, FoW-Tick auf 5 Hz) erreicht – **das Sim-Tick-Budget gilt unverändert**, da die Simulation aus Determinismus-Gründen (D-033) nicht qualitätsskalierbar ist.

## 2. Frame-Budget-Aufteilung (60 FPS, 16,6 ms)

Ein Sim-Tick fällt bei 10 Hz auf jeden 6. Frame. Der Tick muss an dem Frame, auf dem er läuft, vollständig in sein Zeitfenster passen (kein implizites Spreading über Folge-Frames; Time-Slicing ist *innerhalb* des Ticks erlaubt, z. B. Pfad-Anfragen über mehrere Ticks verteilt, vgl. research/Pathfinding.md §4.1).

| Posten | Tick-Frame (jeder 6.) | Normal-Frame | 30-FPS-Modus | Bemerkung |
|---|---|---|---|---|
| Sim-Tick gesamt | ≤ 8,0 ms | 0 ms | ≤ 8,0 ms | Unterbudgets (D-042.1, führend [Architecture.md](Architecture.md)): Pathfinding ≤4 ms (D-034), FoW ≤1,0 ms (an FoW-Tick-Frames), Rest-Sim (Kampf, Wirtschaft, Produktion, KI-Command-Verarbeitung) ≤3 ms |
| Rendering CPU (Main Thread) | ≤ 4,0 ms | ≤ 4,0 ms | ≤ 8,0 ms | Draw-Call-Aufbereitung, Culling, BatchRendererGroup/Resident Drawer, Animation-Update |
| GPU | ≤ 8,0 ms | ≤ 8,0 ms | ≤ 20,0 ms | URP inkl. Full Screen Pass (FoW-Overlay), Shadow-Update reduziert |
| UI (UI Toolkit) | ≤ 1,0 ms | ≤ 1,0 ms | ≤ 2,0 ms | HUD, Minimap, Healthbar-Overlay (gebatchtes Mesh) |
| Audio | ≤ 0,5 ms | ≤ 0,5 ms | ≤ 1,0 ms | AudioService-Abstraktion, Stimmen-Limit |
| Reserve / Engine-Overhead | ≥ 3,1 ms | ≥ 11,1 ms | ≥ 2,3 ms | Puffer für Spitzen (Zerstörungsevents, Superwaffen), OS-Jitter |

Messregel: Budgets gelten als **P95 über 60 s repräsentatives Match-Szenario** auf der Referenzhardware (§4). Einzelne Ausreißer (P99) dürfen das 1,5-Fache des Postenbudgets nicht überschreiten.

## 3. Einheiten-Skalierungsziele

Die Budgets gelten jeweils am oberen Ende der Einheiten-Skala des betreffenden Meilensteins:

| Meilenstein | Aktive Einheiten | Kartengröße | Besondere Last |
|---|---|---|---|
| MVP (Phase 1) | 100 | S (128 m) | 1 Fraktion, 1 Karte, einfache Separation |
| Alpha (Phase 2) | 300 | M (192 m) | 3 Fraktionen, ORCA, Superwaffen-VFX |
| Release (Phase 3) | 500 | L (256 m) | 500 Einheiten + Gebäude + neutrale Einheiten, volle Zerstörbarkeit |

Wachstumsannahme (im Spike zu verifizieren): Pathfinding/Separation skaliert überlinear (O(n log n) Spatial Hashing), Rest-Sim linear, FoW nahezu konstant (quellenbasiert, ≤ ca. 600 Sichtquellen). Sollte der 300-Einheiten-Alpha-Messwert das Budget übersteigen, wird **vor** dem Release-Ausbau nachoptimiert oder das Release-Ziel neu verhandelt (Eskalation an Technical Director, kein stilles Budget-Stretching).

## 4. Mess-Methodik

- **Referenzhardware (Pflicht):** Alle Budget-Aussagen beziehen sich auf einen festgelegten Windows-Referenz-PC (Desktop primär, D-006). Vorschlag zur Festlegung in Sprint 4: Mittelklasse-Gaming-PC Baujahr 2021 (z. B. Ryzen 5 5600 / Core i5-11400, RTX 3060 / RX 6600, 16 GB RAM) – exakte Spezifikation ist ein Offener Punkt. Apple-Silicon-Macs sind Entwicklungsplattform und werden zusätzlich gemessen, ersetzen aber keine Windows-Messung.
- **Standalone statt Editor:** Messungen ausschließlich in Standalone-Development-Builds (IL2CPP-Release-Kandidat für finale Zahlen; Mono-Development-Build für Iteration). Editor-Messungen sind nicht budget-relevant (Overhead verfälscht Sim- und Render-Posten).
- **Messkette:** Unity Profiler (Timeline-View) + `ProfilerRecorder` auf definierte Marker (pro Sim-Subsystem eigener `ProfilerMarker`: `Sim.Pathfinding`, `Sim.FoW`, `Sim.Combat`, `Sim.Economy`, `Sim.AI`), Frame Timing Manager für CPU-/GPU-Gesamtzeiten, RenderDoc/PIX für GPU-Posten-Aufschlüsselung.
- **Reproduzierbare Szenarien:** Dank D-033 (Commands als einzige Mutation, seedbarer PRNG) werden Benchmarks als aufgezeichnete Command-Streams/Replays definiert – identischer Verlauf auf jeder Maschine. Pflicht-Szenarien: (a) Baseline-Basebuilding 10 min, (b) Massenschlacht mit Einheiten-Obergrenze des Meilensteins, (c) Superwaffen-Einschlag + Gebäudezerstörung (Spitzenlast), (d) FoW-Stress (max. Sichtquellen).
- **Sim-only-Messung:** `Nova.SimRunner` (D-036) misst Tick-Zeiten headless in CI; daraus entsteht die Trend-Historie pro Commit (Regression >10 % auf einem Budget-Posten = Build-Warnung).
- **Budget-Überwachung im Build:** Laufzeit-Budget-Monitor (Debug-Overlay) zeigt Ist vs. Budget pro Posten; Überschreitungen werden geloggt.

## 5. Schnittstellen-Skizze (API-Design, keine Implementierung)

```csharp
namespace Nova.Performance
{
    // Budget-Definition, datengetrieben via SO in der GameDatabase (Vier-Säulen-Prämisse).
    public sealed class PerformanceBudgetSO : ScriptableObject
    {
        public Milestone Milestone;                 // MVP | Alpha | Release
        public BudgetEntry[] Entries;               // siehe unten
        public int TargetUnitCount;                 // 100 / 300 / 500
    }

    public struct BudgetEntry
    {
        public string MarkerName;                   // z. B. "Sim.Pathfinding"
        public BudgetScope Scope;                   // SimTick | FrameCpu | Gpu | Ui | Audio
        public float BudgetMs;
        public float P99LimitMs;                    // i. d. R. 1.5f * BudgetMs
    }

    // Laufzeit-Abfrage (View-/Tool-Schicht, Unity-abhängig erlaubt).
    public interface IBudgetMonitor
    {
        BudgetSample GetSample(string markerName);  // letztes P50/P95/P99
        bool IsOverBudget(string markerName);
        event Action<BudgetViolation> ViolationLogged;
    }

    // Headless-Pendant im SimRunner (D-036): rein .NET, kein Unity.
    public interface ITickProfiler
    {
        void BeginSection(string name);
        void EndSection(string name);
        TickProfileResult Flush(int tickIndex);
    }
}
```

## 6. Phase-0-Spike: Pflicht-Validierungen (aus OpenQuestions übernommen)

Vier Messungen sind Gate-Kriterien für den Phase-0-Abschluss; jede hat ein binäres Erfolgskriterium auf der Windows-Referenzhardware (Standalone-Build):

| # | Validierung | Erfolgskriterium | Bei Scheitern |
|---|---|---|---|
| V1 | **Fixed-Point-Determinismus ARM ↔ x86:** identische Command-Streams erzeugen bit-identische State-Hashes auf Apple Silicon und Windows-x86 | 10.000 Ticks ohne Divergenz | Beta-MP-Plan (D-033) anpassen; ggf. Software-Fixed-Point-Bibliothek oder plattformspezifische Builds evaluieren |
| V2 | **URP GPU Resident Drawer für bewegte Einheiten:** Nutzen bei 500 dynamisch bewegten Skinned/Static-Meshes vs. klassisches Batching | Rendering-CPU-Posten ≤ 4 ms im Massenschlacht-Szenario; sonst Fallback | Fallback: manuelle BatchRendererGroup-Nutzung oder Draw-Reduktion über LOD/Impostor |
| V3 | **Animator vs. Playables bei 500 Einheiten** (vgl. research/Animation_Audio_UI.md) | Animations-Anteil am Rendering-CPU-Posten ≤ 1,5 ms inkl. Animations-LOD | Wechsel auf Playables-API/Animancer für Massen-Infanterie; Mecanim nur für Helden/Nahaufnahmen |
| V4 | **Pathfinding-CPU-Budget ≤ 2–4 ms** (D-034): Flow-Field-Fill + Separation bei 500 Agenten auf L-Karte (256 m) | P95 `Sim.Pathfinding` ≤ 4 ms | Dokumentierter Fallback greift: A* Pathfinding Project (Granberg) evaluieren (D-034) |

Die Spike-Ergebnisse fließen als Version 0.2.0 in dieses Dokument (Budget-Nachjustierung nur mit Begründung und D-ID-Referenz).

## Offene Punkte

- **Budget-Spannung Sim-Tick:** entschieden (D-042.1) – das Sim-Tick-Gesamtbudget beträgt **≤ 8 ms** (führend: [Architecture.md](Architecture.md)); Unterbudgets Pathfinding ≤4 ms (D-034), FoW ≤1,0 ms, Rest-Sim ≤3 ms. Die Spannung „D-034 ≤2–4 ms PF bei nur 4 ms Gesamt-Sim" ist damit aufgelöst; §2 ist entsprechend angeglichen.
- **Exakte Spezifikation der Windows-Referenzhardware** muss beschaffbar und verbindlich fixiert werden (Vorschlag §4); Owner: Lead Performance Engineer, Sprint 4.
- **GPU-Budget-Aufteilung** (Shadows vs. Full Screen Pass vs. Partikel) kann erst nach dem Rendersequenzen-TDD (terminiert Sprint 6, OpenQuestions) final beziffert werden; die 8 ms sind bis dahin Obergrenze ohne Unterposten.
- **KI-Command-Verarbeitung** (Utility-Director + HTN + Squad-BTs) hat noch kein eigenes Unterbudget im Sim-Tick; hängt vom KI-TDD ab (Sprint 3). Vorläufig im Rest-Sim-Posten enthalten.
- **30-FPS-Modus:** Ob die Sim bei 30 FPS weiterhin mit 10 Hz tickt (längere Frames, gleicher Tick) oder ob zusätzliche View-Degradationen definiert werden, ist mit Game Design abzustimmen (Eingabelatenz-Gefühl).

## Nächste Schritte

1. Sprint 4: Referenzhardware-Spezifikation festlegen und beschaffen; Messkette (ProfilerMarker-Namenskonvention, Szenario-Replays) mit Simulation-Architektur-TDD abstimmen.
2. Phase 0 (Spike): V1–V4 durchführen, Ergebnisse als v0.2.0 hier und in research/Pathfinding.md dokumentieren.
3. Sprint 5–6: CI-Integration der SimRunner-Tick-Messung (Regressionsschwelle 10 %); Debug-Budget-Overlay im Development-Build.
4. Sprint 6: GPU-Unterbudgets nach Rendersequenzen-TDD nachziehen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Performance Engineer |
| 0.1.1 | 2026-07-21 | Sim-Tick-Gesamtbudget auf ≤8 ms angehoben mit Unterbudgets (D-042.1, führend Architecture.md); offener Punkt „Budget-Spannung Sim-Tick" als entschieden markiert | Lead Technical Director |
