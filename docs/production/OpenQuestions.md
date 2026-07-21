# Open Questions

**Version:** 1.4.0 | **Status:** aktiv (laufend) | **Verantwortungsbereich:** Executive Producer | **Sprint:** 3

## Zweck

Zentrales Register aller offenen Fragen mit Owner-Sprint und Priorität. Eine Frage gilt als geschlossen, wenn die Entscheidung im [DecisionLog.md](DecisionLog.md) steht und die betroffenen Dokumente aktualisiert sind.

## Abhängigkeiten

- [../analysis/Inconsistencies.md](../analysis/Inconsistencies.md) (Q-001–Q-012)
- [../analysis/PriorityList.md](../analysis/PriorityList.md)
- [DecisionLog.md](DecisionLog.md)

## Offene Fragen

| ID | Prio | Frage | Herkunft | Owner-Sprint | Status |
|---|---|---|---|---|---|
| Q-018 | P3 | Preispunkt: 29,99 / 34,99 / 39,99 €? Markt-Research deckt das nicht ab. | Sprint-2-Review | 6 | offen |
| Q-019 | P2 | Telemetrie-Infrastruktur (Opt-in, ab Beta, für Balancing-Stufe 5): Pflicht-Feature mit eigenem Backend oder Streichung? D-007-Offline-Positionierung beachten. | Balancing.md-Review | 6 | offen (Vorhaltung: Compile-Schaltstelle in tech/Deployment.md) |

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
| Q-013 | **D-033 + D-037 + D-038** – determinismus-fähige Command-Simulation (5 Regeln), Lockstep über Command-Relay ab Beta; Burst/Managed-Doppelstruktur; Disconnect-Regel final | Sprint 3 |
| Q-014 | **D-034** – Integer-Grid 1 m + Flow Fields + lokale Vermeidung (ORCA ab Alpha), Budget ≤4 ms | Sprint 3 |
| Q-015 | **D-035** – MonoBehaviour-OOP + SO + Burst/Jobs-Hotspots, Unity-freie `Nova.Simulation`, kein Entities im MVP | Sprint 3 |
| Q-016 | **D-007** – Premium SP/Skirmish-first, H1 C&C-Nostalgiker primär | Sprint 2 |
| Q-017 | **D-012** – gezielte Zerstörbarkeit, keine Terrain-Deformation | Sprint 2 |
| Q-020 | **D-036** – `Nova.SimRunner` (.NET-Konsole auf Nova.Simulation) für KI-vs-KI-CI-Läufe | Sprint 3 |

## Regeln

- Neue Fragen erhalten die nächste freie ID und werden nie wiederverwendet.
- Bei Sprint-Abschluss wird geprüft, welche Fragen fällig waren und ob sie geschlossen sind.

## Offene Punkte

- Nur noch Q-018 (Preispunkt, Sprint 6) und Q-019 (Telemetrie-Infrastruktur, Sprint 6) offen.
- Aus Research hängen vier Pflicht-Validierungen am Phase-0-Spike: Fixed-Point-Determinismus ARM↔x86, URP GPU Resident Drawer, Animator vs. Playables, Pathfinding-CPU-Budget (Managed-Pfad, D-037).
- Terminierte Folgepunkte aus dem TDD-Review (keine Blocker): KI-Bedrohungskarten-Auflösung, Evolvierte-Plan-Tasks, Snapshot-Größenmessung, Fixed-Point-Bibliothekswahl (Beta), Analyzer-Enforcement (Sprint 7), Windows-Referenzhardware fixieren (Sprint 4).

## Nächste Schritte

- Sprint 3 abschließen (Abschlussbericht), danach Sprint 4: unabhängige Architecture-Review-Agenten mit Widerspruchs-Mandat.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Q-001 bis Q-015 eröffnet (Sprint 0) | Executive Producer |
| 1.1.0 | 2026-07-21 | Q-013–Q-015 Research-Status; Q-016, Q-017 neu aus Sprint 1 | Executive Producer |
| 1.2.0 | 2026-07-21 | Q-001–Q-012, Q-016, Q-017 entschieden (D-007–D-030); Q-018–Q-020 neu aus Konsistenzreview | Executive Producer |
| 1.3.0 | 2026-07-21 | Q-001–Q-012, Q-016, Q-017 formal geschlossen (Sprint-2-Abschluss, D-007–D-032) | Executive Producer |
| 1.4.0 | 2026-07-21 | Q-013, Q-014, Q-015, Q-020 formal geschlossen (Sprint 3, D-033–D-038) | Executive Producer |
