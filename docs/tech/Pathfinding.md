# Technical Design: Pathfinding & Bewegung

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead AI Programmer | **Sprint:** 3

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

Statische Layer pro Tile (ungepackt 7 B): `TerrainCost` (u8, 0 = unpassierbar), `Clearance[3]` (je u8, max. passierbarer Radius in dm je Radienklasse), `Height` (u8), `Flags` (u8: Wasser, unbuildable, NoFlyZone o. ä.), `ZoneId` (u8, Biom/Aetherium-Zone). Budgetannahme: ≤ 32 gleichzeitig aktive Flow Fields → L-Karte ~6 MB dynamisch; auf Desktop unkritisch (bestätigt Research §2.2).

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
- **Pooling & Caching:** Felder werden aus einem Pool allokiert (kein GC im Tick), anhand von `(ZielCluster, RadienKlasse)` gecacht und wiederverwendet; Feld-RefCount über zugewiesene Gruppen.
- **Kosten-Invalidierung:** Bei Dirty-Regionen (s. §3) wird das betroffene Feld **lokal** neu gefüllt: begrenzter Dijkstra-Restart ab der Region-Grenze, kein Voll-Update. Felder ohne Referenzen werden freigegeben.
- **Time-Slicing:** Feld-Fills laufen als Burst-Jobs und werden über Ticks amortisiert; Einheiten folgen 1–2 Ticks dem alten Feld (visuell irrelevant, Research §4.1).

## 3. Dynamische Hindernisse (Dirty-Flagging)

Ereignisgetrieben, niemals Voll-Scan (D-034-Konsequenz). Alle Quellen melden AABB-Regionen an den `IPathGrid`-Dirty-Mechanismus; betroffene Clearance-Layer und aktive Flow Fields werden markiert und im nächsten Update-Fenster partiell neu berechnet:

- **Mauerbau/-zerstörung:** Platzierung setzt Tiles unpassierbar; während des Baus gilt Kostenstrafe statt "unpassierbar" (Bauarbeiter können durch, Research §4.3). Zerstörung gibt Tiles frei.
- **Trümmer (D-012):** Trümmer-Felder = erhöhte Kosten statt Sperrung (passierbar, aber langsamer); Verfall räumt Tiles schrittweise frei.
- **Evolvierte-Keime / Wachstumsbauweise:** Keim-Zonen blockieren Platzierung und melden wachsende Dirty-Regionen bei Ausdehnung.
- **Aetherium-Ausbreitung:** Kristallwachstum kann Gelände blockieren/umformen (GDD); jede Wachstumsstufe meldet ihre Tile-Region. Überernte/Abbau melden entsprechend Freigaben.
- **Vegetationsbrände:** brennende Tiles temporär hohe Kosten; abgebrannte Tiles danach frei/niedrig.

Stehende Einheiten sind **keine** Grid-Hindernisse; Einheit-gegen-Einheit regelt ausschließlich die lokale Vermeidung (§4). Eine Dichtekarte (Einheiten/Tile, im Sicht-Tick aktualisiert) kann später als weicher Kostenaufschlag für Umlenkung dienen – Alpha-Option, nicht MVP.

## 4. Lokale Vermeidung (Steering)

- **MVP (D-034):** einfache Separation + Alignment (Boids-light) über Spatial Hash (Grid-basiertes Bucketing, kein O(n²)); Geschwindigkeitsclamp, keine Kollisionsgarantie. Idle stehende Einheiten weichen aktiv ausweichenden Einheiten minimal aus (kooperatives Wegdrängen, SC2-Vorbild).
- **Alpha (D-034):** Umstieg auf ORCA (RVO2-Prinzip) hinter derselben `ISteering`-Schnittstelle; Eigenbau in Fixed-Point-fähiger Form, kein Fremd-Asset im Sim-Pfad. Austauschbarkeit ist Designziel der Schnittstelle.
- **Determinismus:** Steering arbeitet ausschließlich auf serialisierbarem Sim-State (Positionen, Geschwindigkeiten, Radien) in fester Tick-Reihenfolge; Iterationsreihenfolgen über Spatial-Hash-Buckets sind stabil zu definieren (Sortierung nach UnitId).

## 5. Formationen

- Gruppen-Flow-Field bleibt identisch für alle Einheiten der Gruppe; **Slots** relativ zum Gruppenzentrum (Ziel-Tile) variieren die Zielzelle pro Einheit leicht (Research §2.4B).
- MVP: lockere Slot-Auflösung (Spaltenaufstellung um das Ziel, Slot-Zuweisung nach UnitId sortiert → deterministisch); kein starres Formationshalten unterwegs, das Feld führt den Verband.
- Slot-Struktur ist reine Sim-Daten (serialisierbar); Formationsprofile ggf. später als Definitions-only-SO.

## 6. Lufteinheiten

Separater **2.5D-Steering-Layer** (D-034): kein Boden-Pathfinding, direkte Zielansteuerung mit eigener Separation innerhalb der Luftstaffel. Flughöhen sind konstante Höhenebenen je Lufteinheiten-Typ (kein kontinuierliches Höhen-Pathfinding im MVP). No-Fly-Zonen (Flak-Reichweiten, Sperrgebiete) werden als separates Kostenfeld auf demselben Grid gepflegt und erzeugen Umfleug-Vektoren. Boden-Grid-Updates beeinflussen Luft nur über No-Fly-Flags (§1.1).

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

- **Budget:** ≤ 2–4 ms CPU pro Sim-Tick für Grid-Updates + Feld-Fills + Steering bei 500 Einheiten (D-034, Research §4.1; Messung im Phase-0-Spike).
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
2. **Ziel-Cluster-Toleranz** für geteilte Flow Fields (wie nah müssen Ziel-Tiles beieinander liegen?) – Wert im Spike zu kalibrieren.
3. **Burst-Brücke im Unity-freien Sim-Kern:** `Unity.Burst`/`Unity.Jobs` sind Unity-Pakete; die strikte Regel "keine UnityEngine-APIs im Sim-Pfad" (D-033) gegen "Jobs/Burst für Hotspots" (D-034/D-035) erfordert eine Architektur-Abstimmung (Adapter-Assembly vs. Burst-Referenz im Sim-Kern). Nicht eigenmächtig entschieden.
4. **Dichtekarte als Kostenaufschlag** (Umlenkung in Staus): Alpha-Option, Aufwand/Nutzen offen.
5. **No-Fly-Kostenfeld-Pflege:** Wer ist führendes System für Flak-Reichweiten-Änderungen (Waffensystem vs. Pathing)? Schnittstelle zu klären.
6. **Karten > 256 m** (falls GDD später größere L-Karten definiert): Speicher- und Fill-Budget neu bewerten, ggf. HPA* vorziehen.

## Nächste Schritte

1. Sprint 4: Abstimmung mit Game Design zu Offenem Punkt 1 (Radien) und Level-Design-Regel Chokepoint-Breite.
2. Sprint 4: Klärung Offener Punkt 3 mit System Architecture (Burst-Adapter in CodingGuidelines.md/Assembly-Struktur festlegen).
3. Phase 0 / Sprint 7: Spike gemäß D-034 (Grid + Gruppen-Flow-Field + Separation, 500 Agenten, Messung Feld-Fill/Steering auf M-Serie-Mac und Windows-Referenz); Erfolgskriterium ≤ 2–4 ms Sim-Anteil bei 60 FPS, sonst Fallback-Evaluierung A* Pathfinding Project.
4. Alpha: ORCA-Umsetzung hinter `ISteering`, Dichtekarte evaluieren, HPA*-Trigger prüfen.
5. Messergebnisse als Version 0.2.0 nachpflegen (Living Document).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead AI Programmer |
