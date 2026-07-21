# AGENTS.md – Arbeitsregeln für KI-Agenten & Mitwirkende

Diese Datei ist die **verbindliche Betriebsanleitung** für jeden KI-Coding-Agenten
(Kimi, Claude, Cursor, Codex u. a.) und jede Person, die an *Project Nova* arbeitet.
**Lies diese Datei zuerst, bevor du irgendeine Änderung machst.** Sie wird von den
gängigen Agenten-Tools automatisch als Kontext geladen (`AGENTS.md`-Standard).

Ziel dieser Regeln: ein **dauerhaft sauberes GitHub-Repository** mit
nachvollziehbarer Historie, gepflegtem Changelog und konsistenter Dokumentation –
auch wenn viele verschiedene Agenten-Sessions daran arbeiten.

---

## 1. Projekt in einem Absatz

*Project Nova* (Arbeitstitel) ist ein Echtzeitstrategiespiel (Unity 6.3 LTS, C#, URP)
mit Basisbau, drei Fraktionen und der Ressource **Aetherium**. Das Repo befindet sich
in der **Design-/Planungsphase**: Es enthält **noch keinen Spielcode**, sondern ein
strukturiertes Dokumentations-Wiki unter [`docs/`](docs/). Implementierung ist Sprint 7.
Der aktuelle Fokus ist Sprint 3 (Technical Design).

## 2. Goldene Regeln (nicht verhandelbar)

1. **Push nach Versionsbump ist dauerhaft freigegeben.** Der Projektinhaber hat am
   2026-07-21 ausdrücklich und dauerhaft angeordnet: Nach jedem Versionsbump
   (Sprint-Abschluss, Release-Tag, Wiki-Versionserhöhung) wird der Stand committet und
   zu GitHub gepusht – ohne erneute Einzelfreigabe. Für alle anderen Pushes
   (zwischenzeitliche Feature-Branches, experimentelle Arbeit) gilt weiterhin: `git push`
   nur nach expliziter Freigabe. Committen lokal ist jederzeit erlaubt.
2. **Niemals `main` mit `--force` überschreiben.** Keine History-Rewrites auf geteilten
   Branches. `main` bleibt jederzeit in einem konsistenten Zustand.
3. **Keine Secrets ins Repo.** Keine Tokens, Keys, `.env`-Inhalte, Passwörter oder
   Zugangsdaten – auch nicht in Beispielen oder Commit-Messages.
4. **CHANGELOG immer mitpflegen.** Jede inhaltliche Änderung ergänzt einen Eintrag unter
   `[Unreleased]` in [CHANGELOG.md](CHANGELOG.md) (siehe §6). Undokumentierte Änderungen
   gelten als nicht erfolgt.
5. **Dem Dokumentationsstandard folgen.** Alle Doku-Änderungen halten sich an
   [docs/meta/DocumentationStandard.md](docs/meta/DocumentationStandard.md) (siehe §4).
6. **Entscheiden statt raten – und eskalieren.** Bei echten Design-/Architektur-
   Alternativen: **nicht eigenmächtig entscheiden**, sondern die Optionen samt
   Empfehlung vorlegen. Getroffene Entscheidungen wandern mit ≥3 Alternativen ins
   [DecisionLog](docs/production/DecisionLog.md).
7. **Keine Platzhalter-Dokumente** für zukünftige Sprints anlegen (verhindert veraltete
   Leichen). Geplante Bereiche werden im Index als „geplant" geführt.
8. **Kleine, fokussierte Änderungen.** Ein Commit = eine logische Änderung. Keine
   Sammel-Commits über mehrere unabhängige Themen.

## 3. Repository-Struktur (Schreibhoheiten)

```
README.md            ← Projektübersicht / GitHub-Startseite
AGENTS.md            ← diese Datei
CHANGELOG.md         ← Änderungshistorie (Keep a Changelog) – Single Source of Truth
.gitignore
RTS_*.md             ← historische Quelldokumente (nicht mehr aktiv ändern)
docs/
├── README.md        ← Wiki-Index – bei neuen/entfernten Dokumenten AKTUALISIEREN
├── meta/            ← Dokumentationsstandard
├── analysis/        ← Sprint 0 (abgeschlossen)
├── research/        ← Sprint 1 (abgeschlossen)
├── vision/          ← Sprint 2 (abgeschlossen)
├── gamedesign/      ← Sprint 2 – GDD (abgeschlossen)
├── tech/            ← Sprint 3 – Technical Design (in Arbeit)
└── production/      ← Sprint-Planung, DecisionLog, OpenQuestions, RiskAnalysis, sprints/
```

**„Heiße" Dateien mit einem einzigen Schreiber pro Änderung** (nie parallel bearbeiten):
`CHANGELOG.md`, `docs/README.md`, `docs/production/DecisionLog.md`,
`docs/production/SprintPlanning.md`, `docs/production/RiskAnalysis.md`.

## 4. Dokumentationsregeln (Kurzfassung)

Verbindlich ist [docs/meta/DocumentationStandard.md](docs/meta/DocumentationStandard.md).
Das Wichtigste:

- **Sprache:** Deutsch für Projektinhalte, Englisch für Code, Identifier und Dateipfade.
- **Klein & fokussiert:** ein Dokument = ein Thema; verlinke Abhängigkeiten relativ.
- **Pflichtaufbau jedes Dokuments:** Titel → Kopfzeile (`Version | Status |
  Verantwortungsbereich | Sprint`) → Zweck → Abhängigkeiten → Inhalt → Offene Punkte →
  Nächste Schritte → **Änderungsverlauf** (Tabelle).
- **Versionierung im Dokument:** `0.x` = Entwurf im Sprint, `1.0` = sprint-freigegeben;
  Minor-Bump bei inhaltlicher Änderung, Patch bei Korrektur. Der Änderungsverlauf ist
  Pflicht.
- **Entscheidungen** bekommen fortlaufende IDs (`D-001`, `D-002`, …), bleiben bei
  Revision stehen (Status „ersetzt durch D-xxx"), keine stillen Umschreibungen.
- **Nach jeder Struktur-Änderung** (neues/entferntes Dokument): [docs/README.md](docs/README.md)
  als Index aktualisieren.

## 5. Git- & GitHub-Workflow

### Branches
- `main` ist immer stabil und konsistent.
- Arbeit findet auf **Feature-/Sprint-Branches** statt und wird per **Pull Request**
  nach `main` gebracht:
  - `sprint/03-technical-design`
  - `docs/pathfinding-update`
  - `fix/economy-energy-values`
- Kleine, isolierte Korrekturen dürfen nach Absprache direkt auf `main` – im Zweifel PR.

### Commits – Conventional Commits
Format: `type(scope): kurze Beschreibung im Imperativ`

Erlaubte `type`-Werte:
`feat` · `fix` · `docs` · `refactor` · `chore` · `test` · `perf` · `build` · `ci`

In der aktuellen Doku-Phase ist **`docs`** der häufigste Typ. Beispiele:

```
docs(tech): add deterministic simulation core to Architecture.md
docs(gamedesign): resolve flak DPS corridor between Aircraft and Weapons
docs(production): log D-033 sim/MP model decision
chore(repo): add root README, AGENTS.md and CHANGELOG
fix(economy): correct Aetherium refinery energy value to match Buildings.md
```

Regeln:
- **Imperativ, Englisch, ≤ 72 Zeichen** in der Betreffzeile.
- **Ein Commit = eine logische Änderung.** Lieber mehrere kleine Commits als ein großer.
- Body (optional) erklärt das **Warum**, referenziert D-IDs / Q-IDs / Sprint-Nummern.
- **Keine** „wip", „stuff", „fix" ohne Kontext, keine Debug-Reste.

### Pull Requests
- Titel im Conventional-Commit-Stil; Beschreibung listet: Was, Warum, betroffene
  Dokumente, geänderte Entscheidungen (D-IDs), Changelog-Eintrag.
- Bei sprintabschließenden PRs: Sprint-Bericht verlinken.
- **Merge nach `main` und `git push` nur mit menschlicher Freigabe.**

## 6. CHANGELOG-Disziplin (Keep a Changelog)

[CHANGELOG.md](CHANGELOG.md) ist die zentrale Änderungshistorie. Ablauf:

1. **Bei jeder inhaltlichen Änderung** einen Stichpunkt unter `## [Unreleased]` ergänzen,
   in der passenden Kategorie: `Hinzugefügt`, `Geändert`, `Behoben`, `Entfernt` oder
   `Entschieden` (für DecisionLog-Einträge).
2. **Beim Sprint-Abschluss** wird `[Unreleased]` in eine datierte Version überführt
   (`## [0.4.0] – JJJJ-MM-TT · Sprint N: Thema`) und ein frisches leeres `[Unreleased]`
   darüber angelegt. Die Version folgt dem Dokumentationsstand des Wikis.
3. Vergleichs-Links am Dateiende aktualisieren.

Nie rückwirkend „glätten": bestehende Einträge bleiben stehen.

## 7. Sprint-Ritual (verbindlich pro Sprint)

Quelle: [docs/production/SprintPlanning.md](docs/production/SprintPlanning.md). Jeder
Sprint endet mit:

1. Vollständige Dokumentation des Ergebnisses
2. Self Review
3. Architecture Review (dokument-/architekturbezogen)
4. Risikoanalyse-Update ([RiskAnalysis.md](docs/production/RiskAnalysis.md))
5. Qualitätsbewertung
6. Offene-Punkte-Update ([OpenQuestions.md](docs/production/OpenQuestions.md))
7. Begründete GO/NO-GO-Entscheidung für den nächsten Sprint
8. Sprint-Bericht in [docs/production/sprints/](docs/production/sprints/), Index
   [docs/README.md](docs/README.md) und [CHANGELOG.md](CHANGELOG.md) aktualisieren

Kein Sprint gilt als abgeschlossen, solange nicht alle Exit-Kriterien erfüllt sind und
der Sprint-Bericht vorliegt.

## 8. Definition of Done (für eine Änderung)

Eine Änderung ist erst „fertig", wenn **alle** Punkte erfüllt sind:

- [ ] Inhalt geändert **und** der `Änderungsverlauf` im betroffenen Dokument ergänzt (+Version-Bump)
- [ ] Bei Struktur-Änderung: [docs/README.md](docs/README.md)-Index aktualisiert
- [ ] Entscheidung? → im [DecisionLog](docs/production/DecisionLog.md) mit ≥3 Alternativen
- [ ] Eintrag unter `[Unreleased]` in [CHANGELOG.md](CHANGELOG.md)
- [ ] Interne Links geprüft (keine toten relativen Links)
- [ ] Sauberer Conventional-Commit
- [ ] Push/Merge nur nach menschlicher Freigabe

## 9. Befehls-Spickzettel

```bash
# Status & Historie
git status
git log --oneline -10

# Neuer Arbeits-Branch
git switch -c docs/<thema>

# Änderungen committen (kleinschrittig)
git add <geänderte-dateien>
git commit -m "docs(<scope>): <imperativ>"

# Interne Links auf tote Ziele prüfen (Beispiel)
grep -rIoE '\]\(([^)]+\.md)[^)]*\)' docs | sort -u

# Push – NUR nach Freigabe
git push -u origin <branch>
```

---

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-21 | Initiale Agenten-Arbeitsregeln (Repo-Setup) | Orchestrator |
| 1.1.0 | 2026-07-21 | Goldene Regel 1: Push nach Versionsbump dauerhaft freigegeben (Anordnung Projektinhaber) | Orchestrator |
