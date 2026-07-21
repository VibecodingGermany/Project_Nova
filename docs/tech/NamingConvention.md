# Naming Convention – Benennungsregeln für Project Nova

**Version:** 0.2.0 | **Status:** Entwurf (Korrekturlauf Sprint 4) | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 3–4

## Zweck

Dieses Dokument legt die verbindlichen Benennungsregeln für Code (Namespaces, Typen, Member), SO-Assets, Ordner, Tests, Events und Datei-Header fest. Ziel: Navigierbarkeit einer Codebasis, die auf ~90 Einheitentypen, 12 Gebäudetypen und mehrere hundert Definitions-Assets wächst, sowie unmissverständliche Zuordnung jedes Typs zu seiner Architektur-Schicht (D-033/D-035). Verbindlich ab Sprint 7; Ergänzungen (neue Präfixe, neue Feature-Namespaces) erfolgen nur über Änderung dieses Dokuments.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (Sim/View-Trennung), D-035 (OOP+SO-Gerüst), D-036 (SimRunner), D-043 (kanonische Assembly-Topologie inkl. `Nova.AI`/`Nova.AI.Data`), D-049 (Registry-Sharding)
- [../research/Unity_BestPractices.md](../research/Unity_BestPractices.md) – §3 (Registry-Pattern, stabile IDs)
- [./FolderStructure.md](./FolderStructure.md) – Ordner-/Assembly-Struktur, der die Namespaces folgen
- [./CodingGuidelines.md](./CodingGuidelines.md) – Regeln, deren Rollen hier benannt werden

## 1. Allgemeine C#-Regeln

| Element | Konvention | Beispiel |
|---|---|---|
| Typen, Methoden, Properties, Events | `PascalCase` | `MoveCommand`, `Execute`, `CurrentTick` |
| Interfaces | `I` + `PascalCase`, Rollenname | `ICommand`, `ISimSystem`, `ISimRandom` |
| Parameter, lokale Variablen | `camelCase` | `targetTile`, `elapsedTicks` |
| Private/protected Felder | `_camelCase` | `_unitStates`, `_logger` |
| `const` und `static readonly` | `PascalCase` | `TicksPerSecond`, `MaxEntities` |
| Enums + Werte | `PascalCase` | `FactionId.Allianz` |
| Boolesche Member | Präfix `Is/Has/Can/Should` | `IsVisible`, `CanCapture` |

- Abkürzungen werden wie Wörter behandelt (`FogOfWarSystem`, nicht `FOWSystem`); Ausnahme etablierter Kurzformen: `UI`, `ID`/`Id`, `AI` (als `Ai` in PascalCase-Typen: `Nova.Simulation.Ai`).
- Keine ungarische Notation, keine Unterstrich-Suffixe, keine kryptischen Kurznamen (`mgr`, `hndl`).
- Sprache aller Identifier: Englisch (DocumentationStandard §Sprache). Fraktionsnamen bilden die dokumentierte Ausnahme (§4).

## 2. Namespaces

Namespaces spiegeln exakt die Ordnerstruktur ([./FolderStructure.md](./FolderStructure.md) §3). Neue Feature-Namespaces werden nur auf Ebene unterhalb der Schicht-Roots angelegt.

| Namespace | Schicht | Inhalt (Beispiele) |
|---|---|---|
| `Nova.Core` | Core | `EntityId`, `Tick`, `INovaLogger`, `SimMath` |
| `Nova.Simulation` | Sim (Unity-frei) | `Simulation`, `SimulationConfig`, `CommandEnvelope`, `CommandType` |
| `Nova.Simulation.Commands` | Sim | `MoveCommand`, `AttackCommand`, `BuildCommand` |
| `Nova.Simulation.State` | Sim | `UnitState`, `MatchState`, `PlayerState` |
| `Nova.Simulation.Definitions` | Sim | `UnitDefinition`, `WeaponDefinition` (Unity-freie Snapshots) |
| `Nova.Simulation.Economy` / `.Combat` / `.Movement` / `.Pathfinding` / `.FogOfWar` / `.Ai` | Sim | je ein `ISimSystem` + zugehörige Typen |
| `Nova.Simulation.Burst` | Burst/Jobs | Burst-Varianten der Hotspot-Jobs (D-034, nur hinter Feature-Flag, D-045) |
| `Nova.AI` / `Nova.AI.Strategy` / `.Tactics` / `.Squads` | KI (Unity-frei, D-043) | `AiPlayer`, `StrategicDirector`, `SquadBehavior` |
| `Nova.AI.Data` | Data (SO) | `DifficultyProfileSO`, `StrategyOptionSO`, `AiRegistrySO` |
| `Nova.Data` | Data (SO) | `UnitDefinitionSO`, `UnitRegistrySO`, `GameDatabaseMasterSO` |
| `Nova.Gameplay` / `Nova.Gameplay.<Feature>` | Gameplay | `MatchRunner`, `SimBridge`, Pools, Command-Eingang |
| `Nova.Presentation` / `Nova.Presentation.<Feature>` | Presentation | `UnitView`, `FogOfWarRenderFeature`, `AudioService` |
| `Nova.Editor` | Editor | Inspectors, Validatoren |
| `Nova.Simulation.Tests` / `Nova.Gameplay.Tests` / `Nova.PlayMode.Tests` | Tests | spiegeln die getestete Schicht |

## 3. Typnamen nach Rolle

Suffixe sind verbindlich – sie machen die Schichtzugehörigkeit am Namen erkennbar:

| Rolle | Muster | Beispiel |
|---|---|---|
| Command (Sim, Struct) | `<Aktion>Command` | `MoveCommand`, `SetRallyPointCommand` |
| Command-Transport (Sim, Struct) | `CommandEnvelope` + `CommandType`-Enum + fixed-size Payload (boxfrei, Review F-5; `ICommand` nur als Marker über generische Constraints) | – |
| Sim-System | `<Domäne>System : ISimSystem` | `EconomySystem`, `FogOfWarSystem` |
| State-Struct (Sim) | `<Entität>State` | `UnitState`, `BuildingState` |
| Sim-Definition (Unity-frei) | `<Entität>Definition` | `UnitDefinition`, `TechDefinition` |
| SO-Schema (Unity) | `<Entität>DefinitionSO : ScriptableObject` | `UnitDefinitionSO`, `WeaponDefinitionSO` |
| Sub-Registry-SO (pro Kategorie, D-049) | `<Kategorie>RegistrySO : ScriptableObject` (Instanz: `<Kategorie>Registry.asset`) | `UnitRegistrySO`, `WeaponRegistrySO` |
| Master-Index-SO (generiert, D-049) | `GameDatabaseMasterSO` (Instanz: `GameDatabaseMaster.asset` – generiert, nie händisch) | – |
| View (MonoBehaviour, Presentation) | `<Gegenstand>View` | `UnitView`, `MinimapView`, `HealthbarOverlay` |
| Gameplay-Brücke/Runner | `<Zweck>Bridge` / `<Zweck>Runner` | `SimBridge`, `MatchRunner` |
| Service (Gameplay/Presentation) | `<Domäne>Service` | `AudioService`, `InputService` |
| Sim-Event-Record (Struct, Event-Puffer) | `<Ereignis>Event` | `DamageEvent`, `UnitDiedEvent` |
| Editor-Tool | `<Gegenstand>Validator` / `<Gegenstand>Inspector` | `GameDatabaseValidator` |

Die Paarung `UnitDefinition` (Sim) ↔ `UnitDefinitionSO` (Unity-Asset) ist bewusst gewählt: gleiche Domäne, klar getrennte Schicht – das SO ist die Editier-Quelle, die Definition der Sim-Snapshot.

## 4. SO-Asset-Dateinamen

Muster: `<PREFIX>_<Fraktion>_<Name>.asset`

- **Fraktions-Token:** `Allianz`, `Legion`, `Evolvierte` (deutsche GDD-Namen, dokumentierte Ausnahme zu §1), `Neutral` für neutrale Objekte (D-016), `Shared` für fraktionsübergreifendes.
- **Name:** `PascalCase` ohne Trennzeichen (`Rifleman`, `TitanMech`).

| Präfix | Asset-Typ | Beispiel |
|---|---|---|
| `UNIT_` | Einheiten (Infanterie/Fahrzeug/Luft/Drohne) | `UNIT_Allianz_Rifleman.asset` |
| `BLDG_` | Gebäude | `BLDG_Legion_WarFactory.asset` |
| `WPN_` | Waffen | `WPN_Shared_Railgun.asset` |
| `TECH_` | Forschung | `TECH_Evolvierte_SporeCloud.asset` |
| `FACT_` | Fraktions-Definition | `FACT_Allianz.asset` |
| `AIDIFF_` | KI-DifficultyProfile | `AIDIFF_Shared_Hard.asset` |
| `MAP_` | Karten-Definition | `MAP_Shared_DustBasin.asset` |
| `BIOME_` | Biom-Profil | `BIOME_Shared_Moon.asset` |
| `DB_` | Registry-Assets | Dokumentierte Ausnahme: Registry-Dateien tragen **kein** `DB_`-Präfix, sondern liegen in `Data/Registries/` als `<Kategorie>Registry.asset` plus generiertem `GameDatabaseMaster.asset` (D-049, s. FolderStructure §4) |

Ablage: `Assets/_Project/Data/<Typ>/<Fraktion>/` (vgl. FolderStructure §4).

## 5. Ordnernamen

- `PascalCase`, Plural für Sammlungen (`Units/`, `Commands/`), Singular für Singleton-artige Bereiche (`Editor/`, `Settings/`).
- Keine Sammelordner (`Misc/`, `Common/`, `Util/`) – gemeinsame Basistypen gehören nach `Nova.Core`.
- Ordner unterhalb von `Scripts/` entsprechen 1:1 den Namespaces (§2).

## 6. Tests

- Test-Klassen: `<GetesteterTyp>Tests` (`EconomySystemTests`, `MoveCommandValidationTests`).
- Test-Methoden: `<Methode>_<Bedingung>_<Erwartung>` (`Execute_InsufficientAetherium_CommandRejected`).
- Match-Fixtures/Replays für Sim-Tests: `FIX_<Szenario>` als Dateiname (`FIX_HarvesterLoop_500ticks.json`).
- Test-Assemblies/Namespaces nach §2; Tests benennen ihre Erwartung als Behavior, nicht als Implementierung.

## 7. Events und Delegates

- **View-/Gameplay-Events (C#-`event`):** Muster `On<Subjekt><Veränderung>`, ausgelöst nach der Änderung: `OnHealthChanged`, `OnMatchEnded`, `OnSelectionChanged`. Payload als Struct-Argument (`event Action<HealthChangedPayload>`), nie `EventHandler`/`EventArgs`-Klassen-Hierarchien.
- **Keine selbstdefinierten Delegate-Typen** – immer `Action<>`/`Func<>` (Research §6). Delegate-Namen mit Suffix `Handler` entfallen damit.
- **Sim-Event-Puffer-Records** heißen `<Ereignis>Event` (§3) und sind keine C#-Events; die Namensnähe ist gewollt (DamageEvent = Datensatz, OnDamageReceived = mögliches View-Event daraus).
- **Commands** werden nie `On…` benannt – Commands sind Absichten (Imperativ), Events sind Fakten (Vergangenheit).

## 8. Stabile Definitions-IDs

String-IDs für SO-Definitionen (Registry-Key, Savegames, SimRunner-Auswertung), Format dot-lower:

```text
unit.allianz.rifleman      bldg.legion.war_factory      tech.evolvierte.spore_cloud
```

- Muster: `<typ>.<fraktion>.<name_snake_case>`; Fraktions-Token wie §4 in lower-case.
- IDs sind nach Vergabe **unveränderlich** (Savegame-/Replay-Kompatibilität); Umbenennung eines Assets ändert die ID nicht.

## 9. Datei-Header-Konvention

Jede handgeschriebene `.cs`-Datei beginnt mit:

```csharp
// -----------------------------------------------------------------------------
// Project Nova – <eine Zeile Zweck>
// Assembly: Nova.Simulation | Layer: Simulation (keine UnityEngine-Referenzen, D-033)
// Entscheidungen: D-033, D-035
// -----------------------------------------------------------------------------
```

- `Layer`-Zeile nennt die Schicht; im Sim-Kern inkl. des Hinweises auf die Unity-Freiheit (macht die härteste Regel in jeder Datei sichtbar).
- `Entscheidungen` listet nur die D-IDs, die die Datei unmittelbar binden (kein Sammelsurium).
- Header werden bei Schicht-Wechsel einer Datei angepasst; Header sind Pflicht, aber bewusst kurz – kein Lizenz-/Autorenblock.

## Offene Punkte

- **Präfix-Vollständigkeit:** Die SO-Präfix-Tabelle (§4) deckt den MVP-Scope; Superwaffen-, Commander-Identitäts- und Hazard-Definitionen bekommen ihre Präfixe mit der Sprint-5-Asset-Korrektur bzw. wenn die zugehörigen Tech-Docs entstehen.
- **Fraktions-Token:** `Allianz`/`Legion`/`Evolvierte` folgen den GDD-Namen; falls das GDD lokalisierte interne Namen ändert, ist §4 nachzuziehen (IDs nach §8 bleiben stabil).
- **AIDIFF_-Präfix:** Längeres Token wegen Eindeutigkeit gegenüber einem späteren `AI_`-Sammelpräfix gewählt; bei Einführung weiterer KI-Asset-Typen (Behavior-Trees etc.) Namespace/Präfix gemeinsam final festlegen.

## Nächste Schritte

1. Konsistenzreview gegen Architecture.md und die AI-/Data-Tech-Docs (Namespace-Liste §2 mit den dort geplanten Systemen abgleichen).
2. Sprint 7: Referenzdateien mit Header und korrekten Suffixen anlegen (`MoveCommand` + `CommandEnvelope`, `EconomySystem`, `UnitDefinitionSO`, `UnitRegistrySO`).
3. **Sprint 7 (Tooling-Aufgabe, D-049):** ID-Codegen umsetzen – Generator in `Nova.Editor` erzeugt aus den Sub-Registry-Assets ein Enum pro Kategorie (`UnitId`, `BuildingId`, `WeaponId`, …) plus Lookup-Tabelle als generierte Datei unter `Nova.Data/Generated/` (generierter Code – `#region` hier ausnahmsweise erlaubt, CodingGuidelines §7); die CI prüft die Aktualität der generierten Datei (Rebuild + Diff). Die String-IDs nach §8 bleiben die serialisierbare Quelle der Wahrheit (Savegames/Replays); die Enums sind nur der Compile-Zeit-Zugriff.
4. Präfix-Tabelle nach Sprint-5-Asset-Audit vervollständigen und Version erhöhen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Technical Director |
| 0.2.0 | 2026-07-21 | Korrekturlauf Sprint 4 (D-043–D-052, Review-Findings): Nova.AI-Namespaces (D-043), Sub-Registry-/Master-Index-Benennung (D-049), Command-/CommandEnvelope-Benennung boxfrei (Review F-5), ID-Codegen als Sprint-7-Tooling-Aufgabe konkretisiert | Lead Technical Director |
