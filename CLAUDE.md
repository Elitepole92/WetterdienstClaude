# WetterdienstClaude

Erzeugt 4× täglich (6, 11, 15, 19 Uhr Europe/Berlin) einen frechen norddeutschen
Wetterspruch für Bremen, Östliche Vorstadt. Ergebnis ist `spruch.json` im Repo-Root;
das SenseCraft-HMI-Dashboard (XIAO ePaper 13,3") lädt sie per Data-Komponente über
https://raw.githubusercontent.com/Elitepole92/WetterdienstClaude/main/spruch.json

## Ablauf eines Laufs

1. `python3 scripts/wetter.py > /tmp/wetter.json` – Wetterdaten holen (Bright Sky / DWD).
   Schlägt das fehl: abbrechen, nichts committen, kein Spruch ausdenken.
2. Wetterdaten lesen und **einen** Spruch schreiben (Regeln unten).
3. `python3 scripts/schreibe_spruch.py "<Spruch>" < /tmp/wetter.json`
4. Direkt auf `main` committen und pushen:
   `git add spruch.json && git commit -m "Spruch <TT.MM. HH:MM>" && git push origin main`

## Regeln für den Spruch

- Norddeutscher Schnack auf Hochdeutsch: trocken, knapp, etwas derb. **Kein Platt.**
  Höchstens ein, zwei Färbungen wie „Moin“, „nich“, „büschen“, „Schietwetter“, „Schnack“,
  „klönen“, „Buddel“, „dröge“, „Jung“, „Deern“, „Digger“ – nicht alles auf einmal.
- Darf den Leser ruhig dissen und frech sein (Faulheit, falsche Jacke, Radfahren gegen den
  Wind, Weser, Viertel, Werder, Hamburger …). Keine Beleidigungen von Gruppen, nichts
  Sexistisches/Rassistisches, keine Gewalt.
- Muss sich konkret aufs aktuelle Wetter bzw. die nächsten Stunden beziehen (Temperatur,
  Regen, Wind/Böen, Sonne). Morgens eher auf den Tag, um 19 Uhr auf Abend/Nacht und morgen.
- Max. ca. 160 Zeichen, ein bis zwei Sätze, keine Emojis, keine Anführungszeichen.
- Nicht wiederholen: vorher `git log -p -5 -- spruch.json` anschauen und andere Pointe wählen.

Beispiele für den Ton:
- Elf Grad und Nieselregen. Wer heute in Sneakern losgeht, hat's echt nich anders verdient.
- Böen bis 60 km/h – also ganz normaler Bremer Gegenwind. Stell dich nich so an und tritt in die Pedale.
- Sonne satt im Viertel. Genieß es, Jung, das war's dann für dieses Jahr.
