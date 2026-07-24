# Lizenz-Register

**Version:** 1.1.0 | **Status:** sprint-freigegeben (laufend fortzuschreiben) | **Verantwortungsbereich:** Producer / Technical Director / Project Owner | **Sprint:** 5

## Zweck

Zentrales **Lizenz-Register** für alle externen und KI-generierten Asset-Quellen von *Project Nova*: Lizenzmodell, Seat-Regeln, Attributionspflichten, Weitergabe-/Repo-Beschränkungen und offene Lizenz-Detailfragen je Quelle (gemäß D-054: 0 € Open-Source & KI-Pipeline). Dieses Dokument ist ein verbindliches Sprint-5-Exit-Kriterium und wird **bei jedem Asset-Import fortgeschrieben**. Es ist die Freigabe-Grundlage dafür, welche Assets im öffentlichen Git-Repo liegen dürfen.

## Abhängigkeiten

- [ProcurementStrategy.md](ProcurementStrategy.md) – Strategie B-Zero (D-054), Repo-Hygiene §5
- [AssetRegister.md](AssetRegister.md) – welche Kategorie aus welcher Quelle bezogen wird
- [../research/AssetStore_Landschaft.md](../research/AssetStore_Landschaft.md) – Lizenzfallen-Analyse (§Querschnitt Punkt 2)
- [../tech/AssetBudget.md](../tech/AssetBudget.md) §6 – Lizenz-Kriterium der Prüfung

## 1. Lizenz-Rahmen je Quelle

| Quelle | Lizenzmodell | Seats | Kommerziell | Attribution | Weitergabe / Öffentliches Repo |
|---|---|---|---|---|---|
| **Quaternius / Kenney** | **CC0 (Public Domain)** | unbegrenzt | ja | nein | **Vollständig öffentlich im GitHub-Repo erlaubt** |
| **KI-3D (Hunyuan3D)** | Open Source / Public Domain | unbegrenzt | ja | nein | **Vollständig öffentlich im GitHub-Repo erlaubt** |
| **KI-Tools (Meshy, SD)** | Commercial Free Tier / Custom | unbegrenzt | ja | nein | **Vollständig öffentlich im GitHub-Repo erlaubt** |
| **Sonniss GDC Bundle** | Royalty-Free Audio | unbegrenzt | ja | nein | Öffentliches Repo erlaubt (lizenzfrei) |
| **Mixamo (Adobe)** | Kostenlos für Games | unbegrenzt | ja | nein | **Rohdaten (FBX/Rigs) nicht als lose Packs verteilen**, im Game-Build unbegrenzt |
| **Sketchfab (CC-BY)** | CC-BY | unbegrenzt | ja | **ja (Credits)** | Öffentlich erlaubt mit Attribution in `CREDITS.md` |

## 2. Verbindliche Lizenz-Regeln (D-054)

1. **Öffentliche Repository-Tauglichkeit.** Alle CC0- und KI-generierten Assets dürfen direkt im öffentlichen GitHub-Repository (`VibecodingGermany/Project_Nova`) geteilt werden.
2. **CC-BY = Attribution-Pflicht.** Jedes CC-BY-Modell (v. a. Sketchfab) wird beim Erwerb/Import in `CREDITS.md` (ab erstem CC-BY-Import) mit Autor, Titel, Quelle und Lizenz-URL erfasst.
3. **Keine Per-Seat-Kaufkosten (0 € Budget).** Es werden keine kostenpflichtigen Per-Seat-Store-Packs erworben.
4. **Mixamo-Nutzung.** Mixamo-Clips dürfen im Unity-Projekt eingebunden und gerendert werden; eine Weitergabe loser Raw-Clips an Dritte außerhalb des Projekts ist zu vermeiden.

## 3. Erworbene Lizenzen / Asset-Imports (Ledger)

_Import-Protokoll – laufend zu befüllen._ Jede freigegebene CC0-/KI-Quelle erhält hier eine Zeile:

| Datum | Paket/Quelle | Lizenztyp | Seats | Kosten | Attribution nötig? | Repo-Freigabe |
|---|---|---|---|---|---|---|
| 2026-07-24 | Quaternius Sci-Fi & Kenney Kits | CC0 | unbegrenzt | 0 € | nein | Ja (öffentliches Repo) |

## Offene Punkte

- **`CREDITS.md`** wird mit dem ersten CC-BY-Import angelegt (keine Platzhalter-Dokumente, [../meta/DocumentationStandard.md](../meta/DocumentationStandard.md)).

## Nächste Schritte

1. Sprint 6: CC0/KI-Pipeline-Vorgaben in Produktionsplanung übernehmen; öffentliche Repo-Struktur finalisieren.
2. Phase 0/Sprint 7: Bei erstem CC-BY-Asset `CREDITS.md` anlegen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-22 | Erstfassung Sprint 5: Lizenz-Rahmen je Quelle, verbindliche Lizenz-Regeln, leeres Erwerbs-Ledger angelegt | Producer / Technical Director |
| 1.1.0 | 2026-07-24 | Update auf D-054 (0 € Open-Source & KI-Pipeline), CC0- & KI-Lizenz-Regeln für öffentliches Repo ergänzt | Project Owner / Producer |
