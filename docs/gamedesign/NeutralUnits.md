# Neutrale Einheiten & Map-Objectives

**Version:** 0.2.0 | **Status:** Entwurf (Korrekturlauf Sprint 2) | **Verantwortungsbereich:** Lead Gameplay Designer | **Sprint:** 2

## Zweck

Spezifikation aller neutralen Entitäten auf Skirmish-/Karten gemäß D-016: (1) Critters als biomspezifisches Ambient-Leben, (2) feindliche neutrale Lager als bewachte Objectives mit Belohnung, (3) capturebare Geschütztürme als taktische Kontrollpunkte. Ein Handelssystem mit Händlern ist gemäß D-016 gestrichen und wird nicht spezifiziert. Ziel der Neutralen: Map-Identität, Scouting- und Expansionsanreize sowie frühe Konflikte, ohne den Kernloop (Aetherium-Wirtschaft → Armee → Vernichtung) zu verwässern. Alle Werte sind Startwerte v0.1 zum Tunen und datengetrieben (flache, ScriptableObject-taugliche Datensätze) definiert.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-016 (Neutrale, Händler gestrichen), D-008 (Verteidigungsplattform-Module), D-010 (Aetherium-Wirtschaft), D-017 (Biome/Karten), D-014 (Drohnen), D-022 (Capture-System: Kanal 5 s, Einheit verbraucht, Tunnelgräber schließt Evolvierten-Lücke), D-028 (Brücken reparierbar), D-029 (Artefakt-Sonde nur SP/Koop)
- [./FogOfWar.md](./FogOfWar.md) – Sichtbarkeitsregeln für Neutrale, Artefakt-Cache-Aufdeckung
- [./Factions.md](./Factions.md) – Fraktions-Stammdaten (Engineer-/Besetzer-Einheit pro Fraktion)
- [./Infantry.md](./Infantry.md) – Capture-Einheiten (Engineer/Saboteur/Tunnelgräber, Fähigkeit *Einnehmen* gemäß D-022), Zahlenraum Infanterie
- [./Vehicles.md](./Vehicles.md) – Zahlenraum Fahrzeuge (Referenzwerte für Lager-Fahrzeuge)
- [./Buildings.md](./Buildings.md) – Verteidigungsplattform (Module MG/Flak/Rakete) als Vorbild der capturebaren Türme
- [./Maps.md](./Maps.md) – Platzierungsregeln, Biome (D-017)
- [./Economy.md](./Economy.md) / [./Resources.md](./Resources.md) – AE-Währung, Belohnungshöhe im Wirtschaftskontext

## Grundregeln (alle Kategorien)

- Neutrale gehören einem eigenen Team (`NeutralPassive` für Critters, `NeutralHostile` für Lager/Türme); sie geben **keine Sicht** für Spieler und werden von der FoW normal verdeckt (sichtbar nur im Zustand "sichtbar", nie als Ghost im Zustand "erforscht" – siehe [./FogOfWar.md](./FogOfWar.md)).
- Neutrale sind nicht baubar, nicht produzierbar und nicht auswählbar (Ausnahme: eroberte Türme werden normale Spieleigentum-Objekte).
- KI-Gegner werten Objectives aus und greifen Lager situationsabhängig an (Schnittstelle zu AIArchitecture, dort zu spezifizieren).
- Alle Datensätze flach und ScriptableObject-tauglich; Felder siehe Tabellenköpfe (`id`, `name`, `biome`, `hp`, `damage`, `attackRange`, `aggroRadius`, `moveSpeed`, `sightRange`, `rewardAE`, `respawn`).

## Kategorie 1: Critters (Ambient-Fauna)

Biomspezifische Tiere gemäß D-017-Biombibliothek (10 Biome). Funktion: Lebendigkeit, Welt-Identität, leichtes "Erkunden lohnt sich"-Gefühl. Critters sind passiv oder fliehen, greifen nie an, blockieren kein Pathfinding dauerhaft (sind weich kollidierend / ausweichbar) und geben bei Tod eine optionale, geringe Belohnung.

| id | name | biome | hp | verhalten | rewardAE | respawn |
|---|---|---|---|---|---|---|
| CRI-01 | Sandläufer (Echse) | Wüste | 20 | flieht bei Annäherung | 5 | ja (120 s) |
| CRI-02 | Eishirsch | Schnee | 40 | Herde 3–6, flieht | 10 | ja (120 s) |
| CRI-03 | Glutkäfer | Vulkan | 15 | passiv, leuchtet nachts | 0 | ja (90 s) |
| CRI-04 | Säbelaffen-Trupp | Dschungel | 25 | neugierig, bleibt in Vegetation | 5 | ja (120 s) |
| CRI-05 | Moorleuchtwurm-Schwarm | Sumpf | 10 | passiv, Ambient | 0 | ja (90 s) |
| CRI-06 | Streunerratte | Verlassene Stadt | 10 | flieht | 0 | ja (90 s) |
| CRI-07 | Schrottkrähe | Industriegebiet | 10 | kreist über Schrott | 0 | ja (90 s) |
| CRI-08 | Kristallschleicher | Alien-Welt | 60 | passiv, weicht Aetherium-Ausbreitung aus | 15 | ja (180 s) |
| CRI-09 | Staubwurm (Larve) | Mond | 30 | gräbt sich bei Gefahr ein | 5 | ja (180 s) |
| CRI-10 | Staubwurm (Larve) | Mars | 30 | gräbt sich bei Gefahr ein | 5 | ja (180 s) |

Design-Regeln Critters:

- **Respawn: ja** (begründet): Critters sind reines Ambient-System ohne strategischen Wert; Nicht-Respawn würde Karten nach wenigen Minuten "tot" wirken lassen. Respawn erfolgt zeitverzögert (90–180 s) an Spawn-Punkten, nicht an Todesorten, um Farm-Camping zu vermeiden.
- Belohnungen (0–15 AE) sind bewusst trivial (≈ 1/60 bis 1/20 einer Harvester-Ladung von ~300 AE) – kein Wirtschaftsfaktor, nur Entdecker-Feedback.
- Brennbare Vegetation (D-012) kann Critters in die Flucht treiben – reines Atmo-Verhalten, keine Mechanik.
- Mond/Mars (D-017, Hazards statt Wetter): Staubwurm reagiert auf Staubstürme/Strahlungsfronten (gräbt sich ein), was Hazards indirekt sichtbar ankündigt.

## Kategorie 2: Feindliche neutrale Lager (Objectives)

Lager aus Banditen (menschlich, Schrott-Technik) oder Mutanten (bio, aetherium-verstrahlt) bewachen strategische Punkte: **Bonus-Aetherium-Felder** (kleines Nebenfeld mit eigenem Mutterkristall gemäß D-010, kein reguläres Startfeld) oder einen **Artefakt-Cache** (einmalige Belohnung). Thematik pro Biom: Banditen in Stadt/Industrie/Wüste, Mutanten in Sumpf/Alien-Welt/von Aetherium überwucherten Karten.

### Schwierigkeitsstufen

| stufe | besatzung (Richtwert) | gesamt-hp ≈ | empfohlene Spielphase | bewacht |
|---|---|---|---|---|
| Leicht | 2–3 Plänkler (Schusswaffen, schwach) | 150–250 | Minute 1–4, mit Startarmee räumbar | kleines Bonus-Aetherium-Feld oder Cache 400 AE |
| Mittel | 4–6 Einheiten + 1 leichtes Fahrzeug/Emplacement | 500–800 | ab Minute 5, braucht kleine Kampfgruppe | Bonus-Feld nahe Kartenmitte oder Cache 800 AE |
| Schwer | 6–10 Einheiten + Geschützturm + Elite-Mutant | 1.200–1.800 | ab Minute 8, braucht dedizierte Truppe | großes Bonus-Feld oder Artefakt-Cache (1.200 AE + Kartenaufdeckung) |

### Beispiel-Datensätze (Einheiten des Lagers)

| id | name | typ | hp | damage | attackRange | aggroRadius | moveSpeed | sightRange |
|---|---|---|---|---|---|---|---|---|
| NEU-B01 | Banditen-Plänkler | Infanterie | 60 | 8 | 8 m | 14 m | 4 m/s | 10 m |
| NEU-B02 | Banditen-Schrotte | Infanterie (Nah) | 90 | 14 | 3 m | 12 m | 5 m/s | 10 m |
| NEU-B03 | Schrott-Buggy | leichtes Fahrzeug | 220 | 18 | 10 m | 16 m | 9 m/s | 12 m |
| NEU-B04 | Rohr-Geschütz | stationär | 350 | 30 | 14 m | 14 m | 0 | 14 m |
| NEU-M01 | Mutanten-Kriecher | Infanterie (Nah) | 110 | 16 | 2,5 m | 12 m | 6 m/s | 9 m |
| NEU-M02 | Speier | Infanterie (Fern) | 80 | 12 | 9 m | 14 m | 4 m/s | 11 m |
| NEU-M03 | Aetherium-Brut (Elite) | schwer | 600 | 40 | 4 m | 12 m | 4,5 m/s | 10 m |

### Verhaltens- und Respawn-Regeln

- **Leash-Verhalten:** Lager-Einheiten verfolgen Angreifer maximal ~25 m vom Lagerzentrum und kehren dann zurück (schnelle Regeneration auf dem Rückweg) – verhindert Kiting-Exploits und versehentliches "Lager in die Basis ziehen".
- **Kein FoW-Vorteil:** Lager patrouillieren nur in ihrem Revier; sie scouten nicht.
- **Respawn: nein** (begründet): Einmal geräumt, bleibt das Objective geräumt. Respawning Lager würden (a) passive AE-Farm-Loops ermöglichen und die Belohnungswirtschaft unterlaufen, (b) die strategische Aussage "wer zuerst expandiert, sichert das Feld" verwässern und (c) mit der Ziel-Matchdauer von 20–35 Minuten (D-010) nur 1–2 Respawn-Zyklen erlauben – zu wenig, um als System zu tragen, genug, um zu nerven. Stattdessen: mehrere Lager pro Karte mit gestaffelter Schwierigkeit (Maps.md).
- **Belohnung Artefakt-Cache:** einmalig beim Zerstören des Cache-Objekts: AE (s. Tabelle) + bei der schweren Variante temporäre Aufdeckung eines Kartenbereichs (~30 s Sicht auf den gegnerischen Basisraum, "Artefakt-Sonde" – Schnittstelle [./FogOfWar.md](./FogOfWar.md)). Gemäß **D-029** ist die Artefakt-Sonde **nur in SP/Koop aktiv** und im PvP deaktiviert (Informations-Balance); im PvP entfällt die Aufdeckung, die AE-Belohnung bleibt unverändert.
- Bonus-Aetherium-Felder unterliegen denselben Regeln wie Hauptfelder (Mutterkristall, Nachwachsen, Überernte, Ausbreitung gemäß D-010), nur mit kleinerer Gesamtreserve (~30–50 % eines Startfelds, Richtwert).

## Kategorie 3: Capturebare Geschütztürme

Verlassene Verteidigungsanlagen früherer Konfliktparteien (narrativ: Vorkriegs-Relikte). Baukasten lehnt an die Verteidigungsplattform (D-008) an: drei Modulvarianten **MG** (Anti-Infanterie), **Flak** (Anti-Luft), **Rakete** (Anti-Fahrzeug). Türme sind fest auf Karten positioniert (Maps.md), starten unbesetzt/inaktiv und sind sichtbar als "verlassen" (eigenes Icon, kein Besitzer).

### Eroberungsmechanik

1. Voraussetzung: eine Capture-fähige Infanterie der eigenen Fraktion mit der Fähigkeit *Einnehmen* (Kanal) gemäß **D-022** und [./Infantry.md](./Infantry.md): Allianz **Engineer**, Legion **Saboteur**, Evolvierte **Tunnelgräber** (D-022 schließt die Evolvierten-Capture-Lücke; thematisch: untergräbt und besetzt). Die Regel gilt für feindliche Gebäude und neutrale Türme gleichermaßen.
2. Einheit in Reichweite (≤ 3 m) → Eroberungs-Channel **5 s**; Schaden an der Einheit bricht den Channel ab (kein Fortschritt-Erhalt).
3. Bei Erfolg wird die Einheit **verbraucht** (wird zur Turmbesatzung, klassisches C&C-Muster; einheitliche Verbrauchsregel gemäß D-022, Datenmodell in [./Infantry.md](./Infantry.md)) und der Turm wechselt in Spieleigentum: volle HP-Wiederherstellung über 10 s ("Inbetriebnahme"), danach feuerbereit.
4. Eroberte Türme benötigen **keine Energie** (eigenständige Anlagen; verhindert, dass Low-Power-Regel rückwirkend Kartenpositionen entwertet), zählen aber nicht als Verteidigungsplattform für Tech-/Doktrin-Boni.
5. Nicht rück-eroberbar solange intakt; Zerstörung ist final (Trümmer, kein Respawn) – Positionen sind damit einmalige, umkämpfte Machtpunkte.

### Datensätze

| id | name | modul | hp | damage | attackRange | sightRange | zieltypen |
|---|---|---|---|---|---|---|---|
| TUR-01 | Verlassener MG-Turm | MG | 500 | 12 (Schnellfeuer) | 12 m | 14 m | Boden, Bonus vs. Infanterie |
| TUR-02 | Verlassener Flak-Turm | Flak | 500 | 25 | 16 m | 18 m | nur Luft |
| TUR-03 | Verlassener Raketen-Turm | Rakete | 500 | 35 | 15 m | 15 m | Boden, Bonus vs. Fahrzeuge |

Design-Regeln Türme:

- Werte bewusst **unter** den baubaren Verteidigungsplattformen angesetzt (Richtwert ~70 % der Kampfkraft): Türme sind Positionsvorteil, kein Ersatz für eigenes Base-Building; Reparatur nur über Reparatur-Fähigkeiten (z. B. Repair-Drohne gemäß D-014), keine Selbstheilung.
- Platzierung und Anzahl gemäß [./Maps.md](./Maps.md): S-Karten 1, M 2, L 3 Türme; Positionen decken zentrale Engstellen oder Hochwege, nie in Reichweite einer Startbasis, symmetrisch für 1v1-Fairness.
- Neutrale Lager (Kategorie 2) können Türme **nicht** besetzen; ein Turm im Lager-Radius gehört dem Spieler-Objective, nicht dem Lager.
- **Brücken-Reparatur (D-028):** Zerstörte/beschädigte Brücken (zerstörbar gemäß D-012) sind reparierbar – über den Engineer-/Builder-/Tunnelgräber-Kanal nach der D-022-Mechanik (Kanal, Abbruch bei Schaden). Platzierung und Zustände der Brücken definiert [./Maps.md](./Maps.md).

## Gestrichen (gemäß D-016)

- **Händler und jedes Handelssystem:** kein Tausch-UI, keine Handelsrouten, keine neutrale Ökonomie. Verweis auf DecisionLog D-016, Begründung dort.

## Offene Punkte

- Critter-Belohnungen (Töten von Tieren für AE) sind bewusst minimal; falls die H1-Zielgruppe "Critter-Hunting" als unpassend empfindet, Fallback: Belohnung auf 0, rein ambient. Usability-Frage, kein Blocker – Status: offen, Evaluierung mit erstem Usability-Test.
- Konkrete Lager-Kompositionen pro Karte und Spawn-Dichte der Critters gehören in Maps.md (D-017); hier nur Systemwerte – Status: offen, Übergabe an Maps.md läuft.

*(Entschieden im Korrekturlauf Sprint 2: Artefakt-Sonde im PvP → deaktiviert, D-029; Evolvierten-Capture-Einheit → Tunnelgräber, D-022; Verbrauchsregel *Einnehmen* → 5-s-Kanal, Einheit verbraucht, D-022.)*

## Nächste Schritte

1. ~~Abgleich mit [./Infantry.md](./Infantry.md)~~ – erledigt im Korrekturlauf: Capture-Einheiten (Engineer/Saboteur/Tunnelgräber) und Verbrauchsregel sind gemäß D-022 einheitlich festgelegt; Infantry.md zieht das Datenmodell nach.
2. [./Maps.md](./Maps.md): Platzierungsregeln für Lager (Stufen-Staffelung), Türme (Anzahl/Symmetrie), Brücken (D-028) und Critter-Spawns übernehmen.
3. Schnittstelle KI: Priorisierung von Objectives für Skirmish-KI in AIArchitecture-Dokument notieren.
4. Sprint-3-Übergabe: Datenmodelle (flache SO-Records gemäß Tabellenköpfen) ins Technical Design Document aufnehmen lassen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Gameplay Designer |
| 0.2.0 | 2026-07-21 | Korrekturlauf Sprint 2 (D-020–D-030) | Lead Gameplay Designer |
