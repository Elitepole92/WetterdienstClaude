#!/usr/bin/env python3
"""Vogel-Lexikon für das SenseCraft-HMI-Dashboard.

1. Fragt bei iNaturalist ab, welche Vogelarten in den letzten Tagen rund um
   Bremen gemeldet wurden, und wählt eine davon (Abwechslung über den Verlauf).
2. Sucht auf Wikimedia Commons eine handkolorierte Tafel aus einem Vogelwerk
   des 19. Jahrhunderts (Naumann, Gould, Keulemans, Susemihl …; gemeinfrei).
3. Setzt daraus ein quadratisches Bild mit deutschem und lateinischem Namen
   und dem Datum der letzten Sichtung; schreibt vogel/vogel.png (1200×1200)
   und vogel/vogel.json.

Aufruf: python3 vogel/vogel.py [--art "Turdus merula"]
Schlägt etwas fehl, wird nichts überschrieben (Exit-Code != 0).
"""
import argparse
import io
import json
import math
import random
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

HIER = Path(__file__).resolve().parent
FONTS = HIER / "fonts"
TAFELN = HIER / "tafeln.json"      # Cache: Art -> gefundene Tafel (oder null)
INFO = HIER / "vogel.json"

LAT, LNG, RADIUS_KM = 53.08, 8.81, 20
TZ = ZoneInfo("Europe/Berlin")
UA = "VogelLexikon/1.0 (https://github.com/Elitepole92/WetterdienstClaude)"
INAT = "https://api.inaturalist.org/v1"
COMMONS = "https://commons.wikimedia.org/w/api.php"
VERLAUF_LAENGE = 20

PAPIER = (251, 248, 240)
TINTE = (28, 22, 16)
SEPIA = (92, 64, 40)

# Illustratoren bzw. Werke, deren Tafeln wir suchen (Suchbegriff, Bonus).
WERKE = [
    ("Naumann", 6), ("Gould", 5), ("Keulemans", 4), ("Susemihl", 4),
    ("von Wright", 4), ("Dresser", 3), ("Thorburn", 3), ("Lilford", 3),
    ("Frohawk", 2), ("Kleinschmidt", 2), ("Friderich", 2), ("Meyer", 1),
]
SPERRWOERTER = ("egg", "eier", "oolog", "skelet", "skull", "schädel", "map", "karte",
                "nest", "feder", "feather", "stamp", "briefmarke", "photo")
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
          "September", "Oktober", "November", "Dezember"]


# ---------------------------------------------------------------- HTTP

def hole_json(url, params):
    url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def hole_bild(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


# ---------------------------------------------------------------- iNaturalist

def gesichtete_arten(tage):
    d = hole_json(f"{INAT}/observations/species_counts", {
        "lat": LAT, "lng": LNG, "radius": RADIUS_KM, "iconic_taxa": "Aves",
        "d1": (date.today() - timedelta(days=tage)).isoformat(),
        "captive": "false", "hrank": "species", "locale": "de", "per_page": 200,
    })
    return [{
        "id": r["taxon"]["id"],
        "latein": r["taxon"]["name"],
        "deutsch": r["taxon"].get("preferred_common_name") or r["taxon"]["name"],
        "meldungen": r["count"],
    } for r in d["results"] if r["taxon"].get("rank") == "species"]


def letzte_sichtung(art, tage):
    obs = hole_json(f"{INAT}/observations", {
        "taxon_id": art["id"], "lat": LAT, "lng": LNG, "radius": RADIUS_KM,
        "d1": (date.today() - timedelta(days=tage)).isoformat(),
        "order_by": "observed_on", "order": "desc", "per_page": 1,
    })["results"]
    if obs and obs[0].get("observed_on"):
        art["zuletzt"] = obs[0]["observed_on"]
    return art


def waehle(arten, verlauf, rng):
    kandidaten = [a for a in arten if a["latein"] not in verlauf] or arten
    # Häufige Arten etwas bevorzugen, seltene aber nicht ausschließen.
    gewichte = [math.sqrt(a["meldungen"]) + 1 for a in kandidaten]
    reihenfolge = []
    while kandidaten:
        i = rng.choices(range(len(kandidaten)), weights=gewichte)[0]
        reihenfolge.append(kandidaten.pop(i))
        gewichte.pop(i)
    return reihenfolge


# ---------------------------------------------------------------- Commons

def jahr(meta):
    for feld in ("DateTimeOriginal", "DateTime"):
        txt = re.sub(r"<[^>]+>", " ", meta.get(feld, {}).get("value", ""))
        m = re.search(r"\b(1[6-9]\d\d)\b", txt)
        if m:
            return int(m.group(1))
    return None


def suche_tafel(art):
    latein, deutsch = art["latein"], art["deutsch"]
    gattung, epitheton = (latein.split() + [""])[:2]
    stamm = epitheton[:5].lower()
    treffer = {}
    anfragen = [f'"{latein}" {w}' for w, _ in WERKE[:6]]
    anfragen += [f'"{latein}" lithograph', f'{deutsch} Naumann Tafel', f'{epitheton} Naumann']
    for q in anfragen:
        try:
            d = hole_json(COMMONS, {
                "action": "query", "format": "json", "generator": "search",
                "gsrnamespace": 6, "gsrsearch": q, "gsrlimit": 25,
                "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
                "iiurlwidth": 1600,
            })
        except Exception as e:  # einzelne Suche darf scheitern
            print(f"  Commons-Suche '{q}' fehlgeschlagen: {e}", file=sys.stderr)
            continue
        for seite in d.get("query", {}).get("pages", {}).values():
            treffer.setdefault(seite["title"], seite)

    beste, beste_punkte = None, 0
    for titel, seite in treffer.items():
        ii = (seite.get("imageinfo") or [{}])[0]
        if ii.get("mime") not in ("image/jpeg", "image/png", "image/tiff"):
            continue
        meta = ii.get("extmetadata", {})
        text = " ".join([titel] + [re.sub(r"<[^>]+>", " ", meta.get(k, {}).get("value", ""))
                                   for k in ("ImageDescription", "ObjectName", "Artist",
                                             "Categories", "Credit")]).lower()
        if any(w in titel.lower() for w in SPERRWOERTER):
            continue
        name_ok = latein.lower() in text or (stamm and stamm in text and
                                            (gattung.lower() in text or deutsch.lower() in text))
        if not name_ok:
            continue
        punkte = 3 if latein.lower() in titel.lower() else 1
        werk = next(((w, b) for w, b in WERKE if w.lower() in text), None)
        j = jahr(meta)
        if werk:
            punkte += werk[1]
        if j and j <= 1925:
            punkte += 3
        elif not werk:
            continue  # vermutlich Foto oder moderne Zeichnung
        if j and j > 1940:
            continue
        b, h = ii.get("width", 0), ii.get("height", 0)
        if min(b, h) < 700:
            continue
        if h >= b:
            punkte += 1
        if punkte > beste_punkte:
            kuenstler = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ",
                                                    meta.get("Artist", {}).get("value", ""))).strip()
            beste_punkte, beste = punkte, {
                "datei": titel,
                "url": ii.get("thumburl") or ii["url"],
                "seite": ii.get("descriptionurl"),
                "kuenstler": kuenstler[:120],
                "werk": werk[0] if werk else None,
                "jahr": j,
            }
    return beste


# ---------------------------------------------------------------- Gestaltung

def schrift(name, groesse):
    datei = {"normal": "IMFeENrm28P.ttf", "kursiv": "IMFeENit28P.ttf",
             "kapitaelchen": "IMFeENsc28P.ttf"}[name]
    return ImageFont.truetype(str(FONTS / datei), groesse)


def bereite_tafel_auf(bild):
    """Papierton der Vorlage neutralisieren und Kontrast fürs E-Ink anheben."""
    b, h = bild.size
    rand = max(4, min(b, h) // 50)
    bild = bild.crop((rand, rand, b - rand, h - rand))  # Scannerkanten weg
    klein = bild.resize((200, int(200 * bild.height / bild.width)))
    pixel = sorted(klein.getdata(), key=sum)
    hell = pixel[int(len(pixel) * 0.80):int(len(pixel) * 0.97)]
    papier = [sum(p[i] for p in hell) / len(hell) for i in range(3)]
    # Papierton der Vorlage auf den Papierton der Seite abbilden
    kanaele = [k.point(lambda v, f=PAPIER[i] / max(papier[i], 1): min(255, int(v * f)))
               for i, k in enumerate(bild.split())]
    bild = Image.merge("RGB", kanaele)
    bild = ImageOps.autocontrast(bild, cutoff=(0.5, 0), preserve_tone=True)
    bild = ImageEnhance.Color(bild).enhance(1.25)
    bild = ImageEnhance.Contrast(bild).enhance(1.08)
    return bild.filter(ImageFilter.UnsharpMask(radius=1.5, percent=60, threshold=2))


def mittig(draw, text, font, y, x0, x1, farbe=TINTE):
    w = draw.textlength(text, font=font)
    draw.text(((x0 + x1 - w) / 2, y), text, font=font, fill=farbe)


def passe_an(draw, text, art, groesse, max_breite):
    while groesse > 20 and draw.textlength(text, font=schrift(art, groesse)) > max_breite:
        groesse -= 2
    return schrift(art, groesse)


def rahmen(draw, b, h, m):
    draw.rectangle((m, m, b - m, h - m), outline=TINTE, width=5)
    draw.rectangle((m + 12, m + 12, b - m - 12, h - m - 12), outline=TINTE, width=2)


def datum_text(iso):
    d = date.fromisoformat(iso)
    return f"{d.day}. {MONATE[d.month - 1]}"


def seite(platte, art, groesse=1200):
    """Quadratische Seite: Tafel, darunter deutscher und lateinischer Name,
    klein die letzte Sichtung."""
    platte = stelle_frei(platte)
    img = Image.new("RGB", (groesse, groesse), papierton(platte))
    d = ImageDraw.Draw(img)
    m = 28
    x0, x1 = m + 50, groesse - m - 50
    _setze_platte(img, platte, (x0, m + 40, x1, groesse - 300))
    rahmen(d, groesse, groesse, m)

    y = groesse - 285
    f = passe_an(d, art["deutsch"], "normal", 84, x1 - x0)
    mittig(d, art["deutsch"], f, y, x0, x1)
    f = passe_an(d, art["latein"], "kursiv", 58, x1 - x0)
    mittig(d, art["latein"], f, y + 100, x0, x1, SEPIA)
    if art.get("zuletzt"):
        mittig(d, f"Zuletzt gesichtet am {datum_text(art['zuletzt'])}",
               schrift("kursiv", 28), y + 168, x0, x1, SEPIA)
    return img


def stelle_frei(platte):
    """Nur den Bildteil mit den Vögeln behalten: Tafelnummer, Beschriftung und
    leeres Papier fallen weg. Dünne Linien (Schrift) werden über ein Opening
    der Maske ignoriert, flächige Zeichnung bleibt stehen."""
    f = 400 / platte.width
    klein = platte.resize((400, max(1, int(platte.height * f))))
    abstand = ImageChops.difference(klein, Image.new("RGB", klein.size, PAPIER)).convert("L")
    maske = abstand.point(lambda v: 255 if v > 40 else 0)
    maske = maske.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(15))
    box = maske.getbbox()
    if not box:
        return platte
    rand = 8
    x0, y0, x1, y1 = (max(0, box[0] - rand), max(0, box[1] - rand),
                      min(klein.width, box[2] + rand), min(klein.height, box[3] + rand))
    return platte.crop(tuple(int(v / f) for v in (x0, y0, x1, y1)))


def papierton(platte):
    """Median der Randpixel, damit die Seite denselben Papierton hat wie die Tafel."""
    k = platte.resize((100, 100))
    rand = [k.getpixel((x, y)) for x in range(100) for y in range(100)
            if min(x, y) < 3 or max(x, y) > 96]
    return tuple(sorted(p[i] for p in rand)[len(rand) // 2] for i in range(3))


def _setze_platte(img, platte, feld):
    x0, y0, x1, y1 = feld
    p = platte
    faktor = min((x1 - x0) / p.width, (y1 - y0) / p.height)
    p = p.resize((int(p.width * faktor), int(p.height * faktor)), Image.LANCZOS)
    # Ränder weich ins Seitenpapier auslaufen lassen, damit keine Kante sichtbar ist
    weich = 30
    maske = Image.new("L", p.size, 0)
    ImageDraw.Draw(maske).rectangle((weich, weich, p.width - weich, p.height - weich), fill=255)
    maske = maske.filter(ImageFilter.GaussianBlur(weich / 2))
    x = x0 + (x1 - x0 - p.width) // 2
    y = y0 + (y1 - y0 - p.height) // 2
    img.paste(p, (x, y), maske)


# ---------------------------------------------------------------- Ablauf

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--art", help="lateinischer Name erzwingen (zum Testen)")
    args = ap.parse_args()

    jetzt = datetime.now(TZ)
    stand = jetzt.strftime("%d.%m. %H:%M Uhr")
    info_alt = json.loads(INFO.read_text("utf-8")) if INFO.exists() else {}
    verlauf = info_alt.get("verlauf", [])
    tafeln = json.loads(TAFELN.read_text("utf-8")) if TAFELN.exists() else {}

    tage = 7
    arten = gesichtete_arten(tage)
    if len(arten) < 8:
        tage = 30
        arten = gesichtete_arten(tage)
    if not arten:
        sys.exit("Keine Vogelbeobachtungen gefunden.")
    print(f"{len(arten)} Arten in {tage} Tagen gemeldet.")

    if args.art:
        reihenfolge = [a for a in arten if a["latein"] == args.art] or [
            {"id": hole_json(f"{INAT}/taxa", {"q": args.art, "rank": "species", "locale": "de"})
             ["results"][0]["id"], "latein": args.art, "deutsch": args.art, "meldungen": 0}]
    else:
        reihenfolge = waehle(arten, verlauf, random.Random())

    gewaehlt = None
    for art in reihenfolge[:12]:
        if art["latein"] in tafeln:
            tafel = tafeln[art["latein"]]
        else:
            print(f"Suche Tafel für {art['latein']} ({art['deutsch']}) …")
            tafel = suche_tafel(art)
            tafeln[art["latein"]] = tafel
        if tafel:
            gewaehlt = (art, tafel)
            break
        print(f"  keine Tafel für {art['latein']}")
    TAFELN.write_text(json.dumps(tafeln, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                      "utf-8")
    if not gewaehlt:
        sys.exit("Für keine der gemeldeten Arten eine historische Tafel gefunden.")

    art, tafel = gewaehlt
    print(f"Gewählt: {art['deutsch']} ({art['latein']}) – {tafel['datei']}")
    art = letzte_sichtung(art, tage)
    platte = bereite_tafel_auf(hole_bild(tafel["url"]))
    seite(platte, art).save(HIER / "vogel.png", optimize=True)

    info = {
        "deutsch": art["deutsch"],
        "latein": art["latein"],
        "zuletzt": art.get("zuletzt"),
        "tafel": tafel["datei"],
        "tafel_seite": tafel.get("seite"),
        "stand": stand,
        "slot": jetzt.strftime("%Y-%m-%d %H"),  # verhindert Doppelläufe pro Stunde
        "verlauf": ([art["latein"]] + [v for v in verlauf if v != art["latein"]])[:VERLAUF_LAENGE],
    }
    INFO.write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
