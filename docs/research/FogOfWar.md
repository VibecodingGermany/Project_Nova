# Fog of War – Technikvergleich für RTS

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Graphics Engineer | **Sprint:** 1

## Zweck

Vergleich und Bewertung von Fog-of-War-Techniken (FoW) für *Project Nova* als Entscheidungsvorlage für Sprint 3 (Technical Design). Abgedeckt werden die drei Sichtzustände (unerforscht / erforscht / aktuell sichtbar), Sichtweite pro Einheit, Radar, Tarnung/Aufdeckung, Team-Sicht, Minimap-Integration, Line-of-Sight vs. Radius, Performance bei 100–500+ Einheiten, URP-Kompatibilität und Netcode-/Maphack-Aspekte. Verbindlich für Graphics-, Tech-Design- und spätere Netcode-Arbeit; kein produktiver Code (Sprint-1-Disziplin).

## Abhängigkeiten

- [../analysis/KnowledgeBase.md](../analysis/KnowledgeBase.md) – Projektkontext: FoW als Kernsystem (§Kernsysteme), URP-Stack, 3D-Welt mit schräger Top-Down-Kamera, 100–500+ Einheiten
- [../production/OpenQuestions.md](../production/OpenQuestions.md) – Schnittstellen zu Q-013 (Simulations-/MP-Modell), Q-015 (ECS/DOTS vs. OOP)
- [../production/DecisionLog.md](../production/DecisionLog.md) – Zielort der aus dieser Vorlage abgeleiteten Entscheidung
- [../meta/DocumentationStandard.md](../meta/DocumentationStandard.md) – Dokumentationsregeln (≥3 geprüfte Alternativen)

## Anforderungen aus dem Projektkontext

- **Desktop-first** (Windows/macOS, Entwicklung auf Apple Silicon → Metal-Kompatibilität aller GPU-Pfade Pflicht).
- **MVP-Disziplin:** FoW gehört laut KnowledgeBase erst zur Phase 2 (Vertical Slice), ist aber Teil des Kernsystems-Katalogs; die MVP-Architektur darf FoW nicht ausgeschlossen machen.
- **Datengetrieben:** Sichtweiten, Radar- und Tarnparameter gehören in ScriptableObjects (Leitplanke), nicht in Code-Konstanten.
- **60 FPS bei 100–500+ Einheiten:** Sichtberechnung muss in ein festes CPU-Budget passen (Ziel-Einschätzung: ≤1 ms pro Sicht-Tick auf Apple Silicon).
- **Spätere MP-Autorität:** Das Sichtmodell muss serverseitig replizierbar sein (Maphack-Resistenz), auch wenn der MP erst nach dem Singleplayer-Kern kommt (Q-013).
- **Stil:** Stylized Military Sci-Fi, Lesbarkeit vor Realismus → weiche, klare FoW-Kanten statt physikalischer Nebel-Simulation.

## Begriffsmodell: drei Sichtzustände

Branchenüblich (u. a. StarCraft II) und für Nova übernommen:

1. **Unerforscht (unexplored):** Zelle wurde nie gesehen → vollständig schwarz, Minimap zeigt nichts.
2. **Erforscht (explored):** Zelle wurde einmal gesehen, ist aber aktuell nicht sichtbar → gedämpfte/graue Darstellung, Terrain und statische Gebäude (zuletzt bekannter Zustand) sichtbar, keine Einheiten, keine Live-Änderungen.
3. **Aktuell sichtbar (visible):** Zelle liegt im Sichtbereich mindestens einer eigenen/verbündeten Quelle → volle Darstellung, Einheiten sichtbar und anwählbar.

Daraus folgt die kanonische Datenstruktur (Referenz: [Gemserk – FoW for RTS in Unity 2/2](https://blog.gemserk.com/2018/11/20/implementing-fog-of-war-for-rts-games-in-unity-2-2/)): ein `values`-Array (aktuell sichtbar, wird pro Tick neu berechnet) und ein `visited`-Array (je einmal gesehen, monoton wachsend), jeweils als **Bitmask pro Spieler/Team**. Team-Sicht ist damit eine O(1)-Bit-Operation (`IsVisible(i, j, teamMask)`), was Novas Allianz-/Coop-Szenarien nativ abdeckt. Sichtweite ist eine Eigenschaft der Sichtquelle (`VisionSource { teamMask, range, position, heightLevel, flags }`), nicht der Zelle.

## Lösungsansätze im Vergleich

### Ansatz A: Textur-/RenderTexture-basiertes FoW (Splat-Rendering)

Sichtkreise aller Quellen werden als weiche Sprites/„Splats" per Kamera oder CommandBuffer in eine RenderTexture (Weltprojektion) gerendert; ein zweiter RT hält den kumulierten „erforscht"-Zustand (Ping-Pong/persistenter `RTHandle`). Ein Fullscreen- oder Terrain-Shader blendet die Welt anhand dieser Textur ab. Referenzen: [Andrew Hung – Attractive FoW in Unity](https://andrewhungblog.wordpress.com/2018/06/23/implementing-fog-of-war-in-unity/), Unity-Diskussionen zu persistentem RT in URP ([RTHandle über Frames wiederverwenden](https://discussions.unity.com/t/urp-scriptable-render-pass-will-temp-render-texture-persist-indefinitely/1530185)).

**Projektbezogene Vorteile:**
- Sehr gute Optik (weiche Kanten, Höhenfading, stilisierte Übergänge) mit wenig Aufwand – passt zu „Stylized, Lesbarkeit vor Realismus".
- GPU-seitig billig: 500 Splats sind 500 günstige Draws in eine kleine Textur; auf Apple Silicon vernachlässigbar.
- Minimap bekommt dieselbe Textur quasi gratis (zweiter Shader, gleiche Daten).

**Projektbezogene Nachteile:**
- **Keine Spiellogik-Daten:** Die GPU-Textur beantwortet keine Gameplay-Fragen („Kann Einheit X Ziel Y sehen/angreifen?"). Ein Readback auf die CPU ist langsam und stallt die Pipeline → es braucht ohnehin ein paralleles CPU-Sichtmodell, dann ist der GPU-Pfad redundant.
- Drei Zustände erfordern sauberes Channel-/Ping-Pong-Management; Fehler zeigen sich als visuelles Flackern (bekanntes URP-Problemfeld, vgl. [Unity Discussions: FoW (URP) on large maps](https://discussions.unity.com/t/fog-of-war-urp-on-large-maps-without-tanking-performance/920374)).
- Für Netcode/Determinismus wertlos: Der Server rendert nichts.

### Ansatz B: Grid-/Bitmask-basiertes FoW (CPU-Simulation + Textur-Ausgabe)

Die Welt wird in ein Sichtraster (z. B. 1 Zelle = 1–2 m) diskretisiert. Pro Sicht-Tick rastern alle `VisionSource`s gefüllte Kreise (Radius-Modell) bzw. Linien mit Höhenvergleich (LoS) in das `values`-Array; `visited` wird mit-aktualisiert. Die GPU bekommt das Ergebnis als kleine Textur (z. B. 256×256 R8/RG8), die im Shader upsampled und geblurrt wird. Das ist das SC2-nahe Standardmodell, ausführlich dokumentiert bei [Gemserk](https://blog.gemserk.com/2018/11/20/implementing-fog-of-war-for-rts-games-in-unity-2-2/) (inkl. `UnitVision`-/`VisionGrid`-Strukturen, Höhen-Blocking, Easing).

**Projektbezogene Vorteile:**
- **Ein Modell für Logik UND Darstellung:** Angriffsprüfung, KI-Sicht, Radar, Tarnung und Rendering lesen dieselben Daten – keine Divergenz.
- Determinismusfähig (Integer/Fixed-Point möglich) und **serverseitig replizierbar** – direkte Antwort auf die MP-Autorität aus Q-013.
- CPU-Kosten sind vorhersagbar und burstbar (siehe Performance-Abschnitt); passt sowohl zu MonoBehaviour-OOP als auch später zu ECS/Jobs (Q-015-neutral).
- Datengetrieben: `VisionSource`-Parameter kommen aus ScriptableObjects; Grid-Auflösung ist ein Projekt-Setting.

**Projektbezogene Nachteile:**
- Raster-Artefakte: kantige Sichtkreise, wenn die Textur unbehandelt bleibt → erfordert Upscaling/Blur/Easing (Gemserk beschreibt genau dieses Problem und seine Lösung).
- Grid-Auflösung ist eine frühe, schwer revidierbare Entscheidung (Speicher vs. Genauigkeit); bei sehr großen Karten (>4 km²) steigt der Speicher linear.
- LoS-Variante (Höhenlinien) multipliziert die Tick-Kosten grob um Faktor 3–5 (Einschätzung, abhängig von Linienlänge).

### Ansatz C: GPU-Compute-Shader-FoW

Alle `VisionSource`s werden als StructuredBuffer an einen ComputeShader gegeben, der die Sicht-Textur direkt auf der GPU aufbaut (ein Thread pro Gridzelle, Test gegen alle Quellen oder gegen ein vorab akkumuliertes Höhenfeld). Community-Praxisbeispiel in URP: [Unity Discussions: Fog Of War & URP](https://discussions.unity.com/t/fog-of-war-urp/878413) (DOTS sammelt Fog-Affectors, ComputeShader schreibt die FoW-Textur).

**Projektbezogene Vorteile:**
- Skaliert am besten bei extremer Quellenzahl: 500 Quellen × 65k Zellen sind für einen ComputeShader trivial (<0,1 ms, Einschätzung auf M-Serie).
- Kein CPU-Aufwand pro Tick; CPU-Buffer-Upload von 500 × ~32 Byte ist billig.
- Höhen-LoS als Parallel-Algorithmus (Raymarching im Höhenfeld pro Zelle) auf der GPU vergleichsweise günstig.

**Projektbezogene Nachteile:**
- **Readback-Problem wie Ansatz A:** Spiellogik (Angriffe, KI, Tarnung) braucht die Sichtbarkeit auf der CPU → asynchroner Readback mit 1–2 Frames Latenz oder paralleles CPU-Modell. Für eine KI, die „sieht" wie der Spieler, ist Frame-Latenz heikel.
- Metal-Spezifika auf macOS (Threadgroup-Größen, Buffer-Limits) erhöhen den Portierungs-/Testaufwand; Debugging auf zwei Plattformen (DX11/12 + Metal) ist teurer als reiner C#-Code.
- Schlechter determinismusfähig (GPU-Float, keine Garantie plattformübergreifend) → riskant für Q-013-Varianten mit Lockstep.
- Overkill für 500 Einheiten: Der Ansatz löst ein Skalierungsproblem, das Nova voraussichtlich nicht hat (B brechnet 500 Quellen in <1 ms auf der CPU, siehe unten).

### Ansatz D (mitgeprüft): Mesh-/Geometrie-basiertes FoW (Visibility-Meshes)

Pro Sichtquelle wird ein Sichtpolygon (2D-Shadowcasting gegen Hindernisse) erzeugt und als Mesh gerendert; FoW ist die invertierte Vereinigungsmenge. Verbreitet in Top-Down-/Stealth-Spielen mit wenigen Agenten.

**Verwerfungsgrund (vorab):** Bei 500 Quellen degeneriert das zu 500 dynamischen Meshes pro Frame (CPU-Aufbau + Drawcalls), die Vereinigungsmenge benötigt Stencil-Tricks oder komplexe Boolean-Geometrie, und es gibt wieder kein Logik-Datenmodell. Für RTS-Einheitenmengen ungeeignet; nur für Einzel-Agenten-Perspektiven sinnvoll. Wird nicht weiter verfolgt.

### Vergleichstabelle

| Kriterium | A: RenderTexture-Splats | B: Grid/Bitmask (CPU) | C: Compute-Shader (GPU) |
|---|---|---|---|
| Spiellogik nutzbar (Angriff/KI/Tarnung) | nein (Readback nötig) | **ja, nativ** | nur mit Readback-Latenz |
| Visuelle Qualität | **sehr gut** | gut (mit Blur/Easing) | sehr gut |
| CPU-Kosten @500 Einheiten | sehr niedrig | niedrig (~0,2–1 ms/Tick, Einschätzung) | ~null |
| GPU-Kosten | niedrig | sehr niedrig | sehr niedrig |
| Determinismus / Server-Replikation | nein | **ja** | eingeschränkt |
| Minimap-Integration | direkt (gleiche Textur) | direkt (gleiche Textur) | direkt (gleiche Textur) |
| Team-Sicht (Allianzen) | pro Team eigener RT nötig | **Bitmaske, O(1)** | pro Team eigener Pass nötig |
| macOS/Metal-Risiko | mittel (RT-Ping-Pong) | **niedrig** | mittel-hoch |
| Komplexität/Busfaktor | mittel | niedrig-mittel | hoch |
| MVP-Tauglichkeit | ja (aber Logik fehlt) | **ja** | overengineered |

## Line-of-Sight vs. Radius-Modell

- **Radius-Modell (rein):** Sicht = Kreis, keine Hindernisse. Billigste Variante, komplett ausreichend für MVP. Referenz-Praxis: Age-of-Empires-Reihe arbeitet weitgehend radiusbasiert mit Höhenbonus statt echtem LoS (Einschätzung auf Basis des öffentlich dokumentierten Verhaltens, keine Primärquelle verifiziert).
- **Höhen-LoS (SC2-artig):** Klippen/Hochgelände blockieren Sicht; Umsetzung als Linien-Rasterung (Bresenham) zum Kreisrand mit Höhenvergleich im Grid – genau so bei [Gemserk](https://blog.gemserk.com/2018/11/20/implementing-fog-of-war-for-rts-games-in-unity-2-2/) beschrieben. Erzeugt starkes taktisches Verhalten (High-Ground-Advantage), kostet Faktor 3–5 pro Tick.
- **Volles 3D-LoS (Raycasts gegen Geometrie):** Physik-Raycasts pro Einheit/Ziel skalieren bei 500 Einheiten nicht in ein 1-ms-Budget und liefern unruhige Ergebnisse; verworfen. Raycasts bleiben für Einzelfragen (z. B. „sieht Scharfschütze Ziel X") legitim.

**Einordnung für Nova:** Nova hat Aetherium-Felder, die „die Umwelt verändern" – das spricht für ein Grid-Modell mit Höhenleveln, in das solche Veränderungen (z. B. blockierende Kristallformationen) als Höhen-/Blocker-Update einfließen können. Empfehlung: **MVP = Radius; Höhen-LoS als datengetriebene Option im selben Grid ab Phase 2** (der Umstieg ist dann ein Algorithmus-Tausch im Raster-Schritt, kein Architekturbruch).

## Querschnittsthemen

- **Sichtweite pro Einheit:** `VisionProfile` als ScriptableObject (Reichweite, Höhenlevel, Update-Priorität, Flags: `revealsStealth`, `seesOverCliffs`, `isRadar`). Fraktionsasymmetrie wird damit Konfiguration: Allianz = hohe Reichweite/teure Aufklärung, Legion = kurze Sicht/viele Augen, Evolvierte = organische Sensoren mit Sonderregeln – ohne Codeänderung.
- **Radar-Mechanik:** Radar-Gebäude (GDD-Gebäudeliste) als `VisionSource` mit großer Reichweite, aber nur „Signatur"-Stufe: Feinde erscheinen als Minimap-Pings/unklare Marker statt voll aufgedeckt. Technisch: separater `radar`-Bitplane im selben Grid oder eigener Low-Freq-Tick (z. B. 1 Hz Sweep) → deutlich günstiger als permanente Vollsicht.
- **Tarnung/Aufdeckung:** Einheiten tragen `stealth`-Flag; eine Zelle ist für getarnte Einheiten nur dann „enttarnt", wenn eine Quelle mit `revealsStealth` sie sieht. Implementierung als zweite Auswertung desselben Grids (kein eigenes System). SC2-Detektor-Modell als Referenz.
- **Team-Sicht:** Bitmask-Modell (s. o.); gemeinsame Sicht verbündeter Spieler ist reine ODER-Verknüpfung. Spectator/Replay = Maske „alle" (Gemserk nutzt exakt das für Replays).
- **Minimap-Integration:** Minimap-Shader sampelt dieselbe FoW-Textur wie der Hauptpass (unerforscht = schwarz, erforscht = entsättigt, sichtbar = voll). Kein zweites System; nur ein zweites Material. Radar-Pings sind UI-Icons über der Minimap.
- **Einheiten-Sichtbarkeit:** Angriffs-/Auswahlprüfung fragt `IsVisible(position, teamMask)` ab (Grid-Lookup statt Physik); versteckte Einheiten werden per Culling-Layer oder Renderer-Deaktivierung ausgeblendet (Praxis bei Gemserk: Layer-Swap).

## Performance auf großen Karten mit 500 Einheiten

Annahme: Karte 512×512 m, Grid 1 m/Zelle → 512×512 Zellen = 262 kZellen; `values`+`visited` als 8-Bit-Bitmasken (8 Spieler) ≈ 512 kB – unkritisch.

- **Radius-Rasterung:** gefüllter Kreis r=12 ≈ ~450 Zellen; 500 Quellen ≈ 225 k Zell-Schreibzugriffe pro Sicht-Tick. Mit Burst/Jobs ist das ein Sub-Millisekunden-Job (Einschätzung; Gemserk berichtet 50+ Einheiten auf Mobile bei 60 FPS mit naivem C#, Optimierungspotenzial explizit).
- **Sicht-Tick ≠ Frame-Tick:** SC2 aktualisiert Sicht spürbar verzögert (Gemserk: ~1 s). Für Nova Ziel: 5–10 Hz Sicht-Tick mit Easing/Interpolation im Shader → CPU-Budget pro Frame praktisch null, kein Poppen.
- **Inkrementelle Updates:** stationäre Quellen (Gebäude) werden nur bei Änderung neu gerastert; nur bewegte Einheiten ticken – reduziert die Last im Basisspiel massiv.
- **Textur-Upload:** 512×512 R8-Upload bei 10 Hz ist ~2,6 MB/s – vernachlässigbar; Blur/Upscale erfolgt GPU-seitig im Material.
- **GPU-Seite (alle Ansätze):** ein zusätzliches Texture-Sample im Terrain-/Fullscreen-Shader; irrelevant für das 60-FPS-Budget.
- Fazit: **Ansatz B liegt mit großer Reserve im Budget**; Ansatz C löst ein Problem, das bei diesen Größen nicht existiert. Mitgehört: [Brendan Keesing – Fog of War Optimierungen](https://brendankeesing.com/blog/fog_of_war/) (Batching, Downsampled Copies, Compute nur wo nötig).

## URP-Kompatibilität

- URP bietet mit der **Full Screen Pass Renderer Feature** einen dokumentierten, versionsstabilen Einsprungpunkt für FoW-Überlagerung ([Unity Manual URP 14: Full Screen Pass Renderer Feature](https://docs.unity3d.com/Packages/com.unity.render-pipelines.universal@14.0/manual/renderer-features/renderer-feature-full-screen-pass.html)); eigene `ScriptableRendererFeature`/`ScriptableRenderPass` ist der Standardweg für screen-space FoW ([Cyanilux: Custom Renderer Features](https://www.cyanilux.com/tutorials/custom-renderer-features/)).
- Persistente Texturen über Frames hinweg via `RTHandle` sind etablierte Praxis in URP ([Unity Discussions, AljoshaD/Unity-Team-Kontext](https://discussions.unity.com/t/urp-scriptable-render-pass-will-temp-render-texture-persist-indefinitely/1530185)).
- **Unity 6 / RenderGraph beachten:** ältere `CommandBuffer.Blit`-Basismuster müssen auf die RenderGraph-API migriert werden; neue FoW-Pässe direkt RenderGraph-konform schreiben, sonst Migrationsschuld in Sprint 7+ ([Unity Discussions: RenderGraph in URP](https://discussions.unity.com/t/how-to-use-rendergraph-in-urp-learning-resources-and-tricks/1652190)).
- Metal (macOS/Apple Silicon) und DX11/12 (Windows) sind für R8/RG8-Texturen und einfache Fullscreen-Pässe unproblematisch; ComputeShader (Ansatz C) brächte plattformspezifische Pflege.
- Decal-Alternative (URP Decal Projector für FoW-Fläche) wurde geprüft und verworfen: Decals sind für lokale Effekte gedacht, nicht für globale, pro-Pixel-variable Zustandsmasken; Screen-Space-Pass ist der sauberere Weg (Deckt sich mit den Optionen in [Unity Discussions: FoW on large maps](https://discussions.unity.com/t/fog-of-war-urp-on-large-maps-without-tanking-performance/920374)).

## Netcode-Aspekte (Schnittstelle zu Q-013)

- **Kernproblem Maphack:** In deterministischem Lockstep besitzt jeder Client den vollständigen Weltzustand – FoW existiert dann nur als Darstellung im Speicher des Clients und ist per Memory-Read/DLL-Injection auslesbar. Das ist in der SC2-Community ein jahrelang dokumentiertes, nie vollständig gelöstes Problem ([Blizzard-Forenthread zu Maphacks](https://us.forums.blizzard.com/en/sc2/t/so-blizzard-when-are-you-going-to-fix-map-hack-cheating/17718)); akademisch fundiert: [OpenConflict – Preventing Real Time Map Hacks](https://www.shiftleft.org/papers/openconflict/openconflict.pdf) und [Feng et al., NOSSDAV 2005 – Mitigating Information Exposure in RTS Games](https://www.thefengs.com/wuchang/cstrike/nossdav05_mitigating.pdf).
- **Server-autoritativer State-Sync:** Nur der Server berechnet das Sichtgrid; Clients erhalten ausschließlich Daten sichtbarer Entitäten → echter Maphack-Schutz, weil die Information den Server nie verlässt. Referenz-Praxis: dedizierte RTS-Server (z. B. Planetary Annihilation) gelten in der Community als maphack-resistent genau aus diesem Grund ([TL.net-Diskussion, Community-Quelle](https://tl.net/forum/starcraft-2/423044-maphack-and-the-problems-with-protection-from-it?page=3)).
- **Kosten der Server-Sicht:** Das Grid-/Bitmask-Modell (Ansatz B) ist auf einem Headless-Server exakt so lauffähig wie im Client – kein Rendering nötig, nur Integer-Rasterung. Bei textur-/GPU-zentrierten Ansätzen (A/C) müsste der Server ein zweites, paralleles CPU-Modell pflegen → doppelte Wahrheit, doppelte Fehlerquelle.
- **Fog-of-War-Delta-Sync:** Bei State-Sync können Sichtwechsel als Delta (Betreten/Verlassen von Sicht) mit Entitäts-Spawn/Despawn gekoppelt werden – Bandbreitenschonend und verhindert „Ghost-Information".
- **Replays/Spectator:** Bitmask-Design erlaubt serverseitige Vollaufzeichnung mit nachträglicher Perspektivwahl (SC2-/Gemserk-Muster). Hinweis: Stormgate/SnowPlay zeigt mit 64-Tick-Determinismus + Rollback, dass moderne RTS weiterhin auf deterministische Simulation setzen ([Stormgate GDC 2024](https://playstormgate.com/news/first-look-at-the-stormgate-editor-at-gdc)) – die Lockstep-vs-Server-Frage bleibt Q-013 vorbehalten; FoW spricht als Teilkriterium klar für Server-Autorität bzw. für ein Sichtmodell, das beide Varianten bedienen kann.

## Empfehlung

**Vorschlag für den DecisionLog (Sprint 3):** Project Nova implementiert Fog of War als **grid-/bitmask-basiertes CPU-Sichtmodell (Ansatz B) mit textur-basierter Präsentation** – ein 1-m-Sichtraster mit `values`/`visited`-Bitarrays pro Team als einzige Wahrheit für Logik, KI, Radar, Tarnung und Minimap; die Darstellung erfolgt über eine aus dem Grid gespeiste Textur in einem URP-`ScriptableRendererFeature` (RenderGraph-konform, Unity 6). Sichtparameter (Reichweite, Höhenlevel, Radar-/Detektor-Flags) sind ScriptableObject-Daten. MVP startet mit reinem Radius-Modell; Höhen-LoS wird als konfigurierbare Option desselben Raster-Schritts für Phase 2 vorgehalten.

**Geprüfte Alternativen und Verwerfungsgründe:**
- **A (reines RenderTexture-/Splat-FoW):** verworfen, weil es kein Logik-Datenmodell liefert (Angriffe, KI, Tarnung bräuchten CPU-Readback oder Parallelmodell) und netcode-seitig wertlos ist; seine Stärken (Optik, Minimap) erbt die Empfehlung über die Textur-Ausgabe von B.
- **C (GPU-ComputeShader-FoW):** verworfen (vorerst), weil es bei 500 Einheiten ein nicht vorhandenes Skalierungsproblem löst, dafür Readback-Latenz für Spiellogik, Metal/DX-Pflegeaufwand und Determinismus-Risiken (Q-013) einführt; bleibt dokumentierter Ausweichpfad, falls Profiling in Phase 2 CPU-Grenzen zeigt.
- **D (Mesh-/Visibility-Polygon-FoW):** verworfen, weil es bei hunderten Sichtquellen weder CPU- noch drawcall-seitig skaliert und ebenfalls kein Logikmodell liefert.
- **Volles 3D-LoS per Physik-Raycast:** verworfen (skaliert nicht, unruhige Ergebnisse); Höhen-LoS im Grid deckt den taktischen Nutzen ab.

**Netcode-Konsequenz:** Das gewählte Modell läuft identisch auf einem autoritativen Server und stützt die Q-013-Teilthese „server-autoritativer State-Sync wegen Maphack-Resistenz"; es bleibt aber auch mit deterministischem Lockstep kompatibel (Integer-Rasterung), falls Q-013 anders entschieden wird.

## Offene Punkte

- **Grid-Auflösung** (1 m vs. 2 m pro Zelle) und maximale Kartengröße: erst mit Q-010 (Kartengrößen, Sprint 2) final festlegbar. Speicher-/Kostenmodell muss dann nachgerechnet werden.
- **Radar-Detaildesign:** Pings vs. Graustufen-Aufdeckung, Sweep-Frequenz, Allianz-/Legion-/Evolvierte-Sonderformen → Game-Design-Frage (Sprint 2), technisch sind beide Varianten abbildbar.
- **Aetherium-Interaktion:** Verändert nachwachsendes Aetherium Sichtlinien (blockierende Kristalle) oder Sichtweiten? Abhängig von Q-005 und GDD-Entscheidungen (Sprint 2).
- **LoS-Aktivierung:** Messung in Phase 2 nötig, ob Höhen-LoS bei 500 Einheiten im Budget bleibt (Einschätzung: ja, bei 5–10 Hz Tick; unverifiziert).
- **Q-013-Abhängigkeit:** Finale Server-Sicht-Architektur (Delta-Sync-Format) erst nach Simulations-/MP-Entscheidung in Sprint 3.
- Kein Eintrag in [../production/OpenQuestions.md](../production/OpenQuestions.md) nötig – obige Punkte sind Umsetzungsdetails, keine Blocker.

## Nächste Schritte

1. Orchestrator: Empfehlung als DecisionLog-Entwurf (Sprint 3) registrieren; Querverweis auf Q-013-Research (MP-Modell) herstellen.
2. Sprint 2: Grid-Auflösung und Radar-/Aetherium-Fragen mit Game Design klären (Q-005, Q-010).
3. Sprint 3: FoW-Abschnitt ins Technical Design Document übernehmen (Datenmodell `VisionSource`/`VisionGrid`, Tick-Strategie, URP-Pass-Design).
4. Phase 2 (Vertical Slice): Prototyp mit 500 simulierten Quellen auf Apple Silicon profilen (Ziel: ≤1 ms Sicht-Tick bei 10 Hz) und Höhen-LoS-Option vermessen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Research-Erstfassung | Lead Graphics Engineer |
