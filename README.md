# Project Nova

> Modernes Echtzeitstrategiespiel (RTS) mit Basisbau, drei Fraktionen und der lebendigen Kristallressource **Aetherium**. *Project Nova* ist der Arbeitstitel.

**Phase:** Konzeption & Produktionsvorbereitung · **Status:** Sprint 5 (Asset Audit) abgeschlossen · **Repo:** öffentlich (Community-Projekt)

---

## Worum es geht

*Project Nova* ist ein Echtzeitstrategie- und Base-Building-Spiel im Geist klassischer RTS-Titel, technisch neu aufgesetzt auf **Unity 6.3 LTS (C#, URP)**. Kernelemente:

- Große Karten mit schräger Top-Down-/Isometrie-Kamera
- Basisbau, Ressourcenabbau und Produktionsketten rund um die Ressource **Aetherium**
- Drei spielbare Fraktionen mit eigener Identität und Commander-System
- Infanterie, Fahrzeuge, Luftfahrzeuge, Verteidigungsanlagen
- KI-Gegner und Multiplayer, Gefechte mit vielen gleichzeitigen Einheiten

> **Wichtig:** Dieses Repository befindet sich in der **Design- und Planungsphase**. Es enthält **noch keinen Spielcode** – die Implementierung ist als Sprint 7 geplant. Der gesamte aktuelle Wert liegt in der strukturierten, konsistenten Dokumentation unter [`docs/`](docs/).

## Einstieg in die Dokumentation

Das gesamte Wissen ist ein **Wiki aus vielen kleinen, verlinkten Living Documents** (Prinzip statt Monolithen). Startpunkte:

| Einstieg | Beschreibung |
|---|---|
| **[docs/README.md](docs/README.md)** | Zentraler Wiki-Index – von hier aus ist alles erreichbar |
| [docs/meta/DocumentationStandard.md](docs/meta/DocumentationStandard.md) | Verbindlicher Dokumentationsstandard (Aufbau, Versionierung, Sprache) |
| [docs/vision/Vision.md](docs/vision/Vision.md) | Leitbild, Design-Säulen, Anti-Ziele |
| [docs/gamedesign/Factions.md](docs/gamedesign/Factions.md) | Fraktionen (Master-Dokument des Game Designs) |
| [docs/production/DecisionLog.md](docs/production/DecisionLog.md) | Alle getroffenen Entscheidungen (D-001 ff.) mit Alternativen |
| [docs/production/SprintPlanning.md](docs/production/SprintPlanning.md) | Sprint-Definitionen, Ziele und Exit-Kriterien |

## Repository-Struktur

```
Project Nova/
├── README.md              ← diese Datei (GitHub-Startseite)
├── AGENTS.md              ← Arbeitsregeln für KI-Agenten & Mitwirkende
├── CHANGELOG.md           ← Änderungshistorie (Keep a Changelog)
├── RTS_*.md               ← historische Quelldokumente (Ausgangsbasis)
└── docs/
    ├── README.md          ← Wiki-Index
    ├── meta/              ← Dokumentationsstandard
    ├── analysis/          ← Wissensbasis, Gap-/Inkonsistenzanalyse (Sprint 0)
    ├── research/          ← Technologie- & Markt-Research (Sprint 1)
    ├── vision/            ← Leitbild, USP, Zielgruppe, Game Loop (Sprint 2)
    ├── gamedesign/        ← vollständiges GDD (Sprint 2)
    ├── tech/              ← Technical Design (Sprint 3) + review/ (Architecture Review, Sprint 4)
    ├── assets/            ← Asset Audit: Register, Strategie, Lizenzen, Build-Backlog (Sprint 5)
    └── production/        ← Sprint-Planung, Entscheidungen, Risiken, Sprint-Berichte
```

## Projektstatus

| Sprint | Thema | Status |
|---|---|---|
| 0 | Projektinitialisierung & Analyse | ✅ abgeschlossen |
| 1 | Research | ✅ abgeschlossen |
| 2 | Game Design (GDD) | ✅ abgeschlossen |
| 3 | Technical Design | ✅ abgeschlossen |
| 4 | Architecture Review | ✅ abgeschlossen |
| 5 | Asset Audit | ✅ abgeschlossen |
| 6 | Produktionsplanung | 🟢 bereit (GO) |
| 7 | Implementierung | ⛔ blockiert bis Sprint 6 |

Details und Exit-Kriterien: [docs/production/SprintPlanning.md](docs/production/SprintPlanning.md).

## Tech-Stack (geplant)

- **Engine:** Unity 6.3 LTS · **Sprache:** C# · **Render-Pipeline:** URP
- **Architektur-Prämisse:** Vier-Säulen-Architektur mit Unity-freiem, deterministischem Simulationskern (`Nova.Simulation`)
- **In Sprint 3 entschieden (D-033–D-042):** Multiplayer-Simulationsmodell, Pathfinding-Verfahren, ECS/DOTS-Frage

## Arbeitsweise

Die Entwicklung läuft **KI-gestützt** über Coding-Agenten. Verbindliche Regeln für Commits, Branches, CHANGELOG-Pflege und Dokumentationsdisziplin stehen in **[AGENTS.md](AGENTS.md)** – jeder Agent und jede mitwirkende Person liest diese Datei zuerst. Alle Änderungen laufen über **Pull Requests** (kein direkter `main`-Push); der Team-Ablauf steht in **[CONTRIBUTING.md](CONTRIBUTING.md)**.

Grundprinzipien:
- **Living Documents:** Jede Erkenntnis/Entscheidung wird sofort dokumentiert und versioniert – Doku ist nie „fertig".
- **Entscheidungen mit Alternativen:** Jede relevante Entscheidung landet mit ≥3 geprüften Alternativen im [DecisionLog](docs/production/DecisionLog.md).
- **Sprache:** Deutsch für Projektdokumente, Englisch für Code/Identifier/Pfade.

## Änderungshistorie

Siehe [CHANGELOG.md](CHANGELOG.md). Die Versionsnummern folgen dem Dokumentationsstand des Wikis (aktuell `0.6.0`).

## Mitmachen

Öffentliches **Community-Projekt** der Organisation **VibecodingGermany**. Beiträge sind willkommen – bitte zuerst [CONTRIBUTING.md](CONTRIBUTING.md) und [AGENTS.md](AGENTS.md) lesen. Alle Änderungen laufen über Pull Requests.

## Lizenz

© 2026 VibecodingGermany / Dennis Westermann. Eine formale Lizenz ist **noch festzulegen** (`LICENSE` folgt). Bis dahin: Ansehen und Mitwirken per Pull Request ausdrücklich erwünscht; keine Weiterverbreitung als eigenes Werk ohne Absprache.
