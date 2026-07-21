# Prioritätenliste

**Version:** 1.0.0 | **Status:** sprint-freigegeben (Sprint 0) | **Verantwortungsbereich:** Executive Producer | **Sprint:** 0

## Zweck

Priorisierte Arbeitsliste über alle erkannten Aufgaben, Lücken und Risiken hinweg. Steuert die Reihenfolge innerhalb und zwischen den Sprints. Wird am Ende jedes Sprints neu bewertet.

## Abhängigkeiten

- [KnowledgeBase.md](KnowledgeBase.md), [Inconsistencies.md](Inconsistencies.md), [GapAnalysis.md](GapAnalysis.md)
- [../production/RiskAnalysis.md](../production/RiskAnalysis.md), [../production/OpenQuestions.md](../production/OpenQuestions.md)

## Prioritätsstufen

- **P0 – blockierend:** Ohne Klärung ist belastbare Planung oder Architektur unmöglich.
- **P1 – hoch:** Prägt Kernspiel oder Architektur; muss in den frühen Sprints entschieden werden.
- **P2 – mittel:** Wichtig für Produktqualität, aber nicht strukturblockierend.
- **P3 – später:** Bewusst in späte Phasen verschoben (konsistent zu TPD §14/§16).

## P0 – Blockierend

| # | Thema | Begründung | Sprint |
|---|---|---|---|
| P0-1 | Simulations- & Multiplayer-Modell (Q-013) | Lockstep vs. Server-autoritativ vs. Hybrid bestimmt Determinismus-Anforderungen, gesamten Gameplay-Code, Netcode und Replay-System. Muss **vor** Sprint-3-Architektur researched sein. | 1 → 3 |
| P0-2 | Pathfinding-Ansatz (Q-014) | 100–500+ Einheiten, Formationen, dynamische Hindernisse: größtes technisches Risiko laut TPD Phase 0. Research vor Architektur. | 1 → 3 |
| P0-3 | ECS/DOTS vs. klassisches OOP (Q-015) | Fundamentale Codebasis-Entscheidung; nachträglich praktisch nicht änderbar. | 1 → 3 |
| P0-4 | Gebäude-Scope (I-01/Q-001) | 11 vs. 18 Gebäudetypen entscheidet über Asset-Budget, Balancing, UI und Produktionszeit. | 2 |
| P0-5 | Commander-System (I-06/Q-002) | Mögliches Kernfeature ohne jede Definition – beeinflusst Game Design, Assets, UI. | 2 |

## P1 – Hoch

| # | Thema | Begründung | Sprint |
|---|---|---|---|
| P1-1 | Vision, USP, Zielgruppe | Ohne Leitbild keine begründbaren Design-Trade-offs (Qualitätsregel: bewusste Entscheidungen). | 2 |
| P1-2 | Aetherium-Wirtschaftsregel (Q-005) | Regeneration vs. Erschöpfung steuert Match-Dauer, Aggression, Map-Control – zentraler Balance-Hebel. | 2 |
| P1-3 | Fraktions-Vertiefung inkl. Evolvierte-Sonderregeln (Q-009) | Asymmetrie ist Kern des Designs; Evolvierte-Bauweise offen. | 2 |
| P1-4 | Markt-/Wettbewerbsanalyse RTS | Positionierung, USP-Validierung, realistische Scope-Kalibrierung. | 1 |
| P1-5 | Fog-of-War-Technik-Research | Performance-kritisch bei großen Karten; beeinflusst Rendering und Netcode. | 1 |
| P1-6 | Determinismus-Anforderung konkretisieren | TPD §15 sagt "deterministisch oder kontrolliert" – muss für Savegames, Replays, MP präzisiert werden. | 3 |

## P2 – Mittel

| # | Thema | Sprint |
|---|---|---|
| P2-1 | Damage-/Armor-System & Waffenmatrix | 2 |
| P2-2 | ResearchTree (Tier 1–3 Ausarbeitung) | 2 |
| P2-3 | Karten-/Biome-Regelwerk inkl. Wetter (Q-010, Q-012) | 2 |
| P2-4 | Drohnen- & Neutral-Einheiten-Rollen (Q-004, Q-007) | 2 |
| P2-5 | Marine-Entscheidung: streichen oder Phase 4+ (Q-003) | 2/6 |
| P2-6 | UI/UX- und Audio-Konzept | 2–3 |
| P2-7 | Performance-/Memory-/Asset-Budgets | 3 |
| P2-8 | Asset-Store-Recherche & Lizenzregister | 5 |
| P2-9 | Testing- & Deployment-Strategie | 3 |

## P3 – Bewusst später (TPD §16)

Backend-Sprache & Hosting, Matchmaking/Ranglisten, Modding/Workshop, DRM/Vertrieb, Crossplay, Konsolen, Kampagne, Marine (falls nicht gestrichen), Smartphone-Version, WebGL-Build.

## Bewertungslogik

P0-Einträge dominieren die Sprints 1–3, weil sie Architektur und Scope fundamentieren; P1 sichert die Design-Qualität; P2 füllt die Fachdokumente; P3 bleibt explizit offen und darf frühe Arbeit nicht blockieren (TPD-Vorgabe).

## Offene Punkte

- Neu-Priorisierung am Ende jedes Sprints im Sprint-Bericht.

## Nächste Schritte

- Sprint 1 adressiert P0-1, P0-2, P0-3, P1-4, P1-5 durch Research-Dokumente mit je mindestens drei verglichenen Alternativen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Initiale Priorisierung (Sprint 0) | Executive Producer |
