# Savegames & Replays

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead Technical Director | **Sprint:** 3

## Zweck

Definiert Umfang, Dateistruktur, Ablage und Lebenszyklus von Speicherständen und Replay-Dateien: Slot-Struktur, Autosave-Regeln, Versions-Header mit Migrationspfad (TPD §Wartung: Savegame-Versionierung), Korruptions-Schutz (TPD: Schutz vor beschädigten Spieldaten), Replay-Format/-Ablage und die Kompatibilitäts-Policy über Patches. Verbindlich für Sprint 7 (Sim-Kern) und die UI-/Service-Schicht.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-033 (serialisierbarer State, SP = lokaler Server), D-035 (Unity-freie Assembly), D-036 (SimRunner)
- [RTS_Technisches_Planungsdokument.md](../../RTS_Technisches_Planungsdokument.md) – Pflichtmodule Savegames/Replay-Grundlagen; Wartung: Savegame-Versionierung, Schutz vor beschädigten Spieldaten
- [../research/Multiplayer_Simulation.md](../research/Multiplayer_Simulation.md) – Replay = Seed + Befehlsstrom; Replays als Savegame-Grundlage
- [./GameState.md](./GameState.md) – snapshot-fähiger `WorldState`
- [./Serialization.md](./Serialization.md) – Binärformat, `SchemaVersion`, `ReplayHeader`, Checksummen-Basis
- [./Architecture.md](./Architecture.md) – Sim-Tick-Loop, Speicher-/Lade-Hooks (parallel, Sprint 3)

## Savegame-Umfang

Ein Savegame = **vollständiger Sim-Snapshot** (serialisierter `WorldState` gemäß GameState.md, Format gemäß Serialization.md) **+ Meta-Block**:

```csharp
public struct SaveGameMeta
{
    public SchemaVersion Version;        // Header, s. Serialization.md
    public string   GameVersion;         // Build-Nummer
    public uint     DefinitionsHash;     // GameDatabase-Version (Balance-Stand!)
    public string   SaveName;            // Spieler-vergeben oder "Autosave"
    public SaveKind Kind;                // Manual / Quick / Auto
    public DateTime SavedUtc;
    public string   MapId;               // für Slot-Vorschau
    public float    MatchElapsedSeconds; // für Slot-Vorschau
    public PlayerSummary[] Players;      // Fraktion/Team/Commander (Vorschau)
    public uint     Tick;                // Lade- = Weiterspiel-Tick
    // Optional (View-Komfort, NICHT sim-relevant, kein Hash-Bestandteil):
    public float    CameraX, CameraY, CameraZoom;
}
```

Bewusst **nicht** im Savegame: View-/UI-State (Selektion, UI-Fenster), Audio-State, abgeleitete Caches (Flow Fields, Clearance, Sicht-Raster) – diese werden nach dem Laden via `RebuildDerivedState()` (GameState.md) neu aufgebaut. Lade-Ablauf: Header prüfen → migrieren falls nötig → `WorldState` deserialisieren → Checksumme verifizieren → Derived State neu aufbauen → FoW/Sicht für das lokale Team einmalig neu rastern.

## Slot-Struktur

- Ablage: `Application.persistentDataPath/Saves/` (Win: `%userprofile%/AppData/LocalLow/<Studio>/Nova/Saves`, macOS: `~/Library/Application Support/<Studio>/Nova/Saves`), eine Datei pro Speicherstand (`*.novasave`), dazu `slots.json` als Index (Slot-Liste, Vorschau-Meta, Zeitstempel) – die Index-Datei ist rekonstruierbar aus den Savegame-Headern (Selbstheilung bei Index-Korruption).
- Slots: **N manuelle Slots** (Vorschlag 20, UI-Entscheidung Sprint 4), **1 Quicksave** (rotierend auf 2 Dateien `quicksave_a/b`, s. Korruptions-Schutz), **3 Autosaves** (rolling `autosave_1..3`).
- Profil-Trennung: Saves sind profilgebunden (`Saves/<ProfileId>/`), sobald das Profilsystem (Kampagne/Metafortschritt) spezifiziert ist – bis dahin ein Default-Profil.

## Autosave-Regeln

- **Intervall:** alle 5 min Matchzeit (300 s = 3.000 Ticks), konfigurierbar (Einstellungen, 1–15 min), rolling über 3 Slots.
- **Ereignis-Trigger (Skirmish/Kampagne):** nach Missionsziel-Abschluss, vor Boss-/Superwaffen-Ereignissen (soweit vom Missions-Skript markiert).
- **Nie** während eines laufenden Ticks: Autosave wird am Tick-Ende eingeplant und zwischen zwei Ticks ausgeführt (D-033-Disziplin; Speichern darf die Sim nicht mutieren).
- **Kostenrahmen:** Snapshot-Serialisierung ist synchron auf dem Main-Thread zwischen Ticks; Ziel < 50 ms bei L-Karte/500 Einheiten – Messung in Sprint 7, sonst Serialisierung in Worker-Thread auslagern (State ist flach/kopierbar).
- Kein Autosave in Multiplayer-Matches (Beta); Replays übernehmen dort die Absicherung.

## Versions-Header und Migrationspfad

- Header gemäß Serialization.md: Magic, `SchemaVersion`, `GameVersion`, `DefinitionsHash`, `ContentKind`.
- **Ladeentscheidung (in dieser Reihenfolge):**
  1. Magic unbekannt / Checksumme ungültig → Datei korrupt (s. u.).
  2. `SchemaVersion.Major` < aktuell → lineare Migration `v(n)→…→Current` (Migratoren-Kette, Serialization.md); Erfolg → laden, Fehlschlag → Savegame als inkompatibel melden.
  3. `DefinitionsHash` ≠ aktuell → Balance-Patch seit Speicherung → **nicht ladbar** (Policy s. u.), dem Spieler mit Hinweistext anzeigen ("Match-Stand basiert auf älterer Balance-Version").
- Migrationen werden pro Schema-Major als Fixture im SimRunner getestet (alte Referenz-Savegames im Repo, Roundtrip auf `Current`, D-036).

## Korruptions-Schutz

- **Checksumme:** xxHash32 über den gesamten Datei-Payload (Meta + State), im Header gespeichert; Verifikation vor jeder Deserialisierung.
- **Atomares Schreiben:** Schreiben in `*.tmp` im selben Verzeichnis, dann `fsync` + atomares Umbenennen – ein Absturz während des Speicherns hinterlässt nie eine halbe Zieldatei.
- **Rotierende Sicherung:** Quicksave/Autosave schreiben immer auf den älteren von zwei Slots; vor dem Überschreiben eines manuellen Slots wird die Vorgängerdatei als `*.bak` behalten (1 Generation).
- **Fallback beim Laden:** Slot korrupt → automatischer Versuch mit `*.bak` bzw. dem jüngsten Autosave; dem Spieler wird die Wiederherstellung transparent gemeldet. Dauerhaft korrupte Dateien werden nach `Saves/quarantine/` verschoben statt gelöscht (Support-/Debug-Zugriff).

## Replay-Datei-Format und -Ablage

- Format gemäß Serialization.md: `ReplayHeader` + `CommandRecord`-Strom + `HashCheckpoint`s, Dateiendung `*.novareplay`, Ablage `Application.persistentDataPath/Replays/`.
- **Aufzeichnung:** automatisch für jedes Match (SP und Beta-MP), Dateiname `yyyyMMdd_HHmmss_<MapId>_<MatchType>.novareplay`; Aufzeichnungspflicht aus D-033 (Lockstep liefert Replays gratis) und Research (Test-Fixtures/Desync-Tooling).
- **Aufbewahrung:** Vorschlag – die letzten 25 Replays automatisch behalten, ältere löschen; "Favorit"-Markierung verhindert Löschung (UI-Detail Sprint 4+).
- **SimRunner-Nutzung (D-036):** KI-vs-KI-Nachtläufe schreiben Replays + Match-Result in CI-Artefakte; Desync-Fälle hinterlegen Replay + divergierenden HashCheckpoint als Fixture.
- **Observer (Beta):** Replay-Datei ist zugleich das Observer-Format (verzögertes Einspielen des Command-Stroms) – kein separates Format.

## Kompatibilitäts-Policy

| Patch-Art | Beispiel | Savegames | Replays |
|---|---|---|---|
| **Balance-Patch** (GameDatabase-Werte: Kosten, HP, Schaden) | Harvester-Tuning | **inkompatibel** – kein Ladeversuch, `DefinitionsHash`-Mismatch mit Hinweisdialog | **inkompatibel** zur Wiedergabe (Command-Strom würde bei neuen Werten divergieren); Datei bleibt archivierbar |
| **Tech-Patch mit Schema-Änderung** (State-Struktur) | neues Feld in `UnitState` | ladbar **nach Migration** (Migratoren-Kette, Major-Bump) | ladbar nach Migration, HashCheckpoints alter Versionen werden übersprungen |
| **Tech-Patch ohne Schema-Änderung** (Bugfix, `Minor`-Bump) | Pfadfindungs-Fix ohne State-Änderung | voll kompatibel | voll kompatibel (außer der Bugfix ändert Sim-Ergebnisse → dann wie Balance-Patch behandeln und im Changelog kennzeichnen) |

Begründung: Savegames über Balance-Patches hinweg weiterzutragen würde Matches mit gemischtem Regelstand erzeugen (inkonsistente Wirtschaft/HP-Verhältnisse, KI-Fehlverhalten) – der Hash-Vergleich ist billig und eindeutig. Tech-Migrationen sind dagegen reine Struktur-Übersetzungen und regelneutral.

## Offene Punkte

- **Kampagnen-/Metafortschritt:** Kampagne.md sieht persistenten Fortschritt außerhalb einzelner Matches vor; Ablage (separates Profil-Savegame vs. Meta-Block) ist nicht Gegenstand dieses Dokuments und beim Profilsystem (Sprint 4+) zu entscheiden.
- **Cloud-Saves (Steam Cloud o. ä.):** nicht entschieden; Größenbudget und Sync-Konflikte mit `slots.json` erst nach Plattform-Entscheidung bewertbar.
- **Replay-Kompatibilität über Balance-Patches:** Alternativmodell "Replay speichert Definitions-Snapshot" (alte Balance-Werte in der Replay-Datei) würde alte Replays abspielbar halten, erhöht aber Größe/Komplexität – nicht entschieden, Abwägung nach erster Größenmessung.
- **Autosave-Threading:** Auslagerung in Worker-Thread nur falls das 50-ms-Budget reißt; Thread-Snapshot erfordert Copy-on-Save des `WorldState` – Design folgt mit Messung.
- **Slot-Anzahl/Obergrenzen:** 20 manuelle Slots + Replay-Aufbewahrung 25 sind Vorschläge; finale Werte mit UI/UX (Sprint 4).

## Nächste Schritte

- Sprint 7: Save/Load-Pfad (atomares Schreiben, Checksumme, `RebuildDerivedState`) zusammen mit dem Serializer implementieren; Messung Snapshot-Größe/-Dauer (L-Karte, 500 Einheiten) und Dokumentation in v0.2.
- SimRunner-Fixture-Set: Referenz-Savegames je Schema-Version + KI-Match-Replays als CI-Artefakte etablieren (D-036).
- Offene Punkte Cloud-Saves/Replay-Definitions-Snapshot als Eingabe für OpenQuestions.md übergeben.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead Technical Director |
