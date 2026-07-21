#!/usr/bin/env python3
"""Docs-Konsistenz-Check für Project Nova.

Läuft ohne Abhängigkeiten (nur stdlib) und ist damit in der CI sehr günstig.

- HART (exit 1): tote interne Links in Markdown-Dateien (relative Pfade, die auf
  keine existierende Datei/keinen Ordner zeigen). Das ist der teuerste Doku-Fehler
  in einem verlinkten Wiki und mit sehr wenig Fehlalarm erkennbar.
- WEICH (nur Hinweis): docs/-Dateien ohne Standard-Kopfzeile (Version | Status ...).

Aufruf:  python3 .github/scripts/check_docs.py
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HEADER_RE = re.compile(r"\*\*Version:\*\*.*\|\s*\*\*Status:\*\*")

# Bekannte, bewusst geplante Vorwaerts-Verweise auf noch nicht erstellte Dokumente.
# Diese blockieren die CI NICHT (nur Hinweis), damit ein bekanntes "geplant"-Dokument
# den Merge nicht sperrt. JEDER andere tote Link ist ein harter Fehler.
# Eintraege entfernen, sobald das Dokument existiert.
KNOWN_PENDING = {
    "CameraSystem.md",  # von docs/tech/InputSystem.md referenziert; TDD noch offen (Sprint 3/4)
}


def is_external(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "tel:", "#"))


def main() -> int:
    dead: list[str] = []
    pending: list[str] = []
    missing_header: list[str] = []

    for dirpath, dirnames, filenames in os.walk(ROOT):
        # .git ausschliessen; .github enthaelt GitHub-Meta-Dateien (PR-/Issue-Vorlagen),
        # deren relative Links repo-root-relativ sind (andere Aufloesungsregel als im Wiki).
        dirnames[:] = [d for d in dirnames if d not in (".git", ".github")]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT)
            with open(path, encoding="utf-8") as fh:
                lines = fh.readlines()
            text = "".join(lines)

            for i, line in enumerate(lines, 1):
                for m in LINK_RE.finditer(line):
                    target = m.group(1).strip().split(" ")[0].strip()  # drop "title"
                    if not target or is_external(target):
                        continue
                    target_path = target.split("#")[0]  # drop anchor
                    if not target_path:
                        continue
                    resolved = os.path.normpath(os.path.join(dirpath, target_path))
                    if not os.path.exists(resolved):
                        if os.path.basename(target_path) in KNOWN_PENDING:
                            pending.append(f"{rel}:{i}  ->  {target}")
                        else:
                            dead.append(f"{rel}:{i}  ->  {target}")

            if rel.startswith("docs" + os.sep) and not HEADER_RE.search(text):
                missing_header.append(rel)

    if pending:
        print("::notice:: Links auf bekannte, geplante Dokumente (nicht blockierend):")
        for p in pending:
            print(f"  {p}")

    if missing_header:
        print("::notice:: docs/-Dateien ohne Standard-Kopfzeile (informativ, nicht blockierend):")
        for r in sorted(missing_header):
            print(f"  - {r}")

    if dead:
        print(f"\n::error:: {len(dead)} tote interne Link(s) gefunden:")
        for d in dead:
            print(f"  {d}")
        return 1

    print("OK: keine toten internen Links gefunden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
