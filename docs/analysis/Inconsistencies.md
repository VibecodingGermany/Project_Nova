# Inkonsistenzen zwischen den Quelldokumenten

**Version:** 1.0.0 | **Status:** sprint-freigegeben (Sprint 0) | **Verantwortungsbereich:** Lead Gameplay Designer / Executive Producer | **Sprint:** 0

## Zweck

Vollständiges Register aller Widersprüche, Unstimmigkeiten und Mehrdeutigkeiten zwischen den drei Quelldokumenten (GDD-O = Game Design Outline, TPD = Technisches Planungsdokument, APL = Asset Pipeline). Gemäß D-003 werden Inkonsistenzen in Sprint 0 **erfasst, aber nicht aufgelöst** – die Auflösung erfolgt im benannten Owner-Sprint und wird dort dokumentiert.

## Abhängigkeiten

- [KnowledgeBase.md](KnowledgeBase.md)
- [../production/OpenQuestions.md](../production/OpenQuestions.md) – übernimmt die auflösungsbedürftigen Punkte
- [../production/DecisionLog.md](../production/DecisionLog.md) – nimmt später die Auflösungsentscheidungen auf

## Register

| ID | Schwere | Thema | Widerspruch | Quellen | Auflösung in |
|---|---|---|---|---|---|
| I-01 | hoch | Gebäudeanzahl | GDD-O nennt 11 Gebäudetypen; APL kalkuliert 18 Typen × 3 Fraktionen ≈ 54 Assets. 7 Typen sind undefiniert – betrifft Scope, Balancing und Budget. | GDD-O "Gebäude" vs. APL Paket 03 | Sprint 2 (Buildings.md) |
| I-02 | mittel | Spezialeinheiten | APL Paket 08 listet 5 Typen (Titan, Mobile Festung, Eliteheld, Experimentalfahrzeug, Superpanzer); Gesamtübersicht sagt 15. Vermutlich 5 × 3 Fraktionen, aber nicht dokumentiert. | APL Paket 08 vs. APL Gesamtumfang | Sprint 2 (Units-Dokumente) |
| I-03 | mittel | Drohnen | APL Paket 09 definiert 6 Drohnentypen; weder GDD-O noch TPD erwähnen Drohnen. Unklar: fraktionsübergreifend oder je Fraktion? Eigene Produktionskette? | APL Paket 09 vs. GDD-O/TPD | Sprint 2 |
| I-04 | mittel | Karten vs. Biome | GDD-O und APL vermischen "Karten" und "Biome". 10 Biome sind Themen, keine spielbaren Karten; APL-Gesamtumfang zählt trotzdem "Karten: 10". Kartenproduktionsprozess fehlt. | GDD-O "Karten" vs. APL Paket 01/Gesamt | Sprint 2 (Maps.md, Biomes.md) |
| I-05 | mittel | Marine | APL Paket 07 plant 6 Marinetypen (optional); TPD §14 schließt Marine aus dem MVP aus; GDD-O kennt keine Marine. Zusätzlich widersprüchlich: Karten wie Mond/Mars ohne Gewässer. | APL vs. TPD §14 vs. GDD-O | Sprint 2 (Streichkandidat) + Sprint 6 |
| I-06 | hoch | Commander | TPD §7.2 nennt "Commander" als Signature-Asset; kein Dokument definiert ein Commander-System (Rolle im Gameplay? RPG-Element? Nur Kosmetik?). | TPD §7.2 vs. GDD-O (fehlt) | Sprint 2 (CommanderSystem.md) |
| I-07 | niedrig | Neutrale Händler | APL Paket 10 listet "Händler" als neutrale Einheiten; ein Handelssystem existiert in keinem Designdokument. | APL Paket 10 vs. GDD-O | Sprint 2 (NeutralUnits.md) |
| I-08 | mittel | Aetherium-Regeneration | GDD-O: Aetherium "wächst langsam nach"; TPD §8.4 nennt gleichzeitig "Ressourcenwachstum" und "erschöpfte Felder". Die Spielregel (unendlich? endlich mit Nachwachsen? Map-Control-Druck?) ist undefiniert und strategisch zentral. | GDD-O "Ressource" vs. TPD §8.4 | Sprint 2 (Resources.md, Economy.md) |
| I-09 | niedrig | "Isometrisch" | GDD-O sagt "isometrische Kamera"; TPD §6.2 präzisiert: echte 3D-Welt mit schräger Perspektive, optionaler Rotation – also keine starre Isometrie. GDD-Formulierung in Sprint 2 präzisieren. | GDD-O vs. TPD §6.2 | Sprint 2 (CoreGameplay.md) |
| I-10 | mittel | Evolvierte-Gebäude | APL definiert biologische Entsprechungen nur für Fahrzeuge ("Evolvierte erhalten biologische Entsprechungen"). Ob Evolvierte-Gebäude organisch sind und anders funktionieren (wachsen statt bauen?), ist offen – mit großen Folgen für Art, Animation und Bau-Mechanik. | APL Paket 03/05 vs. GDD-O | Sprint 2 (Buildings.md, Factions.md) |
| I-11 | niedrig | Ranked vs. MVP | GDD-O listet "Ranked" als Spielmodus; TPD §14 schließt Ranglisten aus dem MVP aus. Kein echter Widerspruch (Phasenlogik), aber die Phasenzuordnung aller Spielmodi fehlt. | GDD-O "Spielmodi" vs. TPD §14 | Sprint 2 (MultiplayerModes.md) + Sprint 6 |
| I-12 | niedrig | Wetter-VFX vs. Karten | APL Paket 11 umfasst Wetter-Effekte; Karten wie Mond und Mars haben keine Atmosphäre bzw. kein klassisches Wetter. Wetter muss pro Biom definiert statt global angenommen werden. | APL Paket 11 vs. GDD-O Kartenliste | Sprint 2 (Biomes.md) |

## Bewertung

- **Kritisch für Sprint 2:** I-01 (Scope/Budget), I-06 (mögliches Kernfeature ohne Design), I-08 (grundlegende Wirtschaftsregel).
- Keine der Inkonsistenzen blockiert Sprint 1 (Research).
- Die Quelldokumente sind auf technischer Seite (TPD) deutlich ausgereifter als auf Design-Seite (GDD-O) – Sprint 2 hat entsprechend hohen Klärungsbedarf.

## Offene Punkte

- Alle 12 Punkte sind als Q-001 bis Q-012 in [../production/OpenQuestions.md](../production/OpenQuestions.md) übernommen.

## Nächste Schritte

- Auflösung in den benannten Sprints; dieses Register bleibt als historische Referenz bestehen, neue Inkonsistenzen ab Sprint 1 werden direkt in OpenQuestions geführt.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | 12 Inkonsistenzen aus Quellanalyse erfasst (Sprint 0) | Lead Gameplay Designer |
