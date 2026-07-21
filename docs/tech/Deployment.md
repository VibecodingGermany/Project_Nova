# Deployment & Build-Pipeline

**Version:** 0.2.0 | **Status:** Entwurf (Korrekturlauf Sprint 4) | **Verantwortungsbereich:** Lead DevOps Engineer | **Sprint:** 3

## Zweck

Definiert Build- und Auslieferungswege von Project Nova: skriptgesteuerte Unity-Builds, CI-Build-Matrix (Windows/macOS), Versionierung, Steam-Deployment (Depots, SteamPipe, Beta-Branches), Git-/LFS-Policy, Crash-Reporting-Empfehlung und Release-Checklisten. Verbindlich für alle Build- und Release-Prozesse ab Sprint 7. Test-CI-Inhalte (Teststufen, Jobs) sind in [./Testing.md](./Testing.md) definiert; dieses Dokument deckt die Build-/Release-Seite derselben Pipeline ab.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – D-006 (Unity 6.3 LTS, Desktop Win/macOS primär), D-007 (Premium, Steam), D-018 (Modi-Staffelung, Beta-Zeitpunkt), D-050 (Branching-Modell gestuft: main + Feature-Branches bis Sprint 6, develop ab Sprint 7)
- [../../AGENTS.md](../../AGENTS.md) – Goldene Regeln, insbesondere Regel 1 v1.1.0 (Push nach Versionsbump dauerhaft freigegeben) und §5 (PR-Workflow der Doku-Phase)
- [RTS_Technisches_Planungsdokument.md](../../RTS_Technisches_Planungsdokument.md) §12 (Git/Branching, LFS), §13 (Phasen), §16 (Crash-Reporting, Savegame-Versionierung)
- [../production/OpenQuestions.md](../production/OpenQuestions.md) – Q-019 (Telemetrie, offen)
- [./Testing.md](./Testing.md) – CI-Jobs, Release-Gates (Blocker-Klassen)
- [../gamedesign/Balancing.md](../gamedesign/Balancing.md) – Werteset-Versionierung (`balance-v0.x`)

## Build-Pipeline

### Skriptgesteuerte Builds (BuildPipeline-API)

Builds werden nie manuell aus dem Editor erzeugt, sondern über statische Build-Methoden, die lokal und in CI identisch laufen:

```csharp
namespace Nova.BuildTools   // Editor-Assembly, kein Runtime-Code
{
    public static class BuildEntry
    {
        // Aufruf: Unity -batchmode -quit -projectPath . \
        //   -executeMethod Nova.BuildTools.BuildEntry.Standalone -buildTarget win|mac
        public static void Standalone();        // dispatcht auf BuildProfile
        public static BuildReport Build(BuildProfile profile);
    }

    public sealed record BuildProfile(
        string Target,            // "win" (x64) | "mac" (universal oder arm64+x64, s. Offene Punkte)
        string Version,           // SemVer, z. B. "0.4.0"
        int    BuildNumber,       // CI-Run-Nummer (monoton)
        string BalanceSetVersion, // "balance-v0.x" – wird ins Build-Manifest geschrieben
        bool   Development        // Development-Build mit Script Debugging (nur interne Branches)
    );
}
```

- Der Build schreibt ein Manifest (`buildinfo.json`: Version, Build-Nummer, Git-Commit, Werteset-Version) neben die Binaries – Grundlage für Crash-Report-Zuordnung und Support.
- `PlayerSettings.bundleVersion`/`productVersion` werden aus dem Profil gesetzt; kein manuelles Hochzählen im Editor.

### CI-Architektur (GitHub Actions)

- **Runner-Topologie:** Windows-Builds auf GitHub-hosted `windows-latest`; **macOS-Builds auf self-hosted Mac-Runner** im Studio (Apple-Silicon). Begründung: Unity-Lizenzaktivierung, Codesigning/Notarisierung (später) und GPU-nahe Performance-Jobs brauchen kontrollierte Hardware; GitHub-hosted macOS-Runner sind für Unity-Lizenz- und Signing-Pfade teuer/instabil. Der Mac-Runner hostet auch die GPU-abhängigen Nightly-Jobs aus [./Testing.md](./Testing.md).
- **Unity-Ausführung:** `-batchmode -nographics -quit` für Tests und Windows-Builds; macOS-Builds mit Grafik-Backend (URP-Shader-Kompilierung) auf dem self-hosted Runner. Unity-Version gepinnt (D-006: 6000.3.x, Patch-Pinning), Installation via Unity Hub CLI-Cache im Runner-Image.
- **Build-Matrix:** `win-x64` + `mac` parallel; Artefakte als versionierte CI-Artifacts (`nova-win-0.4.0+123.zip`). PRs bauen nur auf Release-relevanten Branches vollständig (Kostenkontrolle), Nightly baut immer beide.
- **Geheimnisse:** Unity-Lizenz, Steam-Credentials, Signing-Zertifikate als GitHub-Environments-Secrets (`staging`, `production`); Production-Deployments erfordern manuelle Freigabe (Environment-Protection).

### Versionierung

- **Semantic Versioning** für Releases: `MAJOR.MINOR.PATCH` (0.x bis Release, 1.0.0 = Release-Version). **Build-Nummer** = monotone CI-Run-Nummer, Anzeige im Spiel als `0.4.0 (Build 1234)`.
- Tags: `v0.4.0` auf `main`; jedes Tag ist reproduzierbar (Manifest + Commit + Werteset).
- Balancing-Daten folgen der eigenen Werteset-Version (`balance-v0.x`, Balancing.md); ein Release pinnt genau ein Werteset – Savegame-/Replay-Kompatibilität bezieht sich immer auf das Paar (App-Version, Werteset).

## Steam-Deployment

Ab Beta relevant (D-018: Online-Modi Beta; interne Steam-Pipeline kann früher aufgesetzt werden, um Release-Reibung zu senken).

- **Depot-Struktur:** zwei Depots in einer App: `depot-win` (Windows x64) und `depot-mac` (macOS), jeweils mit Plattform-Filters im Steamworks-Backend; gemeinsamer Content (lokale Daten, falls plattformgleich auslieferbar) kann in ein drittes Shared-Depot – Entscheidung nach erstem Größen-/Delta-Upload-Messstand (Offene Punkte).
- **SteamPipe-Upload:** `steamcmd` + `app_build.vdf` im CI-Job `steam-upload` (self-hosted Runner wegen Depot-Cache); Upload nur aus Tags auf `main` bzw. `release/…`-Branches, niemals aus PRs.
- **Branches auf Steam:** `default` (öffentlich, erst ab Release), `beta` (öffentlich opt-in, Passwort-geschützt möglich), `internal` (Studio-Nightly/QA). Mapping Git→Steam: `main`-Tag → `internal`/`beta`; erst Release-Freigabe → `default`.
- **DRM/Offline:** D-007 (Premium-Offline-Produkt) – Steam-DRM minimal, Offline-Start muss funktionieren; Teil der Release-Checkliste.

## Git-LFS- & Branching-Policy

Die LFS-Policy übernimmt TPD §12.2 unverändert; das **Branching-Modell ist gestuft (D-050)** und löst den früheren Konflikt zwischen AGENTS.md (PR → `main`) und diesem Dokument (`develop`-Integration) auf:

- **Doku-Phase (bis Sprint 6, D-050):** `main` + kurze Feature-/Sprint-Branches mit PR (z. B. `docs/…`, `sprint/…`, `fix/…`). Es gibt **kein `develop`** in dieser Phase; maßgeblich ist der Workflow in [../../AGENTS.md](../../AGENTS.md) §5.
- **Code-Phase (ab Sprint 7, D-050):** TPD §12.2 vollständig – `main` (stabil, releasefähig), `develop` (Integration), `feature/…`, `fix/…`, `art/…` (größere Asset-Integrationen), `release/…` (Release-Härtung). Parallele Agenten-/Entwickler-Arbeit über getrennte Git-Worktrees (TPD §12.2).
- **Schutz:** `main` ist geschützt – **PR-Pflicht**, mindestens 1 Review; direkte Pushes sind technisch gesperrt. Ab Sprint 7 gilt dasselbe für `develop`, ergänzt um die Statuschecks `editmode-tests` + `replay-tests` grün ([./Testing.md](./Testing.md)).
- **Push-/Merge-Freigabe ([../../AGENTS.md](../../AGENTS.md) §2 Regel 1, v1.1.0):** Nach jedem **Versionsbump** (Sprint-Abschluss, Release-Tag, Wiki-Versionserhöhung) sind Commit und Push dauerhaft freigegeben, ohne Einzelfreigabe. Alle anderen Pushes sowie Merges nach `main` erfolgen nur nach menschlicher Freigabe. Lokales Committen ist jederzeit erlaubt.
- **Merge-Fluss (ab Sprint 7):** `feature|fix|art/* → develop`; `develop → release/x.y.z` bei Meilenstein-Freeze; `release/* → main` + Tag; Hotfixes als `fix/…` direkt auf `release/…` bzw. `main` mit Rückportierung nach `develop`. Bis Sprint 6 gilt schlicht: Feature-Branch → PR → `main`.
- **LFS-Policy:** Git LFS für alle Binär-Assets (Texturen `.png/.tga/.psd`, Audio `.wav/.ogg`, Modelle `.fbx/.blend`, Video). Text-Formate bleiben in Git (`.cs`, `.md`, `.json`, `.asset`-YAML, `.unity`, `.prefab`). Regeln ausschließlich über versionierte `.gitattributes`; LFS-Zeiger dürfen nicht in `main` gebrochen werden (CI-Check `git lfs fsck` im Build-Job). Quell-Assets (PSD/Blend) und abgeleitete Importe werden nicht doppelt versioniert – Quelle ins LFS, Ableitung erzeugt der Unity-Importer.
- **Repo-Hygiene:** Library/Build-Outputs sind ignoriert; CI baut immer aus einem sauberen Checkout.

## Crash-Reporting – Optionen und Empfehlung

| Kriterium | Unity Cloud Diagnostics | Sentry (self-hosted oder SaaS) |
|---|---|---|
| Plattformen Win/macOS, managed + native Crashes | ja, aber Feature-Umfang in den letzten Jahren kaum weiterentwickelt | ja, ausgereift (Unity-SDK, Native-Symbole) |
| Symbolik/Debug-Symbole, Zuordnung zu Build-Nummer | eingeschränkt | vollständig (dSYM/PDB-Upload im CI) |
| Self-hosting/Datensparsamkeit (D-007 Offline-Produkt) | nein (Unity-Cloud) | ja (Self-hosted möglich) |
| Kosten | im Unity-Plan teils enthalten | SaaS staffelweise; Self-hosted Betriebskosten |

**Empfehlung: Sentry.** Ausschlaggebend sind Symbolik-Qualität über beide Plattformen, die Self-hosting-Option (Datensparsamkeit ist laut Balancing.md/D-007 ein Verkaufsargument) und der CI-integrierbare Symbol-Upload. Diese Empfehlung ist noch **keine** verbindliche Entscheidung – sie ist als D-Eintrag (D-037-Kandidat) im [../production/DecisionLog.md](../production/DecisionLog.md) vorzusehen, inkl. der verworfenen Alternativen (Unity Cloud Diagnostics, Eigenbau-Minidump-Sammlung).

- **Datenschutz-Leitplanke (unabhängig vom Tool):** Crash-Reports enthalten keine Savegame-/Kampagnen-Inhalte, werden mit Opt-out-Schalter ausgeliefert und sind strikt von Telemetrie (Q-019) getrennt – Crash-Reporting dient der Stabilität, nicht der Verhaltensmessung.

## Telemetrie-Abhängigkeit (Q-019)

Telemetrie-Infrastruktur ist offene Frage **Q-019** (Owner-Sprint 3/6, [../production/OpenQuestions.md](../production/OpenQuestions.md)) und wird hier **nicht** entschieden. Deployment-seitige Vorhaltung ohne Festlegung:

- Die Release-Builds enthalten eine Compile-Schaltstelle für Telemetrie, die bei negativer Q-019-Entscheidung ungenutzt bleibt (kein toter Pflicht-Code).
- Infrastruktur-Kosten und Backend-Betrieb werden erst nach Q-019-Entscheidung geplant; Balancing-Pipeline Stufe 5 bleibt bis dahin vorbehaltlich (Balancing.md).

## Release-Checklisten

### Release-Kandidat (`release/x.y.z` angelegt)

- [ ] Alle `blocker`-Bugs geschlossen, keine offenen Quarantäne-Tests in Kernbereichen ([./Testing.md](./Testing.md))
- [ ] CI grün: Test-Suiten + Build-Matrix Win/macOS aus dem exakten Release-Commit
- [ ] Werteset-Version gepinnt und im Build-Manifest verifiziert; Balance-Changelog aktuell (BAL-Einträge vollständig)
- [ ] Savegame-Migrations-Tests grün für alle unterstützten Altversionen; nicht mehr unterstützte Versionen in Release-Notes dokumentiert
- [ ] Golden-Master-Fixtures auf dem Release-Stand aufgezeichnet und committed
- [ ] Performance-Nightly ohne unerklärte Regression (Sim-Tick, Pathfinding-Budget D-034, 60-FPS-Ziel)
- [ ] Version/Build-Nummer im Spiel sichtbar und korrekt; `buildinfo.json` geprüft
- [ ] Offline-Start ohne Steam-Login verifiziert (D-007)
- [ ] Crash-Reporting im Release-Build aktiv, Test-Crash einem Build zugeordnet (Symbolik-Probe)

### Veröffentlichung (Steam)

- [ ] Tag `vx.y.z` auf `main`; `steam-upload`-Job aus dem Tag erfolgreich
- [ ] Build auf Steam-Branch `beta` gesetzt und durch QA-Smoke-Test (Win + macOS) verifiziert
- [ ] Erst danach Set-Live auf `default` (manuelle Freigabe, 2-Personen-Prinzip)
- [ ] Release-Notes veröffentlicht (Änderungen, bekannte Probleme, Savegame-Hinweise)
- [ ] Rollback-Plan: vorheriger Build bleibt auf Steam-Branch `rollback` verfügbar

### Hotfix-Prozess

- [ ] `fix/…` vom betroffenen Tag; Patch-Version erhöhen (z. B. 0.4.1)
- [ ] Nur gezielte Änderung + Regressionstest (Bug als roter Test vor Fix, [./Testing.md](./Testing.md))
- [ ] Verkürzte Checkliste: Test-Suiten + Build-Matrix + QA-Smoke; danach wie Veröffentlichung ab Schritt 2
- [ ] Rückportierung nach `develop` (Merge oder Cherry-Pick) im selben Vorgang – gilt ab Sprint 7 (D-050); in der Doku-Phase entfällt sie, da es kein `develop` gibt

## Offene Punkte

- **Crash-Reporting-Entscheidung:** Empfehlung Sentry (s. o.) als D-Eintrag formalisieren; vorher Proof-of-Concept mit Symbol-Upload für beide Plattformen (Sprint 7).
- **macOS-Architektur:** Universal-Binary (arm64+x64) vs. arm64-only – hängt von der Mindest-Hardware-Zielgruppe und dem Fixed-Point-ARM↔x86-Befund (Phase-0-Spike) ab; nicht vorentschieden.
- **Shared-Depot:** Ob plattformübergreifende Assets in ein gemeinsames drittes Steam-Depot ausgelagert werden, entscheidet der erste Delta-Upload-Größenvergleich (Sprint 6/7).
- **Codesigning/Notarisierung macOS & Windows-Signatur:** Zertifikatsbeschaffung (Apple Developer ID, EV-Code-Signing) und Integration in den self-hosted Runner sind noch nicht terminiert – vor erstem externen Build (Alpha) Pflicht.
- **Self-hosted-Runner-Betrieb:** Kosten/Verfügbarkeit des Mac-Runners (Redundanz, Wartungsfenster) sind Kapazitätsfrage der Produktionsplanung (Sprint 6).
- **Epic/eigene Plattform (TPD §16):** außer Scope; Steam-only bis Release-Re-Evaluierung (D-007-konform, aber nicht formal entschieden).

## Nächste Schritte

- Sprint 7: `Nova.BuildTools.BuildEntry` + erster CI-Build-Job (win-x64 auf GitHub-hosted) lauffähig; Mac-Runner einrichten und macOS-Build nachziehen.
- Sprint 7: `.gitattributes`-LFS-Regeln und Branch-Protection-Regeln gemäß diesem Dokument im Repo konfigurieren; `git lfs fsck`-Check in CI.
- Sprint 7: Sentry-PoC (Symbol-Upload Win/macOS, Build-Zuordnung via `buildinfo.json`) als Entscheidungsgrundlage für den D-Eintrag.
- Vor Alpha (externer Build): Codesigning/Notarisierung klären; Steam-App anlegen und `internal`-Branch mit erstem Upload testen.
- Sprint 6: Q-019-Ausgang in Build-Schaltstelle und Infrastruktur-Planung übernehmen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead DevOps Engineer |
| 0.2.0 | 2026-07-21 | Korrekturlauf Sprint 4 (D-043–D-052, Review-Findings) | Lead DevOps Engineer |
