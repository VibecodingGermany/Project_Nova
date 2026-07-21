# KI-Architekturen für RTS-Gegner

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead AI Programmer | **Sprint:** 1

## Zweck

Dieses Dokument vergleicht etablierte KI-Architekturen für den RTS-Gegner von Project Nova (Behavior Trees, Utility AI, GOAP, HTN, ML als Ausblick) und leitet daraus eine Empfehlung ab, die als Entscheidungsvorlage direkt in den DecisionLog übernommen werden kann. Bewertungskriterien sind projektspezifisch: MVP-Disziplin (1 Fraktion, einfache KI im Kernloop), datengetriebene Architektur (ScriptableObjects), 100–500+ gleichzeitige Einheiten bei 60 FPS, 3 asymmetrische Fraktionen perspektivisch, Schwierigkeitsgrade über Entscheidungsqualität statt Ressourcenboni, Testbarkeit/Debuggbarkeit und Kompatibilität mit einem späteren autoritativen Multiplayer bzw. deterministischer Simulation (Q-013).

## Abhängigkeiten

- [../analysis/KnowledgeBase.md](../analysis/KnowledgeBase.md)
- [../production/OpenQuestions.md](../production/OpenQuestions.md) (insb. Q-013 Simulations-/MP-Modell, Q-014 Pathfinding, Q-015 ECS/DOTS vs. OOP)

## Kontext und Anforderungen

Die KI muss elf Funktionsebenen abdecken: strategische Planung, Wirtschaft, Basisbau, Verteidigung, Aufklärung, Armeeproduktion, Angriffsplanung, Einheitensteuerung (Micro), Rückzug, Fähigkeitennutzung und Reaktion auf Spielerstrategien. Diese Ebenen haben stark unterschiedliche Frequenzen und Charaktere:

- **Strategische Ebene (selten, teuer, planend):** Strategiewahl (Rush, Tech, Expand), Timing von Angriffswellen, Reaktion auf erkannte Spielerstrategien. Entscheidungen alle 5–30 s.
- **Taktische Ebene (mittelhäufig, zustandsbasiert):** Basisbau-Platzierung, Produktionswarteschlangen, Verteidigungsdisposition, Aufklärungsrouten, Rückzugsentscheidungen. Entscheidungen alle 0,5–5 s.
- **Operative Ebene (häufig, billig, reaktiv):** Einheitensteuerung, Zielwahl, Fähigkeitennutzung einzelner Einheiten/Squads. Läuft pro Tick, muss bei 100–500+ Einheiten in Mikrosekunden pro Einheit liegen.

Konsequenz: Es gibt keinen einzelnen „besten" Ansatz für alle Ebenen. Die eigentliche Architekturentscheidung ist, welches Paradigma welche Ebene steuert und wie die Ebenen gekoppelt sind (Blackboard/Shared State).

Weitere harte Randbedingungen:

- **MP-Vorwärtskompatibilität (Q-013):** Die KI muss wie ein menschlicher Spieler ausschließlich über Commands auf den Simulationszustand wirken (kein direkter State-Zugriff schreibend), damit sie in deterministischem Lockstep oder unter einem autoritativen Server ohne Sonderweg mitläuft. RNG nur seeded aus dem Simulationskontext; kein `UnityEngine.Random`, kein `DateTime.Now`, keine Float-Nichtdeterminismen in der Entscheidungslogik, falls Lockstep gewählt wird.
- **Performance (Q-015):** Die operative Ebene muss burst-kompatibel/jobbisierbar bzw. zumindest allocationsarm bleiben; die strategische Ebene ist mengenmäßig irrelevant für das Frame-Budget und darf klassisches OOP bleiben.
- **Datengetriebenheit:** Build-Orders, Squad-Zusammensetzungen, Utility-Kurven, Aggressionsparameter und Schwierigkeitsprofile müssen von Designern ohne Codeänderung tunbar sein (ScriptableObjects).

## Vergleich der Ansätze

### (a) Behavior Trees (BT)

Zustandslose, tick-getriebene Entscheidungsbäume (Selector/Sequence/Decorator/Leaf) mit Blackboard. De-facto-Industriestandard für Einheiten-/NPC-Verhalten; BTs sind leicht debuggbar („man folgt dem Baum und findet das Problem", [Aversa 2018](https://www.davideaversa.it/blog/choosing-behavior-tree-goap-planning/)) und decken laut derselben Einschätzung ~80 % typischer Game-AI-Bedarfe ab.

Projektbezogene Vorteile:

- Ideal für die operative Ebene: Einheiten-Micro, Zielwahl, Fähigkeitennutzung, Rückzug sind klassische reaktive BT-Aufgaben.
- Exzellente Debug-Visualisierung (laufender Baum mit aktiven Knoten highlightbar) — bei 100–500 Einheiten entscheidend, um Fehlverhalten einzelner Squads zu finden.
- Determinismus-freundlich: reine Funktionen von Blackboard-State, keine interne Historie nötig.
- Reifes Unity-Ökosystem (siehe Abschnitt Unity-Umsetzung).

Projektbezogene Nachteile:

- Auf der strategischen Ebene skalieren BTs schlecht: Build-Order-Logik mit Abhängigkeiten (Voraussetzungsgebäude, Tech-Pfade, Aetherium-Income-Prognose) wird als BT unübersichtlich; Änderungen an oberen Knoten propagieren nach unten ([JMIS 2023](https://www.jmis.org/archive/view_article?pid=jmis-10-4-321)).
- Kein echtes Vorausplanen — BTs reagieren nur auf aktuellen Zustand; ein „Angriff in 90 s, dafür jetzt 2 Produktionsgebäude" ist als BT nur über implizite Blackboard-Flags abbildbar.
- Designer-Tuning großer Bäume ist fehleranfällig (Prioritäten stecken in der Baumstruktur, nicht in Daten).

### (b) Utility AI

Jede Option (z. B. „Arbeiter bauen", „Kaserne bauen", „Expandieren", „Angreifen") erhält einen Score aus gewichteten Betrachtungen (Considerations) mit Antwortkurven; gewählt wird die höchstbewertete Option (ggf. mit Hysterese). Popularisiert durch Dave Mark (*Behavioral Mathematics for Game AI*); utility-basierte Systeme stecken u. a. in The Sims und Guild Wars 2 (letzteres laut GDC-Vorträgen von ArenaNet/Dave Mark — als gut belegte Sekundärquelle, nicht primär verifiziert).

Projektbezogene Vorteile:

- Sehr starke Passung für Wirtschaft, Armeeproduktion und strategische Optionswahl: „Was ist jetzt am wertvollsten?" ist genau die Frage, die Utility beantwortet — inklusive Aetherium-spezifischer Considerations (Feld-Regenerationsrate, Map-Control-Anteil, eskalierende Umweltveränderung durch Aetherium).
- **Schwierigkeitsgrade fallen architektonisch gratis heraus:** Entscheidungsqualität = Consideration-Set + Kurvenqualität + Bewertungsrauschen + Denkfrequenz (Details siehe Abschnitt Schwierigkeitsgrade).
- Designer-tunbar per Definition: Kurven und Gewichte sind Daten, kein Code — passt exakt zur ScriptableObject-Leitplanke.
- Günstig zu testen: Scoring-Funktionen sind reine Funktionen → Unit-Tests ohne Unity-Szene.

Projektbezogene Nachteile:

- Sequenzielle Pläne (mehrstufige Build-Orders, koordinierte Angriffe aus mehreren Squads) sind nicht nativ abbildbar; Utility wählt immer nur die nächste beste Aktion. Ergebnis ohne Ergänzung: taktisch solide, strategisch planlos wirkende KI.
- Tuning der Kurven ist nicht-lokal: eine Kurvenänderung verschiebt das Gleichgewicht aller Optionen. Erfordert Disziplin und Visualisierungs-Tooling, sonst „Whack-a-Mole".
- Schwieriger zu debuggen als BT: „Warum hat die KI expandiert statt verteidigt?" erfordert Score-Dumps aller Optionen, keinen offensichtlichen Baumpfad.

### (c) GOAP (Goal-Oriented Action Planning)

Planer sucht rückwärts von einem Ziel eine Aktionssequenz über Prä-/Effektbedingungen (bekannt durch F.E.A.R., Monolith 2005). Dynamisch und emergent, aber Verhaltensfluss schwer vorhersagbar ([JMIS 2023](https://www.jmis.org/archive/view_article?pid=jmis-10-4-321)).

Projektbezogene Vorteile:

- Könnte Tech-Pfad- und Produktionsabhängigkeiten (Gebäude A braucht Gebäude B, Einheit C braucht Tech D) elegant als Planungsproblem lösen — bei 3 asymmetrischen Fraktionen mit unterschiedlichen Produktionsketten (Evolvierte „wachsen" statt bauen) konzeptionell reizvoll, weil die Abhängigkeitsgraphen aus denselben Daten generiert werden könnten.

Projektbezogene Nachteile:

- Overkill für den MVP und riskant für den Zeitplan: Planer, World-State-Repräsentation und Aktionenschema müssen erst gebaut werden, bevor irgendetwas spielbar ist.
- Debugging/Vorhersagbarkeit schlecht — für einen Gegner, der *lesbar und glaubwürdig* wirken soll (Stilziel „Lesbarkeit vor Realismus"), ist emergentes Verhalten eher Nachteil.
- Determinismus-Absicherung eines Planers (kanonische Sortierung, fixed-point Kosten) ist Zusatzarbeit, die wir bei BT/Utility nicht haben.
- Re-Planning-Kosten bei hochfrequenten World-State-Änderungen (500 Einheiten ändern laufend Bedrohungslagen) erfordern sorgfältige Budgetierung.

### (d) HTN (Hierarchical Task Networks)

Zerlegt High-Level-Tasks rekursiv in vordefinierte Compound-/Primitive-Tasks; plant vorwärts, kann Partial-Pläne committen und ist rechnerisch leichter als GOAP ([Tiilikainen 2024, Theseus](https://www.theseus.fi/bitstream/handle/10024/893802/Tiilikainen_Toni.pdf)). Industriell u. a. von Guerrilla Games (Killzone-Serie) eingesetzt. Strukturell BT-ähnlich, aber mit echtem Planungsbegriff.

Projektbezogene Vorteile:

- Beste natürliche Abbildung der strategischen Ebene: „ExecuteRush" → {BaueProduktion ×2, ProduziereTrupp X, SammleAngriffspunkt, GreifeAn} ist exakt eine HTN-Method. Build-Orders werden als lesbare, designerfreundliche Task-Netze statt als Kurvenchaos formuliert.
- Pläne sind explizit inspizierbar („KI führt Plan P aus, Schritt 3/7") — gut für Debug-Overlay und Replays.
- Determinismus-freundlich, billig, kein Suchraum nötig wenn Domäne gut strukturiert ist.

Projektbezogene Nachteile:

- Adaptivität auf das beschränkt, was der Designer an Methoden vorformuliert hat ([Tiilikainen 2024](https://www.theseus.fi/bitstream/handle/10024/893802/Tiilikainen_Toni.pdf)) — „Reaktion auf Spielerstrategien" muss vollständig antizipiert werden; unvorhergesehene Situationen führen zu Planabbrüchen/Replanning-Flattern.
- Kein nennenswertes fertiges Unity-Ökosystem: HTN-Frameworks für Unity sind Nischen-Assets oder Eigenbau. Eigenbau ist machbar (HTN-Kern ist wenige hundert Zeilen), aber Sprint-1-Ressourcen fließen dann in Infrastruktur statt Spielbarkeit.
- Domänen-Authoring ist eine eigene Disziplin; Designer brauchen Einarbeitung.

### (e) ML-Ansätze (Ausblick, nicht MVP)

Stand der Forschung: AlphaStar erreichte 2019 Grandmaster-Niveau in StarCraft II über Deep Reinforcement Learning auf der SC2LE/PySC2-Schnittstelle von DeepMind/Blizzard ([DeepMind Blog](https://deepmind.google/blog/deepmind-and-blizzard-open-starcraft-ii-as-an-ai-research-environment/), [PySC2](https://github.com/deepmind/pysc2)). Seit 2023/2024 gibt es LLM-gesteuerte StarCraft-II-Agenten als Forschungsrichtung (z. B. [LLM-PySC2](https://github.com/NKAI-Decision-Team/LLM-PySC2), [TextStarCraft II, arXiv 2312.11865](https://arxiv.org/html/2312.11865v1)). Für OpenRA existiert mit [OpenRA-RL](https://openra-rl.dev/blog/welcome/) ebenfalls eine RL-Umgebung.

Projektbezogene Einordnung (Einschätzung): RL-Training auf eigenem Spiel erfordert Headless-Self-Play-Infrastruktur, stabile Simulations-API und erhebliche Rechenbudgets — für ein Studio unserer Größe und für einen Gegner, der *designed und lesbar* wirken soll, ist das Release-KI-Risiko zu hoch. Sinnvoller Zwischenschritt: Die hier empfohlene Command-basierte KI-Schnittstelle (KI spielt über dieselbe API wie ein Netzwerk-Client) schafft exakt die Voraussetzung, später ML-Agenten (z. B. Unity ML-Agents, Imitation Learning aus Replays) anzudocken, ohne die Architektur zu ändern. LLM-gesteuerte Gegner sind für ein Echtzeit-RTS mit 60-FPS-Tickbudget und Offline-Fähigkeit derzeit keine Option (Latenz, Kosten, Nichtdeterminismus).

### Vergleichsmatrix

| Kriterium | BT | Utility | GOAP | HTN | ML (RL/LLM) |
|---|---|---|---|---|---|
| Strategische Planung (mehrstufig) | schwach | schwach | stark | stark | stark (Forschung) |
| Reaktive Einheitensteuerung | stark | mittel | schwach | mittel | stark |
| Wirtschaft/Produktion (Optionswahl) | mittel | stark | mittel | mittel | – |
| Designer-Tuning datengetrieben | mittel | stark | mittel | stark | schwach |
| Debuggbarkeit/Visualisierung | stark | mittel | schwach | stark | schwach |
| Implementierungsrisiko MVP | niedrig | niedrig | hoch | mittel (Eigenbau) | sehr hoch |
| Unity-Ökosystem | ausgereift | dünn, Eigenbau üblich | dünn | minimal | ML-Agents |
| Determinismus/MP-Tauglichkeit | gut | gut | aufwändig | gut | problematisch |
| Schwierigkeitsgrade via Qualität | mittel | stark | mittel | stark | ungeprüft |

## Empfohlene Zielarchitektur (Hybrid)

Dreischichtig, gekoppelt über einen gemeinsamen, datengetriebenen Blackboard (KI-Wissensmodell: eigene Ressourcen, Aetherium-Feldzustände, Bedrohungskarten/Influence Maps, Aufklärungswissen über den Spieler):

1. **Strategische Schicht — Utility-Director:** Bewertet in niedriger Frequenz (alle 2–5 s) strategische Optionen (Expand, Tech, Rush, Turtlen, Counter) über Considerations. Reaktion auf Spielerstrategien läuft über erkannte Signale (gesichtete Gebäude/Einheiten → Bedrohungsvektor), die als Consideration-Inputs dienen. Difficulty regelt Qualität und Rauschen dieser Bewertung.
2. **Taktische Schicht — Task-Ausführer mit HTN-light-Charakter:** Die vom Director gewählte Strategie instanziiert einen vorformulierten Task-Plan (Build-Order, Angriffswellen-Sequenz) aus ScriptableObject-Daten. Pläne sind flache, sequenzielle Task-Listen mit Bedingungen — bewusst *kein* vollwertiger rekursiver HTN-Planer im MVP, aber dieselbe Datenform, sodass ein echter HTN-Planer später nachrüstbar ist. Deckt Basisbau, Produktion, Verteidigung, Aufklärung, Angriffsplanung ab.
3. **Operative Schicht — Behavior Trees pro Squad/Einheit:** Micro, Zielwahl, Fähigkeitennutzung, Rückzug (Rückzug als BT-Branch getriggert durch Squad-Kohäsions-/HP-Betrachtungen aus der Utility-Schicht). Squads statt Einzelentscheidungen, um das Tick-Budget bei 500 Einheiten zu halten.

Die Kopplung nach unten erfolgt ausschließlich über Commands in die Simulation — dieselbe Schnittstelle, über die später Netzwerk-Inputs laufen. Das macht die KI zur „nullten Netzwerk-Partei" und sichert Q-013-Kompatibilität in beiden Szenarien (Lockstep wie Server-autoritativ).

Illustratives Datenmodell (kein Produktivcode):

```csharp
// ScriptableObject, von Designern befüllt
class StrategyOptionSO : ScriptableObject {
    string id;                       // "expand_aetherium_field_2"
    List<ConsiderationSO> considerations;  // je: Input-Kurve + Gewicht
    TaskPlanSO plan;                 // flache Task-Sequenz (HTN-light)
    DifficultyTier minDifficulty;    // ab welcher Stufe verfügbar
}
```

## Schwierigkeitsgrade ohne Ressourcenboni

Ziel: Leicht/Mittel/Schwer unterscheiden sich in Entscheidungsqualität und Reaktionslogik, nicht in Income. Architektonisch umsetzbare Stellschrauben (alle als `DifficultyProfileSO` datengetrieben):

- **Consideration-Set:** Leicht sieht nur Teilmengen (z. B. keine Counter-Consideration auf Spieler-Army-Composition, keine Aetherium-Regenerations-Prognose). Schwer nutzt alle Signale.
- **Bewertungsrauschen:** Gauß-Noise (seeded!) auf Scores bei Leicht/Mittel; Schwer bewertet unverrauscht.
- **Denkfrequenz/Latenz:** Director-Tick alle 8 s (leicht) bis 2 s (schwer); Reaktionsdelay auf gesichtete Spieleraktionen 15 s → 3 s.
- **Plan-Qualität:** Leicht nutzt einfache, frühe Planabbrüche und verzichtet auf Replanning nach Störung; Schwer replant mit Lookahead (z. B. verzögerte Expansion bei erkannter Bedrohung).
- **Operative Präzision:** Zielwahl-Priorisierung (Fokus-Fire, Fähigkeiten-Timing) als BT-Varianten je Profil; identisches APM-Limit für alle Stufen, aber Schwer „verschwendet" keine Aktionen.
- **Aufklärungsdisziplin:** Scouting-Frequenz und -Abdeckung als Parameter — die glaubwürdigste Difficulty-Quelle, weil sie menschliches Verhalten spiegelt.

Wichtig: Alle Stellschrauben wirken multiplikativ auf dieselbe Codebasis — es gibt *eine* KI mit Profilen, nicht drei gepflegte KIs. Das vermeidet das bei OpenRA beobachtete Problem, wo Schwierigkeitsstufen historisch wenig bedeutsame Unterschiede hatten und erst nachträglich als Issue aufgenommen wurden ([OpenRA #16126](https://github.com/OpenRA/OpenRA/issues/16126)).

## Testbarkeit, Debugging, Visualisierung

- **Unit-Tests:** Utility-Scoring und Plan-Bedingungen als reine Funktionen testbar (EditMode-Tests, keine Szene). BT-Leaves gegen Mock-Blackboard.
- **Replay-/Headless-Selbstläufe:** Weil die KI command-basiert spielt, können KI-gegen-KI-Matches headless mit fixem Seed laufen (CI: Nightly-Balance-Metriken wie „Siegquote Strategie X vs. Y", „Zeit bis erster Angriff"). Das ist gleichzeitig die Infrastruktur für späteres RL/Imitation Learning.
- **Debug-Overlay im Editor:** aktueller Director-Score aller Optionen (Balkendiagramm), aktiver Plan mit Schritt-Indikator, BT-Laufzustand des selektierten Squads, Influence-/Bedrohungskarte als Heatmap. Bei 100–500 Einheiten ist Squad-Level-Visualisierung Pflicht, Per-Unit-Overlay nur für Selektion.
- **Determinismus-Guard:** Decision-Log mit Seed-Hash pro Tick; bei Lockstep-Entscheidung (Q-013) dient das als Desync-Detektor.

## Unity-Umsetzungsoptionen

| Option | Einordnung |
|---|---|
| **Unity Behavior** (`com.unity.behavior`, seit 2024 Preview, erfordert Unity 6000.0.16f1+, [Release-Thread](https://discussions.unity.com/t/behavior-package-1-0-0-preview-is-now-available/1519523)) | Offizieller Graph-Editor, aktiv entwickelt, aber jung; API-Stabilität und Langzeitpflege im Forum kontrovers diskutiert ([Unity Discussions 2025](https://discussions.unity.com/t/are-other-people-going-to-continue-using-the-behavior-package-or-switch-to-a-third-party-asset/1599273)). Für unsere *operative* Schicht nur bedingt geeignet: per-Unit-Graph-Instanzen bei 500 Einheiten sind nicht der vorgesehene Skalierungspfad. |
| **Opsive Behavior Designer Pro** ([DOTS-basiert](https://opsive.com/support/documentation/behavior-designer-pro/version-comparison/), kostenpflichtig) | DOTS-Backend spricht die 100–500+-Einheiten-Frage direkt an; laut Hersteller/Community schnellste BT-Laufzeit ([Vergleichsthread](https://discussions.unity.com/t/behavior-designer-or-nodecanvas/848599)). Kandidat, falls Q-015 zugunsten DOTS-Hybrid ausfällt. |
| **NodeCanvas** ([paradoxnotion](https://nodecanvas.paradoxnotion.com/), kostenpflichtig) | Ausgereifter Editor, enthält auch FSM/Dualogue; Runtime-Performance hinter Behavior Designer. |
| **Eigenbau: Utility-Director + Plan-Executor als Plain C# (SO-basiert), BT nur als schmale Laufzeit** | Strategische/taktische Schicht hat ohnehin kein fertiges Framework — Eigenbau ist hier unvermeidlich und gewollt (Leitplanke Datengetriebenheit). Eine minimale BT-Laufzeit für Squad-Verhalten ist überschaubar. |

Empfohlener Weg: Schichten 1+2 als Eigenbau (SO-datengetrieben, deterministisch), Schicht 3 zunächst als schlanke eigene BT-Laufzeit (Squad-Bäume, keine Per-Unit-Graphen). Kauf-Assets nur evaluieren, wenn der BT-Umfang die Eigenbau-Kosten übersteigt — Entscheidung in Sprint 3 zusammen mit Q-015.

## Referenzprojekte

- **StarCraft II:** Zwei getrennte Welten. Die eingebaute KI ist ein klassisches, skriptbasiertes System (Galaxy-Script/Trigger-Ebene) mit Difficulty-Stufen, die u. a. Reaktionsgeschwindigkeit und Verhaltensumfang begrenzen (Blizzard-intern; Details nicht öffentlich spezifiziert — Einschätzung). Für externe Agenten stellt Blizzard/DeepMind dagegen eine definierte Beobachtungs-/Aktions-API bereit (SC2LE/[PySC2](https://github.com/deepmind/pysc2)), auf der AlphaStar und die RL-Forschung aufsetzen ([DeepMind Blog](https://deepmind.google/blog/deepmind-and-blizzard-open-starcraft-ii-as-an-ai-research-environment/)). Lehre für Nova: eine saubere Agenten-Schnittstelle (Observationen rein, Commands raus) zahlt sich mehrfach aus — Debug-Bots, Balance-Automation, späteres ML.
- **OpenRA (C#, Open Source):** KI als `ModularBot` mit austauschbaren `BotModules` (BaseBuilder, SquadManager, MCV-Manager, Support-Power etc.), komplett per YAML-Daten konfigurierbar ([ai.yaml](https://github.com/OpenRA/OpenRA/blob/bleed/mods/ra/rules/ai.yaml), [BotModules-Verzeichnis](https://github.com/OpenRA/OpenRA/issues/14693)). Das ist faktisch unser Utility/Task-Hybrid in Datenform — Beleg, dass datengetriebene Modularität im RTS trägt. Gleichzeitig Mahnung: trotz Modularität waren die Difficulty-Stufen lange schwach differenziert ([Issue #16126](https://github.com/OpenRA/OpenRA/issues/16126)).
- **Age of Empires II:** Regelbasiertes Expertensystem; KI-Skripte (`defrule`-Regeln, `.per`-Dateien) mit Strategic Numbers als Parameterraum. Difficulty wird über `load-if-defined DIFFICULTY-*`-Konstanten gesteuert, die Parameter wie Villager-/Trade-Limits umschalten ([Beispielskript](https://gist.github.com/mayerwin/ac4a5ec62f51e94a3fa9)) — ein früher, funktionierender Beleg für „eine KI, Difficulty als Parameterprofil", allerdings mit dem damaligen Nachteil massiver Code-Duplikation pro Stufe, den wir über Datenprofile vermeiden.

## Bezug zu Q-013/Q-014/Q-015

- **Q-013 (Sim-/MP-Modell):** Dieses Dokument beantwortet Q-013 nicht direkt, setzt aber eine belastbare Anforderung: Die KI-Architektur (Command-only, seeded RNG, reine Funktionen) ist mit *beiden* Kandidaten (Lockstep, Server-autoritativ) kompatibel und neutralisiert damit den KI-Teil der Q-013-Risiken. Kein KI-Argument erzwingt eine der beiden Optionen.
- **Q-014 (Pathfinding):** Keine direkte Beantwortung; die KI konsumiert Pathfinding nur als Service (Squad-Level-Anfragen). Anforderung an Q-014: Flow-Field-Ausgaben sollten als Influence-/Kostenkarten auch der KI (Bedrohungskarten) zur Verfügung stehen — Synergie prüfen.
- **Q-015 (ECS/DOTS):** Keine direkte Beantwortung. Die KI-Entscheidungslogik selbst ist mengenmäßig klein (Squad-Level, niedrige Frequenz) und benötigt kein DOTS; sie sollte aber keine Annahmen treffen, die einen DOTS-Umzug der Simulation blockieren (keine Unity-Objekt-Referenzen in der Entscheidungslogik, nur Entity-IDs/Structs).

## Empfehlung

**Entscheidungsvorlage (für DecisionLog):** Das Studio entscheidet sich für eine **hybride Drei-Schichten-KI**: (1) strategischer **Utility-Director** (datengetriebene Considerations als ScriptableObjects, niedrige Denkfrequenz), (2) taktischer **Plan-Executor** mit flachen, SO-definierten Task-Plänen (HTN-light: dieselbe Datenform wie HTN-Methoden, ohne rekursiven Planer im MVP), (3) operative **Behavior Trees auf Squad-Ebene** als schmale Eigenbau-Laufzeit. Die KI wirkt ausschließlich über Commands auf die Simulation (MP-/Determinismus-kompatibel, Q-013-neutral). Schwierigkeitsgrade entstehen über ein `DifficultyProfileSO` (Consideration-Set, Score-Rauschen, Denkfrequenz, Reaktionslatenz, Scouting-Disziplin) — niemals über Ressourcenboni. MVP-Umfang: Utility-Director mit ~5 Optionen, 2–3 Task-Pläne, Squad-BT für Kampf/Rückzug/Fähigkeiten.

**Geprüfte und verworfene Alternativen:**

- *Reine BT-Architektur:* verworfen, weil strategische Planung und datengetriebenes Difficulty-Tuning in BTs schlecht skalieren; BTs bleiben auf die operative Schicht beschränkt, wo sie stark sind.
- *Reine Utility-Architektur:* verworfen, weil sequenzielle Pläne (Build-Orders, Angriffswellen) nicht nativ abbildbar sind und Debugging ohne Planbegriff leidet.
- *GOAP:* verworfen wegen Implementierungsrisiko im MVP, schwacher Vorhersagbarkeit/Debuggbarkeit und Zusatzaufwand für Determinismus — trotz konzeptionell guter Passung auf asymmetrische Produktionsketten; Re-Evaluation bei Fraktion 2/3 möglich.
- *Vollwertiges HTN:* verschoben (nicht verworfen): Datenform wird jetzt kompatibel gehalten; rekursiver Planer erst, wenn Task-Pläne Komplexitätsgrenzen zeigen.
- *ML-basierte Release-KI (RL/LLM):* verworfen für Release (Trainingsinfrastruktur, Nichtdeterminismus, Latenz/Kosten, Lesbarkeits-Ziel); als Ausblick über die command-basierte Agenten-Schnittstelle offengehalten.
- *Kauf-Assets für Schicht 1/2 (Behavior Designer Pro, NodeCanvas, Unity Behavior):* verworfen, weil kein Produkt Utility-Director + Plan-Executor abdeckt; für Schicht 3 vorerst Eigenbau, Re-Evaluation gemeinsam mit Q-015 in Sprint 3.

## Offene Punkte

- Konkrete Consideration-Liste und Kurvenformen pro Strategieoption (braucht Sprint-2-Input zu Wirtschaftsregeln, v. a. Q-005 Aetherium-Nachwachsen).
- Schnittstellenformat „erkannte Spielerstrategie" (Bedrohungsvektor aus Scouting-Daten) — abhängig vom Fog-of-War-/Sichtsystem, noch kein Research-Dokument vorhanden.
- Influence-Map-/Bedrohungskarten-Implementierung (Auflösung, Update-Frequenz bei 500 Einheiten) offen; mögliche Synergie mit Flow-Fields aus Q-014.
- Ob Behavior Designer Pro (DOTS) für die operative Schicht langfristig Sinn ergibt — gekoppelt an Q-015-Entscheidung.
- Wie Evolvierte-„Wachstums"-Bauweise (Q-009) die Task-Pläne der Basisbau-Ebene verändert (Bauplatz-Logik vs. Wachstumsknoten).
- Headless-KI-gegen-KI-Runner: Aufwand und CI-Integration noch nicht geschätzt.

## Nächste Schritte

- Sprint 2: DecisionLog-Eintrag aus Abschnitt Empfehlung übernehmen; `StrategyOptionSO`/`DifficultyProfileSO`-Datenmodelle als Schema-Entwurf spezifizieren.
- Sprint 2/3: Minimal-Prototyp Utility-Director + ein Task-Plan + Squad-BT gegen die MVP-Simulation (nach Engine-/Simulations-Entscheid Q-013/Q-015).
- Sprint 3: Re-Evaluation BT-Asset vs. Eigenbau gemeinsam mit Q-015; Bedrohungskarten-Konzept gemeinsam mit Q-014-Verantwortlichem abstimmen.
- Laufend: OpenRA-BotModule-Struktur und AoE-II-Skripte als Referenz für das SO-Datenformat auswerten (konkrete Feldlisten übernehmen, was bewährt ist).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Research-Erstfassung | Lead AI Programmer |
