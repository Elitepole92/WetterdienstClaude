#!/usr/bin/env python3
"""Schreibt spruch.json für das SenseCraft-HMI-Dashboard.

Aufruf: python3 scripts/schreibe_spruch.py "<Spruch>" < wetter.json
Die Wetterdaten (Ausgabe von wetter.py) kommen über stdin.
"""
import json
import sys
from pathlib import Path

ZIEL = Path(__file__).resolve().parent.parent / "spruch.json"


def main():
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        sys.exit("Aufruf: schreibe_spruch.py \"<Spruch>\" < wetter.json")
    spruch = " ".join(sys.argv[1].split())
    w = json.load(sys.stdin)
    a, h = w["aktuell"], w["heute"]

    out = {
        "spruch": spruch,
        "temperatur": f"{a['temp']} °C",
        "gefuehlt": f"{a['gefuehlt']} °C",
        "wetter": a["wetter"],
        "wind": f"{a['wind_kmh']} km/h, Böen {a['boeen_kmh']} km/h",
        "heute": f"{h['min']}–{h['max']} °C, {h['wetter']}, Regenrisiko {h['regen_prozent']} %",
        "stand": w["jetzt"][8:10] + "." + w["jetzt"][5:7] + ". " + w["jetzt"][11:16] + " Uhr",
    }
    ZIEL.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(ZIEL.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
