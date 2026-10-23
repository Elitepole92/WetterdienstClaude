#!/usr/bin/env python3
"""Holt das Wetter für Bremen, Östliche Vorstadt, von Open-Meteo und gibt eine
kompakte Zusammenfassung als JSON auf stdout aus (Grundlage für den Spruch)."""
import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

LAT, LON = 53.074, 8.829
TZ = "Europe/Berlin"

WMO = {
    0: "klar", 1: "überwiegend klar", 2: "teils bewölkt", 3: "bedeckt",
    45: "Nebel", 48: "Raureif-Nebel",
    51: "leichter Niesel", 53: "Niesel", 55: "starker Niesel",
    56: "gefrierender Niesel", 57: "starker gefrierender Niesel",
    61: "leichter Regen", 63: "Regen", 65: "starker Regen",
    66: "gefrierender Regen", 67: "starker gefrierender Regen",
    71: "leichter Schnee", 73: "Schnee", 75: "starker Schnee", 77: "Schneegriesel",
    80: "leichte Schauer", 81: "Schauer", 82: "heftige Schauer",
    85: "Schneeschauer", 86: "starke Schneeschauer",
    95: "Gewitter", 96: "Gewitter mit Hagel", 99: "schweres Gewitter mit Hagel",
}

URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}&timezone={TZ}&forecast_days=2&wind_speed_unit=kmh"
    "&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,"
    "wind_speed_10m,wind_gusts_10m,precipitation"
    "&hourly=temperature_2m,weather_code,precipitation_probability,precipitation,wind_gusts_10m"
    "&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum,"
    "precipitation_probability_max,wind_gusts_10m_max,sunrise,sunset"
)


def main():
    with urllib.request.urlopen(URL, timeout=30) as r:
        d = json.load(r)

    now = datetime.now(ZoneInfo(TZ))
    cur, hourly, daily = d["current"], d["hourly"], d["daily"]

    # die nächsten 6 Stunden ab jetzt
    start = now.strftime("%Y-%m-%dT%H:00")
    i = hourly["time"].index(start) if start in hourly["time"] else 0
    naechste = [
        {
            "zeit": hourly["time"][j][11:16],
            "temp": round(hourly["temperature_2m"][j]),
            "wetter": WMO.get(hourly["weather_code"][j], "?"),
            "regen_prozent": hourly["precipitation_probability"][j],
            "boeen_kmh": round(hourly["wind_gusts_10m"][j]),
        }
        for j in range(i, min(i + 6, len(hourly["time"])))
    ]

    def tag(k):
        return {
            "datum": daily["time"][k],
            "max": round(daily["temperature_2m_max"][k]),
            "min": round(daily["temperature_2m_min"][k]),
            "wetter": WMO.get(daily["weather_code"][k], "?"),
            "regen_mm": daily["precipitation_sum"][k],
            "regen_prozent": daily["precipitation_probability_max"][k],
            "boeen_max_kmh": round(daily["wind_gusts_10m_max"][k]),
            "sonnenaufgang": daily["sunrise"][k][11:16],
            "sonnenuntergang": daily["sunset"][k][11:16],
        }

    out = {
        "ort": "Bremen, Östliche Vorstadt",
        "jetzt": now.strftime("%Y-%m-%d %H:%M"),
        "wochentag": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag",
                      "Samstag", "Sonntag"][now.weekday()],
        "aktuell": {
            "temp": round(cur["temperature_2m"]),
            "gefuehlt": round(cur["apparent_temperature"]),
            "wetter": WMO.get(cur["weather_code"], "?"),
            "luftfeuchte": cur["relative_humidity_2m"],
            "wind_kmh": round(cur["wind_speed_10m"]),
            "boeen_kmh": round(cur["wind_gusts_10m"]),
            "niederschlag_mm": cur["precipitation"],
        },
        "naechste_stunden": naechste,
        "heute": tag(0),
        "morgen": tag(1),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
