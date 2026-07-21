# Technical Design: Pathfinding & Bewegung

**Version:** 0.2.0 | **Status:** Entwurf (Korrekturlauf Sprint 4) | **Verantwortungsbereich:** Lead AI Programmer | **Sprint:** 4

## Zweck

Dieses Dokument konkretisiert die verbindliche Pathfinding-Architektur **D-034** (uniformes Integer-Grid 1-m-Tiles + Flow Fields für Gruppen + lokale Vermeidung, Jobs/Burst) zu einem umsetzungsreifen Design für Sprint 7: Grid-Aufbau und Speicher, Clearance-Layer für drei Radienklassen, Flow-Field-Lebenszyklus, Dirty-Flagging für dynamische Hindernisse, lokale Vermeidung (MVP Separation, Alpha ORCA), Formationen, Luft-Steering, Jobs/Burst-Auslegung, CPU-Budget und Teststrategie. Zielplattform ist die Unity-freie Assembly `Nova.Simulation` (D-033, D-035); das gesamte Modul ist command-getrieben, determinismus-fähig und vollständig serialisierbar.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-006 (Unity 6.3 LTS/URP/C#), D-033 (Tick-Simulation, 10 Hz, Commands als einzige Mutation, kein UnityEngine im Sim-Pfad), D-034 (diese Architektur, Fallback A* Pathfinding Project), D-035 (MonoBehaviour/SO-Gerüst, Burst/Jobs-Hotspots, `Nova.Simulation`), D-036 (Nova.SimRunner für headless Tests), D-012 (Trümmer-Regel)
- [../research/Pathfinding.md](../research/Pathfinding.md) – Anforderungen, Alternativbewertung, Referenztitel (SupCom 2, PA, SC2), ORCA/Dichtefeld-Verweise
- [../gamedesign/Maps.md](../gamedesign/Maps.md) – Kartengrößen S/M/L (128/192/256), Chokepoint-Designregeln
- [../gamedesign/FogOfWar.md](../gamedesign/FogOfWar.md) – FoW nutzt dasselbe 1-m-Grid (D-034-Begründung: eine Grid-Infrastruktur)
- [../gamedesign/Infantry.md](../gamedesign/Infantry.md), [../gamedesign/Vehicles.md](../gamedesign/Vehicles.md), [../gamedesign/Aircraft.md](../gamedesign/Aircraft.md) – Radien- und Bewegungsdaten der Einheitentypen
- ./GameState.md, ./Commands.md, ./Testing.md (Sprint-3-Tech-Docs, Parallelentwürfe) – Serialisierungs- und Command-Verträge

## 1. Grid-Aufbau

### 1.1 Dimensionen und Speicher

Tile-Kante 1 m (D-034). Kartengrößen aus Maps.md:

| Karte | Kantenlänge | Tiles | Statische Layer (7 B/Tile) | Pro Flow Field (3 B/Tile) |
|---|---|---|---|---|
| S | 128 m | 16.384 | ~112 KB | ~48 KB |
| M | 192 m | 36.864 | ~252 KB | ~108 KB |
| L | 256 m | 65.536 | ~448 KB | ~192 KB |

Statische Layer pro Tile (ungepackt 7 B): `TerrainCost` (u8, 0 = unpassierbar), `Clearance[3]` (je u8, max. passierbarer Radius in dm je Radienklasse), `Height` (u8), `Flags` (u8: Wasser, unbuildable, NoFlyZone o. ä.), `ZoneId` (u8, Biom/Aetherium-Zone).

Budgetannahme (Korrekturlauf Sprint 4, Review-Befunde Performance F-4 / Skalierung F-5): **≤ 96 gleichzeitig aktive Flow Fields** (erhöht von 32). Begründung: 6 Parteien × 2–4 aktive Kontrollgruppen × bis zu 3 Clearance-Klassen = 36–72 Felder im Angriffsfall, plus Wirtschafts-Felder (§2) und KI-Squad-Felder – 32 war im 6-Spieler-Fall nachweislich unterschritten. Speicher-Neurechnung: 3 B/Tile × 65.536 Tiles × 96 Felder = 18.874.368 B ≈ **19 MB auf L-Karten** (M: ~10,6 MB; S: ~4,7 MB). Gegen die 100-MB-Sim-Kappe (MemoryBudget.md §1) unkritisch; MemoryBudget.md §3 wurde im selben Korrekturlauf angeglichen (96 Felder / ~19 MB / RefCount-Eviction).

### 1.2 Radienklassen (Clearance)

Drei Klassen (D-034), Radius in dm aus den Unit-SOs, kein Runtime-State in SOs:

| Klasse | Radius (Richtwert) | Beispiele |
|---|---|---|
| `Infantry` | ≤ 3 dm | alle Infanterietypen |
| `Vehicle` | ≤ 8 dm | Standard-Fahrzeuge, Harvester |
| `Heavy` | ≤ 14 dm | Großpanzer, Superwaffen-Träger |

Pro Klasse ein Clearance-Layer, der aus `TerrainCost` + statischen Hindernissen vorberechnet wird (maximaler freier Radius pro Tile). Exakte Radien sind Offener Punkt (Abhängigkeit zu finalen Einheitenmaßen). Designregel an Level Design: Chokepoints breiter als 3× größter Radius (Research §4.4).

### 1.3 Zell-Konventionen

Weltkoordinate → Tile: `tile = floor(worldPos)` (MVP float, Fixed-Point-Umstellung Teil der Beta-MP-Arbeiten, D-033-Konsequenz). Ganzzahlige Tile-Indizes und Integer-Kosten sind von Anfang an verbindlich, um Lockstep-Determinismus (D-033) offenzuhalten.

## 2. Flow-Field-Berechnung

- **Dominanzfall:** Ein Bewegungs-Command an eine Gruppe (10–100 Einheiten) erzeugt **ein** Flow Field pro Ziel-Gruppe, nicht N Einzelsuchen (D-034). Ziel-Gruppierung: Commands mit identischem Ziel-Tile (oder Ziel-Cluster, Toleranz einige Tiles) teilen sich ein Feld.
- **Algorithmus:** Dijkstra-Wellenfront vom Ziel aus über das Grid des passenden Clearance-Layers, Kosten als `int16` (Skala: 1 Tile orthogonal = 10, diagonal = 14), frühes Abbruchkriterium (alle Agenten-Tiles der Gruppe erreicht oder Kostenlimit). Danach Integration pass → Richtungsvektor pro Tile (u8 Richtungsindex in 8/16 Richtungen + Fallback auf Nachbar-Minimum).
- **Pooling & Caching:** Felder werden aus einem Pool allokiert (kein GC im Tick), anhand von `(ZielCluster, RadienKlasse)` gecacht und wiederverwendet; Feld-RefCount über zugewiesene Gruppen. Pool-Kapazität = 96 Felder (§1.1).
- **Wirtschafts-Flow-Sharing (Review Performance F-4):** Harvester erzeugen **keine** eigenen Felder pro Harvester. Alle Harvester, die dasselbe Aetherium-Feld anfahren, teilen sich **ein** Flow Field auf dieses Feld-Ziel (Radienklasse `Vehicle`); analog teilt die Rückkehr-Relation ein Feld auf die Raffinerie als Cluster-Anker. Cluster-Anker der Wirtschaft sind also Feld bzw. Raffinerie, nicht die Einzel-Einheit. Cache-Druck-Rechnung: 6 Parteien × ~2–3 aktive Abbaugebiete × 2 Richtungen ≈ 24–36 Wirtschafts-Felder im Maximum, typisch deutlich darunter – mit den 36–72 Angriffs-Feldern (§1.1) bleibt der Deckel 96 im Worst Case knapp, im Normalfall mit Reserve ausreichend. Eviction-Thrash-Metrik (Fills/Tick) gehört in den Budget-Monitor des V4-Spikes (Szenario „6 Parteien Vollwirtschaft + 3 Angriffe", nicht nur „500 Agenten, 1 Ziel").
- **Eviction-Policy (Review Skalierung F-5):** ausschließlich **RefCount-basiert** – aktive Gruppen pinnen ihr Feld; freigegeben werden nur Felder mit RefCount 0 (älteste zuerst). **Kein LRU über referenzierte Felder**: Ein referenziertes Feld zu verwerfen ließe Einheiten mitten im Pfad ohne Richtungsfeld zurück. (MemoryBudget.md §3 ist auf RefCount-Eviction angeglichen.)
- **Überlauf-Verhalten (Review Skalierung F-5):** Ist der Pool voll (96 referenzierte Felder), erhalten neue Feld-Anfragen kein Feld, sondern fallen auf **direkte A*-Einzelsuche** zurück (Hierarchical-frei, auf dem Clearance-Layer), begrenzt auf **≤ 4 A*-Fills pro Tick**; darüber hinausgehende Anfragen erhalten `PathStatus.Deferred` und werden in Folgeticks bedient. Der Fallback ist ein Command-sichtbares, deterministisches Sim-Ereignis (feste Tick-Reihenfolge, fester A*-Tiebreak), damit Lockstep und Replays identisch bleiben.
- **Kosten-Invalidierung:** Bei Dirty-Regionen (s. §3) wird das betroffene Feld **lokal** neu gefüllt: begrenzter Dijkstra-Restart ab der Region-Grenze, kein Voll-Update. Felder ohne Referenzen werden freigegeben.
- **Time-Slicing:** Feld-Fills laufen als Burst-Jobs und werden über Ticks amortisiert; Einheiten folgen 1–2 Ticks dem alten Feld (visuell irrelevant, Research §4.1).

## 3. Dynamische Hindernisse (Dirty-Flagging)

Ereignisgetrieben, niemals Voll-Scan (D-034-Konsequenz). Alle Quellen melden AABB-Regionen an den `IPathGrid`-Dirty-Mechanismus; betroffene Clearance-Layer und aktive Flow Fields werden markiert und im nächsten Update-Fenster partiell neu berechnet:

- **Mauerbau/-zerstörung:** Platzierung setzt Tiles unpassierbar; während des Baus gilt Kostenstrafe statt "unpassierbar" (Bauarbeiter können durch, Research §4.3). Zerstörung gibt Tiles frei.
- **Trümmer (D-012):** Trümmer-Felder = erhöhte Kosten statt Sperrung (passierbar, aber langsamer); Verfall räumt Tiles schrittweise frei.
- **Evolvierte-Keime / Wachstumsbauweise:** Keim-Zonen blockieren Platzierung und melden wachsende Dirty-Regionen bei Ausdehnung.
- **Aetherium-Ausbreitung:** Kristallwachstum kann Gelände blockieren/umformen (GDD); jede Wachstumsstufe meldet ihre Tile-Region. Überernte/Abbau melden entsprechend Freigaben.
- **Vegetationsbrände:** brennende Tiles temporär hohe Kosten; abgebrannte Tiles danach frei/niedrig.

Stehende Einheiten sind **keine** Grid-Hindernisse; Einheit-gegen-Einheit regelt ausschließlich die lokale Vermeidung (§4). Eine **Dichtekarte** (Einheiten/Tile, u8-Layer, im Sicht-Tick aktualisiert) dient als weicher Kostenaufschlag für Stau-Umlenkung – **Alpha-Plan** (Korrekturlauf Sprint 4: von „Alpha-Option" hochgestuft, Review Skalierung). Kostenrahmen: 64 KB zusätzlicher Layer-Speicher auf L-Karten (innerhalb des Grid-Budgets), Update-Kosten ~0,1–0,3 ms managed im 5-Hz-Sicht-Tick (zählt nicht gegen das 4-ms-PF-Tickbudget, sondern gegen den Sicht-Tick; Messung im Alpha-Meilenstein).

## 4. Lokale Vermeidung (Steering)

- **MVP (D-034):** einfache Separation + Alignment (Boids-light) über Spatial Hash (Grid-basiertes Bucketing, kein O(n²)); Geschwindigkeitsclamp, keine Kollisionsgarantie. Idle stehende Einheiten weichen aktiv ausweichenden Einheiten minimal aus (kooperatives Wegdrängen, SC2-Vorbild).
- **Alpha (D-034):** Umstieg auf ORCA (RVO2-Prinzip) hinter derselben `ISteering`-Schnittstelle; Eigenbau in Fixed-Point-fähiger Form, kein Fremd-Asset im Sim-Pfad. Austauschbarkeit ist Designziel der Schnittstelle.
- **Determinismus:** Steering arbeitet ausschließlich auf serialisierbarem Sim-State (Positionen, Geschwindigkeiten, Radien) in fester Tick-Reihenfolge; Iterationsreihenfolgen über Spatial-Hash-Buckets sind stabil zu definieren (Sortierung nach UnitId).

## 5. Formationen

- Gruppen-Flow-Field bleibt identisch für alle Einheiten der Gruppe; **Slots** relativ zum Gruppenzentrum (Ziel-Tile) variieren die Zielzelle pro Einheit leicht (Research §2.4B).
- MVP: lockere Slot-Auflösung (Spaltenaufstellung um das Ziel, Slot-Zuweisung nach UnitId sortiert → deterministisch); kein starres Formationshalten unterwegs, das Feld führt den Verband.
- Slot-Struktur ist reine Sim-Daten (serialisierbar); Formationsprofile ggf. später als Definitions-only-SO.

## 6. Lufteinheiten

Separater **2.5D-Steering-Layer** (D-034): kein Boden-Pathfinding, direkte Zielansteuerung mit eigener Separation innerhalb der Luftstaffel. Flughöhen sind konstante Höhenebenen je Lufteinheiten-Typ (kein kontinuierliches Höhen-Pathfinding im MVP). No-Fly-Zonen (Flak-Reichweiten, Sperrgebiete) werden als separates Kostenfeld auf demselben Grid gepflegt und erzeugen Umfleug-Vektoren. **Zuständigkeit (Korrekturlauf Sprint 4, entschieden):** Führendes System für das No-Fly-Kostenfeld ist die **Grid-Infrastruktur dieses Moduls** (dieselbe 1-m-Grid-/Dirty-Mechanik wie FoW, D-034-Begründung „eine Grid-Infrastruktur"); das **Kampf-Modul liefert lediglich die Flak-Reichweiten als Kosten-Layer-Daten** (Reichweitenwerte verbindlich aus Weapons.md, D-047) und meldet Änderungen (Flak gebaut/zerstört/versetzt) als Dirty-Regionen an `IPathGrid`. Boden-Grid-Updates beeinflussen Luft nur über No-Fly-Flags (§1.1).

## 7. Schnittstellen (C#-Skizzen, Nova.Simulation)

Alle Typen in `Nova.Simulation.Pathing`; reine Daten/Struct-basiert, Unity-frei, NativeArray-kompatibel für Burst (D-033, D-035).

```csharp
namespace Nova.Simulation.Pathing
{
    public enum ClearanceClass : byte { Infantry = 0, Vehicle = 1, Heavy = 2 }

    /// <summary>Statisches + dynamisches Bewegungsgrid. Einzige Mutation via Sim-Commands (D-033).</summary>
    public interface IPathGrid
    {
        int Width { get; } int Height { get; }           // Tiles (128/192/256)
        byte GetTerrainCost(int tileIndex);
        byte GetClearance(int tileIndex, ClearanceClass cls);
        void MarkDirty(IntRect region, DirtyReason reason); // §3
        bool ConsumeDirtyRegions(Span<IntRect> buffer);   // für partielle Recomputes
    }

    public enum DirtyReason : byte { Building, Rubble, EvolvedGerm, AetheriumSpread, Fire }

    /// <summary>Kosten- + Richtungsfeld für eine Ziel-Gruppe und Radienklasse.</summary>
    public interface IFlowField
    {
        int TargetTile { get; }
        ClearanceClass Class { get; }
        int Version { get; }                              // Invalidierungs-Tracking
        byte GetDirection(int tileIndex);                 // Index in Richtungstabelle
        bool Contains(int tileIndex);                     // Erreichbarkeit
    }

    public readonly struct PathRequest
    {
        public readonly int RequestId;
        public readonly int TargetTile;
        public readonly ClearanceClass Class;
        public readonly int GroupId;                      // Gruppenzugehörigkeit aus Move-Command
        public PathRequest(int id, int target, ClearanceClass cls, int group) { /* … */ }
    }

    public readonly struct PathResult
    {
        public readonly int RequestId;
        public readonly int FieldHandle;                  // Referenz auf gepooltes IFlowField
        public readonly PathStatus Status;                // Ok | Unreachable | Deferred
        public PathResult(int id, int handle, PathStatus status) { /* … */ }
    }

    /// <summary>Lokale Vermeidung; MVP Separation+Alignment, Alpha ORCA (§4).</summary>
    public interface ISteering
    {
        void ComputeVelocities(Span<AgentState> agents, IFlowField field, int tick);
        // AgentState: Position, Velocity, Radius, UnitId – serialisierbarer Sim-State
    }

    /// <summary>Fassade des Subsystems im Sim-Tick.</summary>
    public interface IPathingSystem
    {
        PathResult RequestField(in PathRequest request);  // async via Time-Slicing möglich
        void TickUpdate(int tick);                        // Dirty-Recompute, Steering, Fills
    }
}
```

View-Seite (Unity) liest ausschließlich die resultierenden Positionen aus dem Sim-State; keine View-APIs in diesem Modul (D-033).

## 8. Jobs/Burst-Auslegung und CPU-Budget

- **Budget:** ≤ 4 ms CPU pro Sim-Tick für Grid-Updates + Feld-Fills + Steering (Unterbudget aus D-042.1, Gesamt-Sim ≤ 8 ms) bei 500 Einheiten Kalibrierung; das globale Match-Deckel liegt bei 600 Einheiten (D-048) und muss im V4-Spike als Worst Case mitgemessen werden (Messung im Phase-0-Spike).
- **Ausführungspfad (D-045):** Auslieferung und CI-Messung laufen **Managed-first**; Burst-Jobs sind nur hinter Feature-Flag aktiv (Toleranz-Parität ≤1e-4 im Hash-Vergleich). Alle Budget-Zahlen in diesem Abschnitt gelten daher für den Managed-Pfad.
- **Burst-Jobs:** (1) Clearance-Recompute pro Dirty-Region, (2) Dijkstra-Fill + Integration Pass pro Feld, (3) Spatial-Hash-Build, (4) Steering-Velocities über alle Agenten. Alle Jobs auf `NativeArray`-Views der Sim-Daten; allocation-frei, Pools aus dem Sim-Kern.
- **Parallelisierung:** Feld-Fills unterschiedlicher Felder parallel; Steering parallel über Agenten-Chunks; Write-Konflikte durch disjunkte Regionen/Chunking ausgeschlossen.
- **Amortisierung:** Max. N Feld-Fills bzw. Dirty-Recomputes pro Tick, Rest in Folgeticks (Deferred-Status in `PathResult`).
- **Assembly-Grenze:** Job-Strukturen leben in `Nova.Simulation`; die Job-Scheduling-Brücke (Unity.Burst/Jobs-APIs) sitzt in einem dünnen Host-Adapter, damit `Nova.SimRunner` (D-036) headless mit sequentiellem Fallback-Scheduler läuft. Konkrete Adapter-Form: Offener Punkt (s. unten).

## 9. Teststrategie

- **Golden-Paths:** Fixierte Szenarien (Karte, Seed, Command-Sequenz) mit erwarteten Feld-Kosten/Richtungen und Endpositionen; Regressionstests deterministisch wiederholbar, lauffähig unter `Nova.SimRunner` (D-036) im CI.
- **Engstellen-Stress:** 500 Einheiten durch minimale Chokepoint-Breite (3× Heavy-Radius) auf S- und L-Karte; Kriterien: kein Deadlock, Durchsatz-Schwelle, Tick-Zeit ≤ Budget.
- **Dirty-Stresstest:** fortlaufende Mauer-Setzung/Sprengung + Aetherium-Ausbreitung während Massenbewegung; Kriterium: partielles Recompute bleibt im Budget, keine stale Felder (Versionsprüfung).
- **Desync-Jagd:** identische Command-Sequenzen auf ARM (Apple Silicon) und x86 (Referenz-PC) müssen identische States liefern (D-033-Konsequenz; Float-MVP-Einschränkung beachten).
- **Unit-Tests:** Clearance-Berechnung, Dijkstra-Korrektheit (kleine Handgrids), Dirty-Region-Verschmelzung, Slot-Zuweisung.

## 10. HPA*-Erweiterungsoption (L-Karten)

Vorgemerkt, **nicht verplant** (D-034-Konsequenz): Bei nachgewiesenem Budget-Überschreiten der Dijkstra-Fills auf L-Karten (256²) kann das Grid in Regionen (z. B. 16×16 Tiles) abstrahiert werden; Fernweg-Planung auf Regionsebene, Verfeinerung lokal. Trigger ist ausschließlich die Spike-/Alpha-Messung, kein vorzeitiger Ausbau (Research §2.4A).

## Offene Punkte

1. **Exakte Einheitenradien je Klasse** hängen von finalen Unit-Maßen ab (GDD-Detailgrad); Richtwerte in §1.2 sind Platzhalter. Abstimmung mit Game Design nötig.
2. **Ziel-Cluster-Toleranz** für geteilte Flow Fields (wie nah müssen Ziel-Tiles beieinander liegen?) – Wert im Spike zu kalibrieren; die Wirtschafts-Anker (Feld/Raffinerie, §2) sind davon ausgenommen, sie sind feste Cluster.
3. **Burst-Brücke im Unity-freien Sim-Kern:** D-043 (`Nova.Simulation.Burst`) und D-045 (Managed-first, Burst nur Feature-Flag) haben das Ob geklärt; offen ist nur noch das Wie der Verschaltung (Hotspot-Vertrag im Kern, Injektion der Burst-Implementierung beim Match-Setup). Abstimmung mit System Architecture (Architecture.md/DependencyGraph.md), nicht eigenmächtig entschieden.
4. **Abgleich MemoryBudget.md – erledigt (Korrekturlauf Sprint 4):** MemoryBudget.md §3 ist auf 96 Felder / ~19 MB / RefCount-Policy (`MaxActiveFlowFields = 96`) nachgezogen; die 100-MB-Sim-Kappe wird auch mit ~19 MB eingehalten.
5. **Karten > 256 m** (falls GDD später größere L-Karten definiert): Speicher- und Fill-Budget neu bewerten, ggf. HPA* vorziehen.

~~Dichtekarte als Kostenaufschlag~~ → entschieden: Alpha-Plan mit Kostenrahmen (§3).
~~No-Fly-Kostenfeld-Pflege~~ → entschieden: Grid-Infrastruktur führend, Kampf-Modul liefert Flak-Reichweiten als Kosten-Layer (§6).

## Nächste Schritte

1. Sprint 4: Abstimmung mit Game Design zu Offenem Punkt 1 (Radien) und Level-Design-Regel Chokepoint-Breite.
2. Sprint 4: Klärung Offener Punkt 3 mit System Architecture (Burst-Injektionsform in Architecture.md/DependencyGraph.md festlegen; Rahmen: D-043, D-045).
3. Phase 0 / Sprint 7: Spike gemäß D-034 (Grid + Gruppen-Flow-Field + Separation, 500 Agenten Kalibrierung / 600 Worst Case, Messung Feld-Fill/Steering auf M-Serie-Mac und Windows-Referenz Ryzen 5 5600/RTX 3060, D-052); V4-Szenario „6 Parteien Vollwirtschaft + 3 Angriffe" mit Eviction-Thrash-Metrik (Fills/Tick); Erfolgskriterium ≤ 4 ms Sim-Anteil im Managed-Pfad (D-045), sonst Fallback-Evaluierung A* Pathfinding Project.
4. Alpha: ORCA-Umsetzung hinter `ISteering`, Dichtekarte umsetzen (§3), HPA*-Trigger prüfen.
5. Messergebnisse als Version 0.3.0 nachpflegen (Living Document).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead AI Programmer |
| 0.2.0 | 2026-07-21 | Korrekturlauf Sprint 4 (D-043–D-052, Review-Findings) | Lead AI Programmer |
