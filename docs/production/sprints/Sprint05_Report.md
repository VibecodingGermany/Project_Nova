# Sprint-5-Bericht – Asset Audit

**Version:** 1.0.0 | **Status:** Sprint abgeschlossen | **Verantwortungsbereich:** Executive Producer | **Sprint:** 5

## Zweck

Verbindlicher Abschlussbericht von Sprint 5 (Asset Audit) gemäß Sprint-Ritual ([../SprintPlanning.md](../SprintPlanning.md)): Dokumentationsstand, Entscheidungen, Konsistenzreview, Self Review, Architecture Review, Risikoanalyse, Qualitätsbewertung, offene Punkte, begründete Empfehlung für den nächsten Sprint.

## Abhängigkeiten

- Alle vier Asset-Dokumente unter [../../assets/](../../assets/)
- [../DecisionLog.md](../DecisionLog.md) (D-053), [../OpenQuestions.md](../OpenQuestions.md) (Q-035–Q-037), [../RiskAnalysis.md](../RiskAnalysis.md) (R-04/R-07)
- [../SprintPlanning.md](../SprintPlanning.md) (Sprint-5-Definition, Sprint-6-Scope „Produktionsplanung")
- Eingaben: [../../research/AssetStore_Landschaft.md](../../research/AssetStore_Landschaft.md), [../../tech/AssetBudget.md](../../tech/AssetBudget.md), [Sprint04_Report.md](Sprint04_Report.md)

## 1. Ergebnisse des Sprints

**Vier Asset-Audit-Dokumente erstellt** (neuer Wiki-Bereich [../../assets/](../../assets/), alle im Dokumentstandard):

| Dokument | Inhalt |
|---|---|
| [ProcurementStrategy.md](../../assets/ProcurementStrategy.md) | Strategie B ratifiziert (D-053), Klassifikations-Rubrik BUY/MODIFY/BUILD, vier Bewertungsdimensionen operationalisiert, Repo-Hygiene |
| [AssetRegister.md](../../assets/AssetRegister.md) | Master-Register über **14 Kategorien**: kanonische GDD-Bedarfszahlen, Kandidatenquelle, Lizenz, Kosten-/Aufwandsschätzung, URP/Qualität, Klassifikation; APL-Reconciliation |
| [Licenses.md](../../assets/Licenses.md) | Lizenz-Register: Lizenzrahmen je Quelle (Seats/Attribution/Weitergabe), verbindliche Lizenz-Regeln, leeres Erwerbs-Ledger |
| [BuildBacklog.md](../../assets/BuildBacklog.md) | 14 priorisierte Eigenbau-Pakete, Grobsumme ~110–180 PT, kritischer Phase-0-Pfad |

**Eine Entscheidung getroffen** (DecisionLog v1.7.0):
- **D-053** Asset-Beschaffungsstrategie **B (Multi-Store-Mix mit Synty als Stil-Anker)** ratifiziert; menschliche Fraktionen/Biome/UI-Icons/Basis-Animationen = Kauf, Aetherium + Evolvierte + Fraktions-Signaturen = MODIFY/BUILD; Leitplanken URP-K.O.-Kriterium, keine RTS-Komplett-Frameworks, einheitlicher URP-Material-Standard, Lizenz-Register-Pflicht.

**Kanonische Zahlen gegen die historische APL abgeglichen** (Single Source of Truth, D-047): Die überholten Mengen aus [../../../RTS_Asset_Pipeline.md](../../../RTS_Asset_Pipeline.md) wurden gegen die maßgeblichen GDD-Entscheidungen korrigiert (Gebäude 36 statt 54 = D-008; Karten 12 statt 10 = D-017; Elite 3→9 statt 15 = D-015; Neutrale ohne Händler = D-016; Marine gestrichen = D-013). Ein nicht-destruktiver **Korrekturhinweis** an der Spitze der APL verweist auf das AssetRegister als führende Quelle (historisches Quelldokument wird nicht umgeschrieben, [AGENTS.md](../../../AGENTS.md) §3).

**Exit-Kriterien** (laut [../SprintPlanning.md](../SprintPlanning.md)): pro benötigtem Asset Recherche/Lizenz/Kosten/Qualität/Anpassungsaufwand ✓ | Klassifikation BUY/MODIFY/BUILD ✓ | vollständiges Asset-Register inkl. **Licenses.md** ✓ | Sprint-Bericht ✓ (dieses Dokument).

## 2. Konsistenzreview (Zusammenfassung)

- **Single Source of Truth durchgehalten:** Alle Bedarfszahlen im Register verweisen auf das jeweils führende GDD-Dokument (Buildings.md, Infantry.md, Vehicles.md, Aircraft.md, Biomes.md, Maps.md, NeutralUnits.md, Resources.md, CommanderSystem.md) statt eigene Zahlen zu setzen – keine neue Werte-Doppelpflege (D-047-Grundsatz eingehalten).
- **APL-Widersprüche systematisch aufgelöst:** Jeder Konflikt zwischen der historischen Wunschliste und dem GDD ist in [AssetRegister.md](../../assets/AssetRegister.md) §2 einer DecisionLog-Entscheidung zugeordnet; die APL selbst bleibt als historisches Dokument erhalten, trägt aber jetzt einen Verweis auf das führende Register.
- **Technische Rückbindung:** Klassifikation und Aufwand sind an die Budgets aus [../../tech/AssetBudget.md](../../tech/AssetBudget.md) (§1 Polycount, §6 Kauf-Prüfung) gekoppelt; URP-K.O.-Kriterium spiegelt D-006.
- **Architektur-Rückbindung:** „Keine RTS-Komplett-Frameworks" (D-053) schützt D-033/D-035/D-043 vor Kollision mit gekauften Sim-/Netcode-Kits.

## 3. Self Review

**Stärken:** Der Audit hat die zentrale Projektwahrheit sichtbar gemacht – der reale Aufwand liegt **nicht** im Kaufpreis (~200–600 USD), sondern im Eigenbau der kompletten Evolvierten-Fraktion und der Aetherium-Signatur (~110–180 PT, [BuildBacklog.md](../../assets/BuildBacklog.md)); diese Zahl ist die konkrete Eingabe für R-16. Die Research-Vorlage aus Sprint 1 erwies sich als entscheidungsreif: Strategie B ließ sich mit drei geprüften Alternativen ohne Zusatzrecherche ratifizieren. Die APL-Reconciliation schließt eine seit Sprint 0 offene Baustelle („wird in Sprint 5 korrigiert").

**Schwächen (offen benannt):**
- **Kosten- und Person-Tage-Schätzungen sind Vorab-Einschätzungen** ohne kalibrierten Referenz-Frame – erst der Phase-0-Bau des Aetherium-Signature-Assets (B-01) liefert echte Zahlen; die Register-/Backlog-Werte sind entsprechend als v1.1.0-Nachjustierung markiert. Das ist bewusste, deklarierte Unsicherheit, keine falsche Präzision.
- **Die Budget-Obergrenze wurde bewusst NICHT erfunden** (Q-035): Sie ist eine Inhaber-/Kapazitätsentscheidung (gekoppelt an R-16) und lag außerhalb der Autorität dieses Sprints ([AGENTS.md](../../../AGENTS.md) §2 Regel 6). Der Audit liefert die Entscheidungsgrundlage, nicht die Entscheidung.
- **Keine realen URP-Testprojekt-Validierungen** durchgeführt: Der Audit klassifiziert auf Basis von Store-Badges und Research; die verbindliche Testprojekt-Prüfung von Custom-Shader-Käufen (VFX, Vegetation, Kristalle) ist als Pflicht **vor** jedem realen Kauf terminiert, nicht in diesem Doku-Sprint geleistet.
- **Q-031–Q-034 wurden nicht bearbeitet** – korrekt, denn es sind TDD-Authoring-/Doku-Aufgaben ohne Bezug zum Asset-Audit (§7); Q-034 wurde sauber auf Sprint 6 umterminiert statt fälschlich als „gelöst" markiert.

## 4. Architecture Review

Dokument-/prozessbezogenes Eigenreview (Asset-Audit ist kein Code-Sprint):
- **Kohärenz-Absicherung:** R-04 (visuelle Inkohärenz) wird strukturell adressiert – ein Stil-Anker (Synty), ein URP-Material-Standard mit Teamfarben-Masken und die BUILD-Klassifikation aller kohärenzkritischen/organischen Assets statt Fremdmodell-pro-Einheit. Das ist dieselbe „eine Quelle/ein Standard"-Logik, die in Sprint 4 die Werte-Drifts beseitigte.
- **Schnittstelle zur Produktion:** [BuildBacklog.md](../../assets/BuildBacklog.md) ist bewusst als Sprint-6-Eingabe konstruiert (Prioritäten P0–P2, kritischer Phase-0-Pfad, Grobsumme für R-16) – der Audit endet nicht in sich, sondern speist die Roadmap.
- **Bewusste Nicht-Lösung:** Terrain-Verfahren (Unity Terrain vs. Custom Mesh) bleibt einem Render-TDD (Sprint 6) überlassen; das Environment-Aufwandsband ist dadurch noch unscharf – als offener Punkt vermerkt, kein Blocker.

## 5. Risikoanalyse (Update)

[../RiskAnalysis.md](../RiskAnalysis.md) auf **v1.5.0** fortgeschrieben:
- **R-04 (visuelle Inkohärenz) → mitigiert:** Strategie B (D-053), URP-Material-Standard, BUILD-Klassifikation kohärenzkritischer Assets. Restrisiko = Umsetzungsdisziplin bei realem Kauf.
- **R-07 (Lizenz-/Kostenfallen) → mitigiert:** Lizenz-Register [Licenses.md](../../assets/Licenses.md) mit Regeln je Quelle angelegt; Kaufprüf-Checkliste verbindlich. Restrisiko = offene Inhaberentscheidungen Q-035/Q-036.
- **Kein Phase-0-Spike in Sprint 5:** R-03/R-14 (Determinismus/Performance) und die Kapazitätsschritte zu R-13/R-16 bleiben ausdrücklich für Sprint 6/Phase 0 offen – Sprint 5 war der Asset-, nicht der Technik-Spike-Sprint.
- **R-16 (Zeit-/Kapazität):** unverändert unmitigiert, aber jetzt mit einer belastbaren Aufwands-Eingabe versehen (~110–180 PT Eigenbau) – Sprint 6 kann daraus erstmals eine Schätzung ableiten.

## 6. Qualitätsbewertung

| Kriterium | Bewertung | Anmerkung |
|---|---|---|
| Vollständigkeit (Kategorie-Abdeckung) | sehr gut | 14 Kategorien, alle Pipeline-Pakete abgedeckt; Marine korrekt als gestrichen behandelt |
| Entscheidungsdisziplin | sehr gut | D-053 mit 3 geprüften Alternativen; Budget-Obergrenze bewusst als Inhaberfrage offen gelassen statt erfunden |
| Konsistenz (Single Source of Truth) | sehr gut | alle Zahlen auf führende GDD-Docs verlinkt; APL-Konflikte je Entscheidung aufgelöst |
| Umsetzungsreife für Sprint 6 | gut | BuildBacklog priorisiert, Grobsumme für R-16, kritischer Phase-0-Pfad markiert |
| Messbarkeit | mittel | Kosten/PT sind deklarierte Vorab-Schätzungen ohne Phase-0-Kalibrierung (v1.1.0-Nachjustierung terminiert) |
| Verbleibende Unsicherheit | akzeptiert | Preise rotieren, Terrain-Verfahren offen, keine realen URP-Tests – bewusst zum Beschaffungszeitpunkt verschoben |

## 7. Offene Punkte

- **Neu aus Sprint 5:** Q-035 (Asset-Budget-Obergrenze, Sprint 6, gekoppelt R-16), Q-036 (Seat-Planung, Sprint 6), Q-037 (Bundle-Kauffenster, Sprint 6/Phase 0) – alle Inhaber-/Beschaffungsentscheidungen, kein Blocker.
- **Nicht im Asset-Scope, weiterhin offen:** Q-031 (Fähigkeiten-/Status-Effekt-System, vor Sprint 7), Q-032 (MemoryBudget-Abgleich, vor Phase-0-Spike), Q-033 (V5-Gate Kampf-/KI-Kostenmodell, Phase 0), Q-034 (tote TDD-Verweise – als TDD-Authoring erkannt und auf Sprint 6 präzisiert). Diese sind TDD-/Doku-Aufgaben, kein Asset-Audit-Thema, und wurden in Sprint 5 bewusst nicht bearbeitet.
- **Weiterhin offen (Sprint 6):** Q-018 (Preispunkt), Q-019 (Telemetrie).
- **Fachlich terminiert:** Kosten/PT-Kalibrierung nach Phase-0-Signature-Bau (Register/Backlog v1.1.0); Terrain-Verfahren im Render-TDD; reale URP-Testprojekt-Validierung vor jedem Custom-Shader-Kauf.

## 8. Empfehlung für den nächsten Sprint

**Empfehlung an den Projektinhaber: GO für Sprint 6 (Produktionsplanung) – die finale Freigabe trifft der Mensch.**

Begründung: Alle Sprint-5-Exit-Kriterien sind erfüllt – ein vollständiges Asset-Register über 14 Kategorien mit BUY/MODIFY/BUILD-Klassifikation, Kosten-/Aufwandsschätzungen, das Lizenz-Register (Licenses.md) und die ratifizierte Beschaffungsstrategie (D-053) liegen vor; die historische APL ist mit dem GDD abgeglichen. Sprint 6 (Produktionsplanung: MVP/Alpha/Beta/Release, Roadmap.md, Milestones.md) baut direkt auf zwei Sprint-5-Ergebnissen auf: dem priorisierten [BuildBacklog.md](../../assets/BuildBacklog.md) (Grobsumme ~110–180 PT) als Eingabe für die Aufwandsschätzung (R-16) und den offenen Inhaberentscheidungen Q-035/Q-036 (Budget/Seats), die in Sprint 6 mit der Zeit-/Kapazitätsplanung zusammenfallen. Damit ist der in [Sprint04_Report.md](Sprint04_Report.md) §8 vermerkte Zustand („Sprint 6 blockiert bis Sprint 5") aufgehoben. Empfehlung: (a) BuildBacklog-Aufwand in die R-16-Schätzung und Roadmap übernehmen, (b) Q-035/Q-036 mit dem Projektinhaber entscheiden, (c) R-13/R-16 (Bus-Faktor/Zeitmodell, aus Sprint 4) parallel adressieren.

**Sprint-6-Scope (laut [../SprintPlanning.md](../SprintPlanning.md)):** Produktionsplanung – MVP/Alpha/Beta/Release mit Features, Risiken, Abhängigkeiten, Aufwand, Priorität; Roadmap.md, Milestones.md; Plan deckt sich mit den Scope-Entscheidungen aus Sprint 2.

## Nächste Schritte

- Commit/Push (Versionsbump Wiki 0.6.0), SprintPlanning/README/CHANGELOG im Integrationsschritt nachziehen.
- Nach Freigabe durch den Projektinhaber: Sprint 6 (Produktionsplanung) starten; Q-035/Q-036 entscheiden; BuildBacklog in Roadmap/R-16 überführen.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-22 | Sprint 5 (Asset Audit) abgeschlossen, GO für Sprint 6 (Produktionsplanung) | Executive Producer |
