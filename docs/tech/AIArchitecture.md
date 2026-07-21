# KI-Architektur (Technical Design)

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead AI Programmer | **Sprint:** 3

## Zweck

Technische Spezifikation der Drei-Schichten-KI aus [../research/KI_Architektur.md](../research/KI_Architektur.md): (1) Utility-Director (strategisch), (2) HTN-light Plan-Executor (taktisch), (3) Squad-Behavior-Trees (operativ), gekoppelt über ein Blackboard. Festgelegt werden Assembly-Einordnung, Schnittstellen (C#-Skizzen, keine Implementierung), Datenmodelle (SOs), Command-only-Zugriff, FoW-Konformität, Difficulty-Profile, Debugging und Headless-Betrieb. Ziel: umsetzungsreif für Sprint 7, ohne Implementierungslogik.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) (insb. D-033 Tick-Simulation/Commands, D-034 Grid/Flow-Fields, D-035 Nova.Simulation-Assembly, D-036 SimRunner)
- [../research/KI_Architektur.md](../research/KI_Architektur.md) (Architektur-Empfehlung, Schwierigkeitsgrade, Unity-Optionen)
- [../gamedesign/Balancing.md](../gamedesign/Balancing.md) (Messpipeline Stufe 2: ≥200 seeded KI-Matches, Mittel-Profil als Messbasis, Metrik-Anforderungen)
- [../research/FogOfWar.md](../research/FogOfWar.md) (Team-Sicht-Bitmask `IsVisible(i, j, teamMask)`, Sicht-Tick 5–10 Hz)
- [../research/Pathfinding.md](../research/Pathfinding.md) (Grid-Infrastruktur, Flow-Fields)
- Geplante Tech-Docs dieses Sprints: `./SimulationCore.md` (Command-/StateView-API, PRNG), `./FogOfWar.md` (Sicht-Abfragen), `./Pathfinding.md` (Grid/Flow-Field-API) – Dateinamen vorbehaltlich TDD-Konsistenzreview.

## Architekturüberblick und Assembly-Einordnung

Die KI ist ein **Client der Simulation**, strukturell identisch zu einem späteren Netzwerkspieler (D-033): Sie liest ausschließlich eine gefilterte Sicht (`IAiWorldView`, nur Team-Sicht) und wirkt ausschließlich über `ICommandSink` (Commands sind die einzige State-Mutation). Direkter lesender Zugriff auf den vollen Sim-State ist im KI-Assembly-Vertrag nicht vorgesehen; schreibender Zugriff ist ausgeschlossen.

- **`Nova.AI`** (Unity-freie .NET-Assembly, analog D-035): gesamte Entscheidungslogik aller drei Schichten, Blackboard, Plan- und BT-Laufzeit. Keine UnityEngine-APIs, kein `UnityEngine.Random`, kein `DateTime.Now` – Zeit kommt als Sim-Tick, Zufall als `ISimRng` (seedbarer PRNG der Simulation, D-033 Regel 4). Voraussetzung für Headless-Betrieb (D-036) und spätere Lockstep-Kompatibilität.
- **`Nova.AI.Data`** (Unity-Assembly): ScriptableObject-Definitionen (`DifficultyProfileSO`, `StrategyOptionSO`, `TaskPlanSO`, `SquadBehaviorSO`). Beim Match-Start werden sie in **flache, Unity-freie Datensätze** (`…Data`-Records) übersetzt und der `Nova.AI`-Instanz injiziert – SOs selbst betreten nie den Sim-/KI-Pfad (Definitions-only, kein Runtime-State in SOs). Im SimRunner kommen dieselben Records aus einer JSON-/Asset-Befüllung ohne Unity.
- **KI-Update-Rhythmus entkoppelt vom 10-Hz-Sim-Tick (D-033 Regel 3):** Director denkt im Profil-Intervall (2–8 s), Plan-Executor prüft Bedingungen alle ~0,5–1 s, Squad-BTs ticken pro Sim-Tick, aber pro Squad mit Amortisierung (Round-Robin über Squads) statt pro Einheit.

```csharp
namespace Nova.AI
{
    /// Eine KI-Partei pro Match; wird vom Match-Setup (lokal oder SimRunner) erzeugt.
    public interface IAiPlayer
    {
        PlayerId Player { get; }
        void OnSimTick(SimTick tick);              // vom Sim-Loop gerufen, 10 Hz
        void DrainCommands(ICommandSink sink);     // KI gibt Commands NIE direkt ab,
                                                   // sondern puffert tick-rein für den Relay
    }

    /// Gefilterte, Team-sichtbare Welt – einzige Wissensquelle der KI (FoW-konform).
    public interface IAiWorldView
    {
        TeamMask Team { get; }
        ResourceSnapshot Resources { get; }        // eigene AE/Energie, volles Wissen
        IReadOnlyList<EntitySnapshot> OwnEntities { get; }
        IReadOnlyList<EntitySnapshot> VisibleEnemies { get; } // nur FoW-sichtbare
        bool IsVisible(GridPos p);                 // delegiert an FoW-Bitmask (Research/FogOfWar)
        bool IsExplored(GridPos p);
        SimTick Now { get; }
        ISimRng Rng { get; }                       // seeded, D-033 Regel 4
    }
}
```

## Schicht 1: Utility-Director (strategisch)

Bewertet strategische Optionen (Expand, Tech, Rush, Turtle, Counter-Anpassung, Superwaffen-Projekt) als gewichtete Considerations mit Antwortkurven; wählt das Maximum (mit Hysterese gegen Flattern) und instanziiert den zugehörigen Task-Plan in Schicht 2. Denkfrequenz und Consideration-Set kommen aus dem Difficulty-Profil.

- Considerations lesen **nur** Blackboard-/WorldView-Daten: eigene Income-Prognose, Bedrohungsvektor, Map-Control-Anteil, Aetherium-Feldzustände (soweit erforscht), Scouting-Erkenntnisse über den Gegner.
- Scoring ist eine **reine Funktion** `(Option, Blackboard, Rng) → Score` → EditMode-Tests ohne Szene; Score-Rauschen (Gauß, seeded) nur laut Profil.
- Reaktion auf Spielerstrategien läuft nicht über Sonderlogik, sondern über den Bedrohungsvektor im Blackboard als Consideration-Input (Counter-Consideration ab Mittel).

```csharp
namespace Nova.AI.Strategy
{
    public interface IConsideration
    {
        ConsiderationId Id { get; }
        /// Reine Funktion; Kurve (Linear/Sigmoid/Schwelle) liegt in den Daten.
        float Evaluate(in Blackboard bb);          // 0..1, vor Gewichtung
    }

    public readonly record struct ScoredOption(StrategyOptionData Option, float Score, float RawScore);

    public interface IUtilityDirector
    {
        StrategyOptionData? CurrentStrategy { get; }
        /// Wird nur aufgerufen, wenn das Profil-Denkintervall fällig ist.
        DirectorVerdict Deliberate(in Blackboard bb, ISimRng rng, DifficultyProfileData difficulty);
    }

    /// Vollständiger Score-Dump für Debugging/CI (Warum-Log), nicht nur der Gewinner.
    public readonly record struct DirectorVerdict(
        StrategyOptionData Winner, IReadOnlyList<ScoredOption> AllScores, SimTick AtTick);
}
```

## Schicht 2: HTN-light Plan-Executor (taktisch)

Führt den vom Director gewählten **flachen, SO-definierten Task-Plan** aus: Build-Orders, Produktionswarteschlangen, Verteidigungsdisposition, Aufklärungsrouten, Angriffswellen-Sequenzen. Bewusst kein rekursiver Planer im MVP (Research-Empfehlung), aber dieselbe Datenform (Task mit Vorbedingung → später HTN-Method-kompatibel).

- `PlanTask` = { Vorbedingung, Aktion, Abbruchbedingung }. Aktionen erzeugen **Commands** (Baue, Produziere, FormiereSquad, SetzeSquadZiel) oder Blackboard-Einträge (Sammelpunkt, Angriffsfenster) – niemals direkte Sim-Mutation.
- Build-Orders sind reine Daten (`TaskPlanSO` → `TaskPlanData`): Designer ändern Reihenfolgen, Truppenmix und Bedingungen ohne Code.
- Störungen (Produktionsgebäude zerstört, Sammelpunkt überrannt) lösen je nach Profil Planabbruch oder Replanning (Rückfrage an den Director) aus.

```csharp
namespace Nova.AI.Tactics
{
    public enum TaskStatus { Pending, Active, Succeeded, Failed, Aborted }

    public readonly record struct PlanTaskData(
        string Id, TaskConditionData? Precondition, TaskActionData Action,
        TaskConditionData? AbortCondition);

    public interface IPlanExecutor
    {
        TaskPlanData? ActivePlan { get; }
        int CurrentStep { get; }                   // "Schritt 3/7" für Debug-Overlay/Replays
        PlanTickResult Tick(in Blackboard bb, CommandBuffer commands);
        void RequestReplan(ReplanReason reason);   // eskaliert an den Director
    }

    public readonly record struct PlanTickResult(
        TaskStatus Status, ReplanRequest? Replan);
}
```

## Schicht 3: Squad-Behavior-Trees (operativ)

Micro, Zielwahl (Fokus-Feuer nach Konter-Matrix), Fähigkeitennutzung und Rückzug laufen als **Behavior Trees auf Squad-Ebene** (nicht pro Einheit) – Skalierungsvorgabe für 500 Einheiten bei 60 FPS. Rückzug ist ein BT-Branch, getriggert durch Squad-Kohäsions-/HP-Schwellen aus dem Blackboard (Utility-Logik als Decorator).

- **Schmale Eigenbau-BT-Laufzeit** (Selector/Sequence/Decorator/Leaf) als reine Funktionen über dem Squad-Blackboard – keine Kauf-Assets im MVP (Research-Empfehlung; Re-Evaluation war an Q-015 gekoppelt und fällt mit D-035 weg: kein DOTS im MVP, damit entfällt der Behavior-Designer-Pro-Hauptvorteil).
- BTs empfangen Squad-Ziele aus Schicht 2 über das Blackboard und geben pro Einheit Bewegungs-/Angriffs-**Commands** ab (PF-Anfragen über den Pathfinding-Service der Simulation, D-034; die KI pfadet nicht selbst).
- Operative Präzision (Zielpriorisierung, Fähigkeiten-Timing) ist profilabhängig als BT-Varianten-Daten (`SquadBehaviorSO`), identisches Aktionsbudget für alle Stufen.

```csharp
namespace Nova.AI.Squads
{
    public enum BtStatus { Running, Success, Failure }

    public interface IBtNode
    {
        BtStatus Tick(in SquadContext ctx, CommandBuffer commands);
    }

    /// Squad-Sicht: Mitglieder-IDs, Kohäsion, HP-Aggregat, lokale Bedrohung
    /// (aus der Bedrohungskarte), aktuelles Squad-Ziel aus Schicht 2.
    public readonly record struct SquadContext(
        SquadId Squad, IReadOnlyList<EntityId> Members, float Cohesion,
        float HpFraction, float LocalThreat, SquadOrder Order);
}
```

## Blackboard (KI-Wissensmodell)

Gemeinsamer, serialisierbarer State aller drei Schichten pro KI-Partei (D-033 Regel 5: Teil des Savegame-/Replay-States):

- **Influence-/Bedrohungskarten** auf dem gemeinsamen 1-m-Grid (D-034): pro Team eine `float`-Ebene, Update auf dem Sicht-Tick-Raster (5–10 Hz), Quellen = sichtbare Feinde (FoW-gefiltert). Karten liegen als `NativeArray`-kompatible Blöcke vor (Burst-fähig, D-035), Auflösung ggf. gröber als 1 m (Offener Punkt).
- **Aetherium-Kenntnis:** bekannte Felder mit zuletzt gesichtetem Zustand (Mutterkristall-Reserve, Überernte-Stufe) + Zeitstempel; veraltetes Wissen wird als solches geführt (Scouting-Gedächtnis), nicht als aktuelle Wahrheit.
- **Scouting-Gedächtnis:** gesichtete feindliche Gebäude/Einheiten mit Position, Typ, Zeitstempel → speist den Bedrohungsvektor und Counter-Considerations.
- **Strategischer Selbstzustand:** Income-Prognose, Produktionskapazität, Armeezusammensetzung, Elite-Limit-Status, Superwaffen-Fortschritt.

## DifficultyProfileSO (eine KI, drei Datenprofile)

Leicht/Mittel/Schwer unterscheiden sich ausschließlich über Daten, niemals über Ressourcenboni (Research + Balancing.md: Solo-Erlebnis wird über Profile gesteuert, nicht über Winrate-Bänder). Balancing-Simulationsläufe nutzen verbindlich das **Mittel-Profil** (unverrauscht, Standard-Latenz).

```csharp
namespace Nova.AI.Data
{
    // Unity-Assembly: SO ist nur Container; Sim-Seite sieht ausschließlich den Record.
    public sealed class DifficultyProfileSO : ScriptableObject
    {
        public string profileId;                   // "easy" | "normal" | "hard"
        public List<ConsiderationSO> considerationSet;  // Teilmenge bei leicht
        public float scoreNoiseSigma;              // 0 = unverrauscht (schwer)
        public float directorIntervalSec;          // 8 s (leicht) … 2 s (schwer)
        public float reactionLatencySec;           // 15 s → 3 s auf Scouting-Signale
        public float scoutingDiscipline;           // 0..1: Frequenz/Abdeckung der Aufklärung
        public bool replanOnDisruption;            // frühe Abbrüche statt Replanning (leicht)
        public SquadBehaviorSO squadBehavior;      // operative Präzision als Daten
        public DifficultyProfileData ToData();     // Übersetzung in Unity-freien Record
    }
}
```

## FoW-Konformität und Anti-Cheat-Leitplanke

- Die KI sieht exakt die Team-Sicht: `IAiWorldView.VisibleEnemies` und `IsVisible/IsExplored` lesen dieselbe FoW-Bitmask wie Rendering und Angriffsprüfungen (Research/FogOfWar – ein Modell für Logik und Darstellung). Verstecke/Tarnung gelten auch für die KI.
- **Kein Cheating außer Daten-Erlaubnis:** Jede bewusste Abweichung (z. B. leichte KI bekommt Startposition des Spielers) muss als explizites Flag im `DifficultyProfileSO` deklariert sein; implizites Omniwissen ist ein Review-Befund. Radar-Signaturen (nur Position, kein Typ) stehen der KI wie dem Spieler zur Verfügung.
- Scouting-Gedächtnis altert: Wer ein Gebäude einmal sah, kennt dessen letzte Position, aber nicht dessen aktuellen Zustand – identisch zur Nebel-Regel „erforscht" für Spieler.

## Debugging und Testbarkeit

- **Warum-Log:** Jeder `DirectorVerdict` (alle Scores, nicht nur der Gewinner), Plan-Schrittwechsel mit Grund, Squad-BT-Pfad des selektierten Squads – als ringgepufferte, tick-indizierte Ereignisliste, serialisierbar ins Replay.
- **Debug-Overlay (View-Schicht, darf Unity-APIs nutzen):** Score-Balkendiagramm aller Optionen, aktiver Plan mit Schritt-Indikator, BT-Laufzustand pro Squad (Squad-Level pflicht, Per-Unit nur bei Selektion), Bedrohungskarte als Heatmap.
- **Determinismus-Guard:** Seed-Hash des KI-Entscheidungsstroms pro Tick (Research-Empfehlung) – dient in CI und späterem Lockstep als Desync-Detektor.
- **Unit-Tests:** Considerations/Scoring als reine Funktionen, Plan-Bedingungen gegen Mock-Blackboard, BT-Leaves gegen `SquadContext`-Fixtures – alles EditMode-tauglich, da `Nova.AI` Unity-frei ist.

## Headless-Betrieb im SimRunner (D-036)

- `Nova.SimRunner` instanziiert pro Partei eine `IAiPlayer` mit Profil-Daten aus JSON (keine Unity-SOs im Runner) und führt seeded KI-vs-KI-Matches aus; die KI läuft unverändert, weil sie nur `IAiWorldView`/`ICommandSink` kennt.
- **Metrik-Ausgabe für Balancing.md Stufe 2:** Match-Result (Sieger, Matchdauer) plus KI-interne Metriken: gewählte Strategiearchetypen (Director-Verdicts), Zeit bis erster Angriff, First-Expansion-Zeit, Strategiearchetyp-Verteilung – exakt die vom Balancing-Prozess geforderte Anforderungsliste.
- CI-Nachtläufe: ≥200 Matches je Matchup-Cluster bei fixem Seed-Set; Mittel-Profil für beide Seiten (Balancing-Vorgabe), Difficulty-Cross-Matches (leicht vs. schwer) als separater Erwartungs-Check (schwer muss signifikant über 50 % liegen).

## Offene Punkte

- **Auflösung und Update-Frequenz der Bedrohungskarten** bei 500 Einheiten (1 m wie FoW/Pathfinding-Grid oder gröber, z. B. 4 m); mögliche Synergie mit Flow-Field-Kostenkarten (D-034) ist mit dem Pathfinding-Verantwortlichen abzustimmen – in Research/KI_Architektur.md bereits als offen vermerkt, hier nicht entscheidbar.
- **Schnittstellenformat des Bedrohungsvektors** (erkannte Spielerstrategie aus Scouting-Gedächtnis) hängt vom finalen FoW-Tech-Doc ab; die Considerations sind dagegen nur als abstrakter Input definiert.
- **Evolvierte-Wachstumsbauweise:** Ob Bauplatz-Tasks und Wachstumsknoten-Tasks dasselbe `PlanTaskData`-Schema abdecken oder ein fraktionsspezifischer Task-Typ nötig wird, ist offen (abhängig vom Buildings-Tech-Design).
- **Konkrete Consideration-Liste und Kurvenformen** pro Strategieoption brauchen finalisierte Wirtschaftsregeln (Aetherium-Nachwachsen/Überernte) – Daten-Authoring erst nach Economy-Finalisierung.
- **Fixed-Point-Umstellung (D-033, Beta):** Ob Scores/Kurven dann auf Fixed-Point rechnen müssen oder im Float-Toleranzrahmen bleiben dürfen (KI-Entscheidungen erzeugen Commands, mutieren aber keinen State direkt), ist beim Beta-MP-Umbau zu entscheiden; das Dokument spezifiziert bewusst nur float-freie *Schnittstellenpositionen*, nicht die Arithmetik.
- **APM-/Aktionsbudget-Kappung** der operativen Schicht (Research verlangt identisches Limit für alle Stufen): konkrete Obergrenze (Commands/Sekunde pro KI) ist noch nicht quantifiziert.

## Nächste Schritte

- Schnittstellen `IAiWorldView`/`ICommandSink` mit dem SimulationCore-TDD abgleichen (Namens- und Tick-Konventionen), Ergebnis ins Konsistenzreview.
- `StrategyOptionSO`/`TaskPlanSO`/`SquadBehaviorSO`-Feldlisten als Schema-Entwurf ausformulieren (Sprint 3/4, mit Game Design).
- Bedrohungskarten-Auflösung gemeinsam mit Pathfinding-/FoW-Verantwortlichen festlegen; Ergebnis hier und in `./Pathfinding.md`/`./FogOfWar.md` nachziehen.
- SimRunner-Metrikschema (Match-Result + Director-Verdict-Aggregate) als JSON-Contract mit QA/Balancing abstimmen (Input für Testing.md/CI).
- Sprint 7: MVP-Umfang gemäß Research-Empfehlung umsetzen (Director mit ~5 Optionen, 2–3 Task-Pläne, Squad-BT Kampf/Rückzug/Fähigkeiten).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead AI Programmer |
