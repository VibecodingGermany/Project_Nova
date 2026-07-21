# Unity Best Practices für ein RTS – Validierung von D-002 (Unity/C#/URP)

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 1

## Zweck

Dieses Dokument validiert die in Sprint 0 per D-002 als Ausgangslage übernommene Stack-Entscheidung des TPD (Unity, C#, URP, Desktop-first Windows/macOS) anhand des Marktstands 2025/2026. Es konsolidiert die Unity-Best-Practices, die für Project Nova konkret relevant sind: Versionswahl, Render-Pipeline, ScriptableObjects-Datenmodell, Projektstruktur, Performance-Disziplin (Pooling, GC, Profiling) für 100–500+ Einheiten bei 60 FPS, macOS/Apple-Silicon-Entwicklungsrealität und Build-Pipeline. Ergebnis ist eine Entscheidungsvorlage: D-002 bestätigen oder revidieren.

## Abhängigkeiten

- [../analysis/KnowledgeBase.md](../analysis/KnowledgeBase.md) – §6 (verbindlicher Stack), §12 (Qualitätsziele), §9 (Phasen)
- [../production/OpenQuestions.md](../production/OpenQuestions.md) – Q-013 (Simulations-/MP-Modell), Q-014 (Pathfinding), Q-015 (ECS/DOTS vs. MonoBehaviour)
- [../production/DecisionLog.md](../production/DecisionLog.md) – D-002 (Stack-Ausgangslage)
- Quelle B (TPD): §11, §15 (Architektur-Leitplanken, Qualitätsziele)

## 1. Unity-Version: Stand 2025/2026 und Empfehlung

Seit Unity 6 (Oktober 2024, ehemals 2023.3) veröffentlicht Unity jährliche LTS-Linien. Stand Juli 2026:

| Version | Status | Support bis | Bewertung für Project Nova |
|---|---|---|---|
| Unity 2022.3 LTS | Alt-LTS | abgelaufen/Ende 2025 | Verworfen: kein GPU Resident Drawer, kein Render Graph als Standard, kein STP |
| Unity 6.0 LTS (6000.0.x) | LTS | Oktober 2026 | Verworfen: Support läuft mitten in der Produktionsphase aus |
| Unity 6.3 LTS (6000.3.x) | **aktuelles LTS (seit Dez 2025)** | **Dezember 2027** (+1 Jahr Enterprise) | **Empfohlen**: 2 Jahre Support decken MVP + Vertical Slice; produktionserprobt |
| Unity 6.4+ (Update-Releases) | kurzfristige Releases | wenige Monate | Verworfen: keine LTS-Stabilität; 6.2 wurde mit Erscheinen von 6.3 bereits eingestellt |

Quellen: [Unity 6 Releases & Support](https://unity.com/releases/unity-6/support), [Unity 6.3 LTS Released (80.lv)](https://80.lv/articles/unity-6-3-lts-released), [Best Unity Version 2026 (Makaka)](https://makaka.org/unity-tutorials/best-version).

**Empfehlung: Unity 6.3 LTS (6000.3.x, konkrete Patch-Version beim Projekt-Setup pinnen).** 6.3 LTS bringt zusätzlich ~50 % schnellere Build-Zeiten, 97–99 % reduzierte TypeTree-Memory-Nutzung, DLSS4-Super-Resolution und das Platform Toolkit ([daily.dev/Unity 6.3](https://daily.dev/posts/unity-6-3-lts-is-now-available-d0zrriknr), [Unity Manual: New in 6.3](https://docs.unity3d.com/6000.5/Documentation/Manual/WhatsNewUnity63.html)). Regel: Patch-Updates innerhalb der 6000.3-Linie nur bei Bedarf (Bugfix-Bedarf), Minor-/Major-Upgrades nur zwischen Meilensteinen.

## 2. Render-Pipeline: URP vs. HDRP vs. Built-in für ein stilisiertes RTS

| Kriterium | URP | HDRP | Built-in |
|---|---|---|---|
| Ziel des Projekts (Stylized Military Sci-Fi, Lesbarkeit vor Realismus) | Sehr gut geeignet: Shader Graph, Renderer Features, Custom Passes für Selection-Rings, FoW-Overlay | Überdimensioniert: PBR/Volumetrik/Raytracing bringt für den Stil keinen Mehrwert | Funktioniert, aber Legacy |
| Performance 100–500+ Einheiten | GPU Resident Drawer, GPU Occlusion Culling, SRP Batcher, STP-Upscaler – alle Unity-6-Leistungsfeatures verfügbar | Gleiche Features, aber höhere Basis-Framekosten | Kein SRP Batcher, kein GPU Resident Drawer |
| Entwicklungskosten | Moderat; große Asset-Store-Auswahl ist URP-kompatibel (wichtig für TPD §7.1 "kaufen statt bauen") | Hoch (komplexere Lighting-/Material-Workflows) | Niedrig, aber sinkende Tool-Unterstützung |
| Zukunftssicherheit | Referenz-Pipeline von Unity, aktiv weiterentwickelt | Aktiv, aber High-End-Nische | Wartungsmodus, keine neuen Features |
| Sekundärplattformen (iPadOS/WebGL laut TPD §17) | Einzige realistische Option | Nicht geeignet | Eingeschränkt |

Quellen: [Unity Manual: Render pipeline feature comparison](https://docs.unity3d.com/6000.5/Documentation/Manual/render-pipelines-feature-comparison.html), [HDRP vs. URP vs. Built-in 2025 (Canixel)](https://canixelarts.com/blog?post_id=64), [Unity vs. Unreal vs. Godot 2026](https://tech-insider.org/unity-vs-unreal-vs-godot-2026/).

**URP ist für Project Nova die richtige Pipeline und wird mit D-002 mitbestätigt.** RTS-relevante Konkretisierungen:

- **GPU Resident Drawer + GPU Occlusion Culling** (Unity 6): GPU-driven Rendering instanzierbarer Objekte; Unity nennt bis zu 50 % CPU-Framezeit-Reduktion bei vielen GameObjects. Für hunderte gleichartige Einheiten-/Gebäude-Meshes der zentrale Hebel ([Unite 2024 Keynote](https://unity.com/blog/unite-2024-keynote-wrap-up), [Unity 6 Feature Highlights](https://forum.unity.com/threads/unity-6-beta-2023-3-feature-highlights.1532590/)). Hinweis: Nutzerberichte zeigen, dass der Nutzen szenenabhängig ist und gemessen werden muss ([Unity Discussions: Resident Drawer performance](https://discussions.unity.com/t/resident-drawer-performance/1554861)) – Pflichtversuch in Phase 0 (Spike).
- **SRP Batcher** ist in URP Standard und optimiert Set-Pass-Calls bei gleicher Shader-Variante; GPU Instancing für identische Mesh+Material-Kombinationen (Einheiten desselben Typs). Faustregel aus der Praxis: SRP-Batcher-kompatible Shader bauen, Instancing per Benchmark entscheiden ([Unity Discussions: SRP Batcher vs. GPU Instancing](https://discussions.unity.com/t/srp-batcher-and-gpu-instancing/918509)).
- **Render Graph** ist in URP seit Unity 6 Standard-Framework für eigene Render Passes (Selection-Rings, Aetherium-Glow, FoW) ([Zengo: Unity 6 URP](https://zengo.eu/en/blog/unity-6-new-features-urp-developers)).
- **STP (Spatial-Temporal Post-Processing)**: plattformübergreifender Upscaler, relevant für schwächere Desktop-GPUs und spätere Tablet-Ports.

## 3. ScriptableObjects-Datenmodell: Muster, Stärken, Grenzen

Das TPD (§11) schreibt ScriptableObjects (SO) für Einheiten-/Gebäude-/Waffen-/Tech-Werte vor. Das ist ein etabliertes Muster (bekannt u. a. durch Ryan Hipples Unite-2017-Talk, [roboryantron.com](http://www.roboryantron.com/2017/10/unite-2017-game-architecture-with.html)), aber mit bekannten Fallstricken:

**Stärken für Project Nova:**
- Datengetriebenheit ohne eigene Toolchain: Designer/Balancer editieren Werte im Inspector, Änderungen sind sofort spielbar – ideal für 3 asymmetrische Fraktionen und Iteration im MVP.
- Assets statt Szenenobjekte: Referenzen überleben Szenenwechsel, Prefabs referenzieren SOs direkt; kein FindObjectOfType-/Singleton-Kleister.
- Versionierbar als YAML-Text (passt zu GitHub + LFS-Strategie des TPD).

**Grenzen und Gegenmaßnahmen:**
- **Laufzeit-Mutation bleibt im Editor bestehen:** Zur Laufzeit geänderte SO-Werte überleben den Play-Modus im Editor. Konsequenz: SOs sind bei Nova ausschließlich **statische Definitionen** (Read-only zur Laufzeit); dynamischer Zustand (HP, Ammo, Produktionsfortschritt) lebt in separaten Runtime-Instanzen (Plain-C#-Objekte/Structs), die das SO referenzieren. Nie Gameplay-State in SOs schreiben.
- **Serialisierungsgrenzen:** Keine Polymorphie über Standard-Serialisierung; `[SerializeReference]` existiert, ist aber brüchig bei Refactoring (Klassen-/Namespace-Umbenennungen verlieren Daten). Vererbungshierarchien für Unit/Gebäude-Definitionen flach halten (max. 2 Ebenen) und Komposition (SO referenziert Weapon-SO, Ability-SO) der Vererbung vorziehen ([Unity Discussions: SO für Stats](https://discussions.unity.com/t/using-scriptableobjects-for-stats-with-different-but-also-shared-stats/928713)).
- **Savegames:** SOs sind Projekt-Assets, kein Runtime-State – Savegames brauchen ohnehin eigenes Serialisierungsformat (JSON/Binary) mit Versionsfeld (TPD §15 fordert Savegame-Versionierung); SOs liefern nur die Definition, per stabiler ID (string/GUID-Feld, nicht Asset-Pfad) referenziert.
- **Referenz-Probleme bei Skalierung:** Bei ~150+ Definitionen (Einheiten, Gebäude, Waffen, Tech über 3 Fraktionen) werden Ordner-Struktur, Naming Convention und ein zentrales Registry-SO (Datenbank-Pattern: eine `GameDatabase`, die alle Definitionen indiziert) Pflicht, sonst entsteht Asset-Chaos. Referenzen per direktem Asset-Link (GUID-stabil), nicht per `Resources.Load`/Pfad-Strings.

## 4. Projektstruktur und Assembly Definitions

Empfohlene Struktur (konkretisiert TPD §11/§12):

```
Assets/
  Nova/
    Core/            # Basistypen, Events, Interfaces        → Nova.Core.asmdef
    Data/            # SO-Definitionen (Schemas)             → Nova.Data.asmdef
    Simulation/      # reine C#-Logik, Unity-unabhängig      → Nova.Simulation.asmdef
    Gameplay/        # MonoBehaviours, Systeme               → Nova.Gameplay.asmdef
    Presentation/    # Rendering, VFX, Audio, UI             → Nova.Presentation.asmdef
    Editor/          # Custom Inspectors, Validatoren        → Nova.Editor.asmdef (Editor-only)
  Tests/             # EditMode/PlayMode                     → Nova.Tests.asmdef (Test-Assemblies)
```

- **Assembly Definitions** senken Kompilierzeiten (nur geänderte Assemblies werden neu gebaut – bei einem wachsenden RTS-Codebase spürbar) und erzwingen die TPD-Trennung Gameplay/Präsentation über Referenz-Richtung: `Presentation` → `Gameplay` → `Simulation` → `Data` → `Core`, nie rückwärts.
- **`Nova.Simulation` ohne UnityEngine-Abhängigkeiten halten** (soweit möglich; `Unity.Mathematics` ist erlaubt): Voraussetzung für deterministische Simulation und späteren autoritativen Server (Q-013) sowie für EditMode-Unit-Tests ohne Szene.
- Test-Assemblies mit `references` nur auf die getesteten Assemblies; CI führt EditMode-Tests headless aus.

## 5. Object Pooling

Bei 100–500+ Einheiten plus Projektilen, VFX und Damage-Numbers sind `Instantiate`/`Destroy` im Match-Betrieb tabu (GC-Spitzen widersprechen TPD §15). Konkret:

- **`UnityEngine.Pool` (`ObjectPool<T>`, `ListPool<T>` etc.)** ist seit 2021 im Core enthalten – kein Eigenbau, keine Asset-Store-Pools nötig. Einsatz für: Projektile, Muzzle-Flash/Impact-VFX, UI-Schadenszahlen, Selection-Decals.
- **Einheiten/Gebäude:** beim Spawn aus Pool holen statt instantiieren; Pool-Größen pro Einheitentyp aus den Daten-SOs ableiten (Legion-Masse treibt Pool-Obergrenze hoch).
- Warm-up beim Match-Start (Ladebildschirm), nicht im laufenden Spiel.

## 6. GC-Vermeidung

Leitplanken für den Code-Standard (Detail ausformuliert in der Coding-Guideline ab Sprint 3):

- Keine Allokationen in `Update`-Pfaden: keine LINQ-Queries, keine String-Konkatenation, keine Closures/Lambdas mit Capture, kein Boxing (`object`-Parameter, nicht-generische Collections) in Hot Paths.
- Wiederverwendbare Buffer (`List<T>`, `NativeArray<T>`) als Member statt lokaler Allokation; `ListPool<T>` für kurzlebige Listen.
- Events (ereignisbasierte Kommunikation laut TPD) über generische `Action<T>` mit Struct-Payloads, nicht über String-Namen oder `SendMessage`.
- Inkrementelles GC (Standard seit Unity 2021) aktiv lassen; GC-Spitzen per Profiler-Modul "GC Alloc" im Spike messen.

## 7. Profiling-Workflow

Verbindlicher Workflow (ab Phase 0 Spike etablieren):

1. **Unity Profiler** (CPU/GPU/Memory-Module) im Editor für schnelle Iteration; **immer** zusätzlich in Development Builds auf Zielhardware messen – Editor-Performance ist nicht repräsentativ (Overhead, andere GC-Dynamik).
2. **Frame Timing Manager** + `FrameTimingManager.CaptureFrameTimings()` für automatisierte 60-FPS-Regressionstests (16,6 ms Budget) im Spike.
3. **Memory Profiler-Package** für Leak-/Fragmentierungsanalysen vor Meilensteinen.
4. **Frame Debugger** und **Rendering Debugger** zur Draw-Call-/Batch-Analyse (SRP Batcher Wirksamkeit, GPU Resident Drawer Coverage).
5. Profiler Analyzer zum Vergleich von Captures (vor/nach Optimierung).
6. Referenz-Messkette des Spikes: 500 Einheiten, Kampfszenario, 5 Minuten Capture auf (a) Apple-Silicon-Mac und (b) Windows-Referenz-PC; Ergebnis dokumentiert Phase 0 ab.

## 8. macOS / Apple Silicon: Entwicklungsrealität

- Der Unity Editor läuft **nativ auf Apple Silicon** (seit 2021.2); **Metal** ist Standard-Grafik-API auf macOS/iOS. Entwicklung auf Apple Silicon ist also First-Class, kein Rosetta-Kompromiss ([Unity Manual: macOS requirements](https://docs.unity3d.com/6000.1/Documentation/Manual/macos-requirements-and-compatibility.html)).
- Unity beendet den Support für **Intel-Macs nach Unity 6.7 LTS** – Apple's Plattformrichtung bestätigt die Nova-Zielsetzung, macOS bedeutet faktisch Apple Silicon ([Unity Discussions, Nov 2025](https://discussions.unity.com/t/lets-celebrate-together-2026-and-still-no-fully-native-apple-silicon-support/1696717)).
- macOS-Builds: Architecture `arm64` (Apple Silicon) als Standard; Universal Binary nur falls Intel-Macs explizit gefordert werden (derzeit nicht Teil der TPD-Zielplattformen).
- Praxis-Restrisiken (Einschätzung, im Spike zu verifizieren): Windows bleibt der primäre Absatzmarkt für RTS – ein Windows-Referenzsystem (oder CI-Runner) für regelmäßige Builds/Profiling ist trotz Mac-Entwicklung Pflicht. Notarization/Signing für macOS-Distribution (außerhalb Steam) benötigt Apple-Developer-Account und Xcode-Kommandozeilen-Tools.

## 9. Build-Pipeline-Optionen

| Option | Projektbezogene Vorteile | Nachteile |
|---|---|---|
| **A) BuildPipeline-API + Batch Mode + CI (GitHub Actions, self-hosted Mac-Runner)** | Volle Kontrolle, kein Zusatzabo, passt zu GitHub-Strategie (TPD §12); `-batchmode -buildTarget StandaloneWindows/OSX` skriptbar; EditMode-Tests im gleichen Workflow | Eigenwartung; Windows-Builds auf Mac-Runner möglich, aber Windows-Profilhardware trotzdem nötig |
| B) Unity Build Automation (Cloud) | Zero-Infrastruktur, Multi-Plattform aus der Cloud | Laufende Kosten, weniger Kontrolle, Abhängigkeit von Unity-Service-Verfügbarkeit |
| C) Lokale manuelle Builds aus dem Editor | Null Setup | Nicht reproduzierbar, keine Regressionssicherheit – für ein Team-Projekt indiskutabel |

**Empfehlung: A** (BuildPipeline-Skript + GitHub Actions), aufgeweicht um B nur falls die Runner-Wartung zum Engpass wird. Addressables für Content-Updates sind erst ab Phase 2 relevant und bleiben offen (TPD §16).

## 10. Kritische Prüfung von D-002: Ist Unity/C#/URP 2026 noch belastbar?

**Geprüfte Alternativen (projektbezogen, nicht generisch):**

| Alternative | Vorteile für Nova | Verwerfungsgrund |
|---|---|---|
| **(a) Unity 6.3 LTS + URP + C# (Status quo D-002)** | Team-Stack laut TPD; URP passt zum Stil; GPU Resident Drawer adressiert direkt das 100–500-Einheiten-Ziel; Asset-Store-Strategie (TPD §7.1: kaufen statt bauen) ist nur in Unity voll wirksam; C#-Simulation ist später serverseitig wiederverwendbar (autoritativer Server, Q-013); native Apple-Silicon-Entwicklung | – (Empfehlung) |
| **(b) Unreal Engine 5** | Nanite/Lumen, starke Default-Visuals; RTS-Referenzen existieren | Für "Stylized, Lesbarkeit vor Realismus" Überdimensionierung; C++/Blueprints statt C#-Ökosystem des Teams; 5 % Royalty ab 1 Mio. USD Umsatz; Asset-Store-Kaufstrategie des TPD müsste komplett neu aufgesetzt werden; Server-Simulation in C++ teurer |
| **(c) Godot 4** | Kostenlos/Open Source, keine Politik-Risiken | 3D-Performance und Tooling für RTS mit 500+ Einheiten 2026 weiterhin am wenigsten belegt; C#-Support zweitklassig gegenüber GDScript; Asset-Markt für die TPD-Kaufstrategie deutlich kleiner; (Einschätzung: Risiko für Phase-0-Performance-Ziele zu hoch) |
| **(d) Full-DOTS/ECS innerhalb Unity** | Maximaler Performance-Headroom, Burst/Jobs; Netcode for Entities | Steile Lernkurve, geringere Ökosystem-Reife; für MVP-Disziplin überschießend → Detailprüfung gehört zu Q-015, nicht zur Engine-Frage |

**Politik-/Reputationsrisiko Unity (ernsthaft geprüft):** Die Runtime-Fee-Krise 2023 ist aufgearbeitet: Die Gebühr wurde im September 2024 vollständig gestrichen und gilt für keine Unity-Version mehr ([Unity: Canceling the Runtime Fee](https://unity.com/blog/unity-is-canceling-the-runtime-fee), [CG Channel](https://www.cgchannel.com/2024/09/unity-scraps-controversial-runtime-fee-but-raises-prices/)); Preismodell ist wieder reines Abo (8 % Erhöhung Jan 2025, Personal kostenlos bis 200 k USD Umsatz, Pro darüber). Verbleibendes Restrisiko ist Vertrauen/Kommunikation, nicht Technik oder Kosten – für ein Projekt in dieser Größenordnung tragbar, aber als Risiko in der Risikoanalyse zu führen.

## Empfehlung

**D-002 bestätigen, konkretisiert als neue Entscheidungsvorlage (D-006-Kandidat):**

> **Kontext:** Validierung des TPD-Stacks (D-002) gegen Marktstand 2025/2026.
> **Alternativen:** (a) Unity 6.3 LTS + URP + C# (mit konkretisierten Best Practices); (b) Wechsel zu Unreal Engine 5; (c) Wechsel zu Godot 4; (d) Unity mit Full-DOTS/ECS als Basisarchitektur.
> **Entscheidung:** (a). Projektversion: **Unity 6.3 LTS (6000.3.x, Patch gepinnt)**, Render-Pipeline **URP** (Render Graph, SRP Batcher, GPU Resident Drawer im Spike verifizieren), Datenmodell **ScriptableObjects als reine Definitions-Assets + separatem Runtime-State**, Assembly-strukturierter Aufbau mit Unity-unabhängiger `Nova.Simulation`.
> **Begründung:** Alle drei Verwerfungsgründe sind projektspezifisch belastbar: Unreal (b) ist für den stilisierten Look überdimensioniert, verwirft die C#-Codebasis-/Server-Strategie und die Asset-Kaufstrategie des TPD; Godot (c) hat für 500+ Einheiten in 3D die geringste Beleglage und den kleinsten Asset-Markt; Full-DOTS (d) widerspricht der MVP-Disziplin (Prüfung als Hybrid-Option läuft über Q-015). Unitys Runtime-Fee ist seit Sept 2024 Geschichte; 6.3 LTS ist bis Dezember 2027 supported und deckt MVP, Vertical Slice und Produktionsphase ab. GPU Resident Drawer, SRP Batcher und Render Graph adressieren exakt das 100–500+-Einheiten-Ziel auf Desktop-Hardware.
> **Konsequenzen:** Kein Engine-Wechsel; Phase-0-Spike muss GPU Resident Drawer + Pooling + Profiling-Messkette (500 Einheiten, 60 FPS, Mac + Windows) belegen; Q-013/Q-014/Q-015 werden in dedizierten Research-Dokumenten entschieden; Reputationsrisiko Unity in RiskAnalysis aufnehmen.

## Offene Punkte

- Konkrete 6000.3-Patch-Version wird erst beim Projekt-Setup (Sprint 3) gepinnt – Patch-Stabilität dann anhand der Unity-Issue-Tracker-Lage prüfen.
- Belastbare Zahlen zu GPU Resident Drawer mit *dynamischen* (bewegten) RTS-Einheiten sind dünn; Nutzen muss der Spike messen, nicht die Literatur.
- Ob `Nova.Simulation` vollständig UnityEngine-frei bleiben kann, hängt von Q-013 (Determinismus-Anforderung) ab – Festlegung nach Q-013-Entscheidung.
- Odin Inspector o. ä. Editor-Tools für die SO-Datenbank wurden nicht bewertet (Budget-Frage, Sprint 3).

## Nächste Schritte

1. Orchestrator: Empfehlung als D-006 in den DecisionLog übernehmen (oder Revision diskutieren).
2. Research Q-015 (ECS/DOTS vs. MonoBehaviour vs. Hybrid) – dieses Dokument liefert die Unity-seitige Grundlage (Assembly-Trennung, Simulation-Layer), ersetzt aber nicht die DOTS-Detailprüfung.
3. Phase-0-Spike-Backlog: Messkette 500 Einheiten / 60 FPS (Mac + Windows), GPU Resident Drawer A/B-Test, Pooling-Grundgerüst, Profiler-Baseline.
4. RiskAnalysis: Eintrag "Unity-Unternehmenspolitik/Lizenzänderungen" (Restrisiko, niedrige Eintrittswahrscheinlichkeit, hoher Impact).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Research-Erstfassung | Lead Technical Director |
