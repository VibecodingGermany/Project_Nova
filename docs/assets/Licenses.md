# Lizenz-Register

**Version:** 1.0.0 | **Status:** sprint-freigegeben (laufend fortzuschreiben) | **Verantwortungsbereich:** Producer / Technical Director | **Sprint:** 5

## Zweck

Zentrales **Lizenz-Register** für alle externen Asset-Quellen von *Project Nova*: Lizenzmodell, Seat-Regeln, Attributionspflichten, Weitergabe-/Repo-Beschränkungen und offene Lizenz-Detailfragen je Quelle. Dieses Dokument ist ein verbindliches Sprint-5-Exit-Kriterium und wird **bei jedem realen Kauf fortgeschrieben** (eine Zeile pro erworbenem Paket/Quelle). Es ist die Freigabe-Grundlage dafür, was in ein öffentliches Art-Verzeichnis darf und was nicht.

Solange kein realer Kauf erfolgt ist (Käufe frühestens Phase 0/Sprint 7, [ProcurementStrategy.md](ProcurementStrategy.md) §2.6), erfasst dieses Register die **Lizenz-Rahmenbedingungen pro Quelltyp** als Kaufvorbereitung – noch keine konkreten Käufe.

## Abhängigkeiten

- [ProcurementStrategy.md](ProcurementStrategy.md) – Strategie B (D-053), Repo-Hygiene §5
- [AssetRegister.md](AssetRegister.md) – welche Kategorie aus welcher Quelle bezogen wird
- [../research/AssetStore_Landschaft.md](../research/AssetStore_Landschaft.md) – Lizenzfallen-Analyse (§Querschnitt Punkt 2)
- [../tech/AssetBudget.md](../tech/AssetBudget.md) §6 – Lizenz-Kriterium der Kauf-Prüfung

## 1. Lizenz-Rahmen je Quelle

| Quelle | Lizenzmodell | Seats | Kommerziell | Attribution | Weitergabe / Repo | Restricted-Assets prüfen? |
|---|---|---|---|---|---|---|
| **Unity Asset Store** | Standard-Asset-Store-EULA (per Seat) | „Seat 1" im Checkout; Team/Externe nachlizenzieren | ja | nein | Runtime-Content im Spiel unbegrenzt verteilbar; **Rohdaten nicht in öffentliche Repos** | **ja** (EULA §2.2.2) |
| **Synty Store** | Synty-Publisher-EULA | **5 Seats/Lizenz** | ja | nein | wie oben; Rohdaten privat halten | – |
| **Humble Bundle (Synty)** | Publisher-EULA (meist Synty) | wie Synty (Keys publisherseitig einlösen) | ja | nein | Seat-Verwaltung beachten | – |
| **Fab (Epic)** | Fab Standard License (**pro Produkt** prüfen) | pro Produkt | i. d. R. ja | pro Produkt | pro Produkt; UE-lastig | **ja** (pro Produkt) |
| **Sketchfab** | CC-BY / CC0 / Paid – **pro Modell** | pro Modell | pro Lizenz | **CC-BY: Pflicht** (Credits) | pro Lizenz | – |
| **itch.io (Kenney/Quaternius)** | häufig **CC0**, je Pack individuell | – | ja | CC0: nein | CC0 unkritisch; kein Unity-Package-Format | – |
| **Sonniss GDC Bundle** | royalty-free (kommerziell, keine Attribution) | – | ja | nein | **nicht weitervertreibbar → nie in öffentliches Repo** | – |
| **Mixamo (Adobe)** | kostenlos, kommerziell im gerenderten Spiel | – | ja | nein | **Rohdaten (Rigs/Clips) nicht weitergeben** → geteilte Repos mit Externen prüfen | – |
| **Composer-/VO-Auftrag** | Werkvertrag (Buy-out anstreben) | – | ja (per Vertrag) | vertragsabhängig | Vertrag muss interaktive Nutzung + Buy-out abdecken | – |

## 2. Verbindliche Lizenz-Regeln

1. **Kein Rohdaten-Upload in das öffentliche Repo.** Asset-Store-/Synty-/Sonniss-/Mixamo-Rohdaten gehören ausschließlich in das private Asset-Repo (LFS). Der `.gitignore` des öffentlichen Repos hält Art-Binärordner draußen ([ProcurementStrategy.md](ProcurementStrategy.md) §5).
2. **CC-BY = Attribution-Pflicht.** Jedes CC-BY-Modell (v. a. Sketchfab) wird beim Erwerb in einem `CREDITS.md` (ab erstem CC-BY-Kauf anzulegen) mit Autor, Titel, Quelle und Lizenz-URL erfasst.
3. **Seat-Disziplin.** Synty = 5 Seats/Lizenz; bei Team-Wachstum/Externen nachlizenzieren. Editor-Tools (z. B. Terrain-Tooling) sind streng per Seat – nie über die Lizenzmenge hinaus installieren.
4. **Restricted Assets** (Asset-Store-EULA §2.2.2) und **Fab-Einzellizenzen** werden vor Kauf auf abweichende Bedingungen geprüft; das Ergebnis kommt in §3.
5. **Keine RTS-Komplett-Frameworks** – nicht nur Architektur- (D-053), sondern auch Lizenzgrund: Code-Kits binden das Projekt an fremde EULA-/Update-Zyklen im Sim-Kern.
6. **Interactive-Klausel bei Musik.** Store-Musik trägt teils „nicht für Interactive Media" – Lizenztext vor Kauf lesen; im Zweifel Composer-Auftrag mit Buy-out.

## 3. Erworbene Lizenzen (Ledger)

_Noch keine realen Käufe – Beschaffung ab Phase 0/Sprint 7._ Jede erworbene Lizenz erhält hier eine Zeile:

| Datum | Paket/Quelle | Lizenztyp | Seats | Kosten | Attribution nötig? | Repo-Regel | Nachweis/Order-ID |
|---|---|---|---|---|---|---|---|
| – | – | – | – | – | – | – | – |

## Offene Punkte

- **Fab-Standard-License-Detailtext** für Unity-Nutzung und aktuelle Megascans-Bedingungen (Markt rotiert; Stand Juli 2026) – Detailprüfung zum Beschaffungszeitpunkt.
- **Mixamo in geteilter Pipeline:** Rohdaten-Weitergabe an externe Dienstleister lizenzrechtlich final klären, bevor Externe hinzukommen (koppelt an Seat-Planung **Q-036**).
- **Composer-/VO-Vertragsmuster** (Buy-out, interaktive Nutzung, Nachvertonung) ist noch nicht erstellt – Sprint 6, sobald Signature-Audio beauftragt wird.
- **`CREDITS.md`** wird erst mit dem ersten CC-BY-Kauf angelegt (keine Platzhalter-Dokumente, [../meta/DocumentationStandard.md](../meta/DocumentationStandard.md) Grundprinzip 5).

## Nächste Schritte

1. Sprint 6: Composer-/VO-Vertragsmuster vorbereiten; Seat-Planung (Q-036) festlegen; privates Asset-Repo + `.gitignore`-Regeln für das öffentliche Repo finalisieren.
2. Phase 0/Sprint 7: Beim ersten Kauf §3-Ledger befüllen; bei erstem CC-BY-Asset `CREDITS.md` anlegen.
3. Laufend: Jede Kauf-Prüfung ([../tech/AssetBudget.md](../tech/AssetBudget.md) §6) endet mit einem §3-Eintrag hier.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-22 | Erstfassung Sprint 5: Lizenz-Rahmen je Quelle, verbindliche Lizenz-Regeln, leeres Erwerbs-Ledger angelegt | Producer / Technical Director |
