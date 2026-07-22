# Beschaffungsstrategie & Audit-Methodik

**Version:** 1.0.0 | **Status:** sprint-freigegeben | **Verantwortungsbereich:** Producer / Lead Environment Artist | **Sprint:** 5

## Zweck

Legt die verbindliche Beschaffungsstrategie für alle Assets von *Project Nova* fest und definiert die **Audit-Methodik**, nach der jedes benötigte Asset im [AssetRegister.md](AssetRegister.md) klassifiziert wird (**BUY / MODIFY / BUILD**). Dieses Dokument ratifiziert die in Sprint 1 vorbereitete Entscheidungsvorlage aus [../research/AssetStore_Landschaft.md](../research/AssetStore_Landschaft.md) als **D-053** und operationalisiert die vier Bewertungsdimensionen (URP, Lizenz, Stil-Kohärenz, Performance) zu einer Prüf-Checkliste. Verbindlich für: Producer (Budget/Beschaffung), Lead Environment Artist, Technical Art Director, alle Mitwirkenden mit Asset-Kaufberechtigung.

## Abhängigkeiten

- [../research/AssetStore_Landschaft.md](../research/AssetStore_Landschaft.md) – Marktrecherche und Strategie-Vorlage (A/B/C), Kategorie-Analyse
- [../tech/AssetBudget.md](../tech/AssetBudget.md) – technische Kauf-Prüfung (§6), Polycount-/Textur-/LOD-Budgets, Gesamtdeckel 1,8 GB
- [../production/DecisionLog.md](../production/DecisionLog.md) – D-006 (URP), D-053 (diese Strategie), D-047 (ein Wert, eine Quelle)
- [../production/RiskAnalysis.md](../production/RiskAnalysis.md) – R-04 (visuelle Inkohärenz gekaufter Assets)
- [AssetRegister.md](AssetRegister.md), [Licenses.md](Licenses.md), [BuildBacklog.md](BuildBacklog.md) – nachgelagerte Sprint-5-Ergebnisdokumente

## 1. Ratifizierte Strategie (D-053)

**Strategie B – Multi-Store-Mix mit Synty als Stil-Anker.** Der Unity Asset Store (Synty-Polygon-Packs für Allianz/Legion-Militär, Biome, UI-Icons) ist Hauptquelle, ergänzt um:

- **Humble Bundle** als Preishebel (wiederkehrende Synty-Sci-Fi-Bundles: ~8 Packs / 30 USD statt >600 USD Listenpreis),
- **CC0-Quellen** (Kenney, Quaternius) für Prototyping und Lückenfüller,
- **Fab / Sketchfab** für Einzelmodelle nach Bedarf (Lizenz pro Modell prüfen),
- **Sonniss GDC Bundles** (kostenlose, royalty-freie SFX) als Audio-Basis.

**Aetherium-Assets (Shader/Wachstum/Verseuchung), die Evolvierten-Fraktion (biologisch) und alle Fraktions-Signaturen** werden als **MODIFY/BUILD** klassifiziert – sie sind weder stilistisch noch funktional käuflich abgedeckt (siehe [BuildBacklog.md](BuildBacklog.md)).

### Geprüfte Alternativen (D-053)

| Strategie | Kosten Kernumfang (Einschätzung) | Stil-Kohärenz | Abdeckung 3 asymm. Fraktionen | Zeit bis MVP | Verworfen, weil |
|---|---|---|---|---|---|
| **A: Asset Store only (Synty)** | ~300–800 USD (mit Sales) | hoch | Lücke bei Evolvierten + Aetherium | schnell | biologische Evolvierte und Signature-Aetherium nicht abgedeckt; Publisher-Abhängigkeit ohne Preishebel |
| **B: Multi-Store-Mix (gewählt)** | ~200–600 USD | mittel (Material-Standard erzwingt Kohärenz) | am besten, aber heterogen | mittel | – gewählt – |
| **C: BUILD-first (nur Tools + Audio kaufen)** | ~100–300 USD + hohe Personalkosten | maximal, aber langsam | volle Kontrolle | langsam | Eigenbau von ~130+ Modellen gefährdet MVP-Disziplin und Zeitplan ohne Qualitätsvorteil auf RTS-Distanz |

**Begründung B:** Nutzt den dokumentierten Preishebel (Humble-Bundles) und CC0 für Prototyping, deckt die menschlichen Fraktionen (Allianz/Legion) käuflich ab und reserviert Eigenbau gezielt für das, was das Spiel unverwechselbar macht (Aetherium, Evolvierte, Signaturen). Die dafür nötige Lizenz- und URP-Disziplin institutionalisiert genau dieser Sprint (Audit + [Licenses.md](Licenses.md)).

## 2. Verbindliche Leitplanken

1. **URP-Kompatibilität ist K.O.-Kriterium.** Store-Badge (Built-in/URP/HDRP pro Unity-Version) ist der erste Filter; Custom-Shader-Assets (VFX, Vegetation, Wasser, Kristalle) werden **vor jedem Kauf** in einem URP-Testprojekt validiert (Badge allein genügt nicht – siehe PBR-Stylized-Crystals-Fall in [../research/AssetStore_Landschaft.md](../research/AssetStore_Landschaft.md) §6).
2. **Keine RTS-Komplett-Frameworks kaufen.** Gekaufte Sim-/Determinismus-/Netcode-Kits kollidieren frontal mit D-033 (Command-Sim), D-035 (OOP+Burst) und D-043 (Assembly-Topologie) und wären ein Rewrite-Risiko. Solche Kits sind ausschließlich als Referenz-Lektüre zugelassen, nie als Codebasis.
3. **Ein Stil-Anker (Synty-Polygon-Look).** Fremdquellen werden über einen **einheitlichen URP-Material-Standard mit Teamfarben-Masken** und Post-Processing-Grading angeglichen (Gegenmittel R-04). Realismus-Packs werden nicht mit dem Low-Poly-Anker gemischt.
4. **Lizenz-Register-Pflicht ab sofort.** Jeder Kauf/jede Quelle wird in [Licenses.md](Licenses.md) erfasst (Seats, Restricted-Assets-Kennzeichnung, Attribution-Pflichten, Weitergabe-Verbote). Keine Rohdaten (Asset-Store-Quellen, Sonniss-SFX) in das **öffentliche** Repo – privates Asset-Repo/LFS ist Pflicht (siehe §5).
5. **Technische Kauf-Prüfung bindend.** Jedes gekaufte Paket durchläuft die Checkliste aus [../tech/AssetBudget.md](../tech/AssetBudget.md) §6; **≥3 „Nein" = Kaufverzicht oder Aufbereitungsaufwand explizit einkalkulieren** (fließt als MODIFY-Aufwand in [AssetRegister.md](AssetRegister.md)).
6. **Kaufzeitpunkt.** Der Audit klassifiziert und schätzt; **tatsächliche Käufe erfolgen bedarfsgesteuert ab Phase 0/Sprint 7** (Signature-Asset-Referenz zuerst), Humble-Bundle-Fenster werden opportunistisch genutzt. Der Audit ist kein Beschaffungsauftrag.

## 3. Klassifikations-Rubrik (BUY / MODIFY / BUILD)

Jedes Asset im Register erhält genau eine Primärklasse nach dieser Rubrik:

| Klasse | Definition | Entscheidungsregel |
|---|---|---|
| **BUY** | Direkt nutzbar nach reinem Import + Material-Angleichung (Teamfarben-Pass, LOD-Check). | URP-tauglich **und** ≤2 „Nein" in der AssetBudget-§6-Prüfung **und** stilistisch Synty-nah **und** funktional generisch (kein Nova-Spezialverhalten am Modell). |
| **MODIFY** | Gekaufte Basis + nennenswerter Eigenaufbau (Retopo/LOD-Kette, Kitbash-Detail, Shader-Erweiterung, Rig-/Retarget-Anpassung). | Store-Basis vorhanden, aber Budget-/Stil-/Funktionslücke schließbar mit ~0,5–3 PT je Asset(-Gruppe). |
| **BUILD** | Vollständiger Eigenbau; kein tragfähiger Kauf-Kandidat. | Signature/USP-Element, funktional einzigartig (Umweltveränderung), biologisch-organisch oder gameplay-verzahnt (RTS-UI-Layout, FoW-Textur). |

**Grenzfall-Regel:** Im Zweifel zwischen BUY und MODIFY gilt **MODIFY** (ehrliche Aufwandsbilanz statt Kauf-Optimismus – Lehre aus R-04). Im Zweifel zwischen MODIFY und BUILD entscheidet, ob eine stilistisch passende **Basisgeometrie** existiert; wenn ja → MODIFY.

## 4. Die vier Bewertungsdimensionen (operationalisiert)

| Dimension | Messbares Kriterium | Konsequenz für die Klassifikation |
|---|---|---|
| **URP** | Badge für Unity 6.3 LTS **und** Testprojekt-Validierung bei Custom-Shadern | Nicht konvertierbar → Kandidat verworfen; „≤1 PT konvertierbar" → MODIFY-Aufschlag |
| **Lizenz** | kommerziell, keine Umsatzbeteiligung, keine In-Game-Quellenpflicht; Seats geklärt; Weitergabe-/Repo-Regel eingehalten | CC-BY (Attribution) → [Licenses.md](Licenses.md)-Eintrag Pflicht; „nicht weitervertreibbar" → Repo-Hygiene (§5) |
| **Stil-Kohärenz (R-04)** | Silhouette/Material-Nähe zum Synty-Anker auf RTS-Betrachtungsdistanz | Bruch mit Anker → MODIFY (Material-Pass) oder Verwerfen |
| **Performance** | LOD-Kette (≥2), Textur-Atlas-fähig, GPU-Instancing-taugliches Material, Polycount ≤ Klassenbudget ([AssetBudget.md](../tech/AssetBudget.md) §1/§2) | fehlende LODs/Atlas → MODIFY-Aufwand ~0,5–1 PT je Asset |

## 5. Repo-Hygiene für Asset-Rohdaten

- Das **öffentliche** Repo (`VibecodingGermany/Project_Nova`) enthält **keine gekauften/lizenzierten Rohdaten** (Asset-Store-Modelle, Sonniss-SFX, Synty-FBX). `.gitignore` hält Asset-Binärordner draußen; Sim/Doku bleiben trennbar von Art-Binaries.
- Art-Binaries leben im **separaten, privaten Asset-Repo mit Git LFS** (Beschaffung/Struktur → Sprint 6 Produktionsplanung).
- **Nur** eigenbaufreie, CC0- **oder** eigen-erstellte Assets dürfen später in ein öffentliches Art-Verzeichnis – die Klassifikation in [Licenses.md](Licenses.md) ist dafür die Freigabe-Grundlage.
- CC-BY-Quellen (v. a. Sketchfab) werden in einem späteren `CREDITS.md` (ab erstem CC-BY-Kauf) attribuiert.

## Offene Punkte

- **Asset-Budget-Obergrenze (USD):** Der Audit liefert Kostenschätzungen je Kategorie, aber die verbindliche Studio-Obergrenze ist eine Inhaber-/Kapazitätsentscheidung → [../production/OpenQuestions.md](../production/OpenQuestions.md) **Q-035** (Owner Sprint 6, gekoppelt an R-16 Zeit-/Kapazitätsmodell).
- **Seat-Planung (Teamgröße/Externe):** steuert Synty-5-Seat-Lizenzen und Editor-Tool-Käufe → **Q-036** (Owner Sprint 6).
- **Humble-Bundle-Kauffenster:** zeitlich limitiert; Beobachtung erst ab tatsächlichem Beschaffungsstart (Phase 0) sinnvoll → **Q-037** (Owner Sprint 6/Phase 0).

## Nächste Schritte

1. Sprint 6 (Produktionsplanung): Budget-Obergrenze (Q-035) und Seat-Planung (Q-036) mit dem Projektinhaber festlegen; privates Asset-Repo/LFS aufsetzen.
2. Phase 0: Signature-Asset (TPD §7.2, Aetherium-Feld) gegen [AssetBudget.md](../tech/AssetBudget.md) §1/§2 bauen und als Referenz-Frame vermessen; URP-Testprojekt für Custom-Shader-Käufe etablieren.
3. Laufend: Jeder Kauf → Checkliste [AssetBudget.md](../tech/AssetBudget.md) §6 + Eintrag in [Licenses.md](Licenses.md).

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2026-07-22 | Erstfassung Sprint 5: Strategie B ratifiziert (D-053), Klassifikations-Rubrik und 4 Bewertungsdimensionen operationalisiert, Repo-Hygiene festgelegt | Producer / Lead Environment Artist |
