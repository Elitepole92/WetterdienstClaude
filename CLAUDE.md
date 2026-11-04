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

Ton: **trockenes Norddeutsch, frech mit echtem Seitenhieb** – Untertreibung, Gelassenheit,
null Aufregung, aber nicht brav. Die Pointe wird hingestellt, nicht erklärt. Nicht cringe,
nicht gewollt lustig. Hochdeutsch, **kein Platt**.

**So entsteht der Spruch:** erst das Wetter lesen und eine konkrete Beobachtung wählen
(grau und trocken, ordentlich Böen, Nebel, morgen Regen …), dann die Pointe *daraus*
ableiten. Nie zuerst einen Witz bauen und das Wetter danach dranhängen.

- **Hauptstil (meistens): trocken mit Seitenhieb.** Das Wetter lakonisch
  kommentieren und dann ein Stich gegen Hamburger, Süddeutsche, Werder, Touristen,
  Schönwetter-Optimisten, Leute mit falscher Jacke … – Beispiele:
  - Ordentlich Böen heute. Für Hamburger ist das Sturm, für uns ist das Lüften.
  - Grau und frisch. Wer jetzt noch auf goldenen Oktober wartet, wartet auch auf Werders Meisterschaft.
  - Heute Wind, morgen Regen. Der Herbst macht's wenigstens gründlich.
- **Ab und zu (etwa jeder vierte Spruch): gelassene Lebensweisheit.** – Beispiele:
  - Es gibt kein schlechtes Wetter. Nur Leute aus dem Süden.
  - Der Wind weht. Das tut er hier seit Jahrhunderten, regt sich keiner drüber auf.
  - Wer bei dem Wetter rausgeht, kommt auch wieder rein. Meistens.
- **So klingt es richtig** (vom Nutzer als gut bewertet, ebenfalls nur Ton, nicht übernehmen):
  - Kein Regen, kein Wind, keine Sonne. Der Bremer sagt: geht. Der Optimist sagt: gleich reißt's auf. Der Optimist wohnt nicht lange hier.
  - Grau, trocken, kaum Wind. Für Bremen ist das ein schöner Sonntag. Wer jetzt nach Sonne fragt, kommt aus Süddeutschland.
  - Grau und windstill, es passiert einfach nichts. Wie Werder in der zweiten Halbzeit.
  - Heute grau und trocken, morgen grau mit Regen. Für den einen derselbe Mist, für den Bremer aufregende Abwechslung.
  - Der Niesel hat aufgehört, grau bleibt's trotzdem. Der Bremer nennt das Aufklaren, der Rest der Republik Novemberdepression.
  - Morgen soll der Himmel stellenweise aufreißen. Das ist hier ungefähr so selten wie ein Werder-Auswärtssieg.
  - Niesel bis in den Mittag. Wer dafür extra den Schirm aufspannt, outet sich als Zugezogener.
  - Morgen startet die Woche mit Niesel. In München wär das ein Grund zum Krankmelden, hier ist das ein ganz normaler Montag.
  - Grau und frisch, aber kein Tropfen fällt. Der Tourist bucht trotzdem schon die Heimfahrt.
  - Morgen kälter und ordentlich Wind, aber trocken. Der Hamburger kauft dafür eine neue Funktionsjacke, der Bremer holt Omas Pulli raus.
  - Ordentlich Gegenwind auf dem Rad zur Arbeit. Die Bayern haben Berge, wir haben das hier, und zwar in beide Richtungen.
  - Sonne satt, aber ordentlich Wind. Vom Fenster aus sieht's nach Frühling aus. Das Fenster lügt.
  - Sonne und ordentlich Böen. Wer die Lederjacke angezogen hat, weil's so schön aussah, steht jetzt bibbernd an der Sielwall-Kreuzung.
  - Heute Sonne, heute Nacht fast Frost. Wer die Balkonpflanzen noch draußen hat, verabschiedet sich am besten jetzt.
  - Erste richtig kalte Nacht. Wer im Bremer Altbau wohnt, merkt jetzt, dass das Haus ganz von allein lüftet.
- **Die Beispiele oben zeigen nur den Ton. Nie einen Beispielsatz oder dessen Pointe
  übernehmen, auch nicht abgewandelt.** Jeder Spruch braucht eine eigene, neue Idee.
- **Pointe muss ohne Vorwissen zünden.** Das Ziel des Seitenhiebs klar benennen
  („kommt aus Süddeutschland“ statt „ist zu Besuch“). Keine Anspielungen, die man erst
  erklären müsste.
- **Pointe braucht einen echten Kontrast.** Kein Wortspiel mit zwei fast gleichbedeutenden
  Wörtern (z. B. „kein Wetterwechsel, sondern Abwechslung“) – das dreht sich im Kreis.
- **Keine Sprünge ohne Anlass.** Andere Tage (morgen, Montag …) nur erwähnen, wenn der
  Spruch das von Anfang an aufbaut, nicht als Überraschung am Ende.
- **Eine Beobachtung ist noch keine Pointe.** „Leute machen X“ reicht nicht; es braucht eine
  Wendung oder Übertreibung, über die man stolpert (schwach: „Am Osterdeich stehen Leute mit
  Sonnenbrille, als hätten sie den Himmel bestellt“).
- **Der Seitenhieb muss logisch stimmen.** Das Ziel muss sich beim Thema wirklich von
  Bremern unterscheiden: Süddeutsche/Münchner haben mehr Sonne, Touristen und Zugezogene
  kennen das Wetter nicht. Hamburger haben dasselbe Wetter – ein Kontrast „Hamburger finden
  Grau trist, Bremer nicht“ ergibt keinen Sinn. Hamburger nur da, wo sie sich wirklich
  unterscheiden (Großstadtgehabe, Elbe, Pfeffersäcke …).
- **Locker statt steif.** Tresensprache, keine Schriftsätze: „Umsonst gibt's hier nichts“
  ist gut, ein angehängtes „auch nicht beim Wetter“ wirkt steif.
- **Keine gewollten Redewendungen.** Lieber schlicht und trocken („hätte sich das sparen
  können“) als ein erzwungenes Wortspiel („hat sein Geld in den Wind geschossen“).
- **Lokalkolorit statt Allerweltsort.** Wo es passt, einen echten Ort aus dem Viertel oder
  Bremen nennen (Sielwall-Kreuzung, Osterdeich, Steintor, Weserstadion …) statt „an der Ampel“
  oder „draußen“. Das macht das Bild konkret.
- **Das Erwartbare ist keine Pointe.** Dass man bei Wind die Mütze festhält, weiß jeder – das
  überrascht niemanden. Die Wendung muss etwas sagen, womit man nicht gerechnet hat.
- **Keine schiefen Bilder.** Keine Vermenschlichungen oder Sprüche, die nur nach Weisheit
  klingen, aber nichts bedeuten (schwach: „ein Wind, der keine Fragen stellt“; „Der
  Zugezogene sagt: schönes Wetter. Der Bremer sagt: Mütze.“). Jeder Satz muss wörtlich Sinn
  ergeben.
- **Kneipentest vor dem Schreiben:** Würde man den Satz am Tresen so sagen, und versteht
  ihn jeder sofort? Wenn nicht, neu formulieren.
- **Keine Messwerte**: keine Grad, km/h, Liter, Prozente, Uhrzeiten. Die Zahlen zeigt das
  Display separat. Stattdessen beschreiben: „frisch“, „ordentlich Böen“, „richtig nass“.
- Muss trotzdem erkennbar zum aktuellen Wetter bzw. den nächsten Stunden passen. Morgens
  eher auf den Tag, um 19 Uhr auf Abend/Nacht und morgen.
- Mundart-Färbung höchstens sparsam („nich“, „büschen“, „Schietwetter“) und nur, wenn sie
  zum Witz beiträgt – nicht reinstreuen, damit es norddeutsch wirkt. Kein „Digger“.
- Ein bis drei kurze Sätze, **höchstens ca. 22 Wörter / 135 Zeichen** (mehr passt nicht ins
  Textfeld des Displays). Keine Emojis, keine Anführungszeichen.
- Frech ist erlaubt, aber keine Beleidigungen von Gruppen, nichts Sexistisches/
  Rassistisches, keine Gewalt.
- Nicht wiederholen: vorher `git log -p -8 -- spruch.json` anschauen und andere Pointe und
  anderes Ziel für den Seitenhieb wählen.
