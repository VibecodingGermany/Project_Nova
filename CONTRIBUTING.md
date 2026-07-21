# Beitragen zu Project Nova

Willkommen! *Project Nova* ist ein **Community-RTS** der Organisation
**VibecodingGermany**. Dieses Dokument beschreibt, **wie** wir zusammenarbeiten,
damit mehrere Menschen (und KI-Agenten) sauber und ohne Chaos am selben Repository
bauen können. Verbindliche Detail-Regeln für Agenten stehen in [AGENTS.md](AGENTS.md);
der Dokumentationsstandard in [docs/meta/DocumentationStandard.md](docs/meta/DocumentationStandard.md).

> **Projektstand:** reine Design-/Planungsphase (noch kein Spielcode). Alle Beiträge
> sind aktuell **Dokumentation** (Game Design, technische Architektur, Reviews).

## Die eine Grundregel

**`main` ist geschützt. Es gibt keine direkten Pushes auf `main` – Änderungen kommen
ausschließlich über Pull Requests rein.** Das ist technisch per GitHub Branch
Protection erzwungen und gilt für alle, inkl. KI-Agenten.

## Ablauf für einen Beitrag

1. **Branch anlegen** (vom aktuellen `main`):
   - `sprint/<NN>-<thema>` – Sprint-Arbeit (z. B. `sprint/04-architecture-review`)
   - `docs/<thema>` – gezielte Doku-Änderung (z. B. `docs/pathfinding-update`)
   - `fix/<thema>` – Korrektur (z. B. `fix/economy-energy-values`)
2. **Ändern & committen** – kleine, fokussierte [Conventional Commits](#commit-konventionen).
   Betroffene Dokumente + `Änderungsverlauf` pflegen, `[Unreleased]` im
   [CHANGELOG.md](CHANGELOG.md) ergänzen.
3. **Branch pushen** – Feature-Branches dürfen jederzeit gepusht werden; nur `main` ist gesperrt.
4. **Pull Request öffnen** – die [PR-Vorlage](.github/pull_request_template.md) ausfüllen.
5. **Grüne CI abwarten** – der Check **`docs-check`** muss bestehen (siehe unten).
6. **Review** – mindestens **eine Freigabe** (Team `trusted-coders`) ist nötig.
7. **Squash-Merge** nach `main`. Der Branch wird nach dem Merge gelöscht.

## Für KI-Agenten (Kimi, Claude, Cursor u. a.)

KI-Agenten **schreiben Dateien**, bedienen aber oft **kein Git**. Deshalb gilt:

- Ein Agent, der Git/PRs beherrscht, arbeitet selbst per Branch → PR (nie direkt auf `main`).
- Ein Agent **ohne** Git-Fähigkeit schreibt nur die Dateien; **ein Maintainer (oder ein
  dafür zuständiger Agent) verpackt die Änderungen in einen Branch + PR.**
- In **keinem** Fall landet etwas ohne PR + grüne CI + Review auf `main`.

Jeder Agent liest zuerst [AGENTS.md](AGENTS.md).

## Commit-Konventionen

Format: `type(scope): kurze Beschreibung im Imperativ` (englisch, ≤ 72 Zeichen).
Typen: `feat` · `fix` · `docs` · `refactor` · `chore` · `test` · `perf` · `build` · `ci`.
In der Doku-Phase ist **`docs`** der häufigste Typ. Beispiele stehen in [AGENTS.md §5](AGENTS.md).

## Continuous Integration (bewusst günstig)

Der Workflow [`.github/workflows/docs-checks.yml`](.github/workflows/docs-checks.yml) läuft
nur bei Markdown-Änderungen und führt [`check_docs.py`](.github/scripts/check_docs.py) aus:

- **Hart (blockiert den Merge):** tote interne Links im Wiki.
- **Weich (nur Hinweis):** fehlende Standard-Kopfzeile in `docs/`-Dateien.

Keine schweren Toolchains, keine Abhängigkeiten → nahezu keine Kosten. Auf öffentlichen
Repos sind GitHub Actions ohnehin kostenlos. **Teurere Prüfungen (Unity/C#-Builds,
Playmode-Tests) kommen erst mit Sprint 7 (Implementierung)** – und werden dann bewusst
schlank gehalten: Der Unity-freie Simulationskern (`Nova.Simulation`) lässt sich mit
einfachem `dotnet test` auf Standard-Runnern prüfen (kein Unity-Lizenz-/GPU-Runner nötig).

## Reviews

- Reviewer sind Mitglieder des Teams **`trusted-coders`** (Write-Zugriff).
- Eigene PRs kann man nicht selbst freigeben – es braucht ein zweites Augenpaar.
- Achte im Review auf: Doku-Standard, gepflegten `Änderungsverlauf`, `[Unreleased]`-Eintrag,
  keine toten Links, saubere Entscheidungsbelege (D-IDs).

## Release-Ablauf

Releases entstehen am **Sprint-Ende**, ebenfalls über einen PR:

1. Sprint-Abschluss-Ritual erfüllen (Bericht, Reviews, offene Punkte – siehe
   [SprintPlanning.md](docs/production/SprintPlanning.md) / [AGENTS.md §7](AGENTS.md)).
2. **Versionsbump**: `[Unreleased]` im [CHANGELOG.md](CHANGELOG.md) in eine datierte
   Version überführen (Wiki-Versionsstand, z. B. `0.5.0`).
3. **Release-PR** → Review → Squash-Merge nach `main`.
4. Nach dem Merge **Tag** `v<version>` setzen (optional GitHub Release). Tags/Releases
   erstellt ein Maintainer mit den nötigen Rechten.

## Verhalten

Sei freundlich, konkret und belegbar. Wir kritisieren Inhalte, nicht Menschen. Wer
unsicher ist, öffnet lieber ein Issue oder einen Draft-PR und fragt.

Fragen? Öffne ein [Issue](https://github.com/VibecodingGermany/Project_Nova/issues).
