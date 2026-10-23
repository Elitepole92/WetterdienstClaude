#!/usr/bin/env python3
"""Holt das Wetter für Bremen, Östliche Vorstadt, von Bright Sky (DWD-Daten,
https://brightsky.dev) und gibt eine kompakte Zusammenfassung als JSON auf
stdout aus (Grundlage für den Spruch)."""
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

LAT, LON = 53.074, 8.829
TZ = ZoneInfo("Europe/Berlin")
API = "https://api.brightsky.dev"

ICON = {
    "clear-day": "klar", "clear-night": "klar", "partly-cloudy-day": "teils bewölkt",
    "partly-cloudy-night": "teils bewölkt", "cloudy": "bedeckt", "fog": "Nebel",
    "wind": "windig", "rain": "Regen", "sleet": "Schneeregen", "snow": "Schnee",
    "hail": "Hagel", "thunderstorm": "Gewitter",
}


def hole(pfad, **params):
    url = f"{API}/{pfad}?" + urllib.parse.urlencode(
        {"lat": LAT, "lon": LON, "tz": "Europe/Berlin", **params})
    req = urllib.request.Request(url, headers={"User-Agent": "WetterdienstClaude"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def wetter(eintrag):
    return ICON.get(eintrag.get("icon"), eintrag.get("condition") or "?")


def runde(x):
    return None if x is None else round(x)


def gefuehlt(t, v):
    # Windchill nach DWD-Formel, sonst Lufttemperatur
    if t is None or v is None or t > 10 or v <= 4.8:
        return t
    return 13.12 + 0.6215 * t - 11.37 * v ** 0.16 + 0.3965 * t * v ** 0.16


def main():
    now = datetime.now(TZ)
    cur = hole("current_weather")["weather"]
    stunden = hole("weather", date=now.date().isoformat(),
                   last_date=(now.date() + timedelta(days=2)).isoformat())["weather"]
    for s in stunden:
        s["_t"] = datetime.fromisoformat(s["timestamp"])

    naechste = [
        {
            "zeit": s["_t"].strftime("%H:%M"),
            "temp": runde(s["temperature"]),
            "wetter": wetter(s),
            "regen_mm": s.get("precipitation"),
            "regen_prozent": s.get("precipitation_probability"),
            "boeen_kmh": runde(s.get("wind_gust_speed")),
        }
        for s in stunden if s["_t"] >= now - timedelta(hours=1)
    ][:6]

    def tag(datum):
        h = [s for s in stunden if s["_t"].date() == datum]
        temps = [s["temperature"] for s in h if s["temperature"] is not None]
        probs = [s["precipitation_probability"] for s in h
                 if s.get("precipitation_probability") is not None]
        boeen = [s["wind_gust_speed"] for s in h if s.get("wind_gust_speed") is not None]
        tags = [s for s in h if 8 <= s["_t"].hour <= 18] or h
        icons = [wetter(s) for s in tags]
        return {
            "datum": datum.isoformat(),
            "max": runde(max(temps)) if temps else None,
            "min": runde(min(temps)) if temps else None,
            "wetter": max(set(icons), key=icons.count) if icons else "?",
            "regen_mm": round(sum(s.get("precipitation") or 0 for s in h), 1),
            "regen_prozent": max(probs) if probs else None,
            "boeen_max_kmh": runde(max(boeen)) if boeen else None,
        }

    t, v = cur.get("temperature"), cur.get("wind_speed_10")
    out = {
        "ort": "Bremen, Östliche Vorstadt",
        "jetzt": now.strftime("%Y-%m-%d %H:%M"),
        "wochentag": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag",
                      "Samstag", "Sonntag"][now.weekday()],
        "aktuell": {
            "temp": runde(t),
            "gefuehlt": runde(gefuehlt(t, v)),
            "wetter": wetter(cur),
            "luftfeuchte": cur.get("relative_humidity"),
            "bewoelkung_prozent": cur.get("cloud_cover"),
            "wind_kmh": runde(v),
            "boeen_kmh": runde(cur.get("wind_gust_speed_10")),
            "niederschlag_mm_10min": cur.get("precipitation_10"),
        },
        "naechste_stunden": naechste,
        "heute": tag(now.date()),
        "morgen": tag(now.date() + timedelta(days=1)),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
