# Sprint-1-Bericht – Research

**Version:** 1.0.0 | **Status:** Sprint abgeschlossen | **Verantwortungsbereich:** Executive Producer | **Sprint:** 1

## Zweck

Verbindlicher Abschlussbericht von Sprint 1 (Research) gemäß Sprint-Ritual ([../SprintPlanning.md](../SprintPlanning.md)): Dokumentationsstand, Synthese inkl. Konfliktlösung, Self Review, Architecture Review, Risikoanalyse, Qualitätsbewertung, offene Punkte, Entscheidung über den nächsten Sprint.

## Abhängigkeiten

- Alle 10 Research-Dokumente unter [../../research/](../../research/)
- [../DecisionLog.md](../DecisionLog.md), [../OpenQuestions.md](../OpenQuestions.md), [../RiskAnalysis.md](../RiskAnalysis.md)

## 1. Ergebnisse des Sprints

Zehn parallele Research-Aufträge, ausgeführt von spezialisierten Subagenten mit Web-Recherche und Quellenbelegen:

| # | Thema | Dokument | Kernergebnis |
|---|---|---|---|
| 1 | RTS-Markt & Wettbewerb | [RTS_Markt_Wettbewerb.md](../../research/RTS_Markt_Wettbewerb.md) | Premium SP/Skirmish-first; Aetherium-USP stärkst; Stormgate als Negativbeleg für Server-MP-Fundament |
| 2 | Multiplayer-Simulation | [Multiplayer_Simulation.md](../../research/Multiplayer_Simulation.md) | Lockstep über autoritativem Command-Relay; 5 Determinismus-Architekturregeln (Vorlage Q-013) |
| 3 | ECS/DOTS | [Unity_ECS_DOTS.md](../../research/Unity_ECS_DOTS.md) | OOP+SO-Gerüst mit Burst/Jobs-Hotspots; kein Voll-DOTS im MVP (Vorlage Q-015) |
| 4 | Pathfinding | [Pathfinding.md](../../research/Pathfinding.md) | Uniformes Integer-Grid + Flow Fields + ORCA-Eigenbau (Vorlage Q-014) |
| 5 | Fog of War | [FogOfWar.md](../../research/FogOfWar.md) | Grid-/Bitmask-Sichtmodell als einzige Wahrheit, URP-Textur nur Präsentation |
| 6 | RTS-Architekturen | [RTS_Architekturen_OpenSource.md](../../research/RTS_Architekturen_OpenSource.md) | Vier-Säulen-Muster (Sim/View-Trennung, Commands, fester Tick, datengetrieben) bei OpenRA, Recoil/BAR, AoE, PA belegt |
| 7 | Unity Best Practices | [Unity_BestPractices.md](../../research/Unity_BestPractices.md) | D-002 bestätigt → **D-006: Unity 6.3 LTS + URP**; SO-Leitplanken, Assembly-Struktur |
| 8 | KI-Architektur | [KI_Architektur.md](../../research/KI_Architektur.md) | Drei-Schichten-Hybrid (Utility-Director + HTN-light + Squad-BTs), Difficulty als Profildaten |
| 9 | Animation/Audio/UI | [Animation_Audio_UI.md](../../research/Animation_Audio_UI.md) | Mecanim/Code-Hybrid + Animations-LOD; Unity Audio MVP → FMOD ab Alpha; UI Toolkit primär |
| 10 | Asset-Store-Landschaft | [AssetStore_Landschaft.md](../../research/AssetStore_Landschaft.md) | Multi-Store-Mix, Synty als Stil-Anker, keine Komplett-Frameworks; Evolvierte/Aetherium = MODIFY/BUILD |

Exit-Kriterium "≥3 Alternativen pro kritischem Thema": **erfüllt** in allen 10 Dokumenten.

## 2. Synthese – konvergierende Architektur-Linie

Über alle Dokumente hinweg konvergiert eine Linie, die in Sprint 3 verbindlich zu fassen ist:

1. **Vier-Säulen-Architektur** (belegt durch 4 Referenzprojekte): harte Trennung Simulation/Präsentation, Commands als einzige mutierende Schnittstelle, fester Sim-Tick mit entkoppeltem Rendering, vollständig datengetriebene Definitionen.
2. **Unity-freier Simulationskern** (`Nova.Simulation`): Voraussetzung für Determinismus-Fähigkeit, autoritativen Server und spätere Engine-Portierbarkeit.
3. **OOP+SO als Gerüst**, Burst/Jobs für Hotspots (Pathfinding, FoW, Sicht); kein Voll-DOTS im MVP.
4. **Singleplayer als "lokaler Server"** strukturieren: Dann ist Multiplayer später ein Transport-Thema, kein Rewrite (löst die TPD-Spannung "MP später" vs. "kein Rewrite").
5. **MVP-Umfang der Markt-These folgend**: Premium, SP-first, Aetherium als spielbarer USP, Zerstörbarkeit gezielt statt vollständig.

## 3. Konfliktlösung (Orchestrierung)

**Konflikt K-1 (Q-013):** Das Multiplayer-Dokument empfiehlt striktes deterministisches Lockstep; das FoW-Dokument zeigt, dass Lockstep Map-Hacks prinzipiell ermöglicht (voller Zustand auf jedem Client) und nur server-autoritativer State-Sync maphack-resistent ist; das Architektur-Referenzdokument verwirft striktes Lockstep zugunsten "determinismus-*fähig*" mit Command-Replikation + Delta-Snapshots (PA-Hybrid).

**Vorverhandelte Linie (finale Entscheidung Sprint 3):**
- Verbindlich ab sofort: **determinismus-fähige, befehlsgetriebene Tick-Simulation** (die 5 Architekturregeln aus [Multiplayer_Simulation.md](../../research/Multiplayer_Simulation.md): Command-getriebener Tick, keine UnityEngine-APIs im Sim-Pfad, fester Takt, eigener PRNG, serialisierbarer State). Diese Regeln sind mit allen drei MP-Modellen kompatibel und kosten nichts.
- Zielbild: Lockstep über autoritativem Input-/Command-Relay-Server (erfüllt TPD §9 "autoritativer Server" über Befehle, Takt und Match-Ergebnis; Replays/Beobachter gratis).
- Maphack-Risiko: für MVP/Koop akzeptiert (SC2-Präzedenzfall); für Ranked (Phase 3+) Pflicht-Re-Evaluierung mit serverseitigem Sichtgrid.
- Offene technische Validierung: Fixed-Point-Determinismus ARM↔x86 im Phase-0-Spike; Fallback Photon Quantum 3.

**Konflikt K-2 (Zerstörbarkeit):** Vision ("vollständig zerstörbar") vs. Markt-Research (parken, kein Marktbeleg, Konflikt mit Q-013/Q-014) und R-05. → Als **Q-017** an Sprint 2 übergeben mit der Empfehlung "gezielte Zerstörbarkeit statt Vollzerstörbarkeit"; keine technische Vorwegnahme.

## 4. Self Review

**Stärken:** Vollständige Abdeckung aller 10 Aufträge; Quellenbelege (u. a. GDC-1500-Archers-Paper, Supreme-Commander-2-Flow-Field-Paper, Unity-Discussions, Recoil-Stress-Tests); Einschätzungen sauber als solche gekennzeichnet; ein echter Inter-Dokument-Konflikt (K-1) wurde erkannt statt übersehen.

**Schwächen:**
- Kein dediziertes Research zu Balancing-Methodik, Lokalisierung und Accessibility – wird in Sprint 2 (Balancing.md) bzw. Sprint 3 nachgeholt, Lücke ist bekannt.
- Teilweise Drittschätzungen bei Verkaufszahlen (als solche markiert); belastbar genug für Richtungsentscheidungen, nicht für Finanzplanung.
- Die Research-Dichte erzeugt Abhängigkeiten zwischen Vorlagen (FoW↔Q-013, KI↔Q-014) – Sprint 3 muss die Entscheidungen im Verbund treffen, nicht isoliert.

## 5. Architecture Review

- **Konsistenz der Vorlagen:** Geprüft; außer K-1/K-2 (gelöst/übergeben) keine Widersprüche. KI-Dokument ist bewusst Q-013-neutral gehalten (Command-only-Zugriff) – bestätigt die Vier-Säulen-Linie.
- **Neuer Architekturgrundsatz (aus Research, zur Sprint-3-Verabschiedung vorgemerkt):** gekaufte RTS-Komplett-Frameworks sind ausgeschlossen, da sie Q-013/Q-015 faktisch vorwegentscheiden würden (Asset-Research, bestätigt durch Architektur-Research).
- **Befund:** Die Research-Ergebnisse verändern keinen verbindlichen Beschluss aus Sprint 0; D-002 wurde ordnungsgemäß validiert und als D-006 konkretisiert. Prozesskonform.

## 6. Risikoanalyse (Update)

Vollständig in [../RiskAnalysis.md](../RiskAnalysis.md) v1.1.0:
- **R-10 neu** (mittel/hoch): Geschäftsmodell-Fehlgriff Server-MP als Fundament (Stormgate-Beleg) → Mitigation via Q-016.
- **R-11 neu** (niedrig/mittel): Unity-Reputations-/Plattformrisiko → Mitigation: Unity-freier Sim-Kern.
- **R-09 teilentschärft** (externe Daten vorhanden); **R-02/R-03 Fortschritt** (Vorlagen vorhanden, Restrisiko an Sprint 3 + Phase-0-Spikes).

## 7. Qualitätsbewertung

| Kriterium | Bewertung | Anmerkung |
|---|---|---|
| Vollständigkeit (10/10 Themen) | gut | alle Aufträge mit Pflichtaufbau geliefert |
| Alternativen-Vergleich ≥3 | gut | in allen Dokumenten erfüllt, mit Verwerfungsgründen |
| Quellenlage | gut | URLs zitiert; Schätzwerte gekennzeichnet |
| Konflikttransparenz | gut | K-1/K-2 dokumentiert und vorverhandelt |
| Entscheidungsreife Q-013/14/15 | gut mit Vorbehalt | Vorlagen decisionlog-fertig; 4 Punkte brauchen Phase-0-Spike-Messungen (Determinismus ARM/x86, Resident Drawer, Animator vs. Playables, PF-Budget) |

## 8. Offene Punkte

- Q-013/Q-014/Q-015: Research geliefert → Entscheidung Sprint 3 (Status in [../OpenQuestions.md](../OpenQuestions.md) aktualisiert).
- **Q-016 neu:** Geschäftsmodell & Zielgruppe (Premium, SP-first, C&C-Nostalgiker H1) – Sprint 2.
- **Q-017 neu:** Zerstörbarkeits-Umfang – Sprint 2.
- Vier Pflicht-Validierungen am Phase-0-Spike registriert (siehe OpenQuestions "Offene Punkte").

## 9. Entscheidung über den nächsten Sprint

**GO für Sprint 2 – Game Design.**

Begründung: Alle Sprint-1-Exit-Kriterien erfüllt; die Design-seitigen P0/P1-Fragen (Q-001, Q-002, Q-005, Q-009, Q-016, Q-017) können jetzt auf recherchierter Markt- und Machbarkeitslage entschieden werden; Sprint 3 benötigt ein konsistentes GDD als Eingabe.

**Sprint-2-Scope (festgelegt):**
1. Vision-Block: Vision.md, USP.md (Aetherium-Fokus), TargetAudience.md (H1 primär), CoreGameplay.md (inkl. Q-008-Kameraklarstellung), GameLoop.md
2. GDD-Kern: Factions.md, Buildings.md (Q-001, Q-009), Vehicles/Aircraft/Infantry.md (Q-004, Q-006), Resources.md + Economy.md (Q-005), ResearchTree.md, Weapons/DamageSystem/ArmorSystem.md
3. Welt & Regeln: Maps.md + Biomes.md (Q-010, Q-012), NeutralUnits.md (Q-007), FogOfWar.md (Design-Regeln auf Research-Basis), VictoryConditions.md, CommanderSystem.md (Q-002), MultiplayerModes.md (Q-011, unter Q-016-Prämisse), Balancing.md (Methodik), Campaign.md (Phase-3-Konzeptrahmen)
4. Verbindliche Prämissen aus Research: Premium SP-first, Aetherium-USP, gezielte Zerstörbarkeit (Q-017-Empfehlung), Marine-Streichung als Empfehlung (Q-003)
5. Alle Entscheidungen als D-007 ff. im DecisionLog; Konsistenzcheck über alle GDD-Dokumente; keine Implementierung.

## Offene Punkte

- Keine zusätzlich zu Abschnitt 8.

## Nächste Schritte

- Sprint 2 starten: Game-Design-Dokumente parallel über Subagenten erstellen, anschließend Konsistenzreview und DecisionLog-Einträge.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Sprint 1 abgeschlossen, GO für Sprint 2 | Executive Producer |
