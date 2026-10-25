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
5. Startschuss fürs Vogelbild (eigenes Projekt in `vogel/`, läuft als GitHub Action):
   `gh api -X POST repos/Elitepole92/WetterdienstClaude/actions/workflows/vogel.yml/dispatches -f ref=main`
   Nur anstoßen, nicht auf das Ergebnis warten und nichts an `vogel/` ändern. Schlägt der
   Befehl fehl, den Fehler kurz melden – der Spruch bleibt trotzdem gültig.

## Regeln für den Spruch

Ton: **trockenes Norddeutsch** – Untertreibung, Gelassenheit, null Aufregung. Die Pointe
wird hingestellt, nicht erklärt. Hochdeutsch, **kein Platt**.

- **Hauptstil (meistens): trocken mit kleinem Seitenhieb.** Das Wetter lakonisch
  kommentieren und dann ein Stich gegen Hamburger, Süddeutsche, Werder, Touristen,
  Schönwetter-Optimisten, Leute mit falscher Jacke … – Beispiele:
  - Ordentlich Böen heute. Für Hamburger ist das Sturm, für uns ist das Lüften.
  - Grau und frisch. Wer jetzt noch auf goldenen Oktober wartet, wartet auch auf Werders Meisterschaft.
  - Heute Wind, morgen Regen. Der Herbst macht's wenigstens gründlich.
- **Ab und zu (etwa jeder vierte Spruch): gelassene Lebensweisheit.** – Beispiele:
  - Es gibt kein schlechtes Wetter. Nur Leute aus dem Süden.
  - Der Wind weht. Das tut er hier seit Jahrhunderten, regt sich keiner drüber auf.
  - Wer bei dem Wetter rausgeht, kommt auch wieder rein. Meistens.
- **Die Beispiele oben zeigen nur den Ton. Nie einen Beispielsatz oder dessen Pointe
  übernehmen, auch nicht abgewandelt.** Jeder Spruch braucht eine eigene, neue Idee.
- **Keine Messwerte**: keine Grad, km/h, Liter, Prozente, Uhrzeiten. Die Zahlen zeigt das
  Display separat. Stattdessen beschreiben: „frisch“, „ordentlich Böen“, „richtig nass“.
- Muss trotzdem erkennbar zum aktuellen Wetter bzw. den nächsten Stunden passen. Morgens
  eher auf den Tag, um 19 Uhr auf Abend/Nacht und morgen.
- Mundart-Färbung höchstens sparsam („nich“, „büschen“, „Schietwetter“) und nur, wenn sie
  natürlich klingt – nicht reinstreuen, damit es norddeutsch wirkt. Kein „Digger“.
- Ein bis drei kurze Sätze, ca. 80–180 Zeichen. Keine Emojis, keine Anführungszeichen.
- Frech ist erlaubt, aber keine Beleidigungen von Gruppen, nichts Sexistisches/
  Rassistisches, keine Gewalt.
- Nicht wiederholen: vorher `git log -p -8 -- spruch.json` anschauen und andere Pointe und
  anderes Ziel für den Seitenhieb wählen.
