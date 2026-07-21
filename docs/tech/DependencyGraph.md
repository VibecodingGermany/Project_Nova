# Abhängigkeitsgraph

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 3

## Zweck

Verbindliche Festlegung der erlaubten Abhängigkeitsrichtungen zwischen Schichten und Assemblies von Project Nova, inklusive Verbotsliste und Assembly-Definition-Abbildung (.asmdef). Grundlage für Code-Reviews und Architektur-Checks ab Sprint 7. Schichtenbeschreibung: [./Architecture.md](./Architecture.md), Moduldetails: [./ModuleOverview.md](./ModuleOverview.md).

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (Sim-Regeln), D-035 (Assembly-Struktur, kein DOTS), D-036 (SimRunner)
- [./Architecture.md](./Architecture.md), [./ModuleOverview.md](./ModuleOverview.md)
- [../research/Unity_BestPractices.md](../research/Unity_BestPractices.md)

## 1. Erlaubte Abhängigkeitsrichtungen

Grundsatz: Abhängigkeiten zeigen ausschließlich **nach unten** Richtung Simulation. Die Simulation kennt niemanden; alle kennen (höchstens) die Simulation. Querverbindungen innerhalb der Präsentation sind erlaubt, solange kein Rückgriff in Bridge/Sim-Interna erfolgt.

```
┌─────────────────────────────────────────────────────────────┐
│ Nova.Tools (Editor-only)                                    │
└──────────────┬──────────────────────────────────────────────┘
               │ (Editor)
┌──────────────▼──────────────┐   ┌───────────────────────────┐
│ Nova.UI                     │   │ Nova.Presentation         │
│ (HUD, Minimap; UI Toolkit)  │◄──│ (Camera, Selection,       │
└──────────────┬──────────────┘   │  UnitsView, VFX, FoW,     │
               │                  │  Audio)                   │
               │                  └─────────────┬─────────────┘
               │                                │
┌──────────────▼────────────────────────────────▼─────────────┐
│ Nova.Game (Bridge)                                          │
│ MatchSession, IMatchTransport/LocalLoopback,                │
│ Input→Command, Event-Dispatch                               │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
┌──────────────▼──────────────┐   ┌────────────▼──────────────┐
│ Nova.Data (SOs,             │   │ Nova.Simulation.Jobs      │
│ GameDatabase → Snapshot)    │   │ (Burst-Fast-Paths,        │
└──────────────┬──────────────┘   │  NativeArray-Spiegel)     │
               │                  └────────────┬──────────────┘
               │                               │ (nur Datentyp-Spiegel,
               │                               │  keine Sim-Interna-Logik)
┌──────────────▼───────────────────────────────▼──────────────┐
│ Nova.Simulation (Unity-frei, reines .NET)                   │
│ Core, Commands, Grid, Pathfinding, FoW, Economy, Combat,    │
│ Production, Research, AI, NeutralUnits, Superweapons,       │
│ Match/Session, Replay, Savegame                             │
└──────────────────────────────▲──────────────────────────────┘
                               │
                  ┌────────────┴────────────┐
                  │ Nova.SimRunner          │
                  │ (reine .NET-Konsole,    │
                  │  CI-Balancing, D-036)   │
                  └─────────────────────────┘
```

Erlaubt (zusammengefasst):

- `Nova.Game → Nova.Simulation`, `Nova.Game → Nova.Data`, `Nova.Game → Nova.Simulation.Jobs`
- `Nova.Data → Nova.Simulation` (nur Definitions-Datentypen für den `DefinitionSnapshot`)
- `Nova.Simulation.Jobs → Nova.Simulation` (nur öffentliche State-Datentypen; Spiegelung in NativeArrays)
- `Nova.Presentation → Nova.Game` (öffentliche Bridge-Verträge: Events, Snapshots, `ICommandSink`), `Nova.Presentation → Nova.Data`
- `Nova.UI → Nova.Game`, `Nova.UI → Nova.Data`, `Nova.UI → Nova.Presentation` (nur Camera/FoW-Textur)
- `Nova.Tools → Nova.Data` (+ UnityEditor), `Nova.SimRunner → Nova.Simulation`
- Sim-Module untereinander entlang der in [./ModuleOverview.md](./ModuleOverview.md) gelisteten Abhängigkeiten (z. B. Combat → FogOfWar, Economy → Grid); Richtung: fachlich höhere Module → Basis-Module, niemals zyklisch.

## 2. Verbotsliste

Verboten (Verstoß = Review-Blocker):

1. **`Nova.Simulation → UnityEngine` / UnityEditor / URP** (D-033 Regel 2, D-035). Kein `using UnityEngine;`, kein `UnityEngine.Random`, kein `Time.*`, kein `Physics.*` im Sim-Pfad. Durchgesetzt über fehlende Assembly-Referenzen (technisch unmöglich, nicht nur Konvention).
2. **`Nova.Simulation → Nova.Game/Data/Presentation/UI`** – die Simulation kennt keine höheren Schichten; Rückmeldung ausschließlich über View-Events/Snapshots.
3. **`Nova.Presentation`/`Nova.UI → Nova.Simulation` direkt** – Zugriff nur über die Bridge-Verträge in `Nova.Game`; keine Sim-Interna (keine `internal`-Umgehung via `InternalsVisibleTo`, außer für Test-Assemblies).
4. **Direkte State-Mutation von außen** – niemand außer Commands/Modul-Ticks schreibt Sim-State (D-033 Regel 1); Bridge/View erhalten Nur-Lese-Snapshots.
5. **Runtime-State in ScriptableObjects** – SOs sind Definitions-only; Laufzeitdaten gehören in den Sim-State (D-033 Regel 5; Vier-Säulen-Regel).
6. **`Nova.SimRunner → Unity-*`** – der Runner referenziert ausschließlich `Nova.Simulation` (D-036); Unity-Paket-Referenzen würden die reine .NET-Lauffähigkeit brechen (siehe Offene Punkte in [./Architecture.md](./Architecture.md) zum Burst-Thema).
7. **Zyklen zwischen Sim-Modulen** (z. B. Economy ↔ Production) – Kommunikation über Core-Mediatoren (Command/Event im selben Tick-Raster), nicht über gegenseitige Referenzen.
8. **Kein Unity Entities/DOTS-Package** in irgendeiner Assembly (D-035; Re-Evaluierung nach Unity 6.4).

## 3. Assembly-Definition-Abbildung

Physische Umsetzung im Unity-Projekt (`Assets/`). Test-Assemblies (`*.Tests`, EditMode/PlayMode) spiegeln die Referenzen ihrer Ziel-Assembly und dürfen zusätzlich `InternalsVisibleTo`-Ziele referenzieren.

| .asmdef | Referenzen (asmdef) | Unity-Referenzen | Plattform | Bemerkung |
|---|---|---|---|---|
| `Nova.Simulation` | – | **keine** | alle (auch Standalone-.NET) | `allowUnsafeCode` nur falls nötig; Kern aller Regeln |
| `Nova.Simulation.Jobs` | `Nova.Simulation` | Unity.Collections, Unity.Burst, Unity.Jobs (Packages) | alle | **kein UnityEngine-API-Aufruf**, nur Packages für Burst/Jobs |
| `Nova.Data` | `Nova.Simulation` | UnityEngine (ScriptableObject) | alle | Definitions-only-SOs, `GameDatabase` |
| `Nova.Game` | `Nova.Simulation`, `Nova.Data`, `Nova.Simulation.Jobs` | UnityEngine | alle | Bridge/Session/Transport |
| `Nova.Presentation` | `Nova.Game`, `Nova.Data` | UnityEngine, URP, RenderGraph | alle | volle Unity-Nutzung erlaubt (D-035) |
| `Nova.UI` | `Nova.Game`, `Nova.Data`, `Nova.Presentation` | UnityEngine, UI Toolkit (uGUI nur World-Space) | alle | |
| `Nova.Tools` | `Nova.Data` | UnityEngine, UnityEditor | **Editor only** | kein Runtime-Code |
| `Nova.Simulation.Tests` | `Nova.Simulation` | – | Editor (EditMode) + .NET-Testprojekt | Paritäts-/Determinismus-Tests |
| `Nova.Game.Tests` / `Nova.Presentation.Tests` | jeweilige Ziel-Assemblies | UnityEngine Test Framework | Editor | |
| `Nova.SimRunner` (eigenes .NET-Projekt, außerhalb von `Assets/`) | `Nova.Simulation` (Projekt-/DLL-Referenz) | **keine** | Standalone .NET | CI-Balancing (D-036) |

Durchsetzung: Die Trennung wird primär über fehlende Referenzen erzwungen (Regeln 1, 3, 6 sind so technisch unmöglich). Zusätzlich werden in `Testing.md` (Sprint 7) statische Architektur-Checks definiert (Namespace-/Referenz-Scan in CI: kein `UnityEngine`-Using in `Nova.Simulation`-Quellen, keine Direktreferenz Presentation→Simulation).

## Offene Punkte

1. **Burst-Brücke:** Ob `Nova.Simulation.Jobs` Ergebnisse bit-identisch zum reinen C#-Pfad liefern muss (SimRunner-Parität, D-036) oder ob der Runner bewusst den C#-Pfad nutzt, ist unentschieden → Offener Punkt 1 in [./Architecture.md](./Architecture.md), Entscheidung nach Phase-0-Spike im DecisionLog.
2. **SimRunner-Bezug der Sim-Assembly:** Quelltext-Sharing (Shared Project/Linked Files) vs. DLL-Referenz aus dem Unity-Build – CI-Detail, Festlegung im Sprint-7-Setup (`Testing.md`).
3. **UI→Presentation-Referenz** (Minimap braucht FoW-Textur/Camera) erzeugt eine Kante, die bei wachsender UI zur Schichten-Unschärfe führen kann; ggf. später über Bridge-Mediatoren ersetzen – Beobachtung im Architecture Review.
4. Test-Assembly-Strategie für `Nova.Simulation` außerhalb von Unity (reines .NET-Testprojekt vs. Unity Test Framework EditMode) offen → `Testing.md`.

## Nächste Schritte

- .asmdef-Gerüst gemäß §3 im Sprint-7-Projekt-Setup anlegen und Referenzmatrix 1:1 umsetzen.
- CI-Architektur-Check (Namespace-Scan) in `Testing.md` spezifizieren.
- Verbotsliste als Review-Checkliste in `CodingGuidelines.md` übernehmen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Technical Director |
