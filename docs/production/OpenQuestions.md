# Open Questions

**Version:** 1.3.0 | **Status:** aktiv (laufend) | **Verantwortungsbereich:** Executive Producer | **Sprint:** 2

## Zweck

Zentrales Register aller offenen Fragen mit Owner-Sprint und Priorität. Eine Frage gilt als geschlossen, wenn die Entscheidung im [DecisionLog.md](DecisionLog.md) steht und die betroffenen Dokumente aktualisiert sind.

## Abhängigkeiten

- [../analysis/Inconsistencies.md](../analysis/Inconsistencies.md) (Q-001–Q-012)
- [../analysis/PriorityList.md](../analysis/PriorityList.md)
- [DecisionLog.md](DecisionLog.md)

## Offene Fragen

| ID | Prio | Frage | Herkunft | Owner-Sprint | Status |
|---|---|---|---|---|---|
| Q-013 | P0 | Simulations- & Multiplayer-Modell: deterministisches Lockstep, Server-autoritativer State-Sync oder Hybrid? Folgen für Determinismus, Replays, Cheating, Architektur. | TPD §9/§15 | 3 | Research geliefert ([../research/Multiplayer_Simulation.md](../research/Multiplayer_Simulation.md)); Konflikt vorverhandelt ([sprints/Sprint01_Report.md](sprints/Sprint01_Report.md) §3); Entscheidung Sprint 3 |
| Q-014 | P0 | Pathfinding: Grid, Flow-Field, NavMesh-Hybrid oder anderes bei 100–500+ Einheiten mit Formationen und dynamischen Hindernissen? | TPD §8.3 | 3 | Research geliefert ([../research/Pathfinding.md](../research/Pathfinding.md)); Entscheidung Sprint 3, Zahlen via Phase-0-Spike |
| Q-015 | P0 | ECS/DOTS vs. klassisches MonoBehaviour-OOP vs. Hybrid (DOTS nur für Simulation)? | Gap-Analyse §3 | 3 | Research geliefert ([../research/Unity_ECS_DOTS.md](../research/Unity_ECS_DOTS.md)); Entscheidung Sprint 3 |
| Q-018 | P3 | Preispunkt: 29,99 / 34,99 / 39,99 €? Markt-Research deckt das nicht ab. | Sprint-2-Review | 6 | offen |
| Q-019 | P2 | Telemetrie-Infrastruktur (Opt-in, ab Beta, für Balancing-Stufe 5): Pflicht-Feature mit eigenem Backend oder Streichung? D-007-Offline-Positionierung beachten. | Balancing.md-Review | 3/6 | offen |
| Q-020 | P1 | Headless-KI-Runner (KI-vs-KI-Simulationen für Balancing): Aufwand ungeschätzt; Voraussetzung für Balancing-Pipeline Stufe 2. Architektur und Aufwand klären. | Balancing.md-Review | 3 | offen |

## Geschlossene Fragen

| ID | Entscheidung | Geschlossen |
|---|---|---|
| Q-001 | **D-008** – 12 Gebäudetypen/Fraktion (Verteidigung als Modulsystem, inkl. Mauer) | Sprint 2 |
| Q-002 | **D-009** – Commander als Identitäts-Layer, keine Match-Mechanik im MVP | Sprint 2 |
| Q-003 | **D-013** – Marine gestrichen, Wasser nur Terrain-Feature | Sprint 2 |
| Q-004 | **D-014** – 2–3 Support-Drohnen/Fraktion, Produktion in bestehenden Fabriken | Sprint 2 |
| Q-005 | **D-010** – Aetherium-Hybrid: endlicher Mutterkristall + Nachwachsen + Ausbreitung + Überernte | Sprint 2 |
| Q-006 | **D-015** – 1 Elite/Fraktion (MVP), 3 (Release), Tier 3, hartes Limit | Sprint 2 |
| Q-007 | **D-016** – kein Handelssystem; Neutrale = Critters, Lager, capturebare Türme | Sprint 2 |
| Q-008 | **D-019** – schräge Top-Down-Perspektive, "isometrisch" ersetzt | Sprint 2 |
| Q-009 | **D-011** – Evolvierte: Keim→Reifung, Aetherium-Beschleunigung, Regeneration | Sprint 2 |
| Q-010 | **D-017** – Biome als Themen, Karten-Roadmap 1/4/8/12, Größen S/M/L | Sprint 2 |
| Q-011 | **D-018 + D-025** – Modi-Staffelung; Alpha-FFA lokal vs. KI, Online ab Beta | Sprint 2 |
| Q-012 | **D-017 + D-028** – Wetter pro Biom; Mond Strahlung, Mars Staub | Sprint 2 |
| Q-016 | **D-007** – Premium SP/Skirmish-first, H1 C&C-Nostalgiker primär | Sprint 2 |
| Q-017 | **D-012** – gezielte Zerstörbarkeit, keine Terrain-Deformation | Sprint 2 |

## Regeln

- Neue Fragen erhalten die nächste freie ID und werden nie wiederverwendet.
- Bei Sprint-Abschluss wird geprüft, welche Fragen fällig waren und ob sie geschlossen sind.

## Offene Punkte

- Q-013–Q-015: Research-Vorlagen liegen vor; Entscheidung in Sprint 3 (Technical Design).
- Q-020: Architektur/Aufwand des Headless-KI-Runners in Sprint 3 klären (Voraussetzung Balancing-Pipeline Stufe 2).
- Aus Research hängen vier Pflicht-Validierungen am Phase-0-Spike: Fixed-Point-Determinismus ARM↔x86, Nutzen des URP GPU Resident Drawer für bewegte Einheiten, Animator vs. Playables bei 500 Einheiten, Pathfinding-CPU-Budget ≤2–4 ms.
- Terminierte Design-Folge-Entscheidungen (keine Fragen, sondern geplante Fenster): Tor-Modul (Beta), Parasiten-Königin (Beta), Flak-DPS-Korridor (Balancing-Pass v0.2), Footprints/Grid-Tile (Sprint 3), Disconnect-Regel/Host-Migration (Sprint 3), Doktrinen (Beta), Rendersequenzen (Sprint 6).

## Nächste Schritte

- Sprint 3: Q-013, Q-014, Q-015, Q-020 entscheiden (als D-033 ff.).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Q-001 bis Q-015 eröffnet (Sprint 0) | Executive Producer |
| 1.1.0 | 2026-07-21 | Q-013–Q-015 Research-Status; Q-016, Q-017 neu aus Sprint 1 | Executive Producer |
| 1.2.0 | 2026-07-21 | Q-001–Q-012, Q-016, Q-017 entschieden (D-007–D-030); Q-018–Q-020 neu aus Konsistenzreview | Executive Producer |
| 1.3.0 | 2026-07-21 | Q-001–Q-012, Q-016, Q-017 formal geschlossen (Sprint-2-Abschluss, D-007–D-032) | Executive Producer |
