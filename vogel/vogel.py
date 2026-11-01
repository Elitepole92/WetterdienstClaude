#!/usr/bin/env python3
"""Vogel-Lexikon für das SenseCraft-HMI-Dashboard.

1. Fragt bei iNaturalist ab, welche Vogelarten in den letzten Tagen rund um
   Bremen gemeldet wurden, und wählt eine davon (Abwechslung über den Verlauf).
2. Sucht auf Wikimedia Commons eine handkolorierte Tafel aus einem Vogelwerk
   des 19. Jahrhunderts (Naumann, Gould, Keulemans, Susemihl …; gemeinfrei).
   Mehrere Kandidaten werden geladen und bewertet: farbig, ruhige große Flächen,
   gute Ausnutzung der kleinen Bildfläche.
3. Setzt daraus ein Bild mit deutschem und lateinischem Namen und dem Datum der
   letzten Sichtung; schreibt vogel/vogel.png (480×680) und vogel/vogel.json.

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
TAFELN = HIER / "tafeln.json"      # Cache: Art -> gewählte Tafel samt Bewertung (oder null)
INFO = HIER / "vogel.json"

LAT, LNG, RADIUS_KM = 53.08, 8.81, 20
TZ = ZoneInfo("Europe/Berlin")
UA = "VogelLexikon/1.0 (https://github.com/Elitepole92/WetterdienstClaude)"
INAT = "https://api.inaturalist.org/v1"
COMMONS = "https://commons.wikimedia.org/w/api.php"
VERLAUF_LAENGE = 20

PAPIER = (244, 234, 211)  # #F4EAD3, fester Sepia-Hintergrund fürs HMI
BREITE, HOEHE = 480, 680   # Bildfläche im HMI (Display 480×800 hochkant)
FELD = (14, 14, BREITE - 14, 620)  # Bereich für die Tafel (bei zweizeiliger Unterschrift kürzer)
CACHE_VERSION = 4
TINTE = (28, 22, 16)
SEPIA = (92, 64, 40)

# Illustratoren bzw. Werke, deren Tafeln wir suchen (Suchbegriff, Bonus). Maler mit
# großen, flächigen Aquarellen/Lithografien vor den feinen Kupferstichen.
WERKE = [
    ("Gould", 5), ("Keulemans", 5), ("Thorburn", 5), ("Lilford", 4),
    ("von Wright", 4), ("Frohawk", 3), ("Susemihl", 3), ("Dresser", 3),
    ("Naumann", 1), ("Kleinschmidt", 1), ("Friderich", 1), ("Meyer", 1),
]
SUCHWERKE = ["Gould", "Keulemans", "Thorburn", "Lilford", "von Wright", "Naumann", "Frohawk"]
MIN_FARBE = 0.15      # mittlere Sättigung der Zeichnung; darunter gilt sie als nicht farbig
MIN_FUELLUNG = 0.35   # darunter bliebe zu viel Leerraum (z. B. Panoramen)
MAX_KANDIDATEN = 6    # so viele Tafeln pro Art herunterladen und bewerten
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
        m = re.search(r"\b(1[6-9]\d\d|20\d\d)\b", txt)
        if m:
            return int(m.group(1))
    return None


def suche_tafel(art):
    latein, deutsch = art["latein"], art["deutsch"]
    epitheton = (latein.split() + ["", ""])[1]
    treffer = {}
    anfragen = [f'"{latein}" {w}' for w in SUCHWERKE]
    anfragen += [f'"{latein}" lithograph', f'{deutsch} Naumann Tafel', f'{epitheton} Naumann']
    for q in anfragen:
        try:
            d = hole_json(COMMONS, {
                "action": "query", "format": "json", "generator": "search",
                "gsrnamespace": 6, "gsrsearch": q, "gsrlimit": 25,
                "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
                "iiurlwidth": 1200,
            })
        except Exception as e:  # einzelne Suche darf scheitern
            print(f"  Commons-Suche '{q}' fehlgeschlagen: {e}", file=sys.stderr)
            continue
        for seite in d.get("query", {}).get("pages", {}).values():
            treffer.setdefault(seite["title"], seite)

    kandidaten = []
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
        # Voller Name, oder (bei alten Gattungsnamen) das Epitheton als ganzes Wort im
        # Dateinamen plus der deutsche Name – sonst rutschen Unterarten/Verwandte durch.
        name_ok = latein.lower() in text or (
            epitheton and re.search(rf"\b{re.escape(epitheton.lower())}\b", titel.lower())
            and deutsch.lower() in text)
        if not name_ok:
            continue
        # Andere Unterart (z. B. "Turdus merula bourdilloni") – nur die Nominatform passt
        unterarten = re.findall(rf"{re.escape(latein.lower())}\s+([a-z]{{5,}})", text)
        if any(u != epitheton.lower() and u not in ("linnaeus", "linnaei", "linne")
               and u.endswith(("i", "ae", "a", "us", "is", "um", "ensis"))
               for u in unterarten):
            continue
        punkte = 3 if latein.lower() in titel.lower() else 1
        werk = next(((w, b) for w, b in WERKE if w.lower() in text), None)
        j = jahr(meta)
        if werk:
            punkte += werk[1]
        if j and j <= 1935:
            punkte += 3
        elif not werk:
            continue  # vermutlich Foto oder moderne Zeichnung
        if j and j > 1940:
            continue
        b, h = ii.get("width", 0), ii.get("height", 0)
        if min(b, h) < 700:
            continue
        kuenstler = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ",
                                                meta.get("Artist", {}).get("value", ""))).strip()
        kandidaten.append({
            "datei": titel,
            "url": ii.get("thumburl") or ii["url"],
            "seite": ii.get("descriptionurl"),
            "kuenstler": kuenstler[:120],
            "werk": werk[0] if werk else None,
            "jahr": j,
            "punkte": punkte,
        })
    kandidaten.sort(key=lambda k: k["punkte"], reverse=True)
    return kandidaten[:MAX_KANDIDATEN]


def bewerte(platte, kandidat):
    """Wie gut taugt die (aufbereitete) Tafel fürs kleine Display? Farbig, große ruhige
    Flächen und gute Ausnutzung des Feldes sind gut; viel Feindetail ist schlecht."""
    p = auf_papier(stelle_frei(platte))
    fb, fh = FELD[2] - FELD[0], FELD[3] - FELD[1]
    faktor = min(fb / p.width, fh / p.height)
    p = p.resize((max(1, int(p.width * faktor)), max(1, int(p.height * faktor))), Image.LANCZOS)
    abstand = ImageChops.difference(p, Image.new("RGB", p.size, PAPIER)).convert("L")
    maske = [v > 40 for v in abstand.getdata()]
    n = max(1, sum(maske))
    saett = p.convert("HSV").getchannel("S").getdata()
    kanten = p.convert("L").filter(ImageFilter.FIND_EDGES).getdata()
    farbe = sum(s for s, m in zip(saett, maske) if m) / n / 255
    detail = sum(1 for k, m in zip(kanten, maske) if m and k > 48) / n
    fuellung = p.width * p.height / (fb * fh)
    inseln = zaehle_inseln(p)
    # Füllung stark gewichtet: hohe Tafeln nutzen das hohe Bildfeld, breite lassen Leerraum
    gesamt = (kandidat["punkte"] * 0.5 + farbe * 20 + fuellung * 12 - detail * 15
              - (inseln - 1) * 3)
    return {"farbe": round(farbe, 3), "detail": round(detail, 3),
            "fuellung": round(fuellung, 3), "inseln": inseln, "gesamt": round(gesamt, 2)}


def zaehle_inseln(p, raster=60):
    """Getrennte Bildinseln zählen – Sammeltafeln mit mehreren einzeln stehenden
    Vögeln haben viele, eine Tafel mit einem großen Motiv nur eine."""
    k = p.resize((raster, max(1, int(raster * p.height / p.width))))
    abstand = ImageChops.difference(k, Image.new("RGB", k.size, PAPIER)).convert("L")
    w, h = k.size
    voll = {(x, y) for y in range(h) for x in range(w) if abstand.getpixel((x, y)) > 30}
    groessen = []
    while voll:
        stapel, n = [voll.pop()], 0
        while stapel:
            x, y = stapel.pop()
            n += 1
            for nb in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if nb in voll:
                    voll.remove(nb)
                    stapel.append(nb)
        groessen.append(n)
    return max(1, sum(1 for g in groessen if g >= 0.03 * w * h))


def beste_tafel(art):
    """Kandidaten suchen, herunterladen, bewerten; die beste farbige Tafel zurückgeben."""
    beste, verglichen = None, []
    for k in suche_tafel(art):
        try:
            bild = bereite_tafel_auf(hole_bild(k["url"]))
        except Exception as e:
            print(f"  {k['datei']}: Download fehlgeschlagen ({e})", file=sys.stderr)
            continue
        k["bewertung"] = bewerte(bild, k)
        print(f"  {k['bewertung']}  {k['datei']}")
        verglichen.append({"datei": k["datei"], **k["bewertung"]})
        if k["bewertung"]["farbe"] < MIN_FARBE or k["bewertung"]["fuellung"] < MIN_FUELLUNG:
            continue
        if not beste or k["bewertung"]["gesamt"] > beste[0]["bewertung"]["gesamt"]:
            beste = (k, bild)
    if beste:
        beste[0]["verglichen"] = verglichen
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
    while groesse > 16 and draw.textlength(text, font=schrift(art, groesse)) > max_breite:
        groesse -= 2
    return schrift(art, groesse)


def rahmen(draw, b, h, m):
    draw.rectangle((m, m, b - 1 - m, h - 1 - m), outline=TINTE, width=3)
    draw.rectangle((m + 6, m + 6, b - 1 - m - 6, h - 1 - m - 6), outline=TINTE, width=1)


def datum_text(iso):
    d = date.fromisoformat(iso)
    return f"{d.day}. {MONATE[d.month - 1]}"


def fernglas(hoehe, farbe=SEPIA):
    """Kleines Fernglas-Symbol (RGBA), vierfach gezeichnet und herunterskaliert."""
    k = 4
    h = hoehe * k
    w = int(h * 1.45)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rohr = int(w * 0.40)
    r = rohr // 2
    for x in (0, w - rohr):
        # Okular oben, Tubus, runde Objektivlinse unten
        d.rounded_rectangle((x + rohr * 0.18, 0, x + rohr * 0.82, h * 0.30), radius=k * 2, fill=farbe)
        d.rounded_rectangle((x, h * 0.22, x + rohr, h - r), radius=k * 3, fill=farbe)
        d.ellipse((x, h - 2 * r, x + rohr, h), fill=farbe)
        d.ellipse((x + r * 0.35, h - 2 * r + r * 0.35, x + rohr - r * 0.35, h - r * 0.35),
                  fill=(0, 0, 0, 0))
    d.rectangle((rohr - k, h * 0.30, w - rohr + k, h * 0.52), fill=farbe)  # Mittelsteg
    return img.resize((w // k, hoehe), Image.LANCZOS)


def seite(platte, art):
    """Seite 480×680: Tafel fast vollflächig, darunter eine Bildunterschrift wie im
    Lexikon – Name, lateinischer Name kursiv, rechts Fernglas und Datum der letzten
    Sichtung. Passt das nicht in eine Zeile, stehen die Namen untereinander."""
    img = Image.new("RGB", (BREITE, HOEHE), PAPIER)
    d = ImageDraw.Draw(img)
    x0, x1 = 22, BREITE - 22
    name, latein = art["deutsch"], art["latein"]
    datum = datum_text(art["zuletzt"]) if art.get("zuletzt") else ""
    f_name, f_lat, f_dat = schrift("normal", 32), schrift("kursiv", 23), schrift("normal", 22)
    b_name, b_lat = d.textlength(name, font=f_name), d.textlength(latein, font=f_lat)
    symbol = fernglas(16) if datum else None
    b_dat = d.textlength(datum, font=f_dat) + (symbol.width + 7 if symbol else 0)

    grund = 658
    if b_name + 12 + b_lat + 18 + b_dat <= x1 - x0:
        linie, unten = 626, 620
        d.text((x0, grund), name, font=f_name, fill=TINTE, anchor="ls")
        d.text((x0 + b_name + 12, grund), latein, font=f_lat, fill=SEPIA, anchor="ls")
    else:
        linie, unten = 594, 588
        f_name = passe_an(d, name, "normal", 32, x1 - x0)
        d.text((x0, grund - 32), name, font=f_name, fill=TINTE, anchor="ls")
        f_lat = passe_an(d, latein, "kursiv", 23, x1 - x0 - b_dat - 18)
        d.text((x0, grund), latein, font=f_lat, fill=SEPIA, anchor="ls")
    if datum:
        d.text((x1, grund), datum, font=f_dat, fill=SEPIA, anchor="rs")
        x_sym = int(x1 - b_dat)
        img.paste(symbol, (x_sym, grund - symbol.height + 3), symbol)
    d.line((x0, linie, x1, linie), fill=SEPIA, width=1)

    _setze_platte(img, auf_papier(stelle_frei(platte)),
                  (FELD[0], FELD[1], FELD[2], unten))
    rahmen(d, BREITE, HOEHE, 4)
    return img


def stelle_frei(platte):
    """Nur den Bildteil mit den Vögeln behalten: Tafelnummer, Beschriftung und
    leeres Papier fallen weg. Dünne Linien werden über ein Opening der Maske
    ignoriert; von dem, was bleibt, zählt nur der größte zusammenhängende Block
    (abgesetzte Bildunterschriften fallen so heraus)."""
    f = 400 / platte.width
    klein = platte.resize((400, max(1, int(platte.height * f))))
    abstand = ImageChops.difference(klein, Image.new("RGB", klein.size, PAPIER)).convert("L")
    maske = abstand.point(lambda v: 255 if v > 40 else 0)
    maske = maske.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(9))
    w, h = maske.size
    px = maske.load()
    zeilen = [sum(1 for x in range(w) if px[x, y]) for y in range(h)]
    y0, y1 = _groesster_block(zeilen, luecke=8)
    spalten = [sum(1 for y in range(y0, y1) if px[x, y]) for x in range(w)]
    x0, x1 = _groesster_block(spalten, luecke=8)
    if x1 <= x0 or y1 <= y0:
        return platte
    rand = 6
    box = (max(0, x0 - rand), max(0, y0 - rand), min(w, x1 + rand), min(h, y1 + rand))
    return ohne_beschriftung(platte.crop(tuple(int(v / f) for v in box)))


def ohne_beschriftung(platte, leer=0.02, luecke=3, anteil=0.15):
    """Textzeilen unter und über der Zeichnung abschneiden (Artname, Tafelnummer,
    Lithograf). Die Zeilen werden in Blöcke zerlegt, die durch leere Zeilen getrennt
    sind; behalten wird der Block mit dem meisten Inhalt plus angrenzende Blöcke mit
    nennenswertem Inhalt. Was am Körper hängt (Kopf, Schwanz), ist kein eigener Block
    und bleibt daher immer stehen."""
    f = 400 / platte.width
    klein = platte.resize((400, max(1, int(platte.height * f))))
    abstand = ImageChops.difference(klein, Image.new("RGB", klein.size, PAPIER)).convert("L")
    w, h = klein.size
    px = abstand.load()
    zeilen = [sum(1 for x in range(w) if px[x, y] > 40) / w for y in range(h)]

    bloecke, start, leerlauf = [], None, 0
    for i, v in enumerate(zeilen + [0] * luecke):
        if v > leer:
            if start is None:
                start = i
            leerlauf, ende = 0, i + 1
        elif start is not None:
            leerlauf += 1
            if leerlauf >= luecke:
                bloecke.append([start, ende, sum(zeilen[start:ende])])
                start = None
    if len(bloecke) < 2:
        return platte
    haupt = max(range(len(bloecke)), key=lambda i: bloecke[i][2])
    von = bis = haupt
    while von > 0 and bloecke[von - 1][2] >= anteil * bloecke[haupt][2]:
        von -= 1
    while bis < len(bloecke) - 1 and bloecke[bis + 1][2] >= anteil * bloecke[haupt][2]:
        bis += 1
    oben, unten = bloecke[von][0], bloecke[bis][1]
    rand = 4
    return platte.crop((0, int(max(0, oben - rand) / f), platte.width,
                        int(min(h, unten + rand) / f)))


def _groesster_block(profil, luecke):
    """Bereich [a, b) mit der meisten Masse, Lücken unter `luecke` werden überbrückt."""
    bloecke, start, leer = [], None, 0
    for i, v in enumerate(profil + [0] * luecke):
        if v:
            if start is None:
                start = i
            leer, ende = 0, i + 1
        elif start is not None:
            leer += 1
            if leer >= luecke:
                bloecke.append((start, ende))
                start = None
    if not bloecke:
        return 0, 0
    return max(bloecke, key=lambda bl: sum(profil[bl[0]:bl[1]]))


def auf_papier(platte):
    """Papierton der freigestellten Tafel exakt auf PAPIER umrechnen, damit sie
    ohne Kante in den festen Seitenhintergrund übergeht."""
    ton = papierton(platte)
    kanaele = [k.point(lambda v, f=PAPIER[i] / max(ton[i], 1): min(255, int(v * f)))
               for i, k in enumerate(platte.split())]
    return Image.merge("RGB", kanaele)


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
    x = x0 + (x1 - x0 - p.width) // 2
    y = y0 + (y1 - y0 - p.height) // 2
    # Bleibt seitlich oder oben/unten Platz, läuft der Bildhintergrund bis zum Rahmen
    # (unten bis zur Linie über der Unterschrift) aus
    links, rechts = x - 5, img.width - 5 - (x + p.width)
    oben, unten = y - 5, y1 + 2 - (y + p.height)
    seitlich, senkrecht = links > 8, oben > 8
    if seitlich:
        breit = Image.new("RGB", (p.width + links + rechts, p.height), PAPIER)
        breit.paste(_verlauf(p, links, "links"), (0, 0))
        breit.paste(p, (links, 0), _feder(p, seitlich=True))
        breit.paste(_verlauf(p, rechts, "rechts"), (links + p.width, 0))
        p, x = breit, x - links
    if senkrecht:
        hoch = Image.new("RGB", (p.width, p.height + oben + unten), PAPIER)
        hoch.paste(_verlauf(p, oben, "oben"), (0, 0))
        hoch.paste(p, (0, oben), _feder(p, seitlich=False))
        hoch.paste(_verlauf(p, unten, "unten"), (0, oben + p.height))
        p, y = hoch, y - oben
    # Übrige Ränder weich ins Seitenpapier auslaufen lassen, damit keine Kante sichtbar ist
    weich = 12
    rx = 0 if seitlich else weich
    ry = 0 if senkrecht else weich
    maske = Image.new("L", p.size, 0)
    ImageDraw.Draw(maske).rectangle((rx, ry, p.width - rx, p.height - ry), fill=255)
    maske = maske.filter(ImageFilter.GaussianBlur(weich / 2))
    img.paste(p, (x, y), maske)


def _feder(p, seitlich, weich=28):
    """Maske, die die Tafel an zwei gegenüberliegenden Kanten weich ausblendet – aber nur
    dort, wo am Rand heller Hintergrund ist. Reicht das Motiv selbst (Kopf, Schwanz) bis
    an die Kante, bleibt es voll sichtbar."""
    w, h = p.size
    hell = sum(PAPIER) * 0.8
    maske = Image.new("L", p.size, 255)
    px = maske.load()
    q = p.load()
    laenge, tiefe = (h, w) if seitlich else (w, h)
    for i in range(laenge):
        for kante in (0, tiefe - 1):
            rand = q[kante, i] if seitlich else q[i, kante]
            if sum(rand) < hell:
                continue
            for t in range(min(weich, tiefe // 2)):
                a = int(255 * t / weich)
                pos = kante + t if kante == 0 else kante - t
                if seitlich:
                    px[pos, i] = a
                else:
                    px[i, pos] = a
    return maske.filter(ImageFilter.GaussianBlur(2))


def _verlauf(p, breite, seite):
    """Streifen, der die Randfarbe der Tafel (geglättet) weich in PAPIER übergehen lässt –
    an der Tafel volle Randfarbe, am Rahmen reines Papier."""
    quer = seite in ("links", "rechts")
    n = p.height if quer else p.width
    rand = {"links": (0, 0, 6, p.height), "rechts": (p.width - 6, 0, p.width, p.height),
            "oben": (0, 0, p.width, 6), "unten": (0, p.height - 6, p.width, p.height)}[seite]
    streifen = p.crop(rand).resize((1, n) if quer else (n, 1))
    # Nur Hintergrundtöne übernehmen: dunkle Motivteile (Vogel, Schilf) am Rand würden
    # sonst als Schlieren in den Verlauf gezogen. Sie werden durch den gewichteten
    # Mittelwert der hellen Nachbarn ersetzt, damit der Hintergrundton durchgeht.
    hell = sum(PAPIER) * 0.8
    farben = list(streifen.getdata())
    gewicht = [1.0 if sum(c) >= hell else 0.0 for c in farben]
    radius = max(20, n // 12)
    glatt = []
    for i in range(n):
        lo, hi = max(0, i - radius), min(n, i + radius + 1)
        g = sum(gewicht[lo:hi])
        if g:
            glatt.append(tuple(int(sum(farben[j][k] * gewicht[j] for j in range(lo, hi)) / g)
                               for k in range(3)))
        else:
            glatt.append(PAPIER)
    streifen.putdata(glatt)
    streifen = streifen.filter(ImageFilter.GaussianBlur(10))
    groesse = (breite, n) if quer else (n, breite)
    farbe = streifen.resize(groesse)
    # linear_gradient: oben 0, unten 255 – so drehen, dass 255 an der Tafel liegt
    drehung = {"links": 90, "rechts": -90, "oben": 0, "unten": 180}[seite]
    rampe = Image.linear_gradient("L").rotate(drehung).resize(groesse)
    rampe = rampe.point(lambda v: int(255 * (v / 255) ** 0.3))  # Randfarbe trägt weit, Sepia erst am Rahmen
    return Image.composite(farbe, Image.new("RGB", groesse, PAPIER), rampe)


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
    if tafeln.get("_version") != CACHE_VERSION:
        tafeln = {"_version": CACHE_VERSION}  # alte Auswahl ohne Bewertung verwerfen

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
        if art["latein"] in tafeln and not args.art:
            tafel = tafeln[art["latein"]]
            if tafel:
                gewaehlt = (art, tafel, bereite_tafel_auf(hole_bild(tafel["url"])))
                break
        else:
            print(f"Suche Tafel für {art['latein']} ({art['deutsch']}) …")
            treffer = beste_tafel(art)
            tafeln[art["latein"]] = treffer[0] if treffer else None
            if treffer:
                gewaehlt = (art, *treffer)
                break
        print(f"  keine farbige Tafel für {art['latein']}")
    TAFELN.write_text(json.dumps(tafeln, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                      "utf-8")
    if not gewaehlt:
        sys.exit("Für keine der gemeldeten Arten eine historische Tafel gefunden.")

    art, tafel, platte = gewaehlt
    print(f"Gewählt: {art['deutsch']} ({art['latein']}) – {tafel['datei']}")
    art = letzte_sichtung(art, tage)
    seite(platte, art).save(HIER / "vogel.png", optimize=True)

    info = {
        "deutsch": art["deutsch"],
        "latein": art["latein"],
        "zuletzt": art.get("zuletzt"),
        "tafel": tafel["datei"],
        "tafel_seite": tafel.get("seite"),
        "bewertung": tafel.get("bewertung"),
        "stand": stand,
        "slot": jetzt.strftime("%Y-%m-%d %H"),  # verhindert Doppelläufe pro Stunde
        "verlauf": ([art["latein"]] + [v for v in verlauf if v != art["latein"]])[:VERLAUF_LAENGE],
    }
    INFO.write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
