# RTS-Markt & Wettbewerbsanalyse (2020–2026)

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Game Director | **Sprint:** 1

## Zweck

Markt- und Wettbewerbsanalyse des Echtzeitstrategie-Genres ca. 2020–2026 als Entscheidungsgrundlage für Project Nova. Das Dokument bewertet relevante Wettbewerbstitel (Rezeption, Spielerzahlen, Geschäftsmodelle), typische Erfolgs- und Scheiternsursachen und leitet daraus ab: (1) eine realistische Scope-Kalibrierung für Project Nova, (2) eine Bewertung der USP-Kandidaten (dynamische nachwachsende Kristallfelder, zerstörbare Umgebung, 3 asymmetrische Fraktionen), (3) Zielgruppen-Hypothesen als Input für Sprint 2. Kein Implementierungsdokument – rein analytisch.

## Abhängigkeiten

- [../analysis/KnowledgeBase.md](../analysis/KnowledgeBase.md) – gemeinsamer Faktenraum (Spielkonzept, Stack, MVP-Abgrenzung)
- [../production/OpenQuestions.md](../production/OpenQuestions.md) – insb. Q-005 (Aetherium-Wirtschaftsregel), Q-011 (Spielmodi-Phasierung), Q-013 (Simulations-/MP-Modell)
- Quelldokumente im Projektroot: `RTS_Game_Design_Outline.md`, `RTS_Technisches_Planungsdokument.md`

## 1. Marktlage 2020–2026: Genre im Nischen-Revival

Das RTS-Genre ist kein Massenmarkt mehr, aber seit ca. 2023–2025 in einem deutlich sichtbaren Revival: Mehrere kleinere und mittlere Titel (u. a. *Tempest Rising*, *Broken Arrow*, *Beyond All Reason*, diverse C&C-inspirierte Indies) erreichen beachtliche Aufmerksamkeit, während der vielbeschworene "AAA-Nachfolger" (*Stormgate*) spektakulär scheiterte. Gleichzeitig halten Legacy-Titel (*Age of Empires IV/II DE*, *StarCraft II*) stabile Kern-Communities. Der Markt ist damit **segmentiert und überlebensfähig, aber nicht wachstumsstark** – ein Realitätscheck für die Scope-Planung von Project Nova.

## 2. Referenztitel im Vergleich

Zahlen sind Stand Juli 2026 (abgerufen 2026-07-21), primär Steam-/SteamDB-/Steam-Charts-Daten; Publisher-interne Zahlen (Game Pass, Battle.net) sind nicht öffentlich und als solche gekennzeichnet.

| Titel | Release | Studio/Größe | Modell | Rezeption | Spielerzahlen (bekannt) |
|---|---|---|---|---|---|
| StarCraft II | 2010 (Legacy-Benchmark) | Blizzard (AAA) | F2P-Kern + bezahlte Kampagnen/Co-op-Commander | Kanonischer Genre-Referenzpunkt; Esports-Katalog weiterhin aktiv (EWC 2025, $700k Preispool) | Keine offiziellen Zahlen; Drittschätzungen stark schwankend (~70k+ täglich, unverlässlich); Esports-Peak-Viewership 2025 ~80k |
| Age of Empires IV | 2021 | Relic/World's Edge (AAA, Microsoft) | Premium ($) + Game Pass + DLCs/Expansions | Sehr positiv, langfristig gepflegt; Franchise meldete 60 Mio. Spieler kumuliert (2025, alle Titel) | Launch-Peak ~74k concurrent; 2026 stabil ~10k avg / ~20k Peak (Steam, Game Pass zusätzlich) |
| Company of Heroes 3 | 2023 | Relic/Sega (AA/AAA) | Premium + DLC | "Mixed" (57 % positiv, ~22k Reviews); Kritik an Kampagne, UI, fehlendem Polish | Launch-Peak ~30k; 2026 nur noch ~2,5k concurrent |
| Stormgate | 2024 (Early Access) | Frost Giant (~$40 Mio. Funding, Ex-Blizzard) | Free-to-Play + Server-basierter MP | Durchwachsen; Art-Stil und unfertiger Launch kritisiert; mehrfache Reworks | All-time-Peak ~4.9k concurrent; 2025 meist <150 concurrent; April 2026: Online-MP wird abgeschaltet (Server-Partner gekauft), nur noch Offline-Patch |
| Tempest Rising | 2025 | Slipgate Ironworks/3D Realms (AA) | Premium ($39,99) + DLC | Sehr positiv (~87 % bei ~11,6k Reviews); als würdiger C&C-Erbe gelobt | Gamalytic-Schätzung: solide Verkäufe; ~300–400 tägliche concurrent (langfristige Singleplayer-Käufe, kein MP-getriebenes Spiel) |
| Beyond All Reason | laufend (Open Source) | Community-Projekt (Recoil/Spring-Engine) | Kostenlos, Open Source, keine Monetarisierung | Sehr positive Community-Rezeption | 2025: >15k täglich aktive Spieler (Eigenangabe), Wachstum seit 2025 verdoppelt; 100-Spieler-Matches, 10k-Einheiten-Schlachten |
| Zero-K | 2018 (Steam) / älter | Community (Spring-Engine) | Kostenlos, Open Source | Kultstatus in der TA/SupCom-Nische | Kleine, aber langlebige Community (hunderte concurrent, unverlässliche öffentliche Zahlen) |

Quellen:
- AoE IV: [Steam Charts AoE IV](https://steamcharts.com/app/1466860), [KitGuru Launch-Peak](https://www.kitguru.net/gaming/matthew-wilson/age-of-empires-4-launches-to-74000-concurrent-players-on-steam-alone/), [Age-Franchise 60 Mio. Spieler](https://devtrackers.gg/aoe/p/99eee32f-what-s-coming-in-2025-for-age-of-empires-and-age-of-mythology)
- CoH 3: [SteamDB CoH 3](https://steamdb.info/app/1677280/charts/), [Steam Charts CoH 3](https://steamcharts.com/app/1677280), [Metacritic CoH 3](https://www.metacritic.com/game/company-of-heroes-3/)
- Stormgate: [SteamDB Stormgate](https://steamdb.info/app/2012510/charts/), [PCGamer: MP-Abschaltung](https://www.pcgamer.com/games/rts/stormgate-the-starcraft-like-rts-that-launched-last-summer-is-losing-online-multiplayer-support-because-its-server-partner-was-bought-by-an-ai-company/), [Esports Insider: Stormgate-Analyse](https://esportsinsider.com/what-happened-to-stormgate), [MassivelyOP](https://massivelyop.com/2025/07/23/multiplayer-rts-stormgate-will-leave-early-access-without-achieving-1-0-or-finishing-core-game-modes/)
- Tempest Rising: [Steam-Store](https://store.steampowered.com/app/1486920/Tempest_Rising/), [Gamalytic-Schätzung](https://gamalytic.com/game/1486920), [Metacritic](https://www.metacritic.com/game/tempest-rising/)
- Beyond All Reason: [GamingOnLinux: Spielerwachstum](https://www.gamingonlinux.com/2025/05/beyond-all-reason-a-free-and-open-source-rts-gets-a-big-visual-overhaul/), [Notebookcheck: Recoil-Engine](https://www.notebookcheck.net/Open-source-RTS-Beyond-All-Reason-showcases-large-scale-engine-update-as-player-interest-climbs.1014152.0.html)
- StarCraft II: [Esports Charts SC2](https://escharts.com/games/sc2), [Liquipedia EWC 2025](https://liquipedia.net/starcraft2/Esports_World_Cup/2025), Drittschätzung [Thunderpick](https://thunderpick.io/blog/starcraft-2-player-count) (unverlässlich, als Einschätzung gewertet)

## 3. Erfolgsmuster

1. **Singleplayer-/Content-first zahlt sich aus.** *Tempest Rising* (2 Kampagnen, Premium-Preis, ~87 % positiv) und *Age of Empires IV* (Kampagnen + lange DLC-Pflege) zeigen: Käufe und Langzeitbewertungen kommen aus PvE-Inhalten, nicht aus dem Ladder-Betrieb. *Tempest Rising* funktioniert kommerziell mit nur wenigen hundert dauerhaften Concurrents, weil Premium-Käufe nicht von einer MP-Kritischen-Masse abhängen.
2. **Nische treue Community > Massenmarkt-Anspruch.** *Beyond All Reason* wächst organisch (>15k täglich, ohne Budget) über extreme Skalierung (100 Spieler, 10k Einheiten) und radikale Transparenz (Open Source). *Zero-K* überlebt seit über einem Jahrzehnt in derselben Nische. Erkenntnis: Eine klar bediente Sub-Nische trägt ein RTS dauerhaft.
3. **Polish und Lesbarkeit schlagen Feature-Breite.** CoH 3 wurde trotz starker Marke und AAA-Budget für fehlenden Polish abgestraft; Tempest Rising wurde für das Gegenteil gefeiert – ein konsequent klassischer, sauber umgesetzter Kernloop mit klarer Fraktionslesbarkeit.
4. **Premium-Modell mit DLC-Longtail ist für Nicht-AAA der robusteste Pfad.** F2P-RTS braucht dauerhafte MP-Population und Live-Betrieb (Server, Matchmaking, Balance) – beides ist für Kleinstudios existenzgefährdend (siehe Stormgate).

## 4. Scheiternsursachen (mit projektbezogener Warnung)

1. **F2P + Server-MP als Kernversprechen (Stormgate).** ~$40 Mio. Funding, Ex-Blizzard-Pedigree – trotzdem Peak <5k concurrent und 2026 Abschaltung des Online-MP, weil ein Server-Partner verkauft wurde. Lektion: Ein RTS, dessen Existenz an dauerhafter MP-Population und fremder Server-Infrastruktur hängt, ist fragil. **Direkt relevant für Q-013** und für Project Novas Langfristziel "autoritativer Server".
2. **Unfertiger Launch verbrät die einzige Aufmerksamkeitswelle.** Stormgate startete Early Access mit kritisiertem Art-Stil und unfertiger Kampagne; die erste Welle Spieler kam, sah und blieb nicht. CoH 3 zeigt dasselbe Muster auf AA/AAA-Ebene.
3. **Feature-Breite statt Kernloop-Tiefe.** Die meisten gescheiterten RTS der Dekade (Einschätzung auf Basis der Rezeptionsmuster) versprachen "mehr von allem" (mehr Fraktionen, Modi, Systeme) und lieferten keinen einzigen herausragend polierten Kernloop.
4. **Fehlende Differenzierung zum Legacy-Angebot.** Wer "StarCraft, aber schlechter" oder "C&C, aber generisch" liefert, konkurriert mit kostenlos bzw. sehr günstig verfügbaren, polierten Klassikern (SC2 F2P, C&C Remastered, AoE II DE).

## 5. Scope-Kalibrierung für Project Nova

Aus den Marktdaten abgeleitete Obergrenzen und Untergrenzen:

- **Kein F2P, kein MP-zentriertes Geschäftsmodell.** Empfehlung: Premium (~$25–40) auf Steam, Windows/macOS. MP ist Feature-Roadmap, nicht Geschäftsmodell-Fundament. Das deckt sich mit der TPD-Reihenfolge (MP erst nach stabilem SP-Kern).
- **MVP-Disziplin bestätigen und verschärfen.** Die erfolgreichen Vergleichstitel gewinnen mit einem polierten Kernloop, nicht mit Breite. Project Novas MVP (1 Fraktion, 1 Karte, 1 Ressource, einfache KI, Sieg/Niederlage) ist marktseitig die richtige Kalibrierung; jede Ausweitung vor Kernloop-Validierung ist gegen die Marktevidenz.
- **Einheitenanzahl als Produktversprechen relativieren.** 100–500+ Einheiten bei 60 FPS ist technisch sinnvoll, aber kein verkaufsfähiger USP – *Beyond All Reason* bietet kostenlos 10k-Einheiten-Schlachten. Skalierung ist Hygienefaktor, nicht Differenzierung.
- **Referenzrahmen für Erfolg:** Realistisches Erfolgsszenario ist die *Tempest-Rising*-Größenordnung (zehntausende Premium-Verkäufe, >85 % Reviews, langlebiger Singleplayer-Longtail), nicht AoE-/SC2-Größenordnungen.

## 6. Bewertung der USP-Kandidaten

### 6.1 Dynamische, nachwachsende Kristallfelder (Aetherium)

- **Marktbeleg:** *Tempest Rising* nutzt exakt diesen Haken (nachwachsende "Tempest"-Felder, die die Karte verändern) und wurde dafür als frische Variante der Tiberium-Formel gelobt. Der Mechanismus ist am Markt **bewiesen attraktiv** und dennoch nicht ausgereizt.
- **Differenzierungsgrad:** Mittel bis hoch – bekanntes Prinzip, aber Raum für eigene Ausprägung (Nachwachsen + Umweltveränderung + Radioaktivität als Spielmechanik).
- **Risiken:** Designregel noch offen (Q-005: endlich vs. nachwachsend vs. Hybrid); Auswirkung auf Match-Dauer und Map-Control muss balancierbar bleiben.
- **Urteil:** **Stärkster USP-Kandidat** – trägt bereits im MVP (1 Ressource) und ist datengetrieben (ScriptableObjects für Wachstumsraten, Feldzustände) gut abbildbar.

### 6.2 Vollständig zerstörbare Umgebung

- **Marktbeleg:** *Company of Heroes* (Zerstörung taktisch relevant) und *Beyond All Reason*/*Zero-K* (Terraforming) zeigen, dass Umgebungsinteraktion geschätzt wird – aber kein erfolgreicher aktueller Titel stellt "vollständige Zerstörbarkeit" ins Zentrum. Die CoH-3-Rezeption zeigt zugleich: Zerstörung allein rettet kein Spiel ohne Polish.
- **Differenzierungsgrad:** Hoch als Versprechen, aber technisch teuer (Physik, Netcode-Sync, Pathfinding-Invalidierung bei dynamischen Hindernissen – direkter Konfliktpunkt mit Q-014).
- **Risiken:** Konflikt mit dem 60-FPS-Ziel bei 100–500+ Einheiten; bei späterem MP (Q-013) ist synchronisierte Zerstörung ein Determinismus-/Bandwidth-Risiko.
- **Urteil:** **Zweitrangig – als MVP-USP streichen, als Post-MVP-Differenzierer parken.** Im MVP: begrenzte, skriptbare Zerstörung (z. B. durch Superwaffen/Aetherium-Effekte) statt generischer Vollzerstörbarkeit.

### 6.3 Drei asymmetrische Fraktionen

- **Marktbeleg:** Drei asymmetrische Fraktionen sind der Genre-Standard-Erwartungswert (SC2, Tempest Rising) – **kein USP, sondern Hygienefaktor**. Asymmetrie-Qualität (wirklich unterschiedliche Wirtschafts-/Kampflogik, nicht nur reskinnte Stats) ist der eigentliche Differenzierer.
- **Differenzierungsgrad:** Niedrig als Behauptung, potenziell hoch als Ausführung (Evolvierte mit Wachsen-statt-Bauen, Q-009, wäre echter Mechanik-Unterschied).
- **Risiken:** Balancing-Aufwand wächst überproportional; drei Fraktionen sind der klassische Scope-Killer für Kleinstudios.
- **Urteil:** **Kein Marketing-USP.** MVP bleibt bei 1 Fraktion; Asymmetrie-Tiefe der Evolvierten (Q-009) ist der einzige fraktionsbezogene Differenzierer und gehört in Phase 2/3, nicht in den MVP.

### 6.4 USP-Gesamtempfehlung

Kommunizierbarer Kern-USP für Project Nova: **"Eine lebendige Ressource, die die Karte zurückeroiert"** – Aetherium-Felder, die nachwachsen, die Umgebung verändern und Map-Control zu einem dynamischen Wettlauf machen. Das ist am Markt belegt (Tempest Rising), im MVP abbildbar, datengetrieben implementierbar und deckt sich mit der Vision aus dem GDD-O.

## 7. Zielgruppen-Hypothesen (Input für Sprint 2)

| Segment | Profil | Evidenz | Ansprache für Project Nova |
|---|---|---|---|
| **H1: C&C-Nostalgiker (Kernzielgruppe)** | 30–50, klassischer Base-Builder, Solo + Skirmish vs. KI, kaufen Premium auf Steam | Tempest Rising (87 % positiv, Premium, Kampagnen-getrieben) | Kernloop-Polish, klare Silhouetten, klassische Ressourcenökonomie mit Aetherium-Twist |
| **H2: Legacy-RTS-Ladder-Spieler** | kompetitiv, SC2/AoE-Hintergrund, 1v1-Fokus, hohe Skill-Erwartung | SC2-Esports weiterhin aktiv (EWC 2025); AoE IV ~10k dauerhafte concurrent | Erst relevant ab stabilem MP (Phase 3); nicht für MVP priorisieren – Stormgate zeigt, dass dieses Segment gnadenlos bewertet |
| **H3: Skalierungs-/Sandbox-Enthusiasten** | TA/SupCom-Tradition, riesige Schlachten, Modding-affin | BAR >15k täglich, Zero-K-Langlebigkeit | 100–500+ Einheiten und spätere Modding-/Workshop-Option (TPD §16) als Longtail-Angebot |
| **H4: Koop-/Casual-RTS** | spielen gegen KI mit Freunden, niedriger Druck | SC2-Co-op war historisch stark (Einschätzung, keine belastbaren öffentlichen Zahlen) | Koop-Modus aus GDD-O als Phase-3-Kandidat (Q-011), nicht MVP |

Priorisierung für Sprint 2: **H1 primär, H3 sekundär, H2/H4 explizit zurückgestellt** bis SP-Kern und MP-Architektur (Q-013) entschieden sind.

## Empfehlung

**Entscheidungsvorlage für den DecisionLog:**

1. **Marktpositionierung: Premium-Singleplayer/Skirmish-first auf Steam (Windows/macOS), kein F2P, kein MP-getriebenes Geschäftsmodell.** Begründung: Die erfolgreichsten jüngsten Wettbewerber (Tempest Rising, AoE IV) funktionieren über Premium-Käufe und PvE-Inhalte; das einzige F2P-/Server-MP-zentrierte Projekt der Dekade (Stormgate, ~$40 Mio. Budget) scheiterte trotz AAA-Pedigree und musste 2026 den Online-MP abschalten. Für Project Nova mit Kleinstudio-Ressourcen ist das F2P-/Server-Modell existenzgefährdend.
   - *Alternative A: F2P mit Server-MP (Stormgate-Modell)* – verworfen: erfordert dauerhafte MP-Kritische-Masse, Live-Betrieb und Fremdinfrastruktur; Marktbeleg eindeutig negativ.
   - *Alternative B: Kostenlos/Open Source (BAR-/Zero-K-Modell)* – verworfen: funktioniert nur mit Community-getragener Entwicklung ohne Umsatzziel; widerspricht der Studio-Finanzierungslogik und der Unity-Asset-Strategie (käufliche Assets, Signature-Assets).
   - *Alternative C: Premium, aber MP-zentriert (Launch mit Ranked/Ladder als Hauptversprechen)* – verworfen: ohne gepflegte Population und Esports-Reichweite unglaubwürdig; CoH 3 und Stormgate zeigen, dass MP-Versprechen ohne Substanz Reviews und Retention zerstören.
2. **Kern-USP: dynamische nachwachsende Aetherium-Felder mit Umweltveränderung.** Am Markt belegt (Tempest Rising), im MVP (1 Ressource) voll abbildbar, passt zur Datengetriebenheit (Wachstums-/Feldparameter als ScriptableObjects). Vollzerstörbare Umgebung wird als Post-MVP-Differenzierer geparkt (Konflikt mit Q-013/Q-014); 3 Fraktionen sind Hygienefaktor, kein USP.
   - *Alternative: Zerstörbarkeit als Kern-USP* – verworfen für MVP: hohe technische Kosten (Physik, Pathfinding-Invalidierung, spätere MP-Sync), kein erfolgreicher aktueller Marktbeleg als Alleinstellungsmerkmal.
   - *Alternative: Fraktions-Asymmetrie als Kern-USP* – verworfen als Marktaussage: Genre-Standard, Differenzierung entsteht erst durch Ausführungstiefe (z. B. Evolvierte-Baumechanik, Q-009) in Phase 2/3.
3. **Zielgruppe: H1 (C&C-Nostalgiker, Solo/Skirmish, Premium) primär; H2 (kompetitiver Ladder) explizit nicht vor Phase 3.** Begründung: H1 ist das einzige Segment mit belegtem Kaufverhalten für Kleinstudio-RTS ohne MP-Population; H2 verlangt Polish- und Balance-Niveau, das vor Kernloop-Validierung nicht erreichbar ist.
4. **Scope-Deckel:** Erfolgsszenario = Tempest-Rising-Größenordnung (zehntausende Premium-Verkäufe, >85 % Reviews). MVP-Umfang (1 Fraktion, 1 Karte, 1 Ressource, einfache KI) bleibt unverändert; jede Erweiterung erst nach Kernloop-Validierung.

## Offene Punkte

- Verkaufszahlen mehrerer Titel (Tempest Rising, CoH 3) sind Schätzungen Dritter (Gamalytic, Steam-Review-Heuristik), nicht Publisher-bestätigt → als Einschätzung zu behandeln.
- SC2-Spielerzahlen sind nicht öffentlich; Esports-Viewership (EWC 2025) ist der einzige harte Indikator.
- Wechselwirkung USP ↔ Q-005 (endliche vs. nachwachsende Felder) muss in Sprint 2 entschieden werden; die Marktanalyse favorisiert Nachwachsen + Umweltveränderung, sagt aber nichts über die konkrete Regel.
- Preispositionierung ($25 vs. $40) nicht untersucht → eigener Research- oder Sprint-2-Punkt.
- Keine Analyse der Vertriebsplattformen (Steam vs. Epic vs. Game Pass) – hängt an TPD §16 (bewusst offen).
- Konsole/Mobile-Markt für RTS bewusst ausgeklammert (Desktop-first).

## Nächste Schritte

- Sprint 2: USP-Entscheidung (Empfehlung §Empfehlung) in den DecisionLog übernehmen; Q-005 mit Marktpräferenz "nachwachsend + umweltverändernd" vorbelasten.
- Sprint 2: Zielgruppen-Hypothesen H1–H4 in GDD-Dokumenten (Vision, Zielgruppe) verankern; Q-011 (Modi-Phasierung) mit H1-Priorisierung abstimmen.
- Sprint 1 (parallel): Technik-Research Q-013 mit der Markterkenntnis "SP-first, Server-MP nicht als Fundament" als Randbedingung füttern.
- Bei Bedarf: Vertiefungs-Research Preispositionierung und Steam-Launch-Strategie (Wishlists, Demo/Next Fest) für AA-/Indie-RTS.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Research-Erstfassung | Game Director |
