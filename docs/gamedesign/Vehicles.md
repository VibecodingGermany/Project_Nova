# Fahrzeuge (Vehicles)

**Version:** 0.2.0 | **Status:** Entwurf (Korrekturlauf Sprint 2) | **Verantwortungsbereich:** Lead Vehicle Artist / Lead Gameplay Designer | **Sprint:** 2

## Zweck

Spezifikation aller Bodenfahrzeuge für die drei Fraktionen (Allianz, Legion, Evolvierte): 12 Fahrzeugtypen pro Fraktion gemäß Zahlengerüst, dazu Support-Drohnen (gemäß D-014) und Elite-Einheiten (gemäß D-015). Alle Werte sind Startwerte v0.2 zum Tunen – Richtwerte mit Begründung, keine Pseudo-Präzision. Ziel: rock-paper-scissors-fähiges Kontergeflecht, das die Fraktionsidentitäten (Allianz = präzise/teuer, Legion = Masse/günstig, Evolvierte = Regeneration/biologisch) spielmechanisch trägt.

## Abhängigkeiten

- [DecisionLog](../production/DecisionLog.md) – D-008 (12 Gebäudetypen), D-010 (Aetherium-Wirtschaft), D-011 (Evolvierte bauen durch Wachstum), D-014 (Drohnen), D-015 (Elite-Einheiten), D-021 (kein Pop-Limit außer Elite), D-026 (Radar-Fahrzeug, Konter-Lücken)
- [Factions](./Factions.md) – Fraktionsidentitäten, Ressourcenprofile
- [Buildings](./Buildings.md) – Produktionsgebäude (Fahrzeugfabrik, Raffinerie), Voraussetzungen
- [Aircraft](./Aircraft.md) – geteilte Schadens-/Panzerungstypen, Flak-Konter
- [ResearchTree](./ResearchTree.md) – Tier-1–3-Freischaltungen
- [Economy](./Economy.md) – Währung AE, Startressourcen 1.000 AE, Harvester-Ladung ~300 AE
- [Resources](./Resources.md) – Überernte-Regeln am Mutterkristall (D-010)
- [KnowledgeBase](../analysis/KnowledgeBase.md) – Asset-Umfang 36 Fahrzeuge (APL Paket 05)

## Datenmodell (ScriptableObject-tauglich)

Jede Einheit ist ein flacher Datensatz mit folgenden Feldern:

| Feld | Typ | Beschreibung |
|---|---|---|
| `id` | string | Eindeutige ID, z. B. `ALL_VEH_LIGHT_TANK` |
| `faction` | enum | Allianz / Legion / Evolvierte |
| `vehicleClass` | enum | Einer der 12 Typen |
| `tier` | int | 1–3 |
| `costAE` | int | Kosten in Aetherium-Einheiten |
| `buildTimeS` | float | Bauzeit in Sekunden (bei voller Energie) |
| `hp` | int | Trefferpunkte |
| `armorType` | enum | Leicht / Schwer |
| `damageType` | enum | Kinetisch / Explosiv / Flamme / Energie / Bio |
| `dps` | float | Schaden pro Sekunde (Richtwert) |
| `rangeM` | float | Schussweite in Metern |
| `speedMS` | float | Geschwindigkeit in m/s |
| `sightM` | float | Sichtweite in Metern |
| `prerequisites` | string[] | Gebäude-/Tech-Voraussetzungen |
| `abilities` | string[] | Aktive/passive Fähigkeiten |

**Schadens-Konter-Matrix (Richtwerte, Schadensmultiplikatoren):**

| Schadenstyp | vs. Leicht | vs. Schwer | vs. Gebäude | vs. Luft |
|---|---|---|---|---|
| Kinetisch | 1,0 | 0,75 | 0,5 | 0,5 |
| Explosiv | 0,75 | 1,0 | 1,25 | 0,5 |
| Flamme | 1,5 | 0,5 | 1,0 (entzündet Vegetation) | 0 |
| Energie | 1,0 | 1,25 | 1,0 | 0,75 |
| Bio | 1,25 | 0,75 | 0,75 | 0,5 |

Flak-Waffen (Verteidigungsplattform-Modul, Radar-Fahrzeug nein) besitzen dedizierte Anti-Luft-Werte; siehe [Aircraft](./Aircraft.md). Mobile Luftabwehr der Evolvierten (Konter-Lücke, D-026): Der Kristallmagier (Infanterie) erhält Zielklasse „Beides" (Boden + Luft) – Details in [Infantry](./Infantry.md).

**Fraktions-Grundregeln für Werte:**

- Allianz: ~+25 % Kosten, ~+15 % Einzelwerte (HP/DPS), Energie-Schaden dominant, längere Reichweiten.
- Legion: ~−20 % Kosten, ~−15 % Einzelwerte, kürzere Bauzeiten (Masse statt Klasse), Flamme/Explosiv dominant.
- Evolvierte: mittlere Kosten, Einheiten regenerieren HP langsam außerhalb von Kampf (~1 % HP/s nach 5 s ohne Schaden) statt Reparatur; Reparatur-Fahrzeug ersetzt durch Heil-Symbionten. Bio-Schaden dominant. Evolvierte "bauen" Fahrzeuge konventionell in der Fahrzeugfabrik – die Wachstums-Regel D-011 gilt ausschließlich für Gebäude (bestätigt im Korrekturlauf Sprint 2). Die Produktion wird optisch als Schlüpfen aus Bio-Kokons inszeniert; Kosten und Bauzeit folgen denselben Regeln wie bei den anderen Fraktionen.

## Die 12 Fahrzeugtypen – Rollen und Konter

| # | Typ | Rolle | Konter gegen | Gekontert von |
|---|---|---|---|---|
| 1 | Scout | Frühe Aufklärung, hohe Sicht | Infanterie (Überfahren), ungeschützte Harvester | Jeder Panzer, Verteidigung |
| 2 | APC | Infanterie-Transport (6 Sitze), leicht bewaffnet | Infanterie im Nahkampf | Battle Tank, Artillerie |
| 3 | Light Tank | Schneller Tier-1-Kampf, Raid | Scout, Harvester, Artillerie (Flanke) | Battle Tank, Rocket Launcher |
| 4 | Battle Tank | Rückgrat der Armee, Tier 2 | Light Tank, APC, Gebäude (mittel) | Heavy Tank, Bomber, Artillerie |
| 5 | Heavy Tank | Durchbruch, langsamer Anker | Battle Tank, Verteidigung (Frontal) | Artillerie, Bomber, Flame Tank (Nähe) |
| 6 | Artillery | Indirektes Feuer, große Reichweite, Mindestreichweite | Gebäude, Verteidigung, statische Verbände | Alles in Nahdistanz, Scout-Raid |
| 7 | Rocket Launcher | Flächen-Salven vs. Fahrzeuggruppen + Luft (leicht) | Massierte leichte Einheiten | Battle Tank (Nahdistanz), Fighter |
| 8 | Flame Tank | Nahkampf, entzündet Vegetation/Dekor (D-012), Gebäude-Killer | Infanterie, Gebäude, Bunkerstellungen | Alles auf Distanz, Heavy Tank |
| 9 | Repair Vehicle | Feldreparatur (Evolvierte: Heilung) | – | Alles, unbewaffnet |
| 10 | Radar Vehicle | Mobiles Radar (erweiterte Sicht/Fog-Aufklärung) + Detektor (enttarnt getarnte Einheiten); Feuerleitungs-Verbandsmechanik gestrichen (D-026) | – (Support) | Alles, unbewaffnet |
| 11 | Harvester | Aetherium-Abbau, Ladung ~300 AE | – | Alles, bevorzugtes Raid-Ziel |
| 12 | Builder | Errichtet Gebäude (Allianz/Legion) bzw. pflanzt Keime (Evolvierte, D-011), langsam, teuer | – | Alles, priorisiertes Ziel |

**Begründung Harvester-Wert ~300 AE/Ladung:** Bei Standardstart 1.000 AE (Zahlengerüst) ermöglicht ein Harvester-Trip alle ~60–75 s einen weiteren Light Tank bzw. halben Battle Tank – passt zur Ziel-Matchdauer 20–35 min (D-010) und macht Harvester-Raids zum wirksamen, aber nicht sofort entscheidenden Druckmittel. Überernte-Details (dauerhafter Schaden am Mutterkristall, D-010) werden nicht hier, sondern in [Resources](./Resources.md) und [Economy](./Economy.md) geregelt; die Harvester-Fähigkeit „Überernte-Warnung" ist nur der UI-Hinweis darauf.

## Allianz (Azurblau/Stahlgrau – High-Tech, präzise, teuer)

| Typ | Name | Tier | Kosten (AE) | Bauzeit (s) | HP | Panzerung | Schaden | DPS | Reichweite (m) | Tempo (m/s) | Fähigkeiten | Voraussetzungen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Scout | Jackal-Aufklärer | 1 | 300 | 12 | 220 | Leicht | Kinetisch | 15 | 25 | 9 | Zielmarkierung (+10 % Trefferchance Verband, 8 s) | Fahrzeugfabrik |
| APC | Guardian-Transporter | 1 | 500 | 18 | 450 | Leicht | Kinetisch | 20 | 22 | 7 | 6 Transportsitze, Schnell-Entladung | Fahrzeugfabrik |
| Light Tank | Lynx | 1 | 600 | 20 | 550 | Leicht | Energie | 35 | 30 | 7 | – | Fahrzeugfabrik |
| Battle Tank | Aegis | 2 | 900 | 28 | 1.100 | Schwer | Energie | 60 | 32 | 5,5 | Präzisionsmodus (stationär: +25 % Reichweite/Schaden) | + Forschungslabor |
| Heavy Tank | Juggernaut | 3 | 1.400 | 40 | 2.000 | Schwer | Energie | 90 | 34 | 4 | Frontschild (−30 % Schaden frontal) | + Tech Tier 3 |
| Artillery | Longbow | 2 | 1.000 | 32 | 350 | Leicht | Explosiv | 70 | 80 (min. 20) | 4,5 | – | + Forschungslabor |
| Rocket Launcher | Tempest MRLS | 2 | 900 | 30 | 400 | Leicht | Explosiv | 55 (Fläche) | 55 | 5 | Salve vs. Luft möglich (reduziert) | + Forschungslabor |
| Flame Tank | Plasma-Ätzstrahler „Kauter" | 2 | 850 | 28 | 800 | Schwer | Flamme (Plasma) | 65 | 14 | 5 | Entzündet Vegetation/Gebäude (DoT) | + Forschungslabor |
| Repair Vehicle | Feldschmiede "Aeskulap" | 1 | 600 | 22 | 400 | Leicht | – | – | – | 6 | Repariert 40 HP/s (ein Ziel) | Fahrzeugfabrik |
| Radar Vehicle | Argus | 2 | 700 | 25 | 350 | Leicht | – | – | – | 5,5 | Sicht 90 m, Detektor (enttarnt Getarntes, 40 m) | + Radar |
| Harvester | Sammler "Demeter" | 1 | 700 | 25 | 800 | Schwer | – | – | – | 5 | Ladung 300 AE, Überernte-Warnung (D-010) | Raffinerie |
| Builder | Pionier "Atlas" | 1 | 800 | 30 | 350 | Leicht | – | – | – | 5 | Errichtet alle 12 Gebäudetypen | HQ |

## Legion (Rostrot/Ocker – Masse statt Klasse, günstig)

| Typ | Name | Tier | Kosten (AE) | Bauzeit (s) | HP | Panzerung | Schaden | DPS | Reichweite (m) | Tempo (m/s) | Fähigkeiten | Voraussetzungen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Scout | Hyäne (Buggy) | 1 | 220 | 9 | 180 | Leicht | Kinetisch | 12 | 22 | 9,5 | Molotov-Wurf (kleiner Flächen-DoT) | Fahrzeugfabrik |
| APC | Rammbock | 1 | 400 | 14 | 550 | Leicht | Kinetisch | 15 | 20 | 6,5 | 6 Sitze, Ramme (Schaden beim Aufprall) | Fahrzeugfabrik |
| Light Tank | Räuber | 1 | 450 | 15 | 480 | Leicht | Kinetisch | 28 | 26 | 7 | – | Fahrzeugfabrik |
| Battle Tank | Koloss | 2 | 700 | 22 | 1.250 | Schwer | Explosiv | 50 | 28 | 5 | – | + Forschungslabor |
| Heavy Tank | Behemoth | 3 | 1.100 | 32 | 2.300 | Schwer | Explosiv | 75 | 30 | 3,5 | Doppelrohr-Salve (alle 20 s, Burst) | + Tech Tier 3 |
| Artillery | Donnerkanone | 2 | 800 | 26 | 320 | Leicht | Explosiv | 60 | 85 (min. 22) | 4 | Streufeuer (größere Fläche, weniger Präzision) | + Forschungslabor |
| Rocket Launcher | Hagelsturm | 2 | 700 | 24 | 380 | Leicht | Explosiv | 70 (Fläche) | 50 | 5 | Volle Salve (Nachladezeit 12 s) | + Forschungslabor |
| Flame Tank | Inferno | 2 | 650 | 20 | 950 | Schwer | Flamme | 85 | 12 | 5 | Doppelflakonstrahl, entzündet Vegetation/Gebäude | + Forschungslabor |
| Repair Vehicle | Flickschuster | 1 | 450 | 16 | 380 | Leicht | – | – | – | 6 | Repariert 30 HP/s (Fläche, mehrere Ziele) | Fahrzeugfabrik |
| Radar Vehicle | Lauscher | 2 | 550 | 20 | 320 | Leicht | – | – | – | 5,5 | Sicht 85 m, Detektor (40 m), Störsender (Feind-Radar −20 % Reichweite, 15 s) | + Radar |
| Harvester | Schürfer | 1 | 550 | 20 | 750 | Schwer | – | – | – | 5 | Ladung 300 AE | Raffinerie |
| Builder | Vorarbeiter | 1 | 650 | 24 | 320 | Leicht | – | – | – | 5 | Errichtet alle 12 Gebäudetypen | HQ |

## Evolvierte (Violett/Bio-Grün – biologisch, Regeneration)

Alle Evolvierten-Fahrzeuge sind lebende Organismen/Kristallsymbiose: Regeneration ~1 % HP/s nach 5 s kampffrei (statt Reparatur). Namen sind Arbeitsnamen für den biologischen Look.

| Typ | Name | Tier | Kosten (AE) | Bauzeit (s) | HP | Panzerung | Schaden | DPS | Reichweite (m) | Tempo (m/s) | Fähigkeiten | Voraussetzungen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Scout | Flinkläufer | 1 | 260 | 11 | 200 | Leicht | Bio | 14 | 24 | 9 | Tarnt sich in Aetherium-Feldern (stehend) | Fahrzeugfabrik |
| APC | Brutträger | 1 | 450 | 16 | 500 | Leicht | Bio | 18 | 20 | 6,5 | 6 Sitze; heilt Insassen 2 % HP/s | Fahrzeugfabrik |
| Light Tank | Stachelreiter | 1 | 520 | 17 | 520 | Leicht | Bio | 32 | 28 | 7 | Stachelhagel (kleiner Flächenschaden) | Fahrzeugfabrik |
| Battle Tank | Panzerbestie | 2 | 800 | 25 | 1.150 | Schwer | Bio | 55 | 30 | 5 | Kristallpanzer (+20 % Panzerung bei vollem HP) | + Forschungslabor |
| Heavy Tank | Urtier | 3 | 1.250 | 36 | 2.100 | Schwer | Bio | 85 | 32 | 4 | Berserker (+30 % DPS unter 30 % HP) | + Tech Tier 3 |
| Artillery | Säurespeier | 2 | 900 | 28 | 330 | Leicht | Bio (Säure) | 65 | 82 (min. 20) | 4,5 | Säurepfütze (DoT-Zone, verweigert Gelände) | + Forschungslabor |
| Rocket Launcher | Sporenwerfer | 2 | 800 | 27 | 390 | Leicht | Explosiv (Sporen) | 60 (Fläche) | 52 | 5 | Sporenwolke verlangsamt Gegner 20 % | + Forschungslabor |
| Flame Tank | Bio-Plasma-Käfer | 2 | 750 | 24 | 880 | Schwer | Flamme (Bio-Plasma) | 75 | 13 | 5 | Entzündet Vegetation/Gebäude (DoT) | + Forschungslabor |
| Repair Vehicle | Symbiont | 1 | 520 | 18 | 420 | Leicht | – | – | – | 6 | Heilt 35 HP/s; verdoppelt Regeneration des Ziels | Fahrzeugfabrik |
| Radar Vehicle | Sensorpolyp | 2 | 620 | 22 | 340 | Leicht | – | – | – | 5,5 | Sicht 88 m; spürt getarnte Einheiten auf (40 m) | + Radar |
| Harvester | Schlürfer | 1 | 620 | 22 | 780 | Schwer | – | – | – | 5 | Ladung 300 AE; +10 % Abbau in Aetherium-Nähe | Raffinerie |
| Builder | Keimweber | 1 | 720 | 26 | 340 | Leicht | – | – | – | 5 | Pflanzt Gebäude-Keime (D-011); Keim reift schneller in Aetherium-Nähe | HQ |

## Drohnen (gemäß D-014)

Produktion in bestehenden Fabriken (Fahrzeugfabrik; keine neue Gebäudeanforderung). Drohnen sind günstig, fragil, schweben bodennah (kein Luft-Layer, kein Flak-Konter). Pro Fraktion 3 Typen. Kein hartes Stückzahl-Limit – die Begrenzung erfolgt über Kosten und Fragilität (D-014-Klarstellung, Korrekturlauf Sprint 2):

| Fraktion | Scout-Drohne | Repair-Drohne | Kampf-Drohne |
|---|---|---|---|
| Allianz | "Spähkugel" – 150 AE, 8 s, 120 HP, Sicht 60 m, Tarnung | "Nadel" – 200 AE, 10 s, 100 HP, repariert 15 HP/s | "Hornet" – 250 AE, 12 s, 150 HP, Energie 12 DPS |
| Legion | "Motte" – 120 AE, 6 s, 100 HP, Sicht 55 m | "Schrauber" – 160 AE, 8 s, 90 HP, repariert 12 HP/s (Fläche) | "Wespe" – 200 AE, 10 s, 130 HP, Kinetisch 10 DPS |
| Evolvierte (Bio) | "Sporenauge" – 140 AE, 7 s, 110 HP, Sicht 58 m, tarnt in Feldern | "Heilpolyp" – 180 AE, 9 s, 95 HP, heilt 14 HP/s + Regen-Boost | "Stachelschwarm" – 220 AE, 11 s, 140 HP, Bio 11 DPS |

**Begründung:** Drohnen glätten die Frühspiel-Aufklärung (H1-Zielgruppe, Solo/Skirmish), ohne den Fahrzeug-Mix zu verwässern; ihre niedrigen HP machen sie zu Wegwerf-Werkzeugen, nicht zu Kampfeinheiten.

## Elite-Einheiten (gemäß D-015)

MVP/Alpha: 1 Elite pro Fraktion, Tier 3, **hartes Limit 1 gleichzeitig**; ab Release: 3 Elites pro Fraktion, hartes Limit 2 gleichzeitig (D-015). Das Elite-Limit ist das einzige harte Stückzahl-Limit im Spiel (D-021: kein sonstiges Pop-/Supply-Limit). Kosten-Richtwert 2.500–3.500 AE, Bauzeit 60–90 s – als spätes Machtwort, nicht als früher Rush. Elites zählen als Signature-Assets (TPD §7.2, eigene Entwicklung).

| Fraktion | Elite | Kosten (AE) | Bauzeit (s) | HP | Panzerung | DPS | Reichweite (m) | Tempo (m/s) | Fähigkeiten | Voraussetzungen |
|---|---|---|---|---|---|---|---|---|---|---|
| Allianz | Titan-Mech | 3.200 | 80 | 6.000 | Schwer | 220 (Energie, Zwillingsgeschütze) | 38 | 4 | Schildkuppel (10 s, absorbiert 1.500 Schaden, CD 45 s); Bodentrampeln (Flächen-Stun) | Fahrzeugfabrik + Forschungslabor + Tier 3 |
| Legion | Mobile Festung | 2.800 | 75 | 8.000 | Schwer | 160 (Vierfach-Mörser, Explosiv-Fläche) | 45 | 3 | Belagerungsmodus (stationär: +50 % Reichweite); 4 Infanterie-Schützenstände | Fahrzeugfabrik + Forschungslabor + Tier 3 |
| Evolvierte | Alpha-Mutant | 3.000 | 70 | 7.000 | Schwer | 200 (Bio, Prankenhiebe Nahkampf + Säurespeichel 20 m) | 20 | 4,5 | Verschlingen (tötet Fahrzeug <500 HP sofort, heilt 500 HP); Panik-Schrei (Feinde fliehen 4 s, CD 60 s) | Fahrzeugfabrik + Forschungslabor + Tier 3 |

**Konter-Regel:** Elites verlieren gegen konzentriertes Tier-2/3-Feuer (Artillerie-Fokus, Bomber-Staffeln, Superwaffe) – sie sind Tempo-Druck, keine "Ich-gewinne"-Taste. Limit 1 verhindert Stapelung; der Verlust ist spürbar teuer (Rebuild-Zeit ~1,5 min).

## Offene Punkte

Derzeit keine unentschiedenen Punkte. Stand nach Korrekturlauf Sprint 2:

- Flame-Tank-Tonalität: **entschieden** (Game Director, Korrekturlauf Sprint 2) – fraktionsspezifische Namen: Allianz „Plasma-Ätzstrahler", Evolvierte „Bio-Plasma-Käfer"; der Typ bleibt regelmechanisch einer der 12 Typen.
- Evolvierte-Fahrzeugproduktion: **entschieden** – konventionelle Fabrikproduktion mit Bio-Optik (Schlüpfen); D-011 (Wachstum) gilt nur für Gebäude.
- Drohnen-Stückzahl: **entschieden (D-014-Klarstellung)** – 3 Typen pro Fraktion, kein hartes Limit, Begrenzung über Kosten/Fragilität.
- Radar-Fahrzeug-Feuerleitung: **entschieden (D-026)** – Verbandsmechanik gestrichen; Radar-Fahrzeug = mobiler Radar + Detektor.
- Harvester-Überernte: **keine eigenen Regeln hier** – Details in [Resources](./Resources.md) und [Economy](./Economy.md) (D-010).

## Nächste Schritte

1. Review durch Game Director und Lead Systems Design (Konter-Matrix, Kostenkurve).
2. Werte-Export als ScriptableObject-Datensätze (Unity 6.3, flache Struktur oben) für das Balancing-Tool.
3. Abstimmung mit [Economy](./Economy.md): Harvester-Zykluszeiten gegen Ziel-Matchdauer 20–35 min simulieren.
4. Abstimmung mit [Aircraft](./Aircraft.md): gemeinsame Schadens-/Panzerungstypen finalisieren.
5. Erste Playtest-Iteration (Skirmish 1v1 vs. KI, D-018) mit Allianz vs. Legion zur Kalibrierung der ±20 %-Kostenkurve.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Vehicle Artist / Lead Gameplay Designer |
| 0.2.0 | 2026-07-21 | Korrekturlauf Sprint 2 (D-020–D-030) | Lead Vehicle Artist / Lead Gameplay Designer |
