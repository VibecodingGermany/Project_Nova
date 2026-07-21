# Technisches Planungsdokument – RTS-Projekt

## 1. Zweck des Dokuments

Dieses Dokument legt die technische Grundausrichtung für die Entwicklung eines Echtzeitstrategie- und Base-Building-Spiels im Stil klassischer RTS-Titel fest.

Es dient als verbindliche Grundlage für:

- Entwicklung
- technische Architektur
- Asset-Auswahl
- Projektplanung
- Aufgabenverteilung
- externe Dienstleister
- KI-Coding-Agenten
- spätere Plattform-Portierungen

---

# 2. Projektziel

Entwickelt werden soll ein modernes Echtzeitstrategiespiel mit:

- großer Karte
- schräger Top-Down- beziehungsweise isometrischer Kamera
- Basisbau
- Ressourcenabbau
- Produktionsketten
- Infanterie
- Fahrzeugen
- Luftfahrzeugen
- Verteidigungsanlagen
- drei spielbaren Fraktionen
- KI-Gegnern
- Multiplayer
- Gefechten mit zahlreichen gleichzeitig aktiven Einheiten

Das Spiel soll zunächst als vollwertiges Desktop-Spiel entwickelt werden.

Eine spätere Veröffentlichung für Browser, Tablets und Smartphones soll technisch nicht ausgeschlossen werden, darf den ersten Entwicklungsabschnitt jedoch nicht unnötig einschränken.

---

# 3. Technische Grundentscheidung

## 3.1 Game Engine

**Unity**

Unity wird als zentrale Game Engine für das Projekt festgelegt.

### Gründe

- Entwicklung auf macOS möglich
- Export für Windows und macOS
- Export für iOS und Android
- WebGL-Export grundsätzlich möglich
- großer Asset-Marktplatz
- zahlreiche fertige RTS-, Pathfinding-, UI-, VFX- und Multiplayer-Systeme
- gute Unterstützung durch Coding-Agenten
- große Entwickler-Community
- geeignet für stilisierte 3D-Grafik
- geeignet für isometrische und Top-Down-Kameras
- vergleichsweise schneller Aufbau eines spielbaren Prototyps

---

## 3.2 Programmiersprache

**C#**

Der gesamte zentrale Gameplay-Code wird in C# entwickelt.

### C# wird verwendet für

- Einheitensteuerung
- Auswahl mehrerer Einheiten
- Befehlsverarbeitung
- Wegfindung
- Formationen
- Ressourcenabbau
- Gebäudeplatzierung
- Produktionssysteme
- Wirtschaftssystem
- Kampfsystem
- Fraktionslogik
- Technologiebaum
- KI-Verhalten
- Fog of War
- Benutzeroberfläche
- Savegames
- Replay-Grundlagen
- Netzwerk-Client
- Multiplayer-Simulation

### Gründe für C#

- stark typisiert
- gut wartbar
- für große Systeme geeignet
- umfangreiche Unity-Unterstützung
- sehr gut dokumentiert
- für KI-gestützte Entwicklung geeignet
- leichter zu strukturieren als ein großes JavaScript-Projekt
- geringere Einstiegshürde als C++

---

# 4. Zielplattformen

## 4.1 Primäre Plattformen

Die erste vollwertige Version wird für folgende Plattformen entwickelt:

1. Windows
2. macOS

Diese Plattformen bilden das primäre Entwicklungs- und Qualitätsziel.

---

## 4.2 Sekundäre Plattformen

Nach erfolgreichem Desktop-Vertical-Slice werden folgende Plattformen geprüft:

1. iPadOS
2. Android-Tablets
3. Webbrowser über WebGL
4. iPhone
5. Android-Smartphones

Eine Veröffentlichung für diese Plattformen wird erst beschlossen, nachdem Performance, Bedienbarkeit und Produktionsaufwand anhand eines funktionierenden Desktop-Builds bewertet wurden.

---

# 5. Plattformstrategie

## 5.1 Desktop zuerst

Das Spiel wird zunächst für Maus und Tastatur optimiert.

Desktop-spezifische Merkmale:

- komplexe Einheitensteuerung
- Mehrfachauswahl
- Kontrollgruppen
- Hotkeys
- große Karten
- hohe Anzahl gleichzeitig aktiver Einheiten
- umfangreiches Bau- und Produktionsmenü
- längere Spielrunden
- höhere Grafikqualität
- detaillierte Benutzeroberfläche

---

## 5.2 Tablet später

Eine Tablet-Version kann auf derselben Codebasis aufbauen, benötigt jedoch eine eigene Bedienlogik.

Erforderliche Anpassungen:

- Touch-Steuerung
- größere Bedienelemente
- Touch-Auswahlrahmen
- vereinfachte Kontrollgruppen
- automatische Formationen
- reduzierte HUD-Dichte
- optimierte Kamera-Gesten
- angepasste Karten- und Einheitengrößen
- Performance-Profile für mobile Hardware

---

## 5.3 Smartphone nur nach Machbarkeitsprüfung

Ein klassisches Desktop-RTS lässt sich nicht unverändert auf ein Smartphone übertragen.

Eine Smartphone-Version würde voraussichtlich benötigen:

- deutlich vereinfachte Bedienung
- kleinere Karten
- weniger Einheiten
- kürzere Matches
- größere UI-Flächen
- automatische Gruppenbildung
- stärkere Assistenzsysteme
- reduzierte Anzahl gleichzeitig sichtbarer Aktionen

Die Smartphone-Version ist deshalb zunächst kein verbindliches Ziel.

---

## 5.4 Browser-Version

Unity WebGL bleibt als spätere Option vorgesehen.

Die Browser-Version kann genutzt werden als:

- Demo
- Testversion
- Community-Build
- reduzierte Spielversion
- Tutorial-Version
- Marketing-Instrument

Mögliche Einschränkungen:

- höherer Speicherbedarf
- lange Asset-Downloads
- geringere Performance
- eingeschränkte Unterstützung großer Karten
- eingeschränkte Anzahl aktiver Einheiten
- Unterschiede zwischen Browsern
- mögliche Probleme mit Hintergrund-Tabs
- geringere Kontrolle über Hardware und Dateisystem

Die Browser-Version wird daher nicht als technische Leitplattform festgelegt.

---

# 6. Rendering und Grafik

## 6.1 Rendering-Pipeline

**Unity Universal Render Pipeline – URP**

URP wird gegenüber einer reinen High-End-Desktop-Pipeline bevorzugt.

### Gründe

- Unterstützung mehrerer Plattformen
- gute Performance
- geeignet für stilisierte 3D-Grafik
- kompatibel mit Desktop und Mobile
- bessere Grundlage für einen möglichen WebGL-Build
- ausreichend für moderne RTS-Grafik

---

## 6.2 Kameraperspektive

Verwendet wird eine:

**dreidimensionale isometrische beziehungsweise schräge Top-Down-Kamera**

Die Welt und die Einheiten bestehen aus echten 3D-Modellen.

Die Kamera zeigt das Spielgeschehen aus einer erhöhten, schrägen Perspektive.

Geplante Funktionen:

- freies Verschieben
- Zoom
- optionales Drehen
- Begrenzung auf Kartenränder
- Fokus auf ausgewählte Einheiten
- weiche Kamerabewegung
- taktische Übersicht
- Minimap-Navigation

---

## 6.3 Visueller Stil

Empfohlene Stilrichtung:

**Stylized Military Science Fiction**

Merkmale:

- klare Silhouetten
- gut unterscheidbare Fraktionen
- vereinfachte, aber hochwertige Formen
- moderate Polygonzahlen
- lesbare Einheiten aus großer Entfernung
- kontrollierte Partikeleffekte
- klare Fraktionsfarben
- keine unnötig fotorealistische Darstellung

Die Lesbarkeit des Spielgeschehens besitzt Vorrang vor maximalem Realismus.

---

# 7. Asset-Strategie

## 7.1 Grundsatz

Für Prototyp und MVP werden möglichst viele Assets gekauft oder aus bestehenden Paketen übernommen.

Dazu gehören insbesondere:

- Fahrzeuge
- Gebäude
- Infanterie-Basismodelle
- Animationen
- Landschaften
- Vegetation
- Felsen
- Straßen
- Ruinen
- Explosionen
- Waffen-VFX
- Soundeffekte
- UI-Basiskomponenten

---

## 7.2 Eigene Signature-Assets

Individuell entwickelt werden vor allem die Assets, die das Spiel unverwechselbar machen.

Dazu gehören:

- zentrale Kristallressource
- Ressourcenfelder
- Sammler
- Fraktionslogos
- Commander
- Hauptquartiere
- Superwaffen
- besondere Eliteeinheiten
- besondere Gebäude
- fraktionsspezifische Effekte
- zentrale UI-Identität
- Key Art

---

## 7.3 Asset-Anforderungen

Vor dem Kauf eines Assetpakets müssen geprüft werden:

- Unity-Kompatibilität
- verwendete Renderpipeline
- Lizenz für kommerzielle Nutzung
- Polygonzahl
- Texturauflösung
- LOD-Stufen
- Animationen
- Rigging
- Materialaufbau
- mobile Eignung
- WebGL-Eignung
- visuelle Kompatibilität mit anderen Paketen
- Anpassbarkeit
- Dateiformate
- Support und Aktualität

---

# 8. Technische Kernsysteme

Folgende Systeme müssen modular entwickelt werden:

## 8.1 Einheitensystem

- Einheitendaten
- Lebenspunkte
- Geschwindigkeit
- Panzerung
- Waffen
- Reichweite
- Sichtweite
- Fähigkeiten
- Fraktionszugehörigkeit
- Erfahrungsstufen
- Status-Effekte
- Animationen
- Audio

---

## 8.2 Auswahl- und Befehlssystem

- Einzelwahl
- Mehrfachauswahl
- Auswahlrahmen
- Kontrollgruppen
- Rechtsklick-Befehle
- Angriffsbefehl
- Bewegungsbefehl
- Patrouille
- Bewachen
- Stoppen
- Position halten
- Wegpunkte
- Formationen

---

## 8.3 Pathfinding

Das Wegfindungssystem muss für große Einheitenzahlen ausgelegt werden.

Anforderungen:

- Infanterie
- Fahrzeuge
- große Fahrzeuge
- Luftfahrzeuge
- unterschiedliche Bewegungsradien
- dynamische Hindernisse
- zerstörte Gebäude
- Engstellen
- Formationen
- Vermeidung von Staus
- möglichst geringe CPU-Belastung

Ein klassisches NavMesh allein reicht für ein großes RTS möglicherweise nicht aus. Daher muss früh geprüft werden, ob ein Grid-, Flow-Field- oder hybrides Pathfinding-System erforderlich ist.

---

## 8.4 Ressourcen- und Wirtschaftssystem

- Kristallfelder
- Sammler
- Raffinerien
- Transportweg
- Ressourcenkonto
- Baukosten
- Produktionskosten
- Reparaturkosten
- Energieversorgung
- Lagerkapazität
- Ressourcenwachstum
- erschöpfte Felder

---

## 8.5 Base-Building-System

- Gebäudemenü
- Bauvoraussetzungen
- Bauzeiten
- Platzierungsvorschau
- gültige und ungültige Bauflächen
- Kollisionsprüfung
- Energieverbrauch
- Produktionsradien
- Fraktionsgrenzen
- Reparatur
- Verkauf
- Zerstörung
- Bauwarteschlange

---

## 8.6 Kampfsystem

- Projektilwaffen
- Hitscan-Waffen
- Raketen
- Explosionen
- Flächenschaden
- Panzerungstypen
- Schadensarten
- Luftabwehr
- Bodenangriffe
- Status-Effekte
- Reichweitenlogik
- Zielpriorisierung
- Friendly Fire als optionale Regel
- Deckung als optionale Regel

---

## 8.7 Fog of War

- unerforschte Karte
- bereits erkundete Bereiche
- aktuell sichtbare Bereiche
- Sichtweite pro Einheit
- Radar
- Tarnung
- Aufdeckung
- Team-Sicht
- Minimap-Integration

---

## 8.8 Produktionssystem

- Infanterieproduktion
- Fahrzeugproduktion
- Luftfahrzeugproduktion
- Warteschlangen
- Produktionszeiten
- Pausieren
- Abbrechen
- Sammelpunkte
- Produktionsboni
- Technologieabhängigkeiten

---

## 8.9 Technologiebaum

- Tech-Stufen
- Forschungsgebäude
- Freischaltungen
- Upgrades
- Fraktionsboni
- Einheitenverbesserungen
- Gebäudeverbesserungen
- Waffenverbesserungen
- Wirtschaftsupgrades
- Superwaffen

---

## 8.10 KI-System

Die KI soll modular aufgebaut werden.

KI-Ebenen:

- strategische Ebene
- wirtschaftliche Ebene
- Basisbau
- Verteidigung
- Aufklärung
- Armeeproduktion
- Angriffsplanung
- Einheitensteuerung
- Rückzug
- Nutzung von Fähigkeiten
- Reaktion auf Spielerstrategien

Schwierigkeitsgrade sollen primär durch Entscheidungsqualität und Reaktionslogik entstehen, nicht ausschließlich durch künstliche Ressourcenboni.

---

# 9. Multiplayer-Architektur

## 9.1 Grundsatz

Für kompetitive Multiplayer-Partien wird langfristig eine autoritative Serverarchitektur empfohlen.

Der Server entscheidet über:

- gültige Befehle
- Einheitenpositionen
- Schaden
- Ressourcen
- Produktion
- Sieg und Niederlage
- Match-Zustand

Dies reduziert Manipulation und Synchronisationsfehler.

---

## 9.2 Multiplayer-Bestandteile

- Benutzerkonten
- Freundesliste
- Lobbys
- Matchmaking
- Ranglisten
- private Matches
- öffentliche Matches
- Teamspiele
- Beobachtermodus
- Replays
- Statistiken
- Match-Historie
- Abbruch- und Reconnect-Logik

---

## 9.3 Backend

Das Backend kann unabhängig vom Unity-Client entwickelt werden.

Empfohlene Optionen:

### Option A

- C#
- ASP.NET Core
- PostgreSQL

### Option B

- TypeScript
- Node.js
- PostgreSQL

Die endgültige Backend-Entscheidung wird erst getroffen, wenn der Multiplayer-Prototyp beginnt.

---

# 10. Projektstruktur

Empfohlene Unity-Projektstruktur:

```text
Assets/
├── Art/
│   ├── Characters/
│   ├── Vehicles/
│   ├── Buildings/
│   ├── Environment/
│   ├── Resources/
│   ├── Materials/
│   ├── Textures/
│   └── VFX/
├── Audio/
│   ├── Music/
│   ├── SFX/
│   ├── UI/
│   └── Voice/
├── Prefabs/
│   ├── Units/
│   ├── Buildings/
│   ├── Projectiles/
│   ├── Environment/
│   └── UI/
├── Scenes/
│   ├── Boot/
│   ├── Menu/
│   ├── Gameplay/
│   └── Test/
├── Scripts/
│   ├── Core/
│   ├── Units/
│   ├── Buildings/
│   ├── Combat/
│   ├── Economy/
│   ├── AI/
│   ├── Pathfinding/
│   ├── Multiplayer/
│   ├── UI/
│   └── Tools/
├── ScriptableObjects/
│   ├── Units/
│   ├── Buildings/
│   ├── Weapons/
│   ├── Technologies/
│   └── Factions/
└── ThirdParty/
```

---

# 11. Datengetriebene Entwicklung

Einheiten, Gebäude, Waffen und Technologien sollen möglichst datengetrieben aufgebaut werden.

Daten werden nicht fest im Gameplay-Code hinterlegt.

Verwendet werden beispielsweise Unity ScriptableObjects für:

- Einheitenwerte
- Gebäudewerte
- Waffenwerte
- Baukosten
- Produktionszeiten
- Fraktionszugehörigkeit
- Upgrade-Werte
- Tech-Voraussetzungen
- visuelle Prefabs
- Soundzuweisungen
- Effekte

Vorteile:

- schnelleres Balancing
- weniger Codeänderungen
- einfachere Arbeitsteilung
- bessere Modifizierbarkeit
- leichtere Erstellung neuer Einheiten
- bessere Automatisierung durch Tools und KI-Agenten

---

# 12. Versionsverwaltung

## 12.1 Git

Das Projekt wird über Git versioniert.

Empfohlen:

- GitHub
- Git LFS für große Binärdateien
- geschützte Hauptbranches
- Pull Requests
- automatisierte Builds
- automatisierte Tests

---

## 12.2 Branching

Empfohlene Struktur:

- `main` – stabile veröffentlichbare Version
- `develop` – integrierter Entwicklungsstand
- `feature/...` – einzelne Funktionen
- `fix/...` – Fehlerbehebungen
- `art/...` – größere Asset-Integrationen
- `release/...` – Release-Vorbereitung

Bei paralleler Arbeit mehrerer Agenten oder Entwickler sollten getrennte Git-Worktrees verwendet werden, damit jeder Arbeitsprozess ein eigenes Verzeichnis und einen eigenen Branch besitzt.

---

# 13. Entwicklungsphasen

## Phase 0 – Technischer Spike

Ziel:

Prüfung der größten technischen Risiken.

Zu testen:

- Kamerasteuerung
- 100 bis 500 bewegte Einheiten
- Pathfinding
- Auswahlrahmen
- einfache Kämpfe
- Gebäudebau
- Ressourcenabbau
- Performance auf Mac und Windows
- Asset-Import
- URP-Kompatibilität

Ergebnis:

Ein technischer Prototyp ohne Anspruch auf finale Grafik.

---

## Phase 1 – Gameplay-Prototyp

Umfang:

- eine Fraktion
- eine Karte
- eine Ressource
- ein Sammler
- eine Raffinerie
- ein Kraftwerk
- eine Kaserne
- eine Fahrzeugfabrik
- zwei Infanterieeinheiten
- zwei Fahrzeuge
- ein Verteidigungsturm
- einfache Gegner-KI
- Sieg und Niederlage

Ziel:

Der vollständige Kernloop muss funktionieren.

Kernloop:

```text
Ressourcen sammeln
→ Basis erweitern
→ Einheiten produzieren
→ Gegner angreifen
→ Karte kontrollieren
→ Match gewinnen
```

---

## Phase 2 – Vertical Slice

Umfang:

- eine visuell ausgearbeitete Fraktion
- eine qualitativ hochwertige Karte
- vollständiges UI
- Audio
- VFX
- mehrere Einheitentypen
- Technologiebaum
- Fog of War
- gute KI
- Tutorial
- Performance-Optimierung
- erste Multiplayer-Tests

Ziel:

Eine kurze, aber qualitativ repräsentative Version des späteren Spiels.

---

## Phase 3 – Produktionsversion

Umfang:

- drei Fraktionen
- mehrere Karten
- vollständige Einheitenlisten
- Kampagne oder Gefechtsmodus
- Multiplayer
- Matchmaking
- Replays
- Ranglisten
- Balancing
- Accessibility
- Lokalisierung
- vollständiges Audio
- finale Art Direction

---

## Phase 4 – Plattform-Ports

Prüfung und mögliche Umsetzung für:

- iPadOS
- Android-Tablets
- WebGL
- iPhone
- Android-Smartphones

Jede Plattform erhält eigene:

- UI-Anpassungen
- Performance-Profile
- Qualitätsstufen
- Eingabemethoden
- Testpläne

---

# 14. MVP-Abgrenzung

Der MVP enthält ausdrücklich nicht:

- drei vollständig ausgearbeitete Fraktionen
- mobile Version
- Browser-Version
- Kampagne
- Ranglisten
- Clans
- Turniere
- umfangreiche Story
- Cinematics
- Marineeinheiten
- hunderte Einheiten
- komplexes Live-Service-System

Der MVP dient ausschließlich der Validierung des Spielkerns.

---

# 15. Technische Qualitätsziele

## Performance

Desktop-Ziel:

- stabile 60 FPS auf typischer Gaming-Hardware
- mindestens 30 FPS auf schwächerer Hardware
- mehrere hundert aktive Einheiten als langfristiges Ziel
- geringe Garbage-Collection-Spitzen
- kontrollierter Speicherverbrauch
- skalierbare Grafikqualität

---

## Stabilität

- deterministische oder kontrollierte Simulation
- reproduzierbare Fehler
- automatisierte Tests für Kernsysteme
- Logging
- Performance-Profiling
- Crash-Reporting
- Savegame-Versionierung
- Schutz vor beschädigten Spieldaten

---

## Wartbarkeit

- modulare Systeme
- klare Schnittstellen
- keine unnötigen globalen Abhängigkeiten
- ereignisbasierte Kommunikation
- datengetriebene Konfiguration
- dokumentierte Architektur
- wiederverwendbare Prefabs
- getrennte Gameplay- und Präsentationslogik

---

# 16. Offene technische Entscheidungen

Folgende Entscheidungen werden bewusst erst später getroffen:

- konkretes Multiplayer-Framework
- dedizierter Serveranbieter
- Backend-Sprache
- Hosting-Anbieter
- genaue Datenbankstruktur
- finale Pathfinding-Lösung
- Modding-Unterstützung
- Workshop-Integration
- DRM
- Vertrieb über Steam, Epic oder eigene Plattform
- Crossplay
- Konsolenversionen

Diese Entscheidungen dürfen den frühen Prototyp nicht blockieren.

---

# 17. Verbindliche Entscheidung

Für die erste Entwicklungsphase wird folgender Stack festgelegt:

```text
Game Engine:
Unity

Programmiersprache:
C#

Rendering:
Universal Render Pipeline

Primäre Plattformen:
Windows und macOS

Entwicklungsplattform:
macOS auf Apple Silicon

Asset-Strategie:
Asset Store zuerst, individuelle Signature-Assets später

Multiplayer:
erst nach stabilem Singleplayer-Kern

Mobile:
spätere Portierung

Browser:
spätere reduzierte WebGL-Version oder Demo

Versionsverwaltung:
GitHub und Git LFS

Architektur:
modular, datengetrieben und plattformübergreifend
```

---

# 18. Nächster konkreter Schritt

Als nächstes wird ein technischer Unity-Prototyp erstellt.

Dieser muss ausschließlich folgende Funktionen enthalten:

1. isometrische Kamera
2. große einfache Testkarte
3. Auswahl einzelner und mehrerer Einheiten
4. Bewegungsbefehle
5. einfaches Pathfinding
6. ein Ressourcenfeld
7. ein Sammler
8. eine Raffinerie
9. Ressourcenanzeige
10. Platzierung eines Gebäudes
11. Produktion einer Einheit
12. einfacher Angriff
13. einfache Gegner-KI
14. Sieg- und Niederlagezustand
15. Performance-Messung

Erst wenn dieser Prototyp stabil funktioniert, beginnt die eigentliche Content-Produktion.
