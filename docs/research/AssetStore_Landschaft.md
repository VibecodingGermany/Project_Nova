# Asset-Store-Landschaft für RTS (Vorbereitung Sprint 5)

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Environment Artist | **Sprint:** 1

## Zweck

Dieses Dokument kartiert die Beschaffungslandschaft für Assets (Unity Asset Store, Fab, Sketchfab, itch.io, Humble Bundles) über alle für Project Nova relevanten Asset-Kategorien. Es dient als Entscheidungsgrundlage für die BUY / MODIFY / BUILD-Klassifikation im Asset Audit (Sprint 5). Es enthält **keine Kaufentscheidungen** – Käufe erfolgen frühestens in Sprint 5, nachdem Art Direction (Sprint 2) und Asset-Budget (Sprint 3) feststehen. Verbindlich für: Lead Environment Artist, Technical Artist, Producer (Budget).

## Abhängigkeiten

- [../analysis/KnowledgeBase.md](../analysis/KnowledgeBase.md) – Ausgangslage: Stylized Military Sci-Fi, URP (D-002), 100–500+ Einheiten, 60 FPS Desktop
- [../production/OpenQuestions.md](../production/OpenQuestions.md) – u. a. Q-013/Q-014/Q-015 (werden durch dieses Dokument **nicht** entschieden, siehe Offene Punkte)
- [../../RTS_Asset_Pipeline.md](../../RTS_Asset_Pipeline.md) – vollständige Bedarfsliste (10 Biome, ~54 Gebäude, 24 Infanterie, 36 Fahrzeuge, 21 Lufteinheiten, Kristallfelder)
- Risiko R-04 (visuelle Inkohärenz gekaufter Assets) in [../production/RiskAnalysis.md](../production/RiskAnalysis.md)

## Marktplätze im Überblick (Stand: Juli 2026)

| Marktplatz | Rolle für Project Nova | Lizenzmodell | Besonderheiten |
|---|---|---|---|
| **Unity Asset Store** | Primärquelle für Unity-native Pakete (VFX, Tools, UI, Synty) | Standard-Asset-Store-EULA; Per-Seat-Logik („Seat 1" im Checkout); „Restricted Assets" (EULA §2.2.2) mit abweichenden Bedingungen | SRP-Kompatibilitäts-Badge pro Unity-Version (Built-in/URP/HDRP) als erster Filter |
| **Fab (Epic)** | Sekundärquelle; hat Unreal Marketplace, Sketchfab Store, Quixel und ArtStation Marketplace vereint (Launch Okt. 2024) | Fab Standard License; Lizenzdetails pro Produkt prüfen | Megascans seit 2025 **nicht mehr kostenlos**; Unity-Inhalt vorhanden, aber UE-lastig |
| **Sketchfab** | Einzelmodelle, Fundgrube für Referenzen | CC-BY / CC0 / Paid – **Lizenz pro Modell prüfbar**, kein Pauschalmodell | Store-Inhalte wandern nach Fab; Attribution-Pflicht bei CC-BY in Credits dokumentieren |
| **itch.io** | CC0-/Low-Poly-Packs (Kenney, Quaternius), Prototyping | Häufig CC0, aber je Pack individuell | Kein Unity-Package-Format; Import- und URP-Umbau selbst zu leisten |
| **Humble Bundle** | Preishebel: Synty-Bundles wiederkehrend (~8 Packs / 30 USD statt >600 USD) | Publisher-EULA (meist Synty-Lizenz, 5 Seats pro Lizenz) | Zeitlich limitiert; Keys werden publisherseitig eingelöst – Seat-Verwaltung beachten |

Quellen: [CG Channel: Fab-Launch](https://www.cgchannel.com/2024/10/epic-games-launches-its-new-fab-marketplace-in-october-2024/), [80 Level: Megascans nicht mehr kostenlos](https://80.lv/articles/megascans-no-longer-free-after-2024), [Unity Asset Store EULA](https://unity.com/legal/as-terms), [Synty Humble Bundle 2026](https://syntystore.com/blogs/blog/sci-fi-game-dev-humble-bundle-2026), [Cinevva: Sketchfab vs. Poly Haven vs. Kenney](https://app.cinevva.com/guides/sketchfab-polyhaven-kenney).

## Kategorien-Analyse

### 1. RTS-Frameworks / Complete Kits

- **Verfügbarkeit:** Mehrere vollständige RTS-Engines existieren, z. B. [Strategy Kit: RTS Engine (Game Dev Spice), 85 USD](https://assetstore.unity.com/packages/tools/game-toolkits/strategy-kit-rts-engine-79732), [RTS Framework](https://assetstore.unity.com/packages/templates/systems/rts-framework-116190) und [RTS Engine uCNC 2D](https://assetstore.unity.com/packages/tools/game-toolkits/rts-engine-ucnc-2d-the-universal-rts-game-kit-ultimate-crush-and-130510). Module wie ein [Save-System-Modul für RTS Engine, 10 USD](https://assetstore.unity.com/packages/tools/game-toolkits/save-system-rts-engine-module-226920) zeigen das Ökosystem.
- **Preisniveau:** 30–110 USD pro Framework, zzgl. Modulen.
- **URP:** Frameworks sind Code-lastig; mitgelieferte Demo-Assets meist Built-in, aber ersetzbar. Geringeres URP-Problem.
- **Lizenzfallen:** Standard-EULA, per Seat. Kein Quellcode-Ausschluss, aber kein Recht auf Weitergabe an Dritte (Outsourcing-Artists brauchen eigene Seats).
- **Stil-Kohärenz:** Irrelevant (Code), aber **Architektur-Risiko:** Diese Kits treffen eigene Simulations-, Determinismus- und OOP-Entscheidungen und kollidieren frontal mit Q-013 (MP-Modell) und Q-015 (ECS/DOTS). Für ein 100–500+-Einheiten-RTS mit späterem autoritativem Server ist ein gekauftes Komplett-Kit ein Wartungs- und Rewrite-Risiko. **Einschätzung:** als Referenz-Lektüre wertvoll, als Codebasis ungeeignet.

### 2. Stilisierte Sci-Fi-Fahrzeuge

- **Verfügbarkeit:** Gut. Synty deckt den Stil „Stylized Military Sci-Fi" fast exakt ab: [POLYGON Sci-Fi City Pack, 49,99 USD](https://assetstore.unity.com/packages/3d/environments/sci-fi/polygon-sci-fi-city-pack-art-by-synty-115950) (inkl. Fahrzeuge), [POLYGON Sci-Fi Space Pack, ~75 USD im Sale / 149,99 USD Liste](https://syntystore.com/products/polygon-sci-fi-space-pack), [POLYGON Military Pack, 149,99 USD (Liste 299,99 USD)](https://www.gameassetdeals.com/?show=allsales&category=&sort=pricedesc), POLYGON Mech Pack ~50 USD im Sale.
- **Preisniveau:** 30–150 USD pro Pack; regelmäßig 50 % Sales; Humble-Bundles drücken den Effektivpreis auf wenige USD pro Pack.
- **URP:** Synty-Packs sind URP-kompatibel (laut Store-Badge, Unity 2022.3+).
- **Lizenzfallen:** Synty Store verkauft **5 Seats pro Lizenz** – für ein kleines Team okay, bei Wachstum nachlizenzieren.
- **Stil-Kohärenz:** Niedriges Risiko innerhalb Synty; hoch beim Mischen mit realistischen Packs. Bedarf: 36 Fahrzeuge + 21 Lufteinheiten über 3 **asymmetrische** Fraktionen – Synty liefert generisches Militär, aber keine fraktionsspezifische Identität (High-Tech vs. Masse vs. biologisch). Die Evolvierten (biologisch) sind im Store kaum abgedeckt → MODIFY/BUILD-Kandidat.

### 3. Sci-Fi-Gebäude

- **Verfügbarkeit:** Sehr gut (Sci-Fi City, Sci-Fi Outpost, modulare Baukästen; CC0-Alternativen: [Quaternius Ultimate Modular Sci-Fi](https://quaternius.com/packs/ultimatemodularscifi.html), [Kenney Modular Space Kit](https://kenney.nl/assets/modular-space-kit)).
- **Preisniveau:** 0 USD (CC0) bis ~150 USD.
- **URP:** Bei Synty gegeben; CC0-Packs kommen als FBX/glTF ohne Unity-Materialien → URP-Materialsetup im eigenen Shader-Standard nötig (ohnehin empfohlen, siehe Empfehlung).
- **Lizenzfallen:** CC0 unkritisch; Fab-Einzelmodelle mit Standard License prüfen (Beispiel: [Modular SciFi Station auf Fab](https://www.fab.com/listings/0667e321-31a7-40ed-b85c-6db5bbc4366b), ehemals kostenlos, inzwischen ~45 USD – Preise rotieren).
- **Stil-Kohärenz:** 54 Gebäude in 3 Fraktionen sind der größte Einzelposten der Pipeline. Modulare Baukästen + eigene fraktionsspezifische Dach-/Detail-Elemente (Kit-Bashing) ist der übliche Weg, Kohärenz zu erzwingen – reine Fremdmodelle pro Gebäude würden R-04 verschärfen.

### 4. Infanterie-Modelle (rigged)

- **Verfügbarkeit:** Gut für menschliche Soldaten (Synty Military/Sci-Fi-Packs, alle „fully rigged"; Sidekick-Charakter-System für modulare Varianten). Schwach für biologische Evolvierte.
- **Preisniveau:** 35–150 USD pro Charakter-Pack; Sidekick-Packs deutlich teurer (Vierstelliger-Yen-Bereich bzw. ~100+ USD, 5 Seats).
- **URP:** Synty ok.
- **Lizenzfallen:** Rigged Characters sind Runtime-Content – Standard-EULA; kein Problem. **Falle:** kostenlose Mixamo-Charaktere/-Animationen (Adobe) erlauben kommerzielle Nutzung im gerenderten Spiel, aber keine Weitergabe der Rohdaten – für interne Pipeline okay, für geteilte Repos mit externen Dienstleistern prüfen (Einschätzung, Detailklärung Sprint 5).
- **Stil-Kohärenz:** Humanoid-Animationen sind zwischen Packs retargetbar (Humanoid-Rig), das senkt das Mischrisiko. 24 Infanteristen × 3 Fraktionen: Synty-Silhouetten + eigene Farb-/Material-Fraction-Pass (Teamfarben!) als Kohärenz-Anker.

### 5. Environment-/Biome-Pakete (Wüste, Schnee, Vulkan, Dschungel, Sumpf, Stadt, Industrie, Alien)

- **Verfügbarkeit:** Synty Nature-Biome-Serie (u. a. Meadow Forest, Swamp Marshland, Snow), Apocalypse Wasteland (Wüste/Dystopie), Sci-Fi City (Stadt/Industrie). Terrain-Generierung: [Gaia Pro VS, 199 USD (109 Ratings)](https://assetstore.unity.com/packages/tools/terrain/gaia-pro-vs-terrain-trees-grass-water-for-unity-6-263149) bzw. Gaia Pro 2021 149 USD; Alternativen: MapMagic 2 (Core kostenlos, Module ~45 USD), MicroVerse.
- **Preisniveau:** Biome-Pack 30–150 USD; Terrain-Tool 0–200 USD.
- **URP:** Gaia Pro VS explizit Built-in/URP/HDRP-kompatibel; Vegetation-Shader (Wind, Translucency) sind der kritische Punkt – Drittanbieter-Bäume mit Built-in-Shadern funktionieren in URP nicht ohne Ersatz-Shader (z. B. The Vegetation Engine).
- **Lizenzfallen:** Gaia per Seat; „Restricted Assets"-Kennzeichnung prüfen.
- **Stil-Kohärenz:** 10 Biome aus 10 verschiedenen Quellen = garantiertes R-04. Empfehlenswert: 1–2 Biome-Quellen (ein Stil!) + eigene Aetherium-Veränderungs-Layer. Die Kristall-Umweltveränderung (Kernfeature!) existiert als fertiges Asset **nicht** → BUILD.

### 6. Kristall-/Ressourcen-Assets (Aetherium)

- **Verfügbarkeit:** Reichlich: [Stylized Crystals and Gems Megapack (Piloto Studio), 19,99 USD, URP-kompatibel](https://assetstore.unity.com/packages/3d/props/stylized-crystals-and-gems-megapack-327094), [PBR Stylized Crystals Pack, 19,99 USD – Achtung: URP **nicht** kompatibel](https://assetstore.unity.com/packages/3d/environments/pbr-stylized-crystals-pack-194812), [Translucent Crystals (SineVFX), kostenlos](https://assetstore.unity.com/top-assets/top-free), Shatter Stone: Stylized Gemstones ~24,99 USD.
- **Preisniveau:** 0–25 USD.
- **URP:** Genau hier zeigt sich das Filterproblem exemplarisch: gleiche Kategorie, gleicher Preis – ein Pack URP-tauglich, das andere nicht. URP-Badge ist Pflichtfilter vor jeder Shortlist.
- **Stil-Kohärenz:** Aetherium ist **das** Signature-Element des Spiels (nachwachsend, umweltverändernd). Gekaufte Kristalle als Basis okay, aber Shader (Glow, Wachstumsstufen, Verseuchung) muss eigen sein → MODIFY/BUILD.

### 7. VFX (Explosionen, Laser, Schilde)

- **Verfügbarkeit:** Sehr gut: [Realistic Effects Pack 4 (KriptoFX), 37 USD](https://assetstore.unity.com/packages/vfx/particles/spells/realistic-effects-pack-4-85675), Hovl Studio Stylized VFX (~10–22 USD pro Pack), War FX (Jean Moreno, kostenlos), Vefects URP-Linien (z. B. Free Fire VFX – URP, Trails VFX – URP).
- **Preisniveau:** 0–40 USD pro Pack.
- **URP:** **Größtes Filterproblem aller Kategorien.** VFX nutzen Custom-Shader (Additive/Alpha-Blend, Grab-Pass, HDRP-Shader-Graph); viele Bestseller sind Built-in-only oder benötigen kostenpflichtige URP-Upgrades. Nur Packs mit explizitem URP-Support shortlisten.
- **Lizenzfallen:** Standard-EULA; VFX-Packs mit beiliegenden SFX unterliegen teils zweier Lizenzen – Einzelprüfung.
- **Stil-Kohärenz:** Realistische KriptoFX-Explosionen auf Synty-Low-Poly-Modellen brechen den Stil („Lesbarkeit vor Realismus"). Für RTS auf Top-Down-Distanz zählen Silhouette und Timing, nicht Detail – eher stylized VFX (Hovl, Vefects) als realistische.

### 8. UI-Packs

- **Verfügbarkeit:** Gut: INTERFACE – Sci-Fi Soldier HUD (Synty, in Humble-Bundles enthalten), diverse Sci-Fi-UI-Packs im Store.
- **Preisniveau:** 10–40 USD.
- **URP:** UI läuft über uGUI/UI Toolkit – weitgehend pipeline-unabhängig. Geringes Problem.
- **Stil-Kohärenz:** RTS-UI (Command-Card, Ressourcenleiste, Minimap, Gruppenporträts) ist stark gameplay-verzahnt; gekaufte HUDs sind generisch. Erwartbar: Layout eigen, Icon-Bibliothek kaufen (Icons sind der teure Teil).

### 9. SFX/Musik

- **Verfügbarkeit:** Herausragend günstig: [Sonniss GDC Game Audio Bundles](https://sonniss.com/gameaudiogdc/) – über 200 GB professionelle, lizenzfreie SFX kostenlos (kommerziell nutzbar, keine Attribution; GDC-2026-Bundle: 347 Dateien / 7,47 GB, [Quelle](https://rekkerd.org/sonniss-releases-gdc-2026-game-audio-bundle/)). Käufliche Libraries (Boom Library etc.) 50–500 USD.
- **Preisniveau:** 0 USD (Sonniss) bis wenige hundert USD; Musik: Gekaufte Tracks 20–100 USD/Track oder Composer-Auftrag.
- **Lizenzfallen:** Sonniss-Dateien sind royalty-free, aber **nicht weitervertreibbar** (kein Upload in öffentliche Repos – Repo-Hygiene beachten). Store-Musik teils „nicht für Interactive" – Lizenztext lesen.
- **Stil-Kohärenz:** Audio-Kohärenz entsteht über Mixing/Mastering-Kette, nicht über Quelle. Geringes Risiko; 100+ gleichzeitige Einheiten erfordern Voice-Management (Audio-Priorisierung), kein Asset-Problem.

### 10. Animationspakete

- **Verfügbarkeit:** Sehr gut: Kevin Iglesias (Human Melee/Ranged Animations, ~11,50 USD pro Pack, Free-Varianten zum Testen), Mixamo (kostenlos, Auto-Rigging), [Quaternius Universal Animation Library (CC0, 250+ Animationen, Retarget-fähig)](https://app.cinevva.com/guides/free-character-animations-rigging), Synty ANIMATION – Base Locomotion (in Bundles).
- **Preisniveau:** 0–30 USD pro Pack.
- **URP:** Irrelevant (Daten, kein Rendering).
- **Lizenzfallen:** Mixamo-Einschränkung (s. Kategorie 4); CC0 unkritisch.
- **Stil-Kohärenz:** Gering; Humanoid-Retargeting gleicht Rig-Unterschiede aus. RTS-Distanz verzeiht generische Animationen – Signature brauchen nur Hero-/Commander-Einheiten.

## Querschnitt: Die vier Bewertungsdimensionen

1. **URP als Filterproblem:** Das Store-Badge (Built-in/URP/HDRP pro Unity-Version) ist der erste und billigste Filter – aber nur für Standard-Shader-Materialien verlässlich. Custom-Shader (VFX, Vegetation, Wasser) brechen trotz Badge-Erwähnung in Reviews; VOR Kauf (Sprint 5): URP-Konvertierung in einem Testprojekt validieren. Der PBR-Stylized-Crystals-Fall (URP: „nicht kompatibel" bei identischem Preis zum kompatiblen Konkurrenten) zeigt, dass Preis/Qualität nichts über Pipeline-Tauglichkeit aussagen.
2. **Lizenzfallen:** (a) **Editor vs. Runtime:** Editor-Extensions (z. B. Odin) sind streng per Seat; Runtime-Content (Modelle, VFX) ebenfalls per Seat erworben, aber im ausgelieferten Spiel unbegrenzt verteilbar. (b) **Restricted Assets** (EULA §2.2.2) können abweichende Bedingungen haben – Kennzeichnung auf der Store-Seite prüfen. (c) **Seat-Lizenzen:** Synty verkauft 5 Seats/Lizenz, Asset Store zeigt „Seat 1" – bei Teamwachstum/Externen nachlizenzieren. (d) **Nicht-Weitergabe:** Sonniss-SFX und Asset-Store-Rohdaten dürfen nicht in öffentliche Repos; privates Repo + LFS ist Pflicht. (e) **CC-BY:** Sketchfab-Modelle erfordern Attribution → Credits-Pflege ab Sprint 5.
3. **Stil-Kohärenz (R-04):** Risiko steigt mit Anzahl der Quellen und Realismus-Spread. Gegenmittel: ein Stil-Anker (Synty-Polygon-Look passt „Stylized Military Sci-Fi"), einheitlicher URP-Shader-/Material-Standard mit Teamfarben-Masken, und Post-Processing-Grading als „Kitt". Aetherium-Assets und Fraktions-Signaturen werden ohnehin selbst gebaut.
4. **Performance für 100–500+ Einheiten:** Store-Assets sind selten für Masseneinheiten optimiert (Skinned-Mesh-Anzahl, Draw Calls, LODs fehlen häufig). Budget-Kriterium für Sprint 5: LOD-Ketten vorhanden? Textur-Atlas-fähig? GPU-Instancing-taugliche Materialien? Das ist ein MODIFY-Treiber, kein Kaufhindernis.

## Vergleich der Beschaffungsstrategien (≥3 Alternativen)

| Kriterium | **A: Asset Store only (Synty-zentriert)** | **B: Multi-Store-Mix (Asset Store + Fab + itch.io + Humble)** | **C: Minimal-Kauf / BUILD-first (nur Tools + Audio kaufen)** |
|---|---|---|---|
| Kosten für Kernumfang (Einschätzung) | ~800–2.500 USD Listenpreise, ~300–800 USD mit Sales | ~200–600 USD (Humble-Bundles + CC0-Anteile) | ~100–300 USD, aber hohe Personalkosten für Eigenbau |
| Stil-Kohärenz | Hoch (ein Publisher, ein Look) | Mittel – bricht ohne strengen Material-Standard (R-04) | Maximal, aber langsam |
| Abdeckung 3 asymmetrischer Fraktionen | Lücken bei Evolvierten (biologisch) | Besser, aber heterogen | Volle Kontrolle |
| Zeit bis spielbarer MVP | Schnell | Mittel (Konvertierung CC0→URP) | Langsam – gefährdet MVP-Disziplin |
| URP-/Lizenz-Aufwand | Gering | Hoch (Fab-Rotation, CC-BY-Attribution, Seat-Tracking) | Gering |
| Abhängigkeit/Resilienz | Publisher-Risiko (Packs verschwinden/rotieren) | Verteilt, aber Verwaltungsaufwand | Kein externes Risiko |
| MP-/Architektur-Folgen | Keine (Art-only), solange Komplett-Kits gemieden werden | Gleich | Gleich |

**Projektbezogene Einordnung:** A scheitert an den Evolvierten und am Signature-Aetherium; C verletzt die MVP-Disziplin (Art-Bottleneck statt Kernloop) und ist für den RTS_Asset_Pipeline-Umfang (~135+ Modelle) unrealistisch. B nutzt den dokumentierten Preishebel (Synty-Humble-Bundle: 8 Packs / 30 USD statt >600 USD) und CC0 für Prototyping, verlangt aber Disziplin bei Lizenzen und URP-Filterung – genau die Disziplin, die Sprint 5 (Asset Audit) ohnehin institutionalisiert.

## Empfehlung

**Entscheidungsvorlage (für DecisionLog, Sprint 5 zu bestätigen):** Das Studio verfolgt **Strategie B – Multi-Store-Mix mit Synty als Stil-Anker**: Unity Asset Store (Synty-Packs für Allianz/Legion-Militär, Biome, UI-Icons) als Hauptquelle, ergänzt um Humble-Bundle-Käufe bei Gelegenheit (Preishebel), CC0-Quellen (Kenney, Quaternius) für Prototyping und Lückenfüller sowie Fab für Einzelmodelle nach Bedarf. **Aetherium-Kristalle (Shader/Wachstum), Evolvierten-Assets und Fraktions-Signaturen werden als MODIFY/BUILD klassifiziert**, da sie weder stilistisch noch funktional (Umweltveränderung) käuflich abgedeckt sind. **Geprüfte Alternativen und Verwerfungsgründe:** (A) „Asset Store only" – verworfen, weil biologische Evolvierte und das Kernfeature Aetherium nicht abgedeckt sind und Publisher-Abhängigkeit ohne Preishebel bleibt; (C) „BUILD-first" – verworfen, weil der Eigenbau von ~135+ Modellen die MVP-Disziplin und den Zeitplan gefährdet, ohne Qualitätsvorteil auf RTS-Betrachtungsdistanz. **Verbindliche Leitplanken ab sofort:** URP-Kompatibilität (Badge + Testprojekt-Validierung) als K.O.-Kriterium; Lizenz-Register (Seats, Restricted Assets, Attribution, kein Rohdaten-Upload in öffentliche Repos) ab Sprint 5; **keine RTS-Komplett-Frameworks kaufen** (Kollision mit Q-013/Q-015); einheitlicher URP-Material-Standard mit Teamfarben-Masken als Kohärenz-Instrument. Kaufentscheidungen bleiben Sprint 5 vorbehalten.

## Offene Punkte

- Das Studio-spezifische **Asset-Budget** (USD-Obergrenze) ist noch nicht definiert → Abhängigkeit zu Sprint 3 (AssetBudget.md laut Gap-Analyse §3) und Sprint 5.
- Seat-Planung (Teamgröße, Externe) unklar → beeinflusst Synty-5-Seat-Lizenzen und Editor-Tool-Käufe.
- Megascans/Fab-Lizenzdetails für Unity-Nutzung und aktuelle Fab-Standard-License-Texte: Detailprüfung erst in Sprint 5 (Markt rotiert; Stand hier: Juli 2026, teils Einschätzung).
- Mixamo-Nutzung in einer geteilten Repository-Pipeline: Lizenzdetail zu klären (Sprint 5).
- Keine neue Open Question erforderlich; Bezüge zu Q-001 (Gebäude-Scope: 11 vs. 18 Gebäudetypen entscheiden über Kaufmenge) notiert.

## Nächste Schritte

1. Sprint 2 (Game Design): Art-Direction-Dokument mit Stil-Anker (Synty-Look vs. Alternative) und Teamfarben-/Silhouetten-Regeln; Gebäude-Scope Q-001 entscheiden (steuert Kaufmenge).
2. Sprint 3 (Technical Design): URP-Material-Standard und LOD-/Draw-Call-Budgets definieren (Kaufkriterien für Sprint 5); Aetherium-Shader als BUILD-Epithema spezifizieren.
3. Sprint 5 (Asset Audit): Dieses Dokument zur Kategorie-Checkliste ausdifferenzieren; pro Asset BUY/MODIFY/BUILD + Lizenz-Register (Licenses.md); URP-Validierung im Testprojekt vor jedem Kauf; Humble-Bundle-Fenster beobachten (Synty-Bundles wiederkehrend).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Research-Erstfassung | Lead Environment Artist |
