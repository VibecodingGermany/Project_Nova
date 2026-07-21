# Risikoanalyse

**Version:** 1.3.0 | **Status:** aktiv (laufend) | **Verantwortungsbereich:** Executive Producer / Lead Technical Director | **Sprint:** 3

## Zweck

Lebendes Risikoregister für das Gesamtprojekt. Wird am Ende jedes Sprints aktualisiert: neue Risiken aufnehmen, Eintrittswahrscheinlichkeit/Auswirkung neu bewerten, Maßnahmen wirksamkeitsprüfen.

## Abhängigkeiten

- [../analysis/KnowledgeBase.md](../analysis/KnowledgeBase.md)
- [../analysis/PriorityList.md](../analysis/PriorityList.md)
- Sprint-Berichte unter [sprints/](sprints/)

## Bewertungsskala

Wahrscheinlichkeit (W) und Auswirkung (A): niedrig / mittel / hoch. Risikowert = Kombination, sortiert absteigend.

## Risikoregister

| ID | Risiko | W | A | Beschreibung | Gegenmaßnahmen | Status |
|---|---|---|---|---|---|---|
| R-01 | Scope-Explosion | mittel | hoch | AAA-Anspruch bei ~54 Gebäuden, 24 Infanterie, 36 Fahrzeugen, 21 Lufteinheiten, 10 Biomen übersteigt jede realistische Einzelstudio-Kapazität um Größenordnungen. | Strikte MVP-Disziplin (TPD §14), Phasenmodell, Scope-Entscheidungen in Sprint 2 mit Kapazitätsrealität, "Feature kommt rein, wenn Kern stabil" | teilentschärft (Sprint 2: Scope beziffert – 36 Gebäude-Assets statt 54, 9 Eliten statt 15, Marine/Handel/Drohnen-Inflation gestrichen; Restrisiko: Umsetzungs-Disziplin) |
| R-02 | Multiplayer-Architektur zu spät entschieden | niedrig | hoch | TPD sagt "MP erst nach Singleplayer-Kern" – aber Simulationsmodell (Q-013) und Determinismus-Anforderung müssen **vor** dem Gameplay-Code stehen, sonst teurer Rewrite. | Entscheidung Q-013 spätestens Sprint 3; Simulation von Anfang an determinismusfähig strukturieren; Research Sprint 1 | entschärft (D-033: determinismus-fähige Command-Simulation verbindlich; MP = Transport-Thema, kein Rewrite) |
| R-03 | Pathfinding skaliert nicht | niedrig | hoch | 100–500+ Einheiten, Formationen, dynamische Hindernisse (zerstörbare Umgebung!) überfordern naive Lösungen; größtes Risiko laut TPD Phase 0. | Research Sprint 1 (Q-014); Performance-Spike in TPD Phase 0 mit echten Zahlen; Budgets in Sprint 3 | reduziert (D-034 entschieden: Flow-Field-Hybrid; Restrisiko nur noch Phase-0-Budget-Messung) |
| R-04 | Visuelle Inkohärenz gekaufter Assets | mittel | mittel | Asset-Store-Mix aus vielen Quellen sieht selten wie ein Spiel aus; widerspricht "Stylized Military Sci-Fi"-Anspruch. | Art-Direction-Dokument in Sprint 2; Stil-Kompatibilität als Kaufkriterium (TPD §7.3); Signature-Assets als Stil-Anker; Audit Sprint 5 | aktiv |
| R-05 | Zerstörbare Umgebung als versteckter Kostentreiber | niedrig | hoch | "Vollständig zerstörbare Sci-Fi-Umgebung" (Vision) multipliziert Aufwand für Pathfinding (dynamische Hindernisse), Netcode (Zustand), VFX und Level-Design. | Feature in Sprint 2 auf realistischen Umfang spezifizieren (was genau ist zerstörbar?); nicht implizit mitplanen | entschärft (D-012: gezielte Zerstörbarkeit, keine Terrain-Deformation; Vision.md präzisiert) |
| R-06 | Living-Docs-Disziplin bricht ein | mittel | mittel | Dokumentation veraltet, sobald Entscheidungen nicht zurückfließen – genau das, was das Studio vermeiden will. | Pflichtabschnitte + Änderungsverlauf erzwingen (D-005); Sprint-Ritual prüft Dokusynchronität; DecisionLog als Single Source of Truth | aktiv |
| R-07 | Lizenz-/Kostenfallen im Asset Store | mittel | mittel | Kommerzielle Nutzung, Seat-Lizenzen, URP-Kompatibilität können Budget und Veröffentlichung gefährden. | Lizenzregister (Licenses.md) in Sprint 5; Kaufprüf-Checkliste TPD §7.3 verbindlich | aktiv |
| R-08 | WebGL-Randbedingung verbaut Architektur | niedrig | mittel | "WebGL nicht ausschließen" kann zu vorschnellen Einschränkungen führen (Threading, Dateisystem, Speicher). | WebGL ist explizit keine Leitplattform (TPD §5.4); Architekturentscheidungen dokumentieren, wo sie WebGL betreffen; Bewertung erst nach Desktop-Vertical-Slice | aktiv |
| R-09 | Bestätigungsfehler durch Quellenlage | mittel | mittel | Alle Quelldokumente stammen aus einer Hand; kein externer Realitätscheck (Markt, Machbarkeit) erfolgt bisher. | Sprint 1: unabhängige Research-Agenten inkl. Wettbewerbsanalyse; Sprint 4: Review-Agenten mit ausdrücklichem Widerspruchs-Mandat | teilentschärft (Sprint 1 hat externe Markt-/Technikdaten geliefert) |
| R-10 | Geschäftsmodell-Fehlgriff (Server-MP als Fundament) | mittel | hoch | Stormgate (~$40 Mio. Funding) hat im April 2026 den Online-MP abgeschaltet; F2P-/MP-getriebene RTS scheitern wiederholt. Project Nova darf sein Fundament nicht auf Server-MP bauen. | Premium, Singleplayer/Skirmish-first (Markt-Research, Vorlage Q-016); MP als Feature nach stabilem SP-Kern, nicht als Geschäftsmodell | aktiv |
| R-11 | Unity-Reputations-/Plattformrisiko | niedrig | mittel | Runtime-Fee-Debakel 2023/24 hat Vertrauen beschädigt; Engine-Abhängigkeit bleibt ein strategisches Risiko auch nach Streichung der Fee. | Simulationskern Unity-unabhängig halten (Architekturregel aus Research); keine proprietären Unity-Services im Kern; LTS-Pinning | aktiv |
| R-12 | Burst/Managed-Paritätsbruch | niedrig | mittel | D-037 führt zwei Implementierungen der Sim-Hotspots (Managed-Referenz + Burst); weichen sie ab, laufen SimRunner/CI und Live-Build auseinander (stille Desync-Quelle). | Pflicht-Hash-Paritätstests in CI (D-037); Burst nur für benannte Hotspots; Re-Eval nach Phase-0-Messung – Managed reicht ggf., Burst entfällt | aktiv (mitigiert) |

## Offene Punkte

- Keine Risiken aktuell eskaliert. R-02 entschärft (D-033), R-03 reduziert auf die Phase-0-Messung (D-034), R-12 neu und mitigiert.
- Beobachtungspunkt (kein eigenes Risiko): Kristallsturm-Aetherium-Kopplung (D-027.1) – Balancing-Beobachtungspflicht im Balancing-Pass v0.2.
- Verbleibende Hauptlast auf R-01 (Umsetzungs-Disziplin) und R-10 (Geschäftsmodell-Disziplin SP-first).

## Nächste Schritte

- Update am Ende von Sprint 4 (Review-Findings können neue Risiken erzeugen oder bestehende entschärfen).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Initiales Risikoregister R-01 bis R-09 (Sprint 0) | Executive Producer |
| 1.1.0 | 2026-07-21 | R-10, R-11 neu; R-09 teilentschärft; Fortschritt R-02/R-03 (Sprint 1) | Executive Producer |
| 1.2.0 | 2026-07-21 | R-01 gesenkt (mittel/hoch), R-05 entschärft (Sprint-2-Scope-Entscheidungen D-007–D-032) | Executive Producer |
| 1.3.0 | 2026-07-21 | R-02 entschärft (D-033), R-03 reduziert (D-034), R-12 neu (Burst/Managed-Parität, D-037) – Sprint 3 | Executive Producer |
