# Animation, Audio und UI in einem Unity-RTS

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead UI/UX Designer (mit Input Audio/VFX) | **Sprint:** 1

## Zweck

Dieses Dokument vergleicht für die drei Presentation-Layer-Disziplinen Animation, Audio und UI jeweils mindestens drei Lösungsansätze im Kontext von Project Nova: Unity + URP, Desktop-first (Windows/macOS), 100–500+ gleichzeitige Einheiten bei 60 FPS, drei asymmetrische Fraktionen, Datengetriebenheit via ScriptableObjects, MVP-Disziplin (1 Fraktion, 1 Karte, Kernloop) und langfristig autoritativer Multiplayer. Ziel ist eine entscheidungsreife Vorlage für den DecisionLog, keine Implementierung.

## Abhängigkeiten

- [../analysis/KnowledgeBase.md](../analysis/KnowledgeBase.md)
- [../production/OpenQuestions.md](../production/OpenQuestions.md) (v. a. Q-013 Simulations-/MP-Modell, Q-015 ECS vs. MonoBehaviour – die Presentation-Layer-Entscheidungen setzen Randbedingungen für beide)

## Grundprinzip: Presentation ist von der Simulation entkoppelt

Eine für RTS-Architektur zentrale Vorgabe vorab: Animation, Audio und UI sind **reine Präsentation** und dürfen niemals in die Spielsimulation zurückwirken. Das hat zwei Konsequenzen:

- Der Presentation-Layer muss **nicht deterministisch** sein. Egal wie Q-013 (Lockstep vs. Server-autoritativ) ausgeht: Animations-Timing, Voice-Variationen und UI-Feedback können frei interpolieren und zufallsvariiert werden, solange sie nur aus Simulationszuständen lesen.
- Alle drei Systeme lesen ihre Daten aus ScriptableObject-Definitionen (Einheitentyp → Animations-Set, Sound-Set, UI-Icons), damit die datengetriebene Leitplanke durchgehend gilt.

## 1. Animation

### RTS-spezifische Ausgangslage

- 100–500+ Einheiten, davon ein großer Teil gleichzeitig sichtbar: Der klassische Engpass ist CPU-Skinning und Animator-Auswertung, nicht die GPU.
- **Infanterie ≠ Fahrzeuge:** Fahrzeuge, Mechs und Gebäude brauchen typischerweise kein Skelett-Rig – Transform-basierte Animation (Code/Tween), einfache rotierende Teile (Türme, Räder) und Shader-Effekte reichen. Nur Humanoid-Infanterie (Allianz-Soldaten, ggf. Evolvierte) braucht echtes Skeletal Animation.
- Asset-Store-/Mixamo-Kompatibilität ist ein Budget-Hebel: Humanoid-Rigs über das Mecanim-Retargeting erlauben Wiederverwendung gekaufter/generierter Clips über alle humanoiden Einheiten.

### Optionen im Vergleich

| Kriterium | Mecanim/Animator (nativ) | DOTS/ECS-Animation | Prozedural / Code-first (z. B. Playables API, Animancer) |
|---|---|---|---|
| Produktionsreife (Stand 2025/26) | Voll produktionsreif, dokumentiert, stabil seit Jahren | **Nicht gegeben:** Unitys offizielles DOTS-Animation-Paket wurde ab DOTS 0.50 aufgegeben und nie ersetzt; das angekündigte neue Animationssystem (Ziel: Unity-6-Lifecycle) ist per Anfang 2026 noch nicht released ([Unity Discussions Q1 2025](https://discussions.unity.com/t/animation-status-update-q1-2025-gdc-roadmap/1614718), [Sommer 2025](https://discussions.unity.com/t/animation-status-update-summer-2025/1672386)) | Produktionsreif; Animancer (Kybernetik Games) ist etabliertes kommerzielles Asset mit kostenloser Lite-Variante; Playables API ist Engine-Bestandteil |
| Performance bei 500 Einheiten | Schlecht im Default (pro Animator Overhead), aber mit Disziplin tragfähig: `Animator.cullingMode = Cull Completely`, `Update When Offscreen` aus, GPU Skinning an, Animations-LOD ([Unity Manual: Mecanim Performance](https://docs.unity3d.com/6000.5/Documentation/Manual/MecanimPeformanceandOptimization.html)) | Theoretisch ideal (Burst/Jobs auf Bone-Evaluation), praktisch nur über Drittanbieter oder Eigenbau erreichbar – hohes Projektrisiko | Gut bis sehr gut: Playables-basierte Auswertung ohne State-Machine-Overhead; volle Kontrolle über Update-Raten (z. B. entfernte Einheiten mit 10 Hz statt 60 Hz) |
| Asset-Store-/Mixamo-Kompatibilität | Nativ: Humanoid-Retargeting, Animator Controller als Standardformat aller Assets | Praktisch keine; Clips müssten in ECS-Datenformate überführt werden | Clips sind dieselben `AnimationClip`-Assets (Mixamo/Store funktionieren), nur die Wiedergabelogik ändert sich |
| Passung zu Project Nova | MVP-tauglich sofort; Gefahr: komplexe Animator Controller pro Einheitentyp werden unwartbar | Kollidiert mit MVP-Disziplin und hängt an der unentschiedenen Q-015; kein belastbarer Release-Pfad | Passt zu RTS-Massenlogik (datengetrieben: Clip-Referenzen direkt im Unit-ScriptableObject, keine visuelle State Machine), erfordert aber Animation-Logik in Code |
| Risiko | Skalierungs-Deckel bei vielen *unterschiedlichen* Animator-Controllern; Profiler-Disziplin nötig | Technologie-Roulette: baut auf nicht-existenter bzw. unfertiger Engine-Funktion auf | Abhängigkeit von Drittanbieter (Animancer) oder Eigenwartung (Playables); Team muss Animationsarchitektur selbst denken |

### Animations-LOD (unabhängig von der Option, Pflichtprogramm)

Drei LOD-Stufen, konfigurierbar pro Einheitentyp im ScriptableObject:

1. **Nah (Held-/Zoom-Ebene):** volle Update-Rate, Blending, Übergänge.
2. **Standard (typische RTS-Kamerahöhe):** reduzierte Update-Rate (15–30 Hz reichen bei schräger Top-Down-Kamera visuell aus), keine komplexen Blends.
3. **Fern/Minimap-Zoom:** Animator pausiert oder auf Einzelpose reduziert; `Cull Completely` für abseits des Bildschirms.

Fahrzeuge/Gebäude (Legion-Masse, Allianz-Panzer): kein Rig – Fahrwerk, Türme, Baufortschritt via Code/Shader. Das spart den Großteil der Skinning-Kosten, da Masse-Fraktionen (Legion) pro Einheit am billigsten sein müssen.

### Einschätzung Animation

Für den MVP und darüber hinaus ist ein **Hybrid aus Mecanim-Humanoid-Rigs (Infanterie) und rig-loser Code-Animation (Fahrzeuge/Gebäude)** der risikoärmste Weg. DOTS-Animation ist 2025/26 keine kaufbare Entscheidung – es gibt schlicht kein produktionsreifes offizielles Paket. Ob statt Animator-Controllern direkt auf Playables/Animancer gesetzt wird, ist eine Feinjustage, die mit einem Performance-Prototype (500 dumme Einheiten, Testszene) in Sprint 2/3 empirisch entschieden werden sollte.

## 2. Audio

### RTS-spezifische Ausgangslage

- Viele gleichzeitige 3D-Quellen (hunderte Einheiten mit Schritten, Waffen, Stimmen) → Voice-Management und Priorisierung sind das Kernthema, nicht Effektqualität.
- Adaptive Musik (Ruhe ↔ Gefecht ↔ Niederlage) ist Kernstimmung des Genres.
- Einheitenvoices (Acknowledge-, Selection-, Combat-Barks) sind ein Lesbarkeits-Feature: Der Spieler hört, was seine Armee tut, ohne hinzusehen. Bei 500 Einheiten braucht es aggressive Spam-Begrenzung (Voice-Stealing, Cooldowns pro Gruppe).

### Optionen im Vergleich

| Kriterium | Unity Audio (nativ) | FMOD (Studio + Unity Integration) | Wwise (Audiokinetic) |
|---|---|---|---|
| Lizenzkosten | Inklusive, keine Zusatzkosten | Kostenlose Indie-Lizenz unter $200k Jahresumsatz bzw. unter $600k Entwicklungsbudget ([fmod.com/licensing](https://www.fmod.com/licensing)); darüber kommerzielle Lizenz | Budgetabhängig und **pro Plattform** lizenziert; Einstiegspreise ab ca. $8.000, reduzierter Community-Zugang für Budgets < $250k ([audiokinetic.com/pricing](https://www.audiokinetic.com/en/wwise/pricing/)) |
| Adaptive Musik | Nur selbst gebaut (Crossfade-Skripte, AudioMixer-Snapshots) – machbar, aber Handarbeit | Nativ: Parameter-gesteuerte Musik mit Übergängen, vertikalem/horizontalem Layering | Nativ und am mächtigsten (Interactive Music Hierarchy, State-Switches) – Industriestandard in AAA |
| Voice-Management bei 500 Quellen | Sehr begrenzt: max. Voices konfigurierbar, aber keine Priorisierungs-/Stealing-Logik out of the box; muss selbst gebaut werden | Eingebaut: Prioritäten, Stealing, Max-Instances pro Event, Cooldowns – genau das RTS-Problem gelöst | Eingebaut und am granulärsten (Playback-Priority, HDR-Audio) |
| Audio-Designer-Workflow | Keiner – alles in Unity/C# | Eigenes Autorentool (FMOD Studio), Nicht-Programmierer können Events, Parameter, Mix bauen; Banks entkoppeln Audio-Content vom Code | Eigenes Autorentool, steilere Lernkurve, dafür tiefste Kontrolle |
| Unity-Integration | Nativ | Offizielles Unity-Package, gereift, weit verbreitet ([Integrations-Guide](https://generalistprogrammer.com/tutorials/fmod-unity-complete-game-audio-integration-tutorial)) | Offizielles Unity-Package, ebenfalls gereift, aber schwereres Setup |
| Passung zu Project Nova | Perfekt für MVP (1 Fraktion, wenige Sounds); skaliert aber nicht zur Zielvision ohne fremdes Voice-Management | Trifft alle RTS-Anforderungen (Barks, adaptive Musik, Performance) bei kostenloser Einstiegshürde | Überdimensioniert für Teamgröße/Budget eines Indie-RTS; Lizenz pro Plattform verschärft das bei Windows+macOS |

### Einschätzung Audio

Unity Audio reicht für den MVP faktisch aus – die Sound-Dichte einer 1-Fraktionen-Karte überfordert das native System nicht, und ein selbstgebautes Mini-Voice-Limit (Cooldown pro Einheitengruppe) ist ein Nachmittag Arbeit. Strategisch führt aber kein Weg an Middleware vorbei, sobald drei Fraktionen, adaptive Musik und hunderte Barks kommen. **FMOD** ist die ökonomisch und technisch passende Wahl: kostenlose Indie-Lizenz, RTS-relevantes Voice-Management ab Werk, Audio-Design ohne Programmierer. Wwise bietet mehr, kostet mehr (pro Plattform) und überfordert den Bedarf. Wichtig: Schon im MVP alle Sound-Aufrufe hinter eine dünne `AudioService`-Abstraktion legen (Konfiguration per ScriptableObject), damit der Middleware-Wechsel später kein Refactoring-Blutbad wird.

## 3. UI

### RTS-spezifische Ausgangslage

- Hohe HUD-Dichte: Ressourcenleiste, Produktionsmenüs/Warteschlangen, Einheitenporträts, Kontrollgruppen (1–0), Kontextbefehle, Minimap mit Ping-System.
- Interaktionsmuster: Maus-first (Drag-Select, Rechtsklick-Kontext, Hover-Tooltips), Hotkeys als First-Class-Feature, Grid-Layout für Befehlskarten (SC2-Vorbild).
- Desktop-first (Windows/macOS), spätere Touch-Option → das UI-System muss Event-Abstraktion erlauben, Touch wird aber nicht jetzt optimiert.
- Performance: Statisches HUD ist unkritisch; kritisch sind dynamische Elemente (Warteschlangen, Gruppen-Icons) und Over-Unit-Elemente (Healthbars bei 500 Einheiten – die gehören **nicht** in ein Canvas-System, sondern in gebatchte Shader/Mesh-Overlays).

### Optionen im Vergleich

| Kriterium | UI Toolkit (UXML/USS, Runtime) | uGUI (Canvas/Unity UI) | Hybrid: UI Toolkit (HUD/Menus) + uGUI/World-Space (Spezialfälle) |
|---|---|---|---|
| Status 2025/26 | Von Unity als strategisches UI-System forciert; seit Unity 6 runtime-seitig als produktionsreif beworben; offizieller Vergleich im Manual ([docs.unity3d.com: UI system comparison](https://docs.unity3d.com/6000.0/Documentation/Manual/UI-system-compare.html)) | Ausgereift, stabil, riesiger Wissensschatz, aber in Wartungsmodus – keine strategische Weiterentwicklung ([Unity Discussions](https://discussions.unity.com/t/official-recommendation-unity-ui-vs-ui-toolkit/892342)) | Von Unity selbst als Migrationspfad anerkannt (beide Systeme koexistieren im selben Projekt) |
| HUD-Dichte / Datenbindung | Stärken bei datengetriebenen, listenartigen UIs (Binding, ListView, Virtualisierung) – passt zu Produktionswarteschlangen und Gruppen | Alles per Hand (MonoBehaviour-Referenzen); bei dichten RTS-HUDs viel Glue-Code | Nutzt jeweils die Stärke |
| Minimap | Kein eingebautes Minimap-Konzept – wird in beiden Fällen über RenderTexture + separates Kamera-Setup gelöst; UI Toolkit kann RenderTexture anzeigen | Dasselbe; uGUI `RawImage` + RenderTexture ist der bewährte, massiv dokumentierte Weg | RenderTexture-Lösung gemeinsam, Darstellung egal in welchem System |
| Hotkeys/Maus (Desktop-first) | Event-System vorhanden; Fokus-/Hotkey-Handling in älteren Versionen holprig, in Unity 6 deutlich verbessert (Einschätzung, aus Community-Berichten: [UI Toolkit Status Feb 2025](https://discussions.unity.com/t/ui-toolkit-development-status-and-next-milestones-february-2025/1607740)) | Bewährtes EventSystem + StandaloneInputModule; Hotkeys laufen ohnehin über Game-Code, nicht übers UI-System | Beide Event-Systeme parallel ist wartbar, aber Kleinteiligkeit im Fokus-Management |
| World-Space-UI / Custom Shader | Schwach: kein echtes World-Space-Rendering, Custom-Shader-Unterstützung begrenzt – laut Unity genau die Domäne von uGUI ([offizielle Empfehlung](https://discussions.unity.com/t/official-recommendation-unity-ui-vs-ui-toolkit/892342)) | Stark: World-Space-Canvas, volles Shader-/Material-Recht | Strategische Schwäche von UI Toolkit wird abgedeckt |
| Team-/Asset-Ökosystem | Kleiner, wachsend; weniger RTS-spezifische Tutorials | Enorm: Tutorials, Assets, Erfahrung am Markt; schnellster Weg zum MVP-HUD | – |
| Performance bei vielen Elementen | Retained-Mode mit Batch-Optimierung; dynamische Listen virtualisierbar | Rebuild-/Canvas-Batch-Kosten bei vielen sich ändernden Elementen bekannt; bei statischem HUD + wenigen dynamischen Listen unproblematisch | Beide Overheads summieren sich; bei unserem HUD-Umfang vernachlässigbar |

### Zum Thema Healthbars & Over-Unit-UI (Präzisierung)

Egal welches UI-System: 500 einzelne World-Space-Canvases oder UI-Toolkit-Elemente über Einheiten sind der falsche Weg. Standard-RTS-Lösung: **ein einziges gebatchtes Mesh/Shader-Overlay** (oder instanziierte Quads per `Graphics.DrawMeshInstanced`), das Lebenspunkte/Selektionsrahmen zeichnet und aus der Simulation liest. Das UI-System rendert nur das Screen-Space-HUD. Diese Trennung sollte ins technische Planungsdokument übernommen werden.

### Einschätzung UI

**UI Toolkit als Primärsystem** für HUD, Produktionsmenüs, Kontrollgruppen und Menüs: Es ist Unitys strategische Zukunft, passt mit Datenbindung ideal zur ScriptableObject-Leitplanke, und wir bauen ohnehin neu auf Unity 6 – eine spätere Migration von uGUI wäre teurer als der jetzige Lernkurven-Aufschlag. **uGUI bleibt als Ergänzung** für die Fälle reserviert, in denen Unity selbst UI Toolkit schwach sieht: World-Space-UI und stark shader-basierte Elemente. Reines uGUI als Alleslöser zu wählen hieße, auf ein Wartungsmodus-System zu setzen und die Migration in die Mitte der Produktion zu legen. Für den MVP gilt: erst HUD-Grundgerüst (Ressourcen, Befehlskarte, Minimap via RenderTexture, Gruppen-Hotkeys), kein Schnickschnack.

## Empfehlung

**Vorschlag für den DecisionLog (zur Abstimmung in Sprint 3):**

1. **Animation:** Hybrid – Mecanim/Humanoid-Rigs für Infanterie (Mixamo-/Asset-Store-kompatibel), rig-lose Code-/Transform-Animation für Fahrzeuge und Gebäude, verbindliches 3-stufiges Animations-LOD. Playables API oder Animancer als Code-first-Alternative für die Massen-Infanterie in Sprint 2/3 per Performance-Prototype (500 Einheiten) empirisch gegen Animator-Default prüfen. *Verworfen:* DOTS-/ECS-Animation – kein produktionsreifes offizielles Paket, Release des neuen Unity-Animationssystems offen (Stand Anfang 2026); zu hohes Technologierisiko für die MVP-Phase. *Ebenfalls verworfen:* reines Animator-Controller-Design für alle Einheiten – skaliert bei 500 Einheiten und drei Fraktionen in unwartbare State Machines.
2. **Audio:** MVP mit Unity Audio (nativ) hinter einer `AudioService`-Abstraktion; **FMOD** als fest eingeplante Middleware ab Alpha (adaptive Musik, Voice-Management für hunderte Barks, kostenlose Indie-Lizenz). *Verworfen:* Unity Audio als Endausbau – kein brauchbares Voice-Priorisierungs- und Musik-Layering bei Zielgröße. *Verworfen:* Wwise – leistungsfähiger, aber budget-/plattformabhängig lizenziert und für Teamgröße und Bedarf überdimensioniert.
3. **UI:** **UI Toolkit (Runtime, Unity 6)** als Primärsystem für HUD/Menus mit ScriptableObject-Datenbindung; **uGUI nur ergänzend** für World-Space-/Custom-Shader-Fälle; Over-Unit-Anzeigen (Healthbars, Selektion) als gebatchtes Mesh/Shader-Overlay außerhalb beider UI-Systeme; Minimap via RenderTexture. *Verworfen:* reines uGUI – Wartungsmodus-Technologie, spätere Migration teurer als jetzige Lernkurve. *Verworfen:* reines UI Toolkit ohne Hybrid-Klausel – World-Space-/Shader-Lücken sind von Unity selbst dokumentiert.

Gemeinsamer Grundsatz für den DecisionLog: Der gesamte Presentation-Layer ist von der Simulation entkoppelt und muss nicht deterministisch sein – dadurch bleibt Q-013 (Lockstep vs. Server-autoritativ) durch diese Entscheidungen unberührt, und Q-015 (ECS-Frage) wird entschärft: Selbst bei DOTS-Simulation bleibt die Visualisierung im klassischen GameObject-/Mecanim-Raum.

## Offene Punkte

- **Performance-Prototype Animation:** Animator vs. Playables/Animancer bei 500 Einheiten auf Apple Silicon – kein belastbarer Messwert vorhanden (Sprint 2/3).
- **Animancer-Lizenz:** Kommerzielle Lizenzkosten und Lite-Einschränkungen prüfen, falls der Prototype für Animancer ausfällt (Einschätzung: einstellige bis niedrige zweistellige Dollarbeträge pro Seat – zu verifizieren).
- **FMOD-Budgetschwelle:** Aktuelle Grenzen der Indie-Lizenz ($200k Umsatz / $600k Budget) gegen die Studio-Finanzplanung spiegeln; Überschreitung macht kommerzielle Lizenz fällig.
- **UI-Toolkit-Reife im Detail:** Hotkey-/Fokus-Handling und RenderTexture-Minimap in Unity 6.x hands-on validieren – Community-Berichte sind gemischt; unsere Einschätzung beruht auf Doku und Foren, nicht auf eigenem Test.
- **Stilfrage Healthbars/Selektionsringe:** Stylized-Military-Sci-Fi-Lesbarkeit (Form, Farbcodierung pro Fraktion) braucht eigene Art-Direction-Recherche außerhalb dieses Dokuments.
- **Evolvierte-Animation:** Falls Q-009 mit „organisch wachsende Gebäude" beantwortet wird, entsteht Animationsbedarf (Wachstum über Shader/Blend-Shapes statt Clips), der die rig-lose Strategie bestätigt, aber Shader-Aufwand erhöht.

## Nächste Schritte

- Sprint 2: Entscheidungsvorlage in den DecisionLog überführen (Abstimmung mit Lead Programmer und Executive Producer).
- Sprint 2/3: Performance-Prototype Animation (500 Einheiten, Testszene, macOS-Build) als Entscheidungsgrundlage Animator vs. Playables/Animancer.
- Sprint 2: `AudioService`-Abstraktionsschnittstelle (Interface + ScriptableObject-Schema für Sound-Sets) mit Lead Programmer definieren, damit der MVP von Anfang an FMOD-kompatibel bleibt.
- Sprint 2: UI-Wireframes für MVP-HUD (Ressourcenleiste, Befehlskarte, Minimap, Kontrollgruppen 1–0) auf Basis UI Toolkit erstellen.
- Sprint 3: Übergabe der Randbedingung „Presentation nicht deterministisch" an die Q-013-/Q-015-Entscheidung.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Research-Erstfassung | Lead UI/UX Designer (mit Input Audio/VFX) |
