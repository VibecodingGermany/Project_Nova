# Waffenkatalog (Weapons)

**Version:** 0.2.0 | **Status:** Entwurf (Korrekturlauf Sprint 2) | **Verantwortungsbereich:** Lead Gameplay Designer | **Sprint:** 2

## Zweck

Führt alle Waffensysteme der drei Fraktionen als datengetriebene Datensätze (ScriptableObject-tauglich, flache Felder): Schadensart, Treffer-Modell, Zielklassen, Reichweiten-/Feuerraten-/Schadens-Rahmen sowie die drei Superwaffen mit Fläche/Dauer/Effekt. Regelwerk (Verrechnung, Status-Effekte, Falloff) steht in [DamageSystem.md](DamageSystem.md), Konter-Multiplikatoren in [ArmorSystem.md](ArmorSystem.md). Alle Werte sind Startwerte **v0.1** zum Tunen.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-008 (Verteidigungsplattform-Module), D-014 (Drohnen), D-015 (Elite-Einheiten), D-017 (Hazards), D-026 (Konter-Lücken: Kristallmagier-AA, Sniper-Profil), D-027 (Fraktions-Sonderregeln: EMP, Ionenstrahl, Kristallsturm)
- [DamageSystem.md](DamageSystem.md) – Schadensarten, Treffer-Modelle, Falloff, Status-Effekte
- [ArmorSystem.md](ArmorSystem.md) – Schaden-gegen-Panzerung-Matrix
- [Factions.md](Factions.md), [Infantry.md](Infantry.md), [Vehicles.md](Vehicles.md), [Aircraft.md](Aircraft.md), [Buildings.md](Buildings.md) – Träger-Einheiten
- [Economy.md](Economy.md) – AE-Währung, Startressourcen 1.000 AE (Referenzrahmen für Waffenstärke vs. Kosten)
- [../analysis/KnowledgeBase.md](../analysis/KnowledgeBase.md) – TPD §8.6, APL Pakete 04–06, 09 (Einheitenlisten)

## Grundregeln

- **Eine Waffe pro Schussmuster:** Einheiten mit zwei Einsatzprofilen (z. B. Rakete gegen Luft+Boden) führen einen Waffendatensatz mit Zielklasse `Both`.
- **Zielklassen:** `Ground`, `Air`, `Both` (Trifft nur, was erreichbar ist; Panzerungs-Multiplikator regelt die Wirksamkeit).
- **Munition:** Kein Munitions-System. Einzige Ausnahme: **Bomber** kehren nach Abwurf zum Flugfeld zurück und rüsten dort nach (C&C-Genre-Erwartung, Rüstzeit Richtwert 10–15 s).
- **Kein Zufalls-To-Hit:** siehe Treffsicherheits-Grundregel in [DamageSystem.md](DamageSystem.md).
- **Rahmen statt Punktwerte:** Reichweite in abstrakten Feldern (1 Feld ≈ 1 Grid-Zelle des Simulationsrasters), Feuerrate als Abklingzeit in Sekunden, Schaden als Basisschaden pro Schuss/Salve vor Matrix.

### Globaler Rahmen (Design-Korridore)

| Profil | Reichweite | Abklingzeit | Basisschaden/Schuss | Beispiele |
|---|---|---|---|---|
| Nahkampf | 1–2 | 0.8–1.5 s | 15–30 | Mutant, Berserker |
| Infanterie-Standard | 6–8 | 0.8–1.2 s | 8–15 | Gewehre, MG |
| Infanterie-Spezial | 8–14 | 2.0–4.0 s | 25–60 | Scharfschütze, Raketenwerfer |
| Fahrzeug-Direkt | 8–10 | 2.0–3.0 s | 30–60 | Panzerkanonen |
| Artillerie/Belagerung | 18–24 (Mindestreichweite 6–8) | 5.0–8.0 s | 80–150 + Fläche | Artillerie, Mörser |
| Luftabwehr | 10–12 | 1.5–2.5 s | 20–40 | Flak, AA-Raketen |
| Verteidigungsplattform | 10–14 | je nach Modul | je nach Modul | D-008-Module |

Begründung der Korridore: Artillerie überragt Verteidigung deutlich (Belagerung muss sich lohnen), hat aber eine Mindestreichweite (Konter durch schnelle Nahdistanz); Luftabwehr-Reichweite ≥ Luft-Angriffsreichweite verhindert risikofreies Gunship-Poking.

## Allianz (High-Tech, präzise, teuer – Kinetisch/Energie)

| Waffe | Träger (Beispiel) | Schadensart | Modell | Ziel | Reichweite | Abklingzeit | Schaden-Rahmen | Besonderheit |
|---|---|---|---|---|---|---|---|---|
| Sturmgewehr | Rifleman | Kinetisch | Hitscan | Ground | 6–7 | 0.9 s | 8–12 | – |
| Schweres MG | Heavy Rifle | Kinetisch | Hitscan | Ground | 7–8 | Dauerfeuer (Burst 0.15 s) | 4–6/Kugel | Unterdrückungs-Feel, kein Status |
| Panzerabwehrrakete | Rocket Soldier | Explosiv | Missile | Both | 9–10 | 2.5 s | 40–60 | Haupt-AA der Infanterie |
| Präzisionsgewehr | Sniper | Kinetisch | Hitscan | Ground | 12–14 | 3.5 s | 60–90 | Anti-Infanterie (Matrix 1.00); 2-Schuss-Profil gegen Standard-Infanterie (D-026) |
| Sprengsatz | Commando | Explosiv | Area | Ground | 2 (anpirschen) | einmalig, Setup ~3 s | 200–300 | Anti-Gebäude, Elite-Infanterie-Profil |
| Energieklinge | Shield Trooper | Energie | Projectile (Nah) | Ground | 1–2 | 1.0 s | 20–30 | Frontline-Halter, Schild = HP-Bonus (Einheitendesign, keine Waffe) |
| Panzerkanone | Light/Battle/Heavy Tank | Kinetisch | Projectile | Ground | 8–10 | 2.0–3.0 s | 30–60 | Kaliber skaliert mit Tier |
| Artilleriegeschütz | Artillery | Explosiv | Area | Ground | 18–22 | 6.0–8.0 s | 90–130, Radius 2–3 | Streuradius 2 |
| Mehrfach-Raketenwerfer | Rocket Launcher (Fahrzeug) | Explosiv | Missile | Both | 10–12 | 3.0 s (Salve 4) | 25–35/Rakete | AA-/Panzer-Konter |
| Ionenkanone | Titan-Mech (Elite, D-015) | Energie | Hitscan | Ground | 11–12 | 3.0 s | 120–180 | Signature-Waffe, kurzer Energie-Strahl |
| Bordkanone | Gunship/Heavy Gunship | Kinetisch | Hitscan | Ground | 8–9 | Dauerfeuer | 5–8/Kugel | – |
| Luft-Luft-Rakete | Fighter | Explosiv | Missile | Air | 9–10 | 2.0 s | 30–45 | – |
| Präzisionsbombe | Bomber | Explosiv | Area | Ground | Abwurf | 10–15 s Rüstzeit | 150–250, Radius 2 | Munitionsregel (siehe Grundregeln) |

## Legion (Masse statt Klasse – Explosiv/Feuer, günstig)

| Waffe | Träger (Beispiel) | Schadensart | Modell | Ziel | Reichweite | Abklingzeit | Schaden-Rahmen | Besonderheit |
|---|---|---|---|---|---|---|---|---|
| Gewehr | Rekrut | Kinetisch | Hitscan | Ground | 6 | 1.0 s | 6–10 | billigster Trupp, schwächstes Gewehr |
| MG | MG-Schütze | Kinetisch | Hitscan | Ground | 7 | Dauerfeuer | 3–5/Kugel | – |
| Flammenwerfer | Flammenwerfer / Flame Tank | Feuer | Area (Kegel) | Ground | 3–4 (Inf) / 5–6 (Fahrzeug) | Dauerstrahl | 8–14/s + Brennen | Kegel statt Punkt; zündet Vegetation an (D-012) |
| Raketenwerfer | Raketenschütze / Rocket Launcher | Explosiv | Missile | Both | 9–11 | 2.5 s | 40–60 | Legion-Raketen: günstiger, etwas unpräziser (Streuradius 1) |
| Mörser | Mörser | Explosiv | Area | Ground | 14–18 (mind. 5) | 5.0 s | 60–90, Radius 2 | Billig-Belagerung der Legion |
| Sprengladung | Saboteur | Explosiv | Area | Ground | 2 | einmalig, Setup ~4 s | 250–350 | Anti-Gebäude/Brücken (D-012) |
| Kampfpistole | Kommando/Offizier | Kinetisch | Hitscan | Ground | 5–6 | 0.8 s | 10–15 | Offizier: Waffe zweitrangig, Aura (Einheitendesign) |
| Flammenkanone | Flame Tank | Feuer | Area (Kegel) | Ground | 5–6 | Dauerstrahl | 12–18/s + Brennen | Gebäude-Konter (Matrix 1.00) |
| Thermobarische Rakete | Heavy Tank / Artillery-Variante | Feuer | Area | Ground | 12–16 | 6.0 s | 100–140, Radius 3 + Brennen | Brücke zur Superwaffen-Fantasy |
| Bombenlast | Bomber | Explosiv | Area | Ground | Abwurf | 12–18 s Rüstzeit | 120–200, Radius 3 | größerer Radius, unpräziser als Allianz |
| Bord-MG/Raketen | Gunship | Kinetisch/Explosiv | Hitscan/Missile | Ground | 8–9 | Dauerfeuer/Salve | 5–8 bzw. 20–30 | – |

## Evolvierte (biologisch, Regeneration – Bio/Kinetisch-Nahkampf)

Evolvierte-Waffen sind Körperteile/Bio-Organe; sie folgen denselben Datensatz-Feldern. Regeneration der Träger siehe [ArmorSystem.md](ArmorSystem.md).

| Waffe | Träger (Beispiel) | Schadensart | Modell | Ziel | Reichweite | Abklingzeit | Schaden-Rahmen | Besonderheit |
|---|---|---|---|---|---|---|---|---|
| Klauen | Mutant | Kinetisch | Projectile (Nah) | Ground | 1–2 | 0.9 s | 12–20 | Schwarm-Profil (günstig, schnell) |
| Kristallsplitter | Kristallkrieger | Kinetisch | Projectile | Ground | 6–7 | 1.0 s | 9–14 | Gewehr-Äquivalent |
| Sporenwurf | Sporenwerfer | Bio | Area | Ground | 8–10 | 3.0 s | 25–40, Radius 1–2 + Verseuchung | Kontert gegnerische Evolvierte; DoT |
| Reißzähne/Klingen | Berserker | Kinetisch | Projectile (Nah) | Ground | 1–2 | 0.7 s | 20–30 | schnellerer Nahkämpfer |
| Kristallblitz | Kristallmagier | Energie | Hitscan | Both | 9–10 | 2.5 s | 35–55 + Verlangsamung | AA-Option der Evolvierten-Infanterie – Zielklasse `Both` verbindlich (D-026) |
| Wühler-Schaufeln | Tunnelgräber | Kinetisch | Projectile (Nah) | Ground | 1–2 | 1.2 s | 25–40 | Tunneln = Mobilitätsfähigkeit (Einheitendesign) |
| Alpha-Pranken | Alpha-Mutant (Elite, D-015) | Kinetisch | Area (Nah) | Ground | 2–3 | 2.0 s | 80–120, Radius 1 | Elite-Nahkampf, Flächenschlag |
| Säurespeichelt (Bio-Kanone) | Bio-Fahrzeug "Battle"-Äquivalent | Bio | Projectile | Ground | 8–10 | 2.5 s | 35–60 + Verseuchung | Panzer-Äquivalent |
| Sporen-Artillerie | Bio-Artillerie-Äquivalent | Bio | Area | Ground | 18–22 (mind. 6) | 7.0 s | 80–120, Radius 2–3 + Verseuchung | Belagerung per Bio-Granate |
| Stachel-Salve (Bio-AA) | Bio-Raketen-Äquivalent | Kinetisch | Missile (Bio-Lenkstachel) | Air | 10–12 | 2.5 s | 25–40/Stachel | Flak-Äquivalent |
| Sporen-Schwarm | Bio-Drohnen (D-014) | Bio | Area (Nah) | Ground | 3–4 | Dauer | 5–8/s + Verseuchung | Kampf-Drohnen-Äquivalent |

## Drohnen (gemäß D-014)

| Waffe/System | Träger | Schadensart | Ziel | Rahmen | Hinweis |
|---|---|---|---|---|---|
| – | Scout-Drohne (alle) | – | – | unbewaffnet | hohe Sichtweite statt Waffe |
| Reparaturstrahl | Repair-Drohne (Allianz/Legion) | Heilung | eigene Ground | ~3–5 % Max-HP/s, Reichweite 3–4 | Werte in [ArmorSystem.md](ArmorSystem.md) |
| Leichte MG/Laser | Kampf-Drohne (Allianz/Legion) | Kinetisch/Energie | Ground | Reichweite 6–7, 4–6/Schuss | schwächer als Infanterie-MG |
| Sporen-Schwarm | Bio-Drohnen (Evolvierte) | Bio | Ground | siehe Tabelle oben | Bio-Äquivalente aller drei Rollen (D-014) |

## Verteidigungsplattform-Module (gemäß D-008)

| Modul | Schadensart | Modell | Ziel | Reichweite | Abklingzeit | Schaden-Rahmen |
|---|---|---|---|---|---|---|
| MG | Kinetisch | Hitscan | Ground | 10–11 | Dauerfeuer | 5–8/Kugel |
| Flak | Kinetisch | Projectile | Air | 11–12 | 1.5 s | 25–40, kleiner Radius 1 |
| Rakete | Explosiv | Missile | Both | 12–14 | 2.5 s | 50–80 |

Evolvierte erhalten dieselben drei Module in Bio-Optik mit identischen Rahmenwerten (D-008/D-011: gleiche Gebäudetypen, asymmetrische Umsetzung liegt im Bau-/Regenerationsmodell, nicht in Verteidigungswerten).

## Superwaffen

Superwaffen schädigen **alle** Ziele im Wirkungsbereich (Friendly-Fire-Ausnahme, siehe DamageSystem.md). Ladezeit-Rahmen nach Bau der Superwaffen-Anlage: **6–8 Minuten** (Richtwert; bei Ziel-Matchdauer 20–35 min gemäß D-010 ~2–3 Einsätze pro Match – Höhepunkt, nicht Dauerwerkzeug).

| Superwaffe | Fraktion | Schadensart | Fläche | Dauer | Schaden-Rahmen | Effekt-Profil |
|---|---|---|---|---|---|---|
| Ionenstrahl | Allianz | Energie | schmale Linie (Breite ~2 Felder, Länge ~15–20 Felder, vom Spieler ziehbar/langsam rotierbar) | 5 s | 400–600 Energie-Schaden über Dauer, volle Matrix-Wirksamkeit | Präzisions-Instrument: reißt einzelne Schlüsselziele (HQ, Superwaffe, Elite) heraus; kein Status-Effekt, **keine EMP-Nebenwirkung** (D-027.3 – EMP bleibt dem Allianz-Sturmjäger vorbehalten) |
| Thermobarische Explosion | Legion | Feuer | Kreis, Radius 8–10 Felder | Sofort + Nachbrennen | 300–500 sofort (Falloff-Zonen) + Brennen 5 s | Flächen-Vernichtung: Armee-Ballungen und Basen; zündet Vegetation/Dekor großflächig an (D-012) |
| Kristallsturm | Evolvierte | Strahlung | Kreis, Radius 6–8 Felder (auf lebenden Aetherium-Feldern 9–12) | 12–15 s anhaltend (auf lebenden Feldern 18–20 s) | 30–50/s während der Dauer + Verlangsamung | Zonen-Verweigerung: kein Sofort-Kill, sondern Sperrgebiet; Aetherium-Kopplung (D-027.1): auf lebenden Feldern verstärkter Radius und längere Dauer (Werte in den Spalten) plus temporär beschleunigte Aetherium-Ausbreitung im Wirkungsbereich (D-010); **Balancing-Beobachtungspflicht** wegen der Kopplung an Resources.md/Economy.md |

Design-Logik der Asymmetrie: **Punkt** (Allianz) vs. **Fläche** (Legion) vs. **Zeit** (Evolvierte) – drei klar unterscheidbare Einsatzantworten (Schlüsselziel töten / Ballung vernichten / Raum sperren), passend zu den Fraktionsidentitäten.

## Datenmodell (SO-Felder je Waffendatensatz)

`id`, `displayName`, `faction`, `damageType` (Enum, 6 Werte), `hitModel` (Enum, 4 Werte), `targetClass` (`Ground|Air|Both`), `baseDamage`, `cooldown`, `range`, `minRange` (0 = keine), `areaRadius` (0 = Einzelziel), `spreadRadius` (0 = präzise), `statusEffect` (optional), `salvoSize`, `salvoInterval`, `requiresRearm` (bool, Bomber). Flache Struktur, keine Vererbung – TPD-§15-konform.

## Offene Punkte

- Entschieden im Korrekturlauf (D-026/D-027) und oben verankert: Kristallmagier als Evolvierte-AA-Infanterie mit Zielklasse `Both` (D-026); Sniper mit 2-Schuss-Profil (D-026); Kristallsturm-Kopplung an Aetherium mit verstärktem Radius/Dauer auf Feldern (D-027.1); Ionenstrahl ohne EMP-Nebenwirkung (D-027.3).
- **Elite-Waffen (Backlog, offen):** Ionenkanone/Alpha-Pranken sind nur für die je 1 MVP-Elite-Einheit (D-015) spezifiziert; die 2 zusätzlichen Release-Eliten pro Fraktion benötigen eigene Waffendatensätze.
- **Arbeitsnamen (offen):** "Säurespeichelt/Bio-Kanone" sind Platzhalter – die APL sieht für Evolvierte nur "biologische Entsprechungen" der 12 Fahrzeugtypen vor; finale Namensgebung erfolgt in Vehicles.md.

## Nächste Schritte

- HP-Rahmen der Einheiten (Infantry/Vehicles/Aircraft.md) gegen diese Schadens-Rahmen kalibrieren → TTK-Zielkorridore in Balancing.md.
- Abgleich mit Economy.md: Waffenstärke je Tier gegen Kosten-/Produktionszeit-Rahmen (Startressourcen 1.000 AE als Referenzpunkt).
- VFX-/Audio-Bedarf je Waffe (Mündungsblitz, Einschlag, Superwaffen-Inszenierung) als Input für Sprint 5 (APL Paket 11/12) erfassen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Gameplay Designer |
| 0.2.0 | 2026-07-21 | Korrekturlauf Sprint 2 (D-020–D-030) | Lead Gameplay Designer |
