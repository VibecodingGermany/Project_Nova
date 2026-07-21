# Testing-Strategie

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead QA Engineer | **Sprint:** 3

## Zweck

Definiert die Test-Strategie von Project Nova: Test-Pyramide, Determinismus- und Golden-Master-Tests auf dem Unity-freien Sim-Kern, KI-vs-KI-Nachtläufe im SimRunner, Desync-Test-Strategie (ab Beta), Coverage-Ziele, Testdaten-Disziplin, CI-Pipeline und den Bug-/Regressionsprozess. Verbindlich für alle Code-Beiträge ab Sprint 7 (Implementierung). Ziel: Die Architekturregeln aus D-033 (Determinismus-Fähigkeit, Command-only-Mutation, Sim/View-Trennung) werden nicht nur gebaut, sondern dauerhaft automatisiert bewacht.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-006 (Unity 6.3 LTS), D-033 (Sim-/MP-Modell, 5 Regeln), D-034 (Pathfinding), D-035 (OOP + Burst, `Nova.Simulation`), D-036 (`Nova.SimRunner`)
- [../research/Multiplayer_Simulation.md](../research/Multiplayer_Simulation.md) – Lockstep-/Desync-Grundlagen
- [../research/KI_Architektur.md](../research/KI_Architektur.md) – KI-Schichten, DifficultyProfileSO
- [../gamedesign/Balancing.md](../gamedesign/Balancing.md) – Messpipeline Stufe 1/2 (Metriken, Kadenz, Wertesets)
- [../gamedesign/VictoryConditions.md](../gamedesign/VictoryConditions.md) – `MatchResult`-Kennzahlen
- [./Deployment.md](./Deployment.md) – CI-/Build-Infrastruktur, Runner

## Test-Pyramide

| Ebene | Werkzeug | Laufumgebung | Umfang-Ziel | Kadenz |
|---|---|---|---|---|
| 1. Sim-Unit-Tests | NUnit (Unity Test Framework, EditMode) | `Nova.Simulation`-Assembly, kein Unity nötig | größte Testmasse (~60–70 % aller Tests) | bei jedem Commit/PR |
| 2. Sim-Integrationstests | NUnit EditMode über `Nova.SimRunner`-Host | headless, vollständige Matches (beschleunigt) | Kernloop, Ökonomie, Kampf, Sieg/Niederlage | PR + Nightly |
| 3. Golden-Master-Replay-Tests | Replay-Fixtures (Seed + Command-Log → State-Hash) | headless | kuratierte Szenarien-Matrix | PR (Pflicht) |
| 4. PlayMode-UI-Tests | Unity Test Framework, PlayMode | Editor/Player, sparsam | nur kritische UI-Flüsse | Nightly |
| 5. Performance-Regressionstests | Profiler-gestützte Mess-Szenen + Sim-Benchmarks | self-hosted Runner | wenige Budget-Tests | Nightly |

Begründung der Verteilung: Der fachliche Kern liegt in `Nova.Simulation` (D-035) und ist ohne Unity testbar (D-033 Regel 2, D-036). View- und UI-Code trägt wenig Regel-Logik; PlayMode-Tests sind langsam und flaky-anfällig, daher bewusst sparsam (nur: Match-Start-Flow, Bau-Menü, Ergebnis-Screen, Savegame-Laden).

### Ebene 1: Sim-Unit-Tests (EditMode)

- Testen reine Sim-Logik: Command-Verarbeitung, Ökonomie (Harvester-Zyklen, Lager-Kapazität, Überernte), Schadens-/Rüstungssystem, FoW-Bitmask-Logik, Flow-Field-Aufbau, PRNG-Sequenzen.
- Keine UnityEngine-APIs im Sim-Pfad (D-033 Regel 2) heißt: Diese Tests laufen als plain .NET/NUnit und können zusätzlich außerhalb von Unity ausgeführt werden (siehe CI).
- Jede Command-Art (D-033 Regel 1) erhält mindestens einen Test: Ausführung, Validierung/Ablehnung, Undo-freie Zustandsänderung.

### Ebene 2: Sim-Integrationstests

- Vollständige Matches headless über denselben Host wie der `Nova.SimRunner` (D-036): zwei KI-Instanzen (Mittel-Schwierigkeit, unverrauscht – Balancing.md), fester Seed, beschleunigter Tick.
- Prüfen fachliche Invarianten über ganze Matches: kein negatives AE-Konto, Elite-Limits (D-015), Superwaffen-Limit (D-023), Vernichtungs-Regel (D-031.4/D-032.2), Match-Terminierung spätestens bei Zeitlimit.
- Ziel-Laufzeit pro Match-Test < 10 s (Sim ohne Rendering), damit die Suite PR-tauglich bleibt.

### Ebene 3: Golden-Master-Replay-Tests (Determinismus-Wächter)

Kernidee (D-033 Regeln 1, 4, 5): Aus `(MapId, Seed, Command-Log)` muss jederzeit exakt derselbe State-Verlauf reproduzierbar sein. Der Test spielt ein aufgezeichnetes Command-Log ab und vergleicht den kanonischen State-Hash an definierten Tick-Marken.

```csharp
namespace Nova.Simulation.Testing
{
    // Kanonische, serialisierbare Momentaufnahme (D-033 Regel 5).
    public interface IStateHasher
    {
        // Stabiler Hash über den vollständigen Sim-State (nicht über View-Daten).
        StateHash ComputeHash(in SimState state);
    }

    // Versionierte Replay-Fixture als Testdaten-Artefakt (JSON im Repo).
    public sealed record ReplayFixture(
        string FixtureId,        // z. B. "eco-harvest-3player-v1"
        int    DataVersion,      // Schema-Version des Command-Logs
        string MapId,
        int    Seed,             // eigener seedbarer PRNG (D-033 Regel 4)
        int    PlayerCount,
        IReadOnlyList<TimedCommand> Commands,   // Tick + Command (einzige Mutation, Regel 1)
        IReadOnlyList<HashCheckpoint> Checkpoints // Tick-Marke + erwarteter StateHash
    );

    public sealed record HashCheckpoint(int Tick, StateHash Expected);
}
```

- Fixture-Pflege: Bei jeder bewussten Sim-Änderung (Balancing-Werteset, Regel-Fix) werden Fixtures neu aufgezeichnet und der Hash-Stand im selben PR committed; unbeabsichtigte Hash-Abweichung = Test-Rot = Regressions-Befund.
- Fixture-Matrix: mindestens 1× Ökonomie, 1× Kampf mit Konter, 1× FoW/Detektion, 1× Aetherium-Ausbreitung/Überernte, 1× volles Match bis Sieg; je Kartengröße S/M/L (128/192/256) mindestens eine Fixture.
- **Bekannte Einschränkung MVP:** Mit Float-Arithmetik (D-033: Float im MVP erlaubt) sind Hashes nur auf derselben Plattform/Compiler-Konfiguration stabil. Cross-Plattform-Hash-Vergleich (ARM macOS ↔ x86 Windows) wird erst mit der Fixed-Point-Umstellung (Beta) Pflicht – bis dahin dokumentiert der Test seine Plattform.

### Ebene 4: PlayMode-UI-Tests (sparsam)

- Nur End-to-End-Glückspfade: Spiel starten → Match beginnt → UI zeigt Ressourcen → Gebäude platzieren → Match beenden → Ergebnis-Screen zeigt `MatchResult`-Daten.
- Keine pixelgenauen Vergleiche, keine Timing-abhängigen Animationstests.

### Ebene 5: Performance-Regressionstests

- Sim-Benchmarks headless: Tick-Dauer bei 500 Einheiten (Ziel: 60 FPS-Budget, Sim-Tick 10 Hz), Pathfinding-Budget ≤ 2–4 ms (D-034), FoW-Sicht-Tick (5–10 Hz) – jeweils mit Warn-/Fail-Schwellen gegen Baseline.
- Rendering-Budgets (GPU, Batches) laufen auf dem self-hosted Runner als Nightly-Mess-Szene; Schwellen als Trend-Warnung, nicht als harter PR-Blocker (GPU-Messungen sind umgebungsabhängig).

## KI-vs-KI-Nachtläufe (Balancing-Pipeline Stufe 2)

Der `Nova.SimRunner` (D-036) ist Pflicht-Träger der Balancing-Messpipeline Stufe 2 ([../gamedesign/Balancing.md](../gamedesign/Balancing.md)): seeded, command-basiert, ohne Renderer.

- **Kadenz/Umfang:** Nightly in CI, ≥ 200 Matches je Matchup-Cluster (Balancing.md), Schwierigkeit Mittel, gespiegelte Startpositionen zur Halbierung des Map-Bias.
- **Auswertung:** Der Runner aggregiert je Lauf die `MatchResult`-Struktur ([../gamedesign/VictoryConditions.md](../gamedesign/VictoryConditions.md)) plus Stufe-2-Metriken: Winrate je Matchup (Zielband 45–55 %), Matchdauer-Median (Korridor 20–35 min, D-010), Zeit bis erster Angriff, Strategiearchetyp-Verteilung, First-Expansion-Zeit.

```csharp
namespace Nova.SimRunner
{
    // Ergebnis-Datensatz eines Nachtlaufs (JSON-Artefakt, Basis der BAL-Einträge).
    public sealed record SimRunReport(
        string RunId,            // CI-Run + Werteset-Version ("balance-v0.x")
        string BalanceSetVersion,
        int    MatchesTotal,
        IReadOnlyList<MatchupStats> Matchups  // Winrate, Matchdauer-Median, ...
    );
}
```

- Reports werden als CI-Artefakt abgelegt und im Balance-Changelog (`BAL-xxx`, Balancing.md) als Datenquelle referenziert. Wertänderungen > ±10–15 % erfordern Simulations-Begründung aus ≥ 200 Matches (Balancing.md) – der Nachtlauf liefert genau diese Evidenz.
- Jede Fixture/Report-Versionierung folgt dem Werteset: Ein Report ist nur zusammen mit seiner `balance-v0.x`-Version interpretierbar.

## Desync-Test-Strategie (ab Beta, D-033-Zielarchitektur)

- **Hash-Sync-Probe:** Ab der Lockstep-Einführung senden Clients periodisch (alle N Ticks, konfigurierbar) ihren `StateHash` an den Command-Relay; Divergenz = Desync-Fund. Debug-Builds erlauben Tick-für-Tick-Hashing zur Eingrenzung.
- **Cross-Plattform-Matrix:** Desync-Tests laufen explizit ARM-macOS ↔ x86-Windows (Pflicht-Validierung aus dem Phase-0-Spike: Fixed-Point-Determinismus ARM↔x86). Voraussetzung ist die Fixed-Point-Umstellung (fester Teil der Beta-MP-Arbeiten, D-033) – vorher sind Cross-Plattform-Desync-Tests nicht aussagefähig.
- **Desync-Forensik:** Bei Divergenz werden Seed, Command-Log und erster divergierender Tick als Replay-Fixture konserviert; die Fixture wird zum Reproduktions-Test (Regression-Dauergast in Ebene 3).
- **MVP-Vorläufer:** Schon im MVP laufen Ebene-3-Tests plattformübergreifend als *diagnostische* (nicht blockierende) Jobs, um Float-Abweichungen früh sichtbar zu machen.

## Coverage-Ziele

| Bereich | Ziel | Messung |
|---|---|---|
| `Nova.Simulation` (Sim-Core) | ≥ 80 % Zeilenabdeckung | Unity Code Coverage (EditMode) + NUnit-Lauf außerhalb Unity |
| Command-Verarbeitung & PRNG | 100 % der öffentlichen Command-Typen | Test-Inventar je Command |
| View/Präsentation, UI | kein Coverage-Ziel; Smoke-Tests (Ebene 4) | – |
| Third-Party/Asset-Store-Code | ausgenommen | – |

Coverage ist PR-Gate nur für `Nova.Simulation`; Verschlechterung > 2 Prozentpunkte gegen `develop` ist reviewpflichtig.

## Testdaten (SO-Fixtures)

- Definitions-only-Prinzip (Vier-Säulen): Testdaten sind **eigene ScriptableObject-Fixture-Sets** (reduzierte `GameDatabase` mit Test-Definitionen) unter einem Test-Ordner außerhalb der Produktiv-Registry; kein Runtime-State in SOs.
- EditMode-Tests instanziieren SOs zur Laufzeit (`ScriptableObject.CreateInstance`) statt Assets zu laden, wo immer möglich – kein Asset-Datenbank-Zugriff im Test = schnelle, stabile Läufe.
- Balance-relevante Tests referenzieren das versionierte Werteset (`balance-v0.x`), damit Test-Aussagen und Nachtlauf-Reports denselben Datenstand abbilden.
- Produktiv-Definitionen werden durch statische Lint-Tests geprüft (Balancing.md Stufe 1: DPS/AE, EHP/AE, Konter-Matrix, Pflichtfelder der 12 Gebäudetypen / ~90 Einheiten).

## CI-Pipeline (GitHub Actions)

| Job | Trigger | Inhalt | Laufzeit-Budget |
|---|---|---|---|
| `editmode-tests` | PR + push auf main/develop | Sim-Unit-Tests, Lint Stufe 1, Coverage-Gate Sim-Core | < 15 min |
| `replay-tests` | PR + push | Golden-Master-Matrix (Ebene 3), plattformgleich | < 10 min |
| `integration-tests` | PR (label-abhängig) + Nightly | Sim-Integrationstests (Ebene 2) | < 30 min |
| `simrunner-nightly` | Nightly | KI-vs-KI ≥ 200 Matches/Cluster, Report-Artefakt | < 4 h |
| `playmode-ui` | Nightly | Ebene 4 auf self-hosted Runner | < 45 min |
| `performance` | Nightly | Ebene 5, Trend-Report | < 1 h |
| `build-matrix` | PR (ausgewählte) + Release-Branches | Windows + macOS Builds (Details: [./Deployment.md](./Deployment.md)) | < 1 h |

- EditMode-Tests auf `Nova.Simulation` laufen zusätzlich als reine `dotnet test`-Ausführung ohne Unity-Editor (D-036-Nebenprodukt) – schnellstes Feedback (< 3 min) und Lizenz-unabhängig.
- Flaky-Policy: Ein Test, der 2× in Folge nicht reproduzierbar fehlschlägt, wird quarantäniert (Issue mit Label `flaky`), blockiert aber nicht dauerhaft den Merge; Quarantäne-Tests haben eine 2-Sprint-Frist zur Behebung oder Löschung.

## Bug-/Regressionsprozess

1. **Reproduktion sichern:** Jeder Sim-Bug wird vor dem Fix als scheiternder Test festgehalten – als Replay-Fixture (falls aus Match/Replay) oder als Sim-Unit-Test. Kein Fix ohne roten Test.
2. **Fix + Grün:** Der Fix macht den Test grün; Fixture-Hashes werden nur bei bewusster Verhaltensänderung neu aufgezeichnet (mit Begründung im PR).
3. **Dauerregression:** Der Test wandert in die Standard-Suite; Desync-/Match-Bugs werden zusätzlich als Golden-Master-Fixture kuratiert.
4. **Triage-Klassen:** `blocker` (Sim-Inkorrektheit, Crash, Datenverlust), `major` (Regelverletzung ohne Crash), `minor` (View/UI). Blocker stoppen den Release-Kandidaten (Checkliste in [./Deployment.md](./Deployment.md)).

## Savegame-Migrations-Tests

- Savegames sind serialisierter Sim-State + Metadaten (D-033 Regel 5) mit expliziter `SaveVersion`. Jede Schema-Änderung erhöht die Version und liefert eine Migration `v(n) → v(n+1)`.
- **Pflicht-Test je Migration:** Referenz-Savegames aller noch unterstützten Altversionen werden als Test-Artefakte vorgehalten; der Test lädt, migriert kaskadierend auf die aktuelle Version und verifiziert per State-Hash (Ebene 3), dass das migrierte Spiel fortsetzbar und deterministisch identisch fortzusetzen ist.
- Kein stilles Droppen: Wird eine Altversion nicht mehr unterstützt, ist das ein dokumentierter Eintrag in den Release-Notes und Teil der Release-Checkliste.

## Offene Punkte

- **Coverage-Tooling:** Unity Code Coverage Package vs. externe .NET-Coverage (z. B. coverlet) für die Unity-freie `Nova.Simulation`-Assembly – Tool-Wahl in Sprint 7 am lauffähigen Setup entscheiden.
- **PlayMode-UI-Testframework:** Unity Test Framework allein vs. Ergänzung um ein UI-Toolkit-Test-Hilfspaket – nach erstem UI-Toolkit-Prototyp (Sprint 7) bewerten; bis dahin Ebene 4 minimal halten.
- **Float-Hash-Stabilität:** Ob Ebene-3-Hashes im MVP bereits editorübergreifend (Windows/macOS-CI) stabil sind, ist empirisch unklar; der Phase-0-Spike (Fixed-Point-Validierung ARM↔x86) liefert die Daten. Bis dahin sind Cross-Plattform-Hash-Jobs nur diagnostisch (s. Desync-Strategie).
- **Performance-Baselines:** Schwellen für Ebene 5 (Sim-Tick-Budget bei 500 Einheiten, FoW-Tick) können erst am Phase-0-Spike-/Sprint-7-Messstand final kalibriert werden; vorläufige Anker: Pathfinding ≤ 2–4 ms (D-034), 60 FPS Gesamtbudget.
- **Desync-Probe-Protokoll:** Intervall N und Hash-Transport im Command-Relay werden erst mit Networking.md/Replication.md (D-033-Konsequenz) final definiert.

## Nächste Schritte

- Sprint 7: `Nova.Simulation`-Testprojekt + `dotnet test`-CI-Job als erstes lauffähiges Artefakt; erste Replay-Fixture ("eco-harvest") mit `IStateHasher`.
- Sprint 7: `Nova.SimRunner`-Report-Format (`SimRunReport`) gemeinsam mit Balancing-Verantwortlichen gegen Stufe-2-Metriken abnehmen.
- Sprint 7: Coverage-Gate (≥ 80 % Sim-Core) in der PR-Pipeline aktivieren.
- Beta-Vorbereitung: Desync-Test-Matrix und Cross-Plattform-Hash-Pflicht in diesen Plan aufnehmen (abhängig von Fixed-Point-Umstellung, D-033).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead QA Engineer |
