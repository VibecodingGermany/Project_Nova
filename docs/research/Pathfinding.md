# Pathfinding für große RTS-Einheitenzahlen (Q-014)

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead AI Programmer | **Sprint:** 1

## Zweck

Dieses Dokument beantwortet die Open Question **Q-014** (Pathfinding: Grid, Flow-Field, NavMesh-Hybrid oder anderes bei 100–500+ Einheiten mit Formationen und dynamischen Hindernissen?) und liefert die Entscheidungsvorlage für den DecisionLog. Es vergleicht die vier im TPD §8.3 genannten Kandidaten plus hybride Varianten, bewertet konkrete Unity-Umsetzungsoptionen und analysiert, wie Referenztitel (StarCraft II, Age of Empires, Planetary Annihilation / Supreme Commander 2) das Problem öffentlich dokumentiert gelöst haben. Verbindlich für Lead AI Programmer, Technical Director und System Architecture; dient als Eingabe für Sprint 3 (Entscheidung).

## Abhängigkeiten

- [../analysis/KnowledgeBase.md](../analysis/KnowledgeBase.md) – verbindlicher Stack (Unity + URP, C#, Windows/macOS, Apple-Silicon-Entwicklung), Qualitätsziele (60 FPS, mehrere hundert Einheiten, wenig GC), Architektur-Leitplanken (datengetrieben via ScriptableObjects, getrennte Simulation/Präsentation)
- [../production/OpenQuestions.md](../production/OpenQuestions.md) – Q-013 (Simulations-/MP-Modell, beeinflusst Determinismus-Anforderung), Q-014 (dieses Dokument), Q-015 (ECS/DOTS vs. OOP, beeinflusst Implementierungsplattform)
- [../production/DecisionLog.md](../production/DecisionLog.md) – Aufnahmeziel der Empfehlung
- TPD §8.3 (Anforderungen Pathfinding), §13 Phase 0 (technischer Spike mit 100–500 Einheiten), §14 (MVP-Abgrenzung)

## 1. Anforderungen aus dem Projektkontext

Konkretisiert aus TPD §8.3 und KnowledgeBase:

- **Skala:** 100–500+ Einheiten gleichzeitig in Bewegung bei 60 FPS Desktop (Frame-Budget 16,6 ms; für Bewegung + Pathfinding + lokale Ausweichlogik ist üblicherweise nur ein Bruchteil verfügbar – als Arbeitsannahme (Einschätzung, zu messen im Spike): ≤ 2–4 ms CPU auf einem Kernevent-Thread-Kontext, Rest via Jobs/Threads).
- **Formationen & Gruppenbefehle:** Bewegungsbefehle gehen typischerweise an 10–100 Einheiten gleichzeitig auf dasselbe Ziel – der dominierende Fall, nicht Einzelpfade.
- **Unterschiedliche Einheitenradien:** Infanterie bis Großpanzer (Legion-Masse, teure Allianz-Einheiten); Engstellen müssen radiusabhängig begehbar sein.
- **Dynamische Hindernisse:** zerstörbare Umgebung und Gebäude (GDD-O: "vollständig zerstörbar"), Spieler-Bauten als Platzierungs-Hindernisse, Aetherium-Kristallfelder, die die Karte verändern (wachsende Kristalle können Gelände blockieren/umformen).
- **Stauvermeidung in Engstellen:** Chokepoints sind kartendesignbedingt; Verhalten in Engstellen ist erfahrungsgemäß der härteste Test (A* Pathfinding Project-Autor zur eigenen ORCA-Demo mit ~220 Einheiten: "worst case for it performance wise is large groups" [Forum](https://forum.arongranberg.com/t/performance-vs-unity-built-in-navmesh-for-large-number-of-agents/4724)).
- **Lufteinheiten:** Allianz hat eine Luftwaffe (KnowledgeBase §3) – brauchen kein Boden-Pathfinding, aber eigene Bewegungsschicht.
- **MP-Vorbehalt (Q-013):** Falls deterministisches Lockstep gewählt wird, muss die Simulation deterministisch sein; NavMesh/Floating-Point-Lösungen sind das i. d. R. nicht plattformübergreifend (Einschätzung, siehe §4.6).
- **MVP-Disziplin:** Phase 1 braucht 1 Fraktion, 1 Karte, "einfaches Pathfinding" (TPD §16/§13) – die Lösung muss inkrementell wachsen können, ohne in Phase 0 überbaut zu werden.

## 2. Lösungsansätze

### 2.1 A* auf Uniform Grid

Klassisch: Karte als Raster, A* pro Einheit (oder pro Gruppe), glätten via String-Pulling/Funnel. Wird u. a. von Age of Empires verwendet (Grid-basiert, siehe §6). Gut verstanden, leicht debuggbar, dynamische Hindernisse = Zellkosten aktualisieren.

**Projektbezogene Vorteile:**
- Passt natürlich zur Aetherium-Mechanik: Kristallwachstum und zerstörte Gebäude ändern nur Zellen (begehbar/Kosten), kein Re-Bake nötig.
- Ganzzahlige Zellkoordinaten vereinfachen spätere deterministische Simulation (Q-013) deutlich stärker als ein Floating-Point-NavMesh.
- Das Grid kann als Datenquelle doppelt genutzt werden: Fog of War, Influence Maps, Kristallfelder, Bau-Platzierung – alles dieselbe Zellstruktur (datengetriebene Leitplanke).

**Projektbezogene Nachteile:**
- 500 Einheiten × eigene A*-Suche auf einer großen Karte sprengt das Budget, wenn Befehle gebündelt kommen (ein Rechtsklick auf 100 selektierte Einheiten = 100 Suchanfragen in einem Frame) – ohne Batching/Caching/Spreading über Frames nicht machbar.
- Grid-Pfade ohne Glättung sehen "zackig" aus; mit Glättung entstehen Radius-Probleme an Engstellen (Einheit schneidet Ecken).
- Löst Gruppenverhalten nicht: A* liefert pro Einheit denselben Korridor → Schlange bilden, Stau (das bekannte AoE-/SC1-Problem, dokumentiert z. B. in [ijcsns.org, A*-based Pathfinding in Modern Computer Games](http://paper.ijcsns.org/07_book/201101/20110119.pdf)).

### 2.2 Flow Fields / Dijkstra-Maps

Vom Ziel aus wird per Dijkstra/BFS ein Kostenfeld über das ganze Grid gefüllt; jede Zelle speichert einen Richtungsvektor zum Ziel. Einheiten lesen nur ihren Vektor – keine individuelle Suche. Referenzimplementierung für Spiele: Elijah Emerson, "Crowd Pathfinding and Steering Using Flow Field Tiles" (Game AI Pro, [PDF](https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter23_Crowd_Pathfinding_and_Steering_Using_Flow_Field_Tiles.pdf)); Tutorials z. B. [leifnode.com](https://leifnode.com/2013/12/flow-field-pathfinding/). Verwendet in Supreme Commander 2 und Planetary Annihilation (siehe §6).

**Projektbezogene Vorteile:**
- Exakt auf unseren Dominanzfall zugeschnitten: Ein Ziel-Feld amortisiert sich über 10–100 Einheiten; die Kosten steigen mit der Zahl *aktiver Ziele*, nicht mit der Einheitenzahl. Skaliert von 100 auf 500+ Einheiten fast kostenlos.
- Integration mit lokaler Vermeidung (Boids/ORCA) ist der dokumentierte Industriestandard für RTS (SC2, SupCom 2: "Flow Fields + Flocking", [sandruski.github.io/rts-group-movement](https://sandruski.github.io/rts-group-movement/)).
- Gleiches Grid wie 2.1: Aetherium-Zerstörung/Wachstum = Feld-Neuberechnung des betroffenen Ausschnitts, determinismusfreundlich.
- Burst/Jobs-freundlich: Feld-Fill ist ein paralleler, allocation-freier Wellenfront-Algorithmus – deckt sich mit Q-015 (DOTS-Hybrid-Option) und dem Qualitätsziel "wenig GC-Spitzen".

**Projektbezogene Nachteile:**
- Pro *unterschiedlichem* Ziel ein volles Feld; viele gleichzeitige Einzelziele (z. B. KI-Mikro, verstreute Sammler) sind teurer als A* pro Einheit. Mitigation: Felder cachen/wiederverwenden, Ziele clustern, frühes Abbruchkriterium.
- Speicherbedarf: Kostenfeld (float/int16 pro Zelle) + Vektorfeld pro aktivem Ziel – bei z. B. 512×512 Zellen und ~20 aktiven Feldern Größenordnung wenige MB, auf Desktop unkritisch (Einschätzung).
- Kein fertiges, gepflegtes Unity-Asset in Reife des A* Pathfinding Project → Eigenbau-Aufwand (allerdings gut dokumentiert und algorithmisch einfach).
- Reine Flow Fields lösen Radius-Unterschiede nur über mehrere Felder bzw. Clearance-Werte (vorberechneter "maximaler Radius pro Zelle", bewährte Technik).

### 2.3 Unity NavMesh (AI Navigation / NavMeshAgent)

Unitys eingebautes System: statisch/runtime gebacktes NavMesh (Recast/Detour-Port), `NavMeshAgent` mit integrierter lokaler Vermeidung, Runtime-Bake via `NavMeshSurface` aus dem Paket `com.unity.ai.navigation` ([Unity Manual – Navigation](https://docs.unity3d.com/Manual/Navigation.html), [AI Navigation Docs](https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/index.html)).

**Projektbezogene Vorteile:**
- Null Eigenbau für den Einstieg; kommt mit Unity, gut für einen Phase-0-Kameraspike ohne Pathfinding-Forschung.
- Qualitativ gute Einzelpfade (beliebige Geometrie, keine Grid-Artefakte).

**Projektbezogene Nachteile (schwerwiegend):**
- Skaliert schlecht mit Agentenzahl: In der Praxis berichten Unity-Projekte Performance-/Verhaltensprobleme ab ~200–800 `NavMeshAgent`s ([Unity Discussions: "Too many NavMeshAgents"](https://discussions.unity.com/t/too-many-navmeshagents-too-complex-navmesh-causing-movement-delay/920275), [GameDev SE: "large number of Navmesh Agents"](https://gamedev.stackexchange.com/questions/205162/how-to-deal-with-large-number-of-navmesh-agents)) – genau unser Zielkorridor 100–500+.
- Dynamische Hindernisse: Runtime-NavMesh-Bakes auf großem Terrain sind langsam und verursachen Frame-Spitzen ([Unity Discussions: "navmeshsurface build time too slow on large terrain"](https://discussions.unity.com/t/navmeshsurface-build-time-too-slow-on-large-terrain/935594)); unabhängige RTS-Prototypen berichten dasselbe ([jdxdev.com](https://www.jdxdev.com/blog/2020/05/03/flowfields/)). Kollidiert direkt mit "vollständig zerstörbarer Umgebung".
- Unterschiedliche Agentenradien erfordern separate NavMesh-Bakes pro Agententyp (Bake-Parameter "Agent Radius") – bei 3 Fraktionen mit mehreren Größenklassen multipliziert sich Speicher und Bake-Zeit.
- Blackbox: kein Source-Zugriff auf die interne Agenten-/Vermeidungslogik, eingeschränkte Steuerung (z. B. kein Gruppen-Formation-Bewusstsein), und für deterministisches Lockstep (Q-013) ungeeignet (Einschätzung).
- TPD §8.3 nennt es selbst: "Ein klassisches NavMesh allein reicht für ein großes RTS möglicherweise nicht aus."

### 2.4 Hybride Ansätze

**Variante A – HPA\* (Hierarchical Path-Finding A\*):** Grid wird in Regionen abstrahiert; Suche läuft auf Abstraktionsebene, Verfeinerung lokal (Botea, Müller, Schaeffer 2004, [Paper (University of Alberta)](https://webdocs.cs.ualberta.ca/~jonathan/publications/ai_publications/jogd.pdf)). Senkt Kosten einzelner Fernwege deutlich, aber: Der Mehrwert liegt bei *vielen unterschiedlichen* Start/Ziel-Paaren – unser Dominanzfall (viele Einheiten, ein Ziel) wird vom Flow Field bereits besser abgedeckt. Hohe Implementierungskomplexität (Cluster-Rebuild bei dynamischen Hindernissen) für marginalen Zusatznutzen in diesem Projekt.

**Variante B – Flow Field (global) + lokale Kollisionsvermeidung (Boids/ORCA):** Flow Field liefert die Makro-Richtung, ein lokaler Vermeidungsalgorithmus (Boids à la Reynolds oder ORCA – van den Berg et al., [RVO2/ORCA, UNC GAMMA](https://gamma.cs.unc.edu/RVO2/)) löst Mikro-Ausweichen, Stau und Überlagerung. Genau die SC2-/SupCom-2-Architektur ([sandruski.github.io](https://sandruski.github.io/rts-group-movement/)). Formationen werden als Ziel-Slots relativ zum Gruppenzentrum modelliert; das Flow Field bleibt identisch, nur die Zielzelle pro Einheit variiert leicht.

**Variante C – Kauf-Asset als Basis (A\* Pathfinding Project, Aron Granberg):** Grid Graphs + Burst/Jobs (5.0: Grid-Scans ~3× schneller, Recast ~3,5×, Local Avoidance ~10× via ORCA/Burst, "Crowded Destination Detection", ECS-basiertes `FollowerEntity`; $140/Sitz, Unity 2021.3+/empfohlen 2022.3+; [5.0-Release-Notes](https://arongranberg.com/2024/02/a-pathfinding-project-5-0/), [Asset Store](https://assetstore.unity.com/packages/tools/behavior-ai/a-pathfinding-project-pro-87744)). Liefert Grid-A*, Graph-Updates für dynamische Hindernisse und produktionsreifes ORCA aus einer Hand – aber kein natives Flow Field für den Massen-Gleichziel-Fall (Dijkstra-Ausbreitung wäre über die API nachbaubar), und Floating-Point-Pfade sind für Lockstep-Determinismus kritisch (Einschätzung).

## 3. Vergleichstabelle

| Kriterium | A* Grid (2.1) | Flow Field (2.2) | Unity NavMesh (2.3) | Hybrid: FF + ORCA (2.4B) | A\* PP als Basis (2.4C) |
|---|---|---|---|---|---|
| 500 Einheiten, 1 Ziel | schlecht (500 Suchen) | **sehr gut** (1 Feld) | mittel (Agent-Overhead) | **sehr gut** | gut (MultiTargetPath) |
| 500 Einheiten, viele Ziele | mittel (Batching nötig) | schlecht–mittel | mittel | mittel | gut |
| Dynamische Hindernisse | gut (Zell-Update) | gut (Feld-Teilupdate) | **schlecht** (Re-Bake) | gut | gut (Graph-Update) |
| Einheitenradien | mittel (Clearance) | mittel (Clearance) | schlecht (Bake pro Radius) | mittel–gut | gut (mehrere Graphs/Cuts) |
| Stauvermeidung Engstellen | schlecht (allein) | mittel (allein) | mittel (Agent-Avoidance) | **gut** (ORCA) | **gut** (ORCA inkl.) |
| Determinismus (Q-013) | gut (int-Grid) | gut (int-Grid) | schlecht | gut | schlecht–mittel |
| Implementierungsaufwand | mittel | mittel | sehr niedrig | mittel–hoch | niedrig |
| Referenz-RTS mit dieser Lösung | AoE | PA / SupCom 2 | (kein großes RTS bekannt) | SC2 | diverse Indie-RTS |
| MVP-Tauglichkeit | gut | gut | sehr gut | zu viel für Phase 0 | sehr gut |

## 4. Querschnittsthemen

### 4.1 CPU-Budget pro Frame
Arbeitsannahme (Einschätzung, im Spike zu verifizieren): Pathfinding + Bewegung ≤ 2–4 ms bei 60 FPS. Implikationen: (1) Feld-Fills und Suchen in Burst-Jobs auslagern, über Frames amortisieren (Time-Slicing); (2) Befehle batchen – ein Rechtsklick = ein Flow Field, nicht N Suchen; (3) ORCA-Nachbarsuche über Spatial Hashing statt O(n²); (4) Pfad-/Feld-Anfragen asynchron, Einheiten laufen 1–2 Frames auf altem Feld weiter (visuell irrelevant).

### 4.2 Unterschiedliche Einheitenradien
Pragmatisch: 2–3 Größenklassen (Infanterie/Fahrzeug/Schwer) statt beliebiger Radien. Pro Klasse ein Clearance-Layer im Grid (max. passierbarer Radius pro Zelle) oder ein eigenes Kostenfeld-Layer. Das ist billiger als pro-Radius-NavMeshes (NavMesh-Lösung) und reicht für die 3-Fraktionen-Unit-Palette (Einschätzung).

### 4.3 Dynamische Hindernisse (zerstörte Gebäude, Kristallwachstum)
Ereignisgetriebenes Dirty-Flagging von Grid-Zellen; betroffene aktive Flow Fields werden lokal neu gefüllt (begrenzter Dijkstra-Restart ab Dirty-Region). Kein Voll-Scan nötig. Gebäude tragen während des Baus eine Kostenstrafe statt "unpassierbar" (Bauarbeiter können durch, siehe SC2-Verhalten) – Einschätzung/Designvorschlag.

### 4.4 Stauvermeidung in Engstellen
Reine Felder oder reine A* lösen das nicht – dafür ist die lokale Schicht da: ORCA bewährt, "Crowded Destination Detection" (A\* PP 5.0) bzw. selbstgebaute Dichtefelder (Zellkosten steigen mit lokaler Einheitendichte → Umlenkung späterer Einheiten). SC2 nutzt zusätzlich kooperatives "Wegschieben" idle stehender Einheiten ([GameDev SE zu SC2](https://gamedev.stackexchange.com/questions/104021/pathfinding-and-collision-avoidance-on-mobile)). Designregel: Karten-Chokepoints breiter als 3× größter Einheitenradius gestalten (an Level Design weiterzugeben).

### 4.5 Lufteinheiten
Eigene Bewegungsschicht: kein Terrain-Pathfinding, nur Höhensteuerung + No-Fly-Zonen (Flak-Reichweiten, Sperrgebiete als Kostenfeld) + einfache Separation (Boids). Auf keinen Fall über das Boden-NavMesh/-Grid zwingen.

### 4.6 Multiplayer-Vorbehalt (Q-013)
Falls deterministisches Lockstep (Szenario A in Q-013): Integer-/Fixed-Point-Grid + eigene ORCA-/Boids-Implementierung in Fixed-Point ist machbar; NavMesh-Detour und Fremd-Assets mit float-Pfaden praktisch nicht plattformübergreifend deterministisch (Einschätzung). Falls Server-autoritativer State-Sync: Determinismus egal, dann ist auch ein Kauf-Asset unkritisch. **Folge: Die Pathfinding-Datenstruktur sollte grid-basiert bleiben, um Q-013 beide Optionen offenzuhalten.**

## 5. Referenzen: Wie lösen es die großen RTS?

- **StarCraft II:** Constrained Delaunay Triangulation → NavMesh; A* mit Funnel-Filter unter Berücksichtigung der Einheitenradien; darüber lokale Steering-/Kollisionsvermeidungsschichten inkl. kooperativem Wegdrängen stehender Einheiten ([GameDev SE, SC2-Zitat](https://gamedev.stackexchange.com/questions/104021/pathfinding-and-collision-avoidance-on-mobile)). Weiterführend beschrieben als Flow-Field-/Flocking-Kombination für Gruppen ([sandruski.github.io](https://sandruski.github.io/rts-group-movement/)). → *Hybrid: globale Struktur + lokale Vermeidung + Gruppenlogik.*
- **Age of Empires (II / Genie Engine):** Grid-basiertes A* mit Gruppen-/Formationslogik; die dauerhaft gepflegten Pathfinding-Fixes in den DE-Patchnotes (z. B. Formation-/Rückzugsverhalten, Durch-Wände-Glitches, [Update 125283](https://ageofempires.fandom.com/wiki/Update_125283)) zeigen eindrücklich, dass Grid+A*+Formationen funktioniert, aber jahrzehntelang Pflege in Gruppenverhalten und Engstellen braucht. → *Warnung vor Unterschätzung der Gruppenschicht, nicht des Grundalgorithmus.*
- **Planetary Annihilation / Supreme Commander 2:** Flow Fields als Kern, bewegt tausende Einheiten; öffentlich dokumentiert über Emersons Game-AI-Pro-Kapitel und zahlreiche Nachbau-Berichte ([Game AI Pro PDF](https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter23_Crowd_Pathfinding_and_Steering_Using_Flow_Field_Tiles.pdf), [howtorts.github.io](http://howtorts.github.io/2013/12/16/first-post.html), [dragonpirategames.com](https://dragonpirategames.com/blog/flowfieldpathfinding)). → *Flow Fields sind die belegte Lösung für das Mengenproblem.*

## Empfehlung

**Entscheidungsvorschlag für den DecisionLog (Sprint 3):**

> Project Nova verwendet als Pathfinding-Architektur einen **hybriden Ansatz: uniformes Grid mit Flow Fields (Dijkstra-Maps) für die globale Wegfindung von Einheitengruppen, ergänzt um eine lokale Kollisionsvermeidungsschicht (ORCA/Boids), implementiert als Eigenbau mit Unity Jobs + Burst auf Integer-/Fixed-Point-Basis.** Für Phase 0/MVP genügt die abgespeckte Stufe: Grid + Gruppen-Flow-Field + einfache Boids-Separation; ORCA, Clearance-Layer für 2–3 Radienklassen und Dichtefelder folgen in Phase 2. Lufteinheiten erhalten eine separate einfache Steering-Schicht.
>
> **Geprüfte Alternativen und Verwerfungsgründe:**
> 1. *A* auf Uniform Grid (allein)* – verworfen: skaliert nicht mit Einheitenzahl beim RTS-Dominanzfall "viele Einheiten, ein Ziel" und löst weder Formationen noch Stau; AoE-Erfahrung zeigt den dauerhaften Wartungsaufwand der Gruppenschicht.
> 2. *Unity NavMesh / NavMeshAgent* – verworfen als Kernlösung: dokumentierte Performance-Probleme ab ~200–800 Agenten, teure Runtime-Re-Bakes bei zerstörbarer Umgebung, ein Bake pro Agentenradius, Blackbox ohne Lockstep-Determinismus. Bleibt zulässig als Wegwerf-Prototyp in Phase 0, falls der Spike früh blockiert.
> 3. *HPA\** – verworfen: adressiert Fernweg-Kosten einzelner Agenten, nicht unser Dominanzproblem; Cluster-Rebuild bei dynamischen Hindernissen treibt Komplexität ohne proportionalen Nutzen.
> 4. *A\* Pathfinding Project (Granberg) als Komplettlösung* – verworfen als Kern, **aber als Risiko-Fallback festgehalten**: liefert Grid-A*, Graph-Updates und produktionsreifes ORCA für $140/Sitz, jedoch kein natives Flow Field und float-basiert (Determinismus-Risiko für Q-013). Wird evaluiert, falls der Eigenbau im Phase-0-Spike das Budget sprengt.

**Begründung in einem Satz:** Nur die Flow-Field-+-lokale-Vermeidung-Kombination ist sowohl für 100–500+ Einheiten bei gemeinsamen Zielen belegt (SupCom 2, PA, SC2) als auch kompatibel mit zerstörbarer Umgebung, Aetherium-Kartenmutation, dem Grid als gemeinsamer Datenquelle (FoW, Bau, Influence Maps) und einer späteren deterministischen Lockstep-Simulation.

## Offene Punkte

- Exakte Zahlen (Feld-Fill-Zeit bei 512×512, ORCA-Kosten bei 500 Agenten auf Apple Silicon und Referenz-Windows-PC) fehlen → Messungen im Phase-0-Spike nötig; Ergebnisse fließen in dieses Dokument und ggf. in Revidierung der Empfehlung ein.
- Anzahl der Radienklassen und Zellgröße des Grids hängt von finalen Einheitenmaßen ab (Blocker: GDD-Detailgrade, Q-004 Drohnen).
- Interaktion mit Q-015: Falls volles DOTS gewählt wird, ändert sich die Implementierungsplattform, nicht die Algorithmenwahl.
- Interaktion mit Q-013: Bei State-Sync statt Lockstep wird das Determinismus-Argument schwächer; der A\*-PP-Fallback rückt näher.
- Formationstiefe (starre Slots vs. lockeres Flocking) ist teilweise Game-Design-Frage → Abstimmung mit Game Design in Sprint 2.

## Nächste Schritte

1. **Sprint 1 (parallel):** Research Q-013/Q-015 abwarten; Schnittstellen dieses Dokuments dorthin bestätigen (Determinismus, DOTS).
2. **Sprint 2:** Design-Abstimmung Radienklassen, Chokepoint-Mindestbreiten, Lufteinheiten-Sonderregeln; Grid-Zellgröße festlegen.
3. **Sprint 3:** Entscheidung D-xxx im DecisionLog auf Basis dieser Empfehlung treffen.
4. **Phase 0 (technischer Spike):** Minimal-Implementierung Grid + Flow Field + Boids-Separation auf Testkarte mit 500 Agenten; Messung: Feld-Fill ms, ORCA/Separation ms, Gesamt-Frame-Budget auf M-Serie-Mac und Windows-Referenz. Erfolgskriterium: 60 FPS mit ≤ 4 ms Simulationsanteil; bei Scheitern → A\* Pathfinding Project evaluieren (Fallback-Plan oben).
5. Erkenntnisse des Spikes als Version 0.2.0 dieses Dokuments nachpflegen (Living Document).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Research-Erstfassung | Lead AI Programmer |
