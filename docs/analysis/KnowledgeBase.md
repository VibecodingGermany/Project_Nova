# Wissensbasis – Destillation der Quelldokumente

**Version:** 1.0.0 | **Status:** sprint-freigegeben (Sprint 0) | **Verantwortungsbereich:** Game Director / Technical Writer | **Sprint:** 0

## Zweck

Verdichtete, quellenreferenzierte Wissensbasis des gesamten bisherigen Projektstands. Sie dient allen nachfolgenden Sprints als gemeinsamer Faktenraum, ohne die drei Quelldokumente erneut vollständig lesen zu müssen. Konflikte zwischen Quellen werden hier **nicht** gelöst, sondern in [Inconsistencies.md](Inconsistencies.md) und [../production/OpenQuestions.md](../production/OpenQuestions.md) erfasst.

## Abhängigkeiten

- Quelle A: `RTS_Game_Design_Outline.md` (Projektroot) – nachfolgend **GDD-O**
- Quelle B: `RTS_Technisches_Planungsdokument.md` (Projektroot) – nachfolgend **TPD**
- Quelle C: `RTS_Asset_Pipeline.md` (Projektroot) – nachfolgend **APL**

## 1. Spielkonzept

- Genre: Echtzeitstrategie (RTS) mit Base-Building, Singleplayer & Multiplayer (GDD-O)
- Kamera: 3D-Welt mit schräger Top-Down-/isometrischer Perspektive, frei beweglich, Zoom, optionale Rotation, Minimap-Navigation (TPD §6.2)
- Visueller Stil: *Stylized Military Science Fiction* – klare Silhouetten, Lesbarkeit vor Realismus, klare Fraktionsfarben (TPD §6.3)
- Kernloop: Ressourcen sammeln → Basis erweitern → Einheiten produzieren → Gegner angreifen → Karte kontrollieren → Match gewinnen (TPD §13 Phase 1)
- Vision laut GDD-O: klassischer Base-Builder mit dynamischen Kristallfeldern und **vollständig zerstörbarer Sci-Fi-Umgebung**

## 2. Ressource

- **Aetherium**: außerirdischer Kristall, radioaktiv, wächst langsam nach, verändert die Umwelt, Grundlage aller Technologien (GDD-O)
- Wirtschaftssystem umfasst: Kristallfelder, Sammler, Raffinerien, Transportwege, Baukosten, Energieversorgung, Lagerkapazität, Ressourcenwachstum und erschöpfte Felder (TPD §8.4)
- Hinweis: "wächst nach" vs. "erschöpfte Felder" ist eine zu klärende Designregel → Q-005

## 3. Fraktionen

| Fraktion | Identität | Merkmale | Superwaffe |
|---|---|---|---|
| Allianz | High-Tech, präzise, teuer | Infanterie, Panzer, Artillerie, Luftwaffe | Ionenstrahl |
| Legion | Masse statt Klasse | günstige Einheiten, schwere Militärtechnik, Flammen-/Raketenwaffen | Thermobarisch |
| Evolvierte | biologisch mutiert | Kristallwesen, organische Fahrzeuge, Regeneration | Kristallsturm |

(Quelle: GDD-O; Einheitenlisten detailliert in APL Pakete 04–06)

## 4. Karten und Biome

Zehn Umgebungsthemen (GDD-O / APL Paket 01): Wüste, Schnee, Vulkan, Dschungel, Sumpf, Verlassene Stadt, Industriegebiet, Alien-Welt, Mond, Mars.
Klärung nötig: Verhältnis Biom ↔ konkrete Karte → Q-010.

## 5. Gebäude und Einheiten (Asset-Umfang laut APL)

- Gebäude: GDD-O nennt 11 Typen (HQ, Raffinerie, Kraftwerk, Lager, Kaserne, Fahrzeugfabrik, Flugfeld, Forschung, Radar, Verteidigung, Superwaffe); APL rechnet mit 18 Typen × 3 Fraktionen ≈ 54 Assets → **Inkonsistenz I-01**
- Infanterie: 8 Typen pro Fraktion = 24 (APL Paket 04)
- Fahrzeuge: 12 Typen pro Fraktion = 36 (APL Paket 05); Evolvierte erhalten biologische Entsprechungen
- Luftfahrzeuge: 7 Typen pro Fraktion = 21 (APL Paket 06)
- Marine: 6 Typen, in APL ausdrücklich optional (Paket 07); im TPD-MVP ausgeschlossen; im GDD-O nicht erwähnt → Q-003
- Spezialeinheiten: 5 Typen gelistet, Gesamtumfang sagt 15 → **Inkonsistenz I-02**
- Drohnen: 6 Typen (APL Paket 09), im GDD-O nicht erwähnt → Q-004
- Neutrale Einheiten: Tiere, Banditen, Mutanten, Händler, Geschütztürme (APL Paket 10) → "Händler" impliziert ggf. Handelssystem → Q-007

## 6. Verbindlicher Technik-Stack (TPD §17, übernommen per D-002)

- Engine: **Unity**; Sprache: **C#**; Rendering: **URP**
- Primärplattformen: **Windows, macOS**; Entwicklung auf macOS/Apple Silicon
- Sekundärplattformen (nach Desktop-Vertical-Slice, nur nach Prüfung): iPadOS, Android-Tablets, WebGL, iPhone, Android-Smartphones
- Architektur-Leitplanken: modular, **datengetrieben** (ScriptableObjects für Einheiten-/Gebäude-/Waffen-/Tech-Werte), ereignisbasierte Kommunikation, getrennte Gameplay- und Präsentationslogik (TPD §11, §15)
- Versionsverwaltung: GitHub + Git LFS, Branching main/develop/feature/fix/art/release, Worktrees bei parallelen Agenten (TPD §12)

## 7. Technische Kernsysteme (TPD §8)

Einheitensystem; Auswahl-/Befehlssystem; Pathfinding (Grid/Flow-Field/Hybrid früh prüfen, NavMesh allein evtl. unzureichend); Ressourcen-/Wirtschaftssystem; Base-Building; Kampfsystem; Fog of War; Produktionssystem; Technologiebaum (Tier 1–3); KI-System (mehrschichtig, Schwierigkeit über Entscheidungsqualität statt Ressourcenboni).

## 8. Multiplayer-Richtung

- Langfristig **autoritative Serverarchitektur** empfohlen (TPD §9.1)
- Bestandteile: Konten, Lobbys, Matchmaking, Ranglisten, private/öffentliche Matches, Teams, Beobachter, Replays, Statistiken, Reconnect (TPD §9.2)
- Backend-Optionen offen: A) C#/ASP.NET Core/PostgreSQL, B) TypeScript/Node.js/PostgreSQL – Entscheidung erst beim Multiplayer-Prototyp (TPD §9.3)
- Reihenfolge: Multiplayer erst nach stabilem Singleplayer-Kern (TPD §17)
- Spielmodi laut GDD-O: Solo, Koop, PvP, Ranked, Survival, FFA, King of the Hill

## 9. Entwicklungsphasen (TPD §13)

- **Phase 0 – Technischer Spike:** Kamera, 100–500 Einheiten, Pathfinding, Auswahl, Kampf, Bau, Abbau, Performance Mac/Windows, Asset-Import, URP
- **Phase 1 – Gameplay-Prototyp:** 1 Fraktion, 1 Karte, vollständiger Kernloop, einfache KI, Sieg/Niederlage
- **Phase 2 – Vertical Slice:** ausgearbeitete Fraktion + Karte, volles UI, Audio, VFX, Tech-Tree, FoW, gute KI, Tutorial, erste MP-Tests
- **Phase 3 – Produktionsversion:** 3 Fraktionen, Karten, MP, Matchmaking, Replays, Ranglisten, Balancing, Accessibility, Lokalisierung
- **Phase 4 – Plattform-Ports**

## 10. MVP-Abgrenzung (TPD §14)

MVP enthält **nicht**: 3 ausgearbeitete Fraktionen, Mobile/Browser, Kampagne, Ranglisten, Clans, Turniere, Story, Cinematics, Marine, hunderte Einheiten, Live-Service. MVP dient ausschließlich der Validierung des Spielkerns.

## 11. Asset-Strategie

- Prototyp/MVP: kaufen statt bauen (Fahrzeuge, Gebäude, Infanterie, Animationen, Landschaft, VFX, SFX, UI-Basis) (TPD §7.1)
- Signature-Assets selbst entwickeln: Aetherium-Kristalle/-Felder, Sammler, Fraktionslogos, Commander, HQs, Superwaffen, Eliteeinheiten, fraktionsspezifische Effekte, UI-Identität, Key Art (TPD §7.2) → Commander-System im GDD nicht definiert → Q-002
- Kaufprüfung: URP-Kompatibilität, kommerzielle Lizenz, Polycount, LODs, Rigging/Animationen, Mobile-/WebGL-Eignung, Stil-Kompatibilität (TPD §7.3)

## 12. Qualitätsziele (TPD §15)

- Performance: 60 FPS Desktop (min. 30 auf schwacher Hardware), mehrere hundert Einheiten langfristig, wenig GC-Spitzen
- Stabilität: deterministische oder kontrollierte Simulation, automatisierte Tests, Logging, Profiling, Crash-Reporting, Savegame-Versionierung
- Wartbarkeit: modulare Systeme, klare Schnittstellen, datengetrieben, dokumentierte Architektur

## 13. Bewusst offene technische Entscheidungen (TPD §16)

Multiplayer-Framework, Serveranbieter, Backend-Sprache, Hosting, DB-Struktur, finale Pathfinding-Lösung, Modding, Workshop, DRM, Vertrieb (Steam/Epic/eigen), Crossplay, Konsolen. Diese dürfen den frühen Prototyp nicht blockieren.

## Offene Punkte

- 12 Inkonsistenzen zwischen den Quellen: siehe [Inconsistencies.md](Inconsistencies.md)
- Fachliche Lücken (Vision, USP, Zielgruppe, Audio, UI/UX, Balancing u. a.): siehe [GapAnalysis.md](GapAnalysis.md)

## Nächste Schritte

- Sprint 1 (Research) nutzt diese Wissensbasis als Ausgangslage; Veränderungen fließen hierher zurück.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Initiale Wissensbasis aus GDD-O, TPD, APL destilliert (Sprint 0) | Game Director |
