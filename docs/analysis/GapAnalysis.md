# Gap-Analyse – Fehlende Bereiche und Dokumente

**Version:** 1.0.0 | **Status:** sprint-freigegeben (Sprint 0) | **Verantwortungsbereich:** Executive Producer | **Sprint:** 0

## Zweck

Inventar aller Bereiche, die für das angestrebte Produkt und die geforderte Dokumentstruktur notwendig, aber in den Quelldokumenten (GDD-O, TPD, APL) nicht oder unzureichend abgedeckt sind. Dient der Sprint-Planung als Vollständigkeitsmaßstab.

## Abhängigkeiten

- [KnowledgeBase.md](KnowledgeBase.md)
- [Inconsistencies.md](Inconsistencies.md)
- [../production/SprintPlanning.md](../production/SprintPlanning.md)

## 1. Fehlende Vision-Dokumente (Sprint 2)

GDD-O liefert zwei Sätze Vision – es fehlt vollständig:

- **Vision.md** – Leitbild, künstlerischer Anspruch, Design-Säulen
- **USP.md** – Alleinstellungsmerkmale gegenüber Konkurrenz (dynamic crystal fields, zerstörbare Umgebung sind Kandidaten, aber unbewertet)
- **TargetAudience.md** – keine Zielgruppendefinition vorhanden (RTS-Veteranen? Neueinsteiger? Competitive?)
- **CoreGameplay.md / GameLoop.md** – Kernloop existiert nur als 6-Schritte-Skizze im TPD; Moment-zu-Moment-Gameplay, Match-Dauer, Tempo undefiniert

## 2. Fehlende Game-Design-Vertiefungen (Sprint 2)

| Bereich | Quellenstand | Lücke |
|---|---|---|
| Factions.md | 3 Fraktionen grob skizziert | keine Einheitenrollen, Stärken/Schwächen-Matrix, Spielstil-Definition |
| Buildings/Units | Listen in APL | keine Werte, Kosten, Rollen, Konter-Logik; I-01 (11 vs. 18 Gebäude) |
| Resources.md / Economy.md | Feature-Liste TPD §8.4 | keine Zahlen, Raten, Kurven; Regenerationsregel offen (Q-005) |
| ResearchTree.md | "Tier 1–3" | komplett offen |
| Weapons/DamageSystem/ArmorSystem | Feature-Liste TPD §8.6 | keine Schadens-/Panzerungstypen-Matrix |
| Maps.md / Biomes.md | 10 Themen | keine Kartengrößen, Spielerzahlen, Layout-Regeln (Q-010) |
| NeutralUnits.md | Liste in APL | keine Regeln (Q-007 Händler) |
| Campaign.md | im MVP ausgeschlossen | keinerlei Konzept für Phase 3 |
| MultiplayerModes.md | Modiliste | keine Regeln, Phasenzuordnung (Q-011) |
| Balancing.md | – | komplett fehlend (Methodik, Zielwerte) |
| CommanderSystem.md | nur Asset-Erwähnung | komplett offen (Q-002) |
| VictoryConditions.md | "Gegner vernichten" | alternative Siegbedingungen undefiniert |
| FogOfWar.md | Feature-Liste TPD §8.7 | Designregeln fehlen (Tarnung, Radar-Mechanik) |

## 3. Fehlende Technical-Design-Dokumente (Sprint 3)

Das TPD ist eine starke Ausgangslage, aber kein TDD. Es fehlen:

- **Architecture.md / ModuleOverview.md / DependencyGraph.md** – Modulstruktur, Schichten, Schnittstellen
- **FolderStructure.md** – TPD §10 liefert einen Vorschlag, der zu validieren und zu verabschieden ist
- **CodingGuidelines.md / NamingConvention.md** – nicht vorhanden
- **GameState.md / Serialization.md / Savegames.md** – Simulations- und Persistenzmodell offen; "deterministische oder kontrollierte Simulation" (TPD §15) ist eine der folgenreichsten offenen Architekturfragen (Wechselwirkung mit Multiplayer, Q-013)
- **Networking.md / Replication.md** – Simulationsmodell (Lockstep vs. State-Sync vs. Server-autoritativ) unentschieden (Q-013)
- **Pathfinding.md** – Grid/Flow-Field/Hybrid offen (Q-014)
- **AIArchitecture.md** – KI-Ebenen gelistet, Architektur (Behavior Trees / Utility / GOAP / HTN) offen
- **Rendering.md / Lighting.md / AnimationSystem.md / InputSystem.md / AudioArchitecture.md** – nicht vorhanden
- **PerformanceBudget.md / MemoryBudget.md / AssetBudget.md** – Ziele genannt (60 FPS), keine Budgets
- **Testing.md / Deployment.md** – "automatisierte Tests" gefordert, Strategie fehlt
- **ECS/DOTS-Frage** (Q-015): TPD entscheidet nicht, ob klassisches OOP/MonoBehaviour oder DOTS – weitreichende Architekturfolgen

## 4. Fehlende Asset-Pipeline-Dokumente (Sprint 5)

APL listet Bedarfe, aber es fehlen: AssetAudit.md, AssetStoreResearch.md, kategoriebezogene Recherchedokumente, SignatureAssets.md (Definition & Produktionsplan), Licenses.md (Lizenzregister). Keine Kosten-, Qualitäts- oder Anpassungsaufwands-Bewertung vorhanden.

## 5. Fehlende Production-Dokumente (Sprint 0–6)

- Vorhanden ab Sprint 0: [SprintPlanning](../production/SprintPlanning.md), [DecisionLog](../production/DecisionLog.md), [OpenQuestions](../production/OpenQuestions.md), [RiskAnalysis](../production/RiskAnalysis.md), Sprint-Berichte
- Fehlen noch: Roadmap.md, Milestones.md (Sprint 6), ArchitectureDecisions.md (ADR-Sammlung, wird ab Sprint 3 aus DecisionLog gespeist)

## 6. Fachliche Querschnittslücken

- **Audio:** kein Konzept (Musikstil, Adaptive Audio, Sprachausgabe) – nur Asset-Bedarf in APL
- **UI/UX:** kein Konzept außer Feature-Erwähnungen; HUD-Dichte, Interaktionsmodelle, Accessibility-Grundsätze fehlen
- **Lokalisierung/Accessibility:** nur als Phase-3-Stichwort im TPD
- **Zielgruppe & Markt:** keine Wettbewerbsanalyse (wird in Sprint 1 Research nachgeholt)

## Offene Punkte

- Die Gap-Liste definiert den Lieferumfang der Sprints 1–6; Vollständigkeit wird in jedem Sprint-Bericht erneut geprüft.

## Nächste Schritte

- Sprint 1: Research-Lücken (§3, §6) mit Markt-/Technikrecherche schließen
- Sprint 2: §1 und §2 vollständig abarbeiten

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Initiale Gap-Analyse (Sprint 0) | Executive Producer |
