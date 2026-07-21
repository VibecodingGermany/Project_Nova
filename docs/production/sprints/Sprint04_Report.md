# Sprint-4-Bericht – Architecture Review

**Version:** 1.0.0 | **Status:** Sprint abgeschlossen | **Verantwortungsbereich:** Executive Producer | **Sprint:** 4

## Zweck

Verbindlicher Abschlussbericht von Sprint 4 (Architecture Review) gemäß Sprint-Ritual ([../SprintPlanning.md](../SprintPlanning.md)): Dokumentationsstand, Entscheidungen, Konsistenzreview, Self Review, Architecture Review, Risikoanalyse, Qualitätsbewertung, offene Punkte, begründete Empfehlung für den nächsten Sprint.

## Abhängigkeiten

- Alle sechs Review-Dokumente unter [../../tech/review/](../../tech/review/)
- [../DecisionLog.md](../DecisionLog.md) (D-043–D-052), [../OpenQuestions.md](../OpenQuestions.md), [../RiskAnalysis.md](../RiskAnalysis.md)
- [../SprintPlanning.md](../SprintPlanning.md) (Sprint-4-Definition, Sprint-5-Scope „Asset Audit")
- [Sprint03_Report.md](Sprint03_Report.md) (§8, Sprint-4-Scope-Definition)

## 1. Ergebnisse des Sprints

**Sechs unabhängige, adversariale Review-Berichte erstellt** (alle unter [../../tech/review/](../../tech/review/), Widerspruchs-Mandat gemäß Sprint-3-Scope):

| Review | Fokus | Befunde |
|---|---|---|
| Review_ArchitekturKohaerenz.md | Architekturfehler, Modul-/Schichtzyklen, Zustandsmodell-Lücken | 17 (2 kritisch, 6 hoch, 5 mittel, 4 niedrig) |
| Review_Performance.md | Budgets, Ausführungsmodell, Hash-Parität | 18 (2 kritisch, 6 hoch, 5 mittel, 5 niedrig) |
| Review_Skalierung_Systemgrenzen.md | 500+ Einheiten, Survival-Wellen, Karten-Density, CI-Realismus | 14 (1 kritisch, 5 hoch, 5 mittel, 3 niedrig) |
| Review_Wartbarkeit_Prozess.md | Doppelpfad, SO-Registry, Branching, Namensräume | 17 (1 kritisch, 6 hoch, 7 mittel, 3 niedrig) |
| Review_Multiplayer_Netcode.md | Lockstep-Relay, Trust-Anchor, Desync, Reconnect | 18 (1 kritisch, 6 hoch, 7 mittel, 4 niedrig) |
| Review_GDD-TDD-Konsistenz.md | Werte-/Einheiten-Widersprüche GDD↔TDD (6. Review, selbst Sprint-4-Ergebnis) | 21 (2 kritisch, 8 hoch, 7 mittel, 4 niedrig) |
| **Summe** | | **105 Befunde (9 kritisch, 37 hoch, 36 mittel, 23 niedrig)** |

**10 Architektur-Entscheidungen getroffen** (DecisionLog v1.6.1, präzisierte Zählung): **7 der 9 kritischen Befunde** sind über D-043–D-052 entschieden (Architektur-Kohärenz F-1 & Wartbarkeit F-01 → D-043 [dieselbe Assembly-Kollision, unabhängig doppelt gemeldet]; GDD↔TDD F-01 → D-047; Multiplayer-Netcode F-01 → D-046; Performance F-1 → D-044; Performance F-2 → D-045; Skalierung F-1 → D-048); **die verbleibenden 2 kritischen Befunde** (GDD↔TDD F-02, Architektur-Kohärenz F-2) sind reine Datenmodell-Lücken zu bereits getroffenen Entscheidungen und wurden ohne eigenen D-Eintrag als Doku-Erweiterung in GameState.md gelöst (s. §4):

- **D-043** Kanonische Assembly-Topologie (Neusynthese aus drei konkurrierenden Schemata; `Nova.AI`/`Nova.AI.Data` als eigene, Unity-freie KI-Assemblies ergänzt)
- **D-044** Sim-Tick-Ausführungsmodell gestuft (MVP synchron, Worker-Tick-Wechsel bei P95 > 6 ms) + Pflicht-Gate V5 (Combat-/KI-Kostenmodell) vor Sprint-7-Kampfmodul
- **D-045** Managed-first-Auslieferungspfad (Burst nur hinter Feature-Flag, Toleranz-Parität ≤1e-4 statt Bit-Parität) – präzisiert D-037
- **D-046** MP-Trust-Anchor: Post-Match-Re-Simulation + Hash-Kette + deterministische KI-Übernahme (löst Relay-ohne-Schiedsrichter-Problem)
- **D-047** Reichweiten-/Einheiten-Harmonisierung: 1 Tile = 1 m, Weapons.md als einzige führende Quelle für Waffenreichweiten
- **D-048** Skalierungs-Deckel: 600 Einheiten/Match, Survival-Wellen-Abflachung ab Welle 25, `AetheriumDensity` ≤1,5 bei 5–6 Spielern
- **D-049** CI-Realismus (Nightly-Sharding, 6×20 Matches/8 Shards), xxHash64 überall, GameDatabase-Sharding (8 Sub-Registries + generierter Master-Index)
- **D-050** Branching-Modell gestuft (Doku-Phase: `main` + Sprint-Branches; ab Sprint 7: TPD-§12-Modell mit `develop`)
- **D-051** Quantum-Fallback gestrichen (Fallback wäre Rewrite gewesen); neuer Beta-Fallback: reduzierter MP-Scope (4 Spieler, 300 Einheiten, EU-only)
- **D-052** Windows-Referenzhardware fixiert (Ryzen 5 5600/RTX 3060/16 GB, Minimum Ryzen 3 3100/GTX 1050 Ti/8 GB, Mac-Baseline Apple M2)

**Findings-Integration in 23 GDD-/TDD-Dokumente** (21 im ersten Korrekturlauf-PR (#1) + ModuleOverview.md und MemoryBudget.md im zweiten Verifikationslauf nachgezogen, s. §3): Aircraft.md, Balancing.md, Buildings.md, Economy.md, Infantry.md, MultiplayerModes.md, Vehicles.md; DocumentationStandard.md; DecisionLog.md; Architecture.md, CodingGuidelines.md, DependencyGraph.md, Deployment.md, FolderStructure.md, GameState.md, MemoryBudget.md, ModuleOverview.md, NamingConvention.md, Networking.md, Pathfinding.md, PerformanceBudget.md, Replication.md, Testing.md.

**Exit-Kriterien:** alle Findings dokumentiert und klassifiziert (kritisch/hoch/mittel/niedrig, je mit empfohlener Maßnahme) ✓ | alle 9 kritischen Befunde vor Sprint-4-Abschluss eingearbeitet (via D-043–D-052 bzw. direkte Zustandsmodell-Fixes) ✓ | Windows-Referenzhardware fixiert (D-052) ✓ | Sprint-Bericht ✓ (dieses Dokument).

## 2. Konsistenzreview (Zusammenfassung)

- **Konvergente Befunde über mehrere Reviews:** Die Assembly-/Namensraum-Kollision wurde unabhängig von Review_ArchitekturKohaerenz.md (F-1, kritisch) UND Review_Wartbarkeit_Prozess.md (F-01, kritisch) gemeldet – wie schon bei D-037 in Sprint 3 der stärkste Beleg dafür, dass unabhängige Review-Agenten denselben Kernwiderspruch finden; einmalig über D-043 gelöst statt doppelt bearbeitet.
- **Der 6. Review (GDD-TDD-Konsistenz) ist selbst ein Sprint-4-Ergebnis:** Er deckt 21 eigene Befunde auf, darunter die beiden verbleibenden kritischen Werte-Widersprüche (Reichweiten/Sichtweiten F-01 → D-047; Status-Effekt-/Fähigkeiten-System ohne technisches Zuhause F-02 → GameState.md-Erweiterung).
- **Grundsatzmuster erkannt:** Vier Dokumente pflegten Regenerationswerte, drei Reparaturwerte, zwei Gebäudekosten, zwei Harvester-Kosten parallel – Verstoß gegen die eigene „Single Source of Truth"-Regel. Als Konsequenz wurde ein neuer Grundsatz in DocumentationStandard.md 1.1.0 verankert: „Jeder Zahlenwert existiert genau einmal, alles andere sind Verweise" (D-047-Folge).
- **Grep-verifizierte Detail-Angleichungen:** Buildings.md/Weapons.md/Vehicles.md/Aircraft.md (Reichweiten- und Schadenswerte), Economy.md (Harvester-Kosten-Verweis statt Doppelpflege), MemoryBudget.md/Pathfinding.md (Flow-Field-Cache-Deckel), GameState.md (Supply-Altfeld), NamingConvention.md (KI-Namensraum) – siehe §3 für die Fundgeschichte.

## 3. Self Review

**Stärken:** Alle 9 kritischen Befunde ließen sich ohne Zusatzrecherche mit ≥3 geprüften Alternativen entscheiden; die vier Cluster-Subagenten (Architektur, Performance/Skalierung, Wartbarkeit/Multiplayer, GDD-TDD-Konsistenz) erkannten die Assembly-Kollision und die Managed/Burst-Spannung unabhängig voneinander und eskalierten statt zu improvisieren; der neue Grundsatz „ein Wert, eine Quelle" (D-047-Folge) beseitigt eine ganze Klasse künftiger Drifts strukturell statt punktuell.

**Schwächen (offen und ehrlich benannt):**
- **Der erste Korrekturlauf-PR (#1) hat neue, kleine Drifts erzeugt, die erst ein zweiter Verifikationslauf gefangen hat** – die zentrale Prozess-Schwäche dieses Sprints:
  - **MemoryBudget.md** behielt den alten Flow-Field-Cache-Deckel (32 Felder / ≤6,5 MB / LRU-Eviction), obwohl **Pathfinding.md im selben Korrekturlauf** bereits auf 96 Felder / RefCount-Eviction umgestellt worden war (Herleitung: 6 Parteien × 2–4 Kontrollgruppen × bis zu 3 Clearance-Klassen) – eine Zahl driftete zwischen zwei im selben PR geänderten Dokumenten auseinander.
  - **Buildings.md** ließ im Offene-Punkte-Abschnitt einen Verweis auf den bereits überholten Aircraft.md-Wert (90 DPS Flak-Luftschaden) stehen, obwohl Weapons.md im selben Korrekturlauf als einzige Werte-Quelle (D-047) festgelegt wurde.
  - **GameState.md** behielt das obsolete Feldpaar `SupplyUsed`/`SupplyCap`, obwohl D-021 (Sprint 2) ein Supply-/Pop-System bereits ausdrücklich ausschließt – eine Altlast, die erst der GDD-TDD-Konsistenzreview (F-18) im zweiten Anlauf fand.
  - **Economy.md** pflegte trotz des neuen „ein Wert, eine Quelle"-Grundsatzes weiterhin eine dritte Harvester-Kosten-Zahl parallel zu Vehicles.md.
  - **NamingConvention.md** führte nach der D-043-Assembly-Trennung (KI als eigene Assembly `Nova.AI`) weiterhin einen Rest-Namensraum `Nova.Simulation.Ai` – dieselbe Entscheidung war in zwei Dokumenten unterschiedlich umgesetzt.
  - **Sprint-Header-Feld:** Mehrere Dokumente (Architecture.md, Deployment.md, Pathfinding.md, PerformanceBudget.md, Testing.md u. a.) waren inhaltlich bereits auf Sprint 4 aktualisiert, führten im Kopf aber noch `Sprint: 3` – reine Metadatendisziplin, aber genau die Art Lücke, die D-005 (Pflicht-Änderungsverlauf/Versionskopf) verhindern soll.
  - **ModuleOverview.md** wurde im ersten PR bewusst zurückgehalten (Agent am Token-Limit) und musste inklusive der KI-Entkopplung (Production↔Research-Zyklus, D-043-Topologie) vollständig im zweiten Anlauf nachgezogen werden.
- **Prozess-Lehre für Sprint 5 ff.:** Ein Korrekturlauf, der viele Dokumente in einem PR anfasst, braucht zwingend einen zweiten, unabhängigen Verifikationslauf (bzw. ein PR-Gate) BEVOR er als abgeschlossen gilt – dieser Sprint hat das eingehalten, aber die Korrekturen des zweiten Laufs sind zum Zeitpunkt dieses Berichts noch **nicht committet** (siehe §7, Red-Flag-würdig).
- Q-018/Q-019 blieben unverändert offen (Sprint 6) – kein Rückschritt, aber auch kein Fortschritt in Sprint 4.

## 4. Architecture Review

Unabhängige Prüfung wie in Sprint 3 vorgesehen (sechs Agenten mit Widerspruchs-Mandat), Ergebnis: alle gemeldeten Topologie- und Wertewidersprüche mit genau einer Entscheidung bzw. einem Dokument-Fix gelöst:

- **Assembly-/Namensraum-Kollision** (drei konkurrierende Schemata `Nova.Game`/`Nova.Core`/eigenständige KI-Benennung) → **D-043**: kanonische Topologie mit `Nova.Core`, `Nova.Simulation` (Unity-frei), `Nova.Simulation.Burst`, `Nova.AI`/`Nova.AI.Data` (Unity-frei, eigener Client der Simulation, keine Modul-Referenzen auf Economy/Production/Research/Combat/FogOfWar/Pathfinding), `Nova.Data`, `Nova.Gameplay`, `Nova.Presentation`, `Nova.UI`, `Nova.Editor`, `Nova.SimRunner`, `Nova.BuildTools`.
- **Burst/Jobs-vs.-SimRunner-Portabilität** (Unity.Burst/Jobs laufen nicht in der Unity-freien Konsolen-App) → **D-043** (eigene `Nova.Simulation.Burst`-Assembly) + **D-045** (Managed als Auslieferungspfad, Burst hinter Feature-Flag mit Toleranz-Parität ≤1e-4 statt unrealistischer Bit-Parität) – löst den in Sprint 3 als „Offener Punkt 1" vertagten Konflikt vollständig.
- **Modul-Zyklus Production↔Research** (gegenseitige fachliche Modul-Referenz trotz Zyklenverbot) → gelöst: Research ist alleiniger Schreiber von `TechState`, publiziert `TechUnlockedEvent`; Production liest nur den State bzw. abonniert das Event – keine gegenseitige Assembly-Referenz mehr (ModuleOverview.md, Dokument-Fix ohne eigenen D-Eintrag).
- **Reichweiten-/Einheiten-Widerspruch** (Grid-Felder vs. Meter, Faktor 2,5–4×) → **D-047**: 1 Tile = 1 m, Weapons.md führend; Angriffsreichweite > Sichtweite bleibt bewusstes Design-Prinzip (Scouting), kein Fehler.
- **MP-Trust-Anchor fehlend** (Relay ohne eigene Sim kann Ergebnis-/Desync-Konflikte nicht schlichten) → **D-046**: Post-Match-Re-Simulation (SimRunner-basiert, on-demand) + Hash-Ketten-Prüfung von Reconnect-Snapshots + deterministisches (kein serverseitiges) KI-Übernahme-Ereignis.
- **Skalierungs-Deckel fehlend** (500-Einheiten-Kalibrierung nirgends erzwungen, Survival-Endlos multiplikativ ohne Cap) → **D-048**: globaler 600-Einheiten-Deckel, Wellen-Abflachung ab Welle 25, Density-Cap bei 5–6 Spielern.
- **Verbleibender, bewusst nicht vollständig gelöster Punkt:** Presentation↔UI-Zyklus (Camera↔Minimap) ist weiterhin als offener Punkt in DependencyGraph.md vermerkt (Bridge-Mediator-Konzept vorgeschlagen, nicht final entschieden) – an Sprint 7 übergeben, kein Blocker für Sprint 5.
- **Validierungs-Rückstellungen unverändert:** alle vier Phase-0-Spikes aus Sprint 3 bleiben Pflicht, ergänzt um das neue **Pflicht-Gate V5** (Combat-/KI-Kostenmodell, D-044) und einen erweiterten Fixed-Point-Scope (ORCA/Flow-Field-Bibliothekswahl, MP-Review-Folge).

## 5. Risikoanalyse (Update)

[../RiskAnalysis.md](../RiskAnalysis.md) wurde für Sprint 4 auf **v1.4.0** fortgeschrieben (Stand dieses Berichts noch uncommittet, s. §7):
- **R-12 (Burst/Managed-Parität)** weiter präzisiert durch D-045 (Managed-first-Auslieferung + Toleranz-Parität ≤1e-4 statt unrealistischer Bit-Parität); bleibt „aktiv (mitigiert)".
- **Vier neue Risiken aufgenommen**, zwei davon unmitigiert und **wichtiger als reine Doku-Findings** – sie verlangen Entscheidungen des Projektinhabers, keine weitere Dokumentarbeit:
  - **R-13 Schlüsselperson-/Bus-Faktor-Risiko (hoch/hoch, unmitigiert):** Das Projekt trägt eine Einzelperson zusammen mit KI-Coding-Agenten, ohne personelle Redundanz in Fachwissen, Entscheidungsfindung oder Review-Kapazität.
  - **R-16 Zeit-/Kapazitätsrisiko (hoch/mittel, unmitigiert):** Weder PLAN.md/SprintPlanning.md noch TPD enthalten eine Aufwandsschätzung (Personentage, Kalenderzeit) für Phase 0–3.
  - **R-14 Cross-Plattform-Determinismus ARM↔x86 (mittel/hoch, neu, mitigiert über Phase-0-Spike-Gate):** Die gesamte MP-Architektur (D-033/D-037/D-045/D-046) setzt bit- bzw. toleranzgenauen Determinismus zwischen Windows-x86-Referenz und Mac-M2-ARM (D-052) voraus; ein Scheitern des Spikes würde diese Entscheidungen nachträglich infrage stellen.
  - **R-15 Fehlerhafter KI-generierter Code in der desync-kritischen Lockstep-Sim (mittel/hoch, neu, mitigiert über CI-Gates):** stille, schwer reproduzierbare Desyncs als Restrisiko der KI-lastigen Implementierung, abgefedert durch V1-Gate/Golden-Master/Paritätstests (D-037/D-045/D-049).
- **Einordnung für §8:** R-13/R-16 sind die einzigen Befunde dieses Sprints, die über Dokumentationsarbeit hinausgehen und eine Kapazitäts-/Zeitplanungsentscheidung des Projektinhabers erfordern – empfohlen vor oder parallel zu Sprint 6 (Produktionsplanung), kein Blocker für Sprint 5 (Asset Audit).

## 6. Qualitätsbewertung

| Kriterium | Bewertung | Anmerkung |
|---|---|---|
| Vollständigkeit (Review-Abdeckung) | sehr gut | 6 unabhängige Reviews, alle im Sprint-4-Scope genannten Bereiche abgedeckt (Architekturfehler, Performance, Skalierung, Wartbarkeit, Multiplayer, GDD↔TDD-Konsistenz) |
| Entscheidungsdisziplin | sehr gut | 10 Entscheidungen mit je ≥3 geprüften Alternativen; alle 9 kritischen Befunde einer Entscheidung oder einem dokumentierten Fix zugeordnet |
| Einarbeitungs-/Prozessqualität | mittel | erster Korrekturlauf-PR (#1) hinterließ mehrere kleine Werte-/Namensraum-Drifts (§3); zweiter Verifikationslauf hat sie gefangen, ist aber zum Berichtszeitpunkt noch **nicht committet** |
| Umsetzungsreife für Sprint 7 | gut (nach Commit) | kanonische Assembly-Topologie einheitlich in allen TDD-Kerndokumenten – vorausgesetzt, die ausstehenden Korrekturen werden gesichert |
| Messbarkeit | gut | V5-Gate (D-044), Referenzhardware fixiert (D-052), Toleranz-Parität-Schwelle (D-045) und Skalierungs-Deckel (D-048) sind konkret beziffert |
| Verbleibende Unsicherheit | akzeptiert | Presentation↔UI-Zyklus, Reconnect-/Stall-Schwellen, Replay-Kompatibilität über Balance-Patches bewusst auf Sprint 5/6 bzw. Phase-0-Spikes verwiesen |

## 7. Offene Punkte

- **Prozess-kritisch:** Zum Zeitpunkt dieses Berichts liegen die Korrekturen des zweiten Verifikationslaufs (u. a. ModuleOverview.md, MemoryBudget.md, DependencyGraph.md, GameState.md, Buildings.md, Economy.md, NamingConvention.md, Architecture.md, DecisionLog.md 1.6.1, OpenQuestions.md 1.5.0, RiskAnalysis.md 1.4.0, Sprint-Header-Korrekturen in mehreren Tech-Dokumenten) **uncommittet im Arbeitsverzeichnis** vor – sie müssen vor dem endgültigen Sprint-4-Abschluss gesichert werden, sonst ist der in diesem Bericht beschriebene „gelöst"-Zustand nicht im Repository nachvollziehbar.
- [../SprintPlanning.md](../SprintPlanning.md) (Sprint-4-Zeile noch „bereit (GO)" statt „abgeschlossen") und [../../README.md](../../README.md) (Wiki-Index noch 0.4.0/Sprint 3) sind noch nicht auf den Sprint-4-Abschluss nachgezogen – Teil des Integrationsschritts, nicht dieses Berichts. [../RiskAnalysis.md](../RiskAnalysis.md) (v1.4.0) und [../OpenQuestions.md](../OpenQuestions.md) (v1.5.0) sind dagegen bereits fortgeschrieben (uncommittet, s. o.).
- CHANGELOG.md `[Unreleased]` beschreibt noch den Zwischenstand vor dem zweiten Verifikationslauf (inkl. „Zurückgehalten: ModuleOverview.md") und muss nach dessen Commit ergänzt werden.
- Verbleibende HOCH-/MITTEL-Befunde (aggregiert aus den 6 Reviews), mehrheitlich eigene D-Kandidaten oder Detail-Anpassungen für Sprint 5/6/7, u. a.: Presentation↔UI-Zyklus (Arch F-3, Rest), Pause-Vote/Reconnect-Stall-Schwellen/Observer-Join-Regel (MP F-04/F-08/F-13, Skal F-8/F-10), Replay-Kompatibilität über Balance-Patches (Arch F-13), Fairness der Gleich-Tick-Konfliktauflösung (Arch F-9), CI-Parallelisierungs-Feinkonzept (Skal F-3), projektweite Restdurchsetzung „ein Wert, eine Quelle" (GDD-TDD F-12–F-15); teilweise bereits als Q-031–Q-034 in OpenQuestions.md v1.5.0 registriert (Fähigkeiten-/Status-Effekt-System, MemoryBudget-Abgleich, V5-Gate-Kostenmodell, tote Doku-Verweise).
- **Neu (RiskAnalysis.md v1.4.0), über Dokumentationsarbeit hinausgehend:** R-13 (Bus-Faktor, hoch/hoch) und R-16 (Zeit-/Kapazitätsmodell, hoch/mittel) sind unmitigiert und erfordern eine Entscheidung/Planung durch den Projektinhaber, keine reine Doku-Anpassung (s. §5).
- Q-018 (Preispunkt) und Q-019 (Telemetrie) bleiben unverändert offen, beide Sprint 6.
- Fixed-Point-Migrationsscope (Beta) um ORCA-/Flow-Field-Bibliothekswahl erweitert (MP-Review-F-04-Folge); float-Direktfelder im GameState sind bis dahin verboten zu halten.

## 8. Empfehlung für den nächsten Sprint

**Empfehlung an den Projektinhaber: bedingtes GO für Sprint 5 (Asset Audit) – die finale Freigabe trifft der Mensch.**

Begründung: Alle Sprint-4-Exit-Kriterien sind in der Sache erfüllt – sechs unabhängige Reviews mit 105 klassifizierten Befunden liegen vor, alle 9 kritischen Befunde sind über D-043–D-052 bzw. direkte Dokument-Fixes gelöst, die Windows-Referenzhardware ist fixiert, RiskAnalysis.md und OpenQuestions.md sind bereits auf Sprint 4 fortgeschrieben. Drei Punkte sprechen gegen ein uneingeschränktes, folgenloses GO: (1) die Korrekturen des zweiten Verifikationslaufs (inkl. DecisionLog/OpenQuestions/RiskAnalysis) liegen noch uncommittet vor (§7) – der „gelöst"-Zustand dieses Berichts ist erst nach deren Commit im Repository nachvollziehbar; (2) SprintPlanning.md-Status und der Wiki-Index sind noch nicht auf Sprint 4 nachgezogen; (3) RiskAnalysis.md v1.4.0 weist mit R-13 (Bus-Faktor) und R-16 (Zeit-/Kapazitätsmodell) zwei unmitigierte, projektweite Risiken aus, die über Dokumentationsarbeit hinausgehen und eine bewusste Entscheidung des Projektinhabers verlangen (nicht blockierend für Sprint 5, aber vor Sprint 6 zu adressieren). Da Sprint 5 (Asset Audit, Recherche/Lizenz/Kosten pro Asset) inhaltlich nicht von den verbleibenden HOCH-/MITTEL-Detailpunkten, von den Sprint-7-Implementierungsfragen oder von R-13/R-16 abhängt, kann es parallel zur Bereinigung dieser Punkte beginnen. Empfehlung: (a) ausstehenden Korrekturlauf committen, (b) SprintPlanning/README/CHANGELOG im Integrationsschritt nachziehen, (c) R-13/R-16 bewusst zur Kenntnis nehmen und für Sprint 6 vormerken, (d) danach Sprint 4 formal auf „abgeschlossen" setzen und Sprint 5 freigeben.

**Sprint-5-Scope (laut [../SprintPlanning.md](../SprintPlanning.md)):** Asset Audit – pro benötigtem Asset Recherche, Lizenz, Kosten, Qualität, Anpassungsaufwand; Klassifikation BUY/MODIFY/BUILD; vollständiges Asset-Register inkl. Licenses.md.

## Offene Punkte

- Keine zusätzlich zu §7.

## Nächste Schritte

- Ausstehende Korrekturen des zweiten Verifikationslaufs committen (ModuleOverview.md, MemoryBudget.md, DecisionLog.md 1.6.1, OpenQuestions.md 1.5.0, RiskAnalysis.md 1.4.0 u. a., s. §7) – bereits inhaltlich fortgeschrieben, nur noch zu sichern.
- SprintPlanning.md (Sprint-4-Status auf „abgeschlossen"), docs/README.md (Wiki-Index) und CHANGELOG.md `[Unreleased]` im Integrationsschritt nachziehen.
- R-13 (Bus-Faktor) und R-16 (Zeit-/Kapazitätsrisiko) dem Projektinhaber zur Kenntnis vorlegen; Adressierung vor/mit Sprint 6 planen.
- Nach Freigabe durch den Projektinhaber: Sprint 5 (Asset Audit) starten.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Sprint 4 abgeschlossen, bedingtes GO für Sprint 5 (Vorbehalt: ausstehender Commit des zweiten Verifikationslaufs) | Executive Producer |
