# Sprint-3-Bericht – Technical Design

**Version:** 1.0.0 | **Status:** Sprint abgeschlossen | **Verantwortungsbereich:** Executive Producer | **Sprint:** 3

## Zweck

Verbindlicher Abschlussbericht von Sprint 3 (Technical Design) gemäß Sprint-Ritual ([../SprintPlanning.md](../SprintPlanning.md)): Dokumentationsstand, Entscheidungen, Konsistenzreview, Self Review, Architecture Review, Risikoanalyse, Qualitätsbewertung, offene Punkte, Entscheidung über den nächsten Sprint.

## Abhängigkeiten

- Alle TDD-Dokumente unter [../../tech/](../../tech/)
- [../DecisionLog.md](../DecisionLog.md) (D-033–D-042), [../OpenQuestions.md](../OpenQuestions.md), [../RiskAnalysis.md](../RiskAnalysis.md)
- [Sprint02_Report.md](Sprint02_Report.md) (Sprint-3-Scope-Definition)

## 1. Ergebnisse des Sprints

**23 Technical-Design-Dokumente erstellt** (alle im Dokumentstandard):

| Bereich | Dokumente |
|---|---|
| Architektur-Kern | Architecture.md, ModuleOverview.md, DependencyGraph.md, FolderStructure.md, CodingGuidelines.md, NamingConvention.md |
| Simulation & Daten | GameState.md, Serialization.md, Savegames.md |
| Multiplayer | Networking.md, Replication.md |
| Gameplay-Systeme | Pathfinding.md, AIArchitecture.md |
| Präsentation | Rendering.md, Lighting.md, AnimationSystem.md, InputSystem.md, AudioArchitecture.md |
| Budgets & Betrieb | PerformanceBudget.md, MemoryBudget.md, AssetBudget.md, Testing.md, Deployment.md |

**10 Architektur-Entscheidungen getroffen** (DecisionLog v1.5.0):
- **D-033** Determinismus-fähige Command-Simulation (5 Regeln), Lockstep über Command-Relay ab Beta (Q-013)
- **D-034** Pathfinding: Integer-Grid + Flow Fields + ORCA ab Alpha (Q-014)
- **D-035** OOP+SO-Gerüst, Burst/Jobs-Hotspots, Unity-freie `Nova.Simulation`, kein DOTS im MVP (Q-015)
- **D-036** `Nova.SimRunner` für headless KI-vs-KI-Läufe (Q-020)
- **D-037** Burst/Managed-Doppelstruktur mit Pflicht-Hash-Parität (löst die zentrale TDD-Spannung)
- **D-038** Disconnect-Regel final (60-s-Grace → KI-Übernahme, kein Re-Entry)
- **D-039** Audio: Unity Audio MVP hinter `IAudioService`, FMOD ab Alpha
- **D-040** Forward-Renderer, Realtime-only-Lighting (kein Baking)
- **D-041** Crash-Reporting: Sentry
- **D-042** Sim-Tick ≤8 ms gesamt (Budget-Spannung aufgelöst), Trümmer-Fade 60 s, keine Replay-Vollaufzeichnung

**Exit-Kriterien:** alle P0-Architekturfragen entschieden (Q-013/14/15/20) ✓ | Schnittstellen dokumentiert (C#-API-Skizzen in allen Kern-Dokumenten) ✓ | keine Implementierung ✓

## 2. Konsistenzreview (Zusammenfassung)

- **Gemeldete Spannungen: 5**, alle aufgelöst und entschieden: Burst vs. Unity-freie Sim (D-037, von drei Agenten unabhängig erkannt – das wichtigste Review-Ergebnis), Disconnect-Regel GDD↔TDD (D-038), Sim-Tick-Budget-Spannung D-034↔PerformanceBudget (D-042.1), zwei Verfahrenslücken (fehlende D-IDs für Audio und Licht, D-039/D-040), Crash-Reporting (D-041).
- **Detail-Angleichungen:** VictoryConditions.md, MultiplayerModes.md, PerformanceBudget.md, Networking.md (Statuskorrekturen) – grep-verifiziert, keine abweichenden Live-Reste.
- **Strukturprüfung:** Assembly-Modell (8 Assemblies, `noEngineReferences` erzwingt D-033/D-035 werkzeugseitig), Dependency-Graph ohne Zyklen, Verbotsliste aktiv.

## 3. Self Review

**Stärken:** Die Research-Vorlagen erwiesen sich als entscheidungsreif – alle vier P0-Fragen fielen ohne Zusatzrecherche; die Agenten erkannten die Burst/Unity-frei-Spannung proaktiv und eskalierten statt zu pfuschen; SimRunner (D-036) macht Balancing-Pipeline Stufe 2 und Golden-Master-Tests zum Nebenprodukt der Architektur.

**Schwächen:**
- Drei Subagenten fielen durch ein Provider-Kontingent aus und mussten fortgesetzt werden – Prozess resilient (Resume), aber Terminunschärfe.
- Eine Datei (`Serialization.md`) kollidierte zwischenzeitlich mit parallelen Läufen und wurde neu geschrieben – bestätigt die AGENTS.md-Regel "heiße Dateien: ein Schreiber".
- Verfahrenslücken (Research-Empfehlungen ohne D-ID) wurden erst in Sprint 3 geschlossen – ab Sprint 4 werden Research-Empfehlungen grundsätzlich im selben Sprint ratifiziert.

## 4. Architecture Review

Eigenreview (die unabhängige Prüfung folgt in Sprint 4):
- **Tragfähigkeit:** Die Architektur beantwortet die drei härtesten Projektfragen (500 Einheiten, MP ohne Rewrite, determinismus-fähige Balancing-CI) mit einem einzigen kohärenten Modell (Command-Pipeline + Unity-freie Sim + Grid-Infrastruktur).
- **Bekannte Schwachstellen (an Sprint 4 übergeben):** (1) Burst/Managed-Doppelpfad = Paritäts-Risiko (D-037-Mitigation: Hash-Tests, Re-Eval nach Spike); (2) Fixed-Point-Umstellung Beta ist ein geplanter, aber nicht unterschätzter Eingriff; (3) KI-Bedrohungskarten-Auflösung und Snapshot-Größen ungemessen; (4) Reconnect-Snapshot-Quelle (Client-Upload vs. Server-Instanz) offen.
- **Validierungs-Rückstellungen:** alle vier Phase-0-Spikes bleiben Pflicht (Fixed-Point ARM↔x86, Resident Drawer, Animator vs. Playables, PF-Budget Managed-Pfad).

## 5. Risikoanalyse (Update)

Vollständig in [../RiskAnalysis.md](../RiskAnalysis.md) v1.3.0:
- **R-02 (MP-Architektur zu spät) entschärft:** D-033 entschieden, MP ist jetzt Transport-Thema.
- **R-03 (Pathfinding) reduziert:** D-034 entschieden; Restrisiko hängt nur noch an der Phase-0-Budget-Messung.
- **Neu R-12 (klein):** Burst/Managed-Paritäts-Risiko (D-037-Mitigation aktiv).

## 6. Qualitätsbewertung

| Kriterium | Bewertung | Anmerkung |
|---|---|---|
| Vollständigkeit (TDD-Liste) | gut | alle 23 geplanten Dokumente, keine Lücken |
| Entscheidungsdisziplin | sehr gut | 10 Entscheidungen mit Alternativen; 5 Spannungen eskaliert statt versteckt |
| Umsetzungsreife für Sprint 7 | gut | API-Skizzen, Assembly-Matrix, Folder-Struktur, Budgets konkret |
| Messbarkeit | gut | Budgets mit P95-Methodik, Referenzhardware-Anforderung, CI-Gates |
| Verbleibende Unsicherheit | akzeptiert | bewusst auf Phase-0-Spikes und Sprint-4-Review verwiesen |

## 7. Offene Punkte

- Nur noch **Q-018** (Preispunkt) und **Q-019** (Telemetrie) offen – beide Sprint 6.
- Folgepunkte (keine Blocker): KI-Bedrohungskarten-Auflösung, Evolvierte-Plan-Tasks, Snapshot-Größenmessung, Fixed-Point-Bibliothekswahl (Beta), Windows-Referenzhardware fixieren (Sprint 4), Analyzer-Enforcement (Sprint 7).
- Vier Phase-0-Spike-Validierungen bleiben als Pflicht-Checkliste für Sprint 7 registriert.

## 8. Entscheidung über den nächsten Sprint

**GO für Sprint 4 – Architecture Review.**

Begründung: Alle Exit-Kriterien erfüllt; die Architektur ist vollständig dokumentiert und entscheidungsfest. Jetzt ist der richtige Moment für unabhängige Prüfung, bevor Sprint 5 (Asset Audit) und Sprint 7 (Implementierung) darauf aufbauen.

**Sprint-4-Scope (festgelegt):** Unabhängige Review-Agenten mit ausdrücklichem Widerspruchs-Mandat prüfen das TDD auf: Architekturfehler, Performance-Risiken (500 Einheiten, Budgets), Skalierungsprobleme (Karten L, Spieler 6), Wartungsprobleme (Doppelpfad D-037, SO-Registry), Multiplayer-Probleme (Lockstep-Relay, Desync, Reconnect). Jeder Befund: dokumentiert, klassifiziert (kritisch/hoch/mittel/niedrig), mit empfohlener Maßnahme. Kritische Befunde werden vor Sprint-4-Abschluss eingearbeitet; Windows-Referenzhardware fixieren.

## Offene Punkte

- Keine zusätzlich zu §7.

## Nächste Schritte

- Commit/Push (Versionsbump 0.4.0, dauerhaft freigegeben), dann Sprint 4 starten.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Sprint 3 abgeschlossen, GO für Sprint 4 | Executive Producer |
