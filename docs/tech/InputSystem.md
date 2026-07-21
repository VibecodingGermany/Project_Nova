# Input System

**Version:** 0.1.0 | **Status:** Entwurf | **Verantwortungsbereich:** Lead UI/UX Designer | **Sprint:** 3

## Zweck

Technisches Design des Eingabe-Systems von Project Nova: Unity Input System als Basis, vollständiges Belegungsschema aus [../vision/CoreGameplay.md](../vision/CoreGameplay.md), strikte Übersetzung aller Eingaben in Simulations-Commands (D-033), Rebinding-Architektur als Accessibility-Pflichtpaket, Eingabe-Abstraktion für die spätere Touch-Portierung (TPD §5.2) und UI-Toolkit-Integration. Umsetzungsreif für Sprint 7, ohne Implementierungslogik.

## Abhängigkeiten

- [../production/DecisionLog.md](../production/DecisionLog.md) – insb. D-033 (Commands als einzige State-Mutation, lokaler Server), D-035 (MonoBehaviour/SO-Gerüst), D-019/D-029 (Kamera, Rotation erst ab Beta)
- [../vision/CoreGameplay.md](../vision/CoreGameplay.md) – verbindliches Belegungsschema, Kamera-Parameter, Responsivitäts-Ziel ≤ 100 ms Feedback
- [../research/Animation_Audio_UI.md](../research/Animation_Audio_UI.md) – UI-Technologiewahl (UI Toolkit primär), Hotkey-Grundsatz (Hotkeys laufen über Game-Code)
- [../../RTS_Technisches_Planungsdokument.md](../../RTS_Technisches_Planungsdokument.md) – §5.1 Desktop-first, §5.2 Tablet später
- [./GameState.md](./GameState.md) – Command-Schema und Command-Eingangsstelle des Sim-Ticks (Schwestervorgabe D-033)
- [./CameraSystem.md](./CameraSystem.md) – Kamera-Controller, der die hier definierten Kamera-Intents konsumiert

## Architektur-Überblick

Vier-Schichten-Pipeline; jede Schicht ist einzeln testbar:

1. **Device-Schicht:** Unity Input System (neues Paket, `InputAction`-Assets) für Maus/Tastatur. Hinter der `IInputSource`-Abstraktion, damit Touch (TPD §5.2) später als zweite Quelle andockt.
2. **Intent-Schicht:** Übersetzt rohe Aktionen in spielerische Absichten (`SelectIntent`, `ContextOrderIntent`, `CameraIntent`, …), inklusive Kontextlogik (Rechtsklick-Auswertung, Drag-Selektion, Doppelklick, Shift-Wegpunkte). Reine View-/Client-Logik, nicht Teil der Simulation.
3. **Command-Schicht:** Befehle, die Spielzustand ändern (Bewegen, Angreifen, Bauen, Produzieren, Aggressions-Modus, Sammelpunkt), werden **ausschließlich** als Commands an die lokale Server-Schleife (Singleplayer = lokaler Server, D-033) übergeben. **Niemals mutiert Input direkt Sim-State.** Selektion, Kamera und UI-Zustand sind Client-State und erzeugen bewusst *keine* Commands (nicht replikationspflichtig).
4. **Feedback-Schicht:** Sofortiges Client-Feedback ≤ 100 ms (Befehlsmarker, akustische Bestätigung) beim Absenden des Commands – unabhängig davon, in welchem Sim-Tick (10 Hz) der Command wirkt.

```csharp
namespace Nova.Input
{
    public interface IInputSource               // Device-Abstraktion (Touch-fähig, TPD §5.2)
    {
        event Action<InputIntent> IntentEmitted;
        PointerState Pointer { get; }           // Position, Buttons, Delta – einheitlich für Maus/Touch
        bool IsAvailable { get; }
    }

    public abstract record InputIntent;         // reine Daten, kein Unity-Typ
    public sealed record SelectIntent(SelectMode Mode, ScreenRect? Area, EntityHandle? Target) : InputIntent;
    public sealed record ContextOrderIntent(OrderKind Kind, Vector3 WorldPos, EntityHandle? Target, bool Queue) : InputIntent;
    public sealed record CommandCardIntent(string ActionId, Vector3? WorldPos, EntityHandle? Target) : InputIntent;
    public sealed record CameraIntent(CameraAction Action, float Value) : InputIntent;
    public sealed record ControlGroupIntent(int Group, GroupOp Op) : InputIntent;

    public interface ICommandEmitter            // einzige Brücke zur Sim (D-033, Regel 1)
    {
        void Emit(ICommand command);            // → CommandQueue des lokalen Servers
    }
}
```

Die Zuordnung `Intent → ICommand` (welche `OrderKind`s welche Command-Typen erzeugen) ist mit ./GameState.md abzustimmen; GameState.md bleibt führend für das Command-Schema.

## Belegungsschema (Werkseinstellung)

Datengetrieben über `InputProfile`-ScriptableObject: flache Liste `action → key` (CoreGameplay), tauschbar ohne Codeänderung; ein vorgefertigtes Grid-Layout-Profil wird mitgeliefert.

```csharp
public sealed class InputProfileSO : ScriptableObject
{
    public string ProfileName;                  // "Default" | "Grid" | benutzerdefiniert
    public List<ActionBinding> Bindings;        // actionId → InputAction-Referenz (flache Liste)
}
```

### Auswahl

| Aktion | actionId | Eingabe (Werk) |
|---|---|---|
| Einzelauswahl / Auswahl aufheben | `select` | Linksklick |
| Auswahlrahmen | `select.drag` | Linksklick halten + ziehen |
| Hinzufügen/Entfernen (Toggle) | `select.modify` | Shift + Klick/Rahmen |
| Typauswahl (Bildschirm) | `select.sametype` | Doppelklick auf Einheit |
| Kampfeinheiten im Bildschirm | `select.combat` | E |
| Ganze Armee (kartenweit) | `select.army` | Strg + A |
| Kontrollgruppe setzen/abrufen/hinzufügen | `group.0`–`group.9` | Strg + 0–9 / 0–9 / Shift + 0–9 |
| Zur Gruppe springen | (implizit) | Doppeltippen auf Gruppennummer |

### Befehle (erzeugen Commands)

| Aktion | actionId | Eingabe (Werk) |
|---|---|---|
| Kontextbefehl (sammeln/angreifen/einsteigen/reparieren/bewegen) | `order.context` | Rechtsklick |
| Bewegen | `order.move` | M (+ Linksklick) |
| Angriff-Bewegen | `order.attackmove` | A + Linksklick |
| Patrouille | `order.patrol` | P + Linksklick |
| Bewachen | `order.guard` | W + Ziel |
| Stoppen | `order.stop` | S |
| Halten (Aggressions-Modus) | `mode.hold` | H |
| Streuen | `order.scatter` | X |
| Wegpunkt anhängen (bis 16) | `order.queue` | Shift + Befehl |
| Rückzug/Sammelruf | `order.retreat` | R |
| Formation Linie/Keil/Block | `formation.line/.wedge/.block` | F6–F8 |
| Befehlskacheln Reihe 1/2 | `card.q/.w/.e/.r`, `card.a/.s/.d/.f` | Q/W/E/R, A/S/D/F (Positionsraster) |

Kontextlogik Rechtsklick (Intent-Schicht): Aetherium-Feld → sammeln; Feind → angreifen; Transport → einsteigen; verbündetes beschädigtes Ziel → reparieren; Gelände → bewegen; **FoW-Gelände → immer bewegen** (Fehlklick-Sicherheit, CoreGameplay).

### Bau und Produktion

| Aktion | actionId | Eingabe (Werk) |
|---|---|---|
| Bau-Menü | `build.menu` | B oder Sidebar-Klick |
| Platzieren / Ausrichten / Mauer-Linie | `build.place` | Linksklick, Ziehen |
| Platzierung abbrechen | `build.cancel` | Rechtsklick/Esc |
| Queue ×5 / Abbruch (75 % Erstattung) | `queue.five` / `queue.cancel` | Shift-Klick / Rechtsklick auf Icon |
| Sammelpunkt setzen | `rally.set` | Rechtsklick mit ausgewählter Fabrik |

### Kamera und Komfort (Client-State, keine Commands)

| Aktion | actionId | Eingabe (Werk) |
|---|---|---|
| Zoomen (stufenlos, Ease 0,15 s) | `cam.zoom` | Scrollrad |
| Edge-Scroll (Stärke 0–100 %, Fenstermodus-Regel) | `cam.edgescroll` | Maus an Bildschirmkante |
| Panning | `cam.pan` | Pfeiltasten / MMB-Drag |
| Kamera-Bookmarks setzen/springen | `cam.mark.1–4` / `cam.jump.1–4` | Strg + F1–F4 / F1–F4 |
| Zum HQ | `cam.home` | Pos1 |
| Zum letzten Ereignis | `cam.event` | Leertaste |
| Folge-Modus (explizit, kein Auto-Follow) | `cam.follow` | F auf Auswahl |
| Idle-Worker-Cycle | `ui.idleworker` | Tab |
| Rotation (Snap 45°, Nord-Reset) | `cam.rotate` | Q/E – **gebunden, aber bis Beta deaktiviert** (D-029) |

## Rebinding-Architektur (Accessibility-Pflicht)

- Sämtliche Belegungen sind zur Laufzeit umlegbar (Accessibility-Pflichtpaket aus CoreGameplay: freie Tastenbelegung); Umsetzung über die Rebinding-API des Input Systems (`InputActionRebindingExtensions`), nie über hart codierte `KeyCode`-Abfragen.
- **Persistenz:** Benutzer-Overrides als JSON (`InputActionAsset.SaveBindingOverridesAsJson`) in den Benutzereinstellungen; `InputProfileSO` bleibt unverändert (Definitions-only-Regel – kein Runtime-State in SOs).
- **Konfliktprüfung:** Beim Belegen wird geprüft, ob die Zieltaste in derselben Kontextgruppe (Global / Auswahl / Befehl / Kamera / Bau) bereits belegt ist; Konflikte werden dem Nutzer angezeigt, Duplikate über Kontextgruppen hinweg sind erlaubt.
- **Profile:** Default, Grid und beliebig viele Nutzerprofile; Wechsel jederzeit, auch im Match.
- Modifier (Strg/Shift/Alt) sind Bestandteil der Bindung und ebenfalls umlegbar; macOS-⌘-Äquivalenz (Strg ↔ Cmd) wird über Binding-Gruppen je Plattform gelöst (D-006: Windows/macOS primär).

## Touch-Portierung (TPD §5.2, Abstraktion jetzt)

- `IInputSource` + `InputIntent` sind geräteneutral definiert; Touch dockt später als zweite Quelle mit eigener Gesten-Erkennung an (Tap = `select`, Two-Finger-Tap = `order.context`, Drag = Auswahlrahmen, Pinch = `cam.zoom`, Edge-Pan-Ersatz über Kartenrand-Geste).
- Intent-Schicht und Command-Schicht bleiben unverändert – nur die Device-Schicht und ein Touch-spezifisches `InputProfileSO` kommen hinzu.
- Explizit **nicht** jetzt gebaut: Touch-Gesten, vereinfachte Kontrollgruppen, reduzierte HUD-Dichte (TPD §5.2). Die Abstraktion darf dafür keine Desktop-Annahmen verankern (z. B. keine Hover-Pflicht in Intents; Hover ist optionaler Intent).

## UI-Toolkit-Integration

- HUD/Menus laufen über UI Toolkit mit `InputSystemUIInputModule` (gleiche Input-System-Quelle, kein Legacy-`StandaloneInputModule`).
- **Hotkeys laufen über Game-Code, nicht über UI-Toolkit-Events** (Research-Grundsatz): Das Eingabe-System feuert Intents, das HUD spiegelt nur Zustand (Kachel-Highlight bei Tastendruck). So bleiben Hotkeys auch bei geändertem UI-Fokus zuverlässig.
- Fokus-Regel: Texteingabefelder (Chat-Ersatz/Savegame-Name) capturen Tastatur; während Capture sind Spiel-Hotkeys suspendiert (Input-System-Action-Map-Umschaltung `UI` vs. `Gameplay`).
- World-Space-Elemente (Healthbars, Selektionsringe) sind gebatchte Mesh-Overlays außerhalb des UI-Systems (Research) und konsumieren keine Eingaben; Hover-/Klick-Treffer liefert der Picking-Dienst der Intent-Schicht (Raycast gegen Sim-Entity-Proxies, FoW-gefiltert).

## Performance und Determinismus

- Eingabe-Verarbeitung ist Frame-gebunden (Client), die Command-Ausführung Tick-gebunden (10 Hz, D-033); Feedback ≤ 100 ms bleibt dadurch eingehalten.
- Kein GC im Hotpath: Intents und Commands werden gepoolt (UnityEngine.Pool, D-035-Leitplanke).
- Eingaben beeinflussen den Sim-State nur über Commands – Replays/Lockstep (ab Beta) müssen dazu nur den Command-Stream aufzeichnen, nicht die Roh-Eingaben.

## Offene Punkte

- **Intent→Command-Mapping:** Verbindliche Zuordnungstabelle (`OrderKind`/`CommandCardIntent` ↔ Command-Typen) muss mit ./GameState.md abgeglichen werden; GameState.md ist führend. Nicht eigenständig entscheidbar.
- **Doppelklick-/Doppeltippen-Timing:** Schwellwerte (ms) für Typauswahl und Gruppen-Sprung sind Gefühlswerte; Festlegung nach erstem Playtest.
- **Edge-Scroll im Fenstermodus:** CoreGameplay sagt „im Vollbild-Fenstermodus standardmäßig aus" – die exakte Erkennungsregel (Fenster-Fokus, Multi-Monitor) ist mit dem CameraSystem abzustimmen.
- **Touch-Gesten-Mapping:** Detailbelegung erst bei Tablet-Konzeption (TPD §5.2); hier nur die Abstraktion festgelegt.
- **Action-Map-Umfang:** Ob Bau-Platzierungsmodus eine eigene Action-Map erhält (sauberere Konfliktprüfung) oder Kontext-Flag bleibt, wird im Sprint-7-Review entschieden.
- **Gamepad:** Nicht gefordert (Desktop Maus/Tastatur, TPD §5.1); Action-Maps sind so strukturiert, dass Gamepad später als dritte Quelle möglich bleibt – kein aktueller Arbeitsumfang.

## Nächste Schritte

- `InputProfileSO`- und `ActionBinding`-Schema mit dem GameDatabase-/DataModel-Design (Sprint-3-Schwesterdokument) abstimmen.
- Intent→Command-Mapping-Tabelle gemeinsam mit dem GameState.md-Verantwortlichen finalisieren.
- Rebinding-UI-Wireframe (Optionsmenü, Konfliktanzeige) als Teil der UI-Wireframes in Sprint 3 erstellen.
- Phase-0: Input-System-Setup (Action-Maps `Gameplay`/`UI`, macOS-Cmd-Binding-Gruppe) im Projekt-Grundgerüst verproben.

## Änderungsverlauf

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-21 | Erstfassung | Lead UI/UX Designer |
