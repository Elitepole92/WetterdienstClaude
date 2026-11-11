# WetterdienstClaude

Erzeugt 2× täglich (3:00 und 15:00 Uhr Europe/Berlin) einen trocken-frechen norddeutschen
Wetterspruch für Bremen, Östliche Vorstadt. Ergebnis ist `spruch.json`; die GitHub Action in
`vogel/` setzt ihn ins Vogelbild fürs E-Ink-Display (480×800).

## Ablauf eines Laufs

1. `python3 scripts/wetter.py > /tmp/wetter.json` – Wetterdaten (Bright Sky / DWD).
   Schlägt das fehl: abbrechen, nichts committen.
2. `git log --since='14 days ago' -p -- spruch.json` ansehen, dann **einen** Spruch schreiben.
3. `python3 scripts/schreibe_spruch.py "<Spruch>" < /tmp/wetter.json`
4. `git add spruch.json && git commit -m "Spruch <TT.MM. HH:MM>" && git push origin main`
5. Vogelbild anstoßen (um 3 Uhr neuer Vogel des Tages, um 15 Uhr nur neuer Spruch im Bild):
   `gh api -X POST repos/Elitepole92/WetterdienstClaude/actions/workflows/vogel.yml/dispatches -f ref=main`
   Nicht auf das Ergebnis warten, nichts an `vogel/` ändern. Fehler nur kurz melden.

## Der Spruch

**Ton:** trockenes Norddeutsch, frech mit echtem Seitenhieb. Untertreibung, Gelassenheit,
null Aufregung, aber nicht brav. Die Pointe wird hingestellt, nicht erklärt. Hochdeutsch,
kein Platt; Mundart („nich“, „büschen“) nur, wenn sie zum Witz beiträgt. Kein „Digger“.

**Form:** ein bis drei kurze Sätze, **höchstens ca. 22 Wörter / 135 Zeichen** (mehr passt
nicht aufs Display). Keine Messwerte (Grad, km/h, Prozent, Uhrzeiten – die zeigt das Display
separat), keine Emojis, keine Anführungszeichen. Der 3-Uhr-Spruch gilt für den Vormittag, der
15-Uhr-Spruch für Nachmittag, Abend und morgen.

**So entsteht er:** erst das Wetter lesen und eine konkrete Beobachtung wählen (grau und
trocken, Böen, Nebel, morgen Regen …), dann die Pointe *daraus* ableiten. Meistens Wetter plus
Seitenhieb; etwa jeder vierte Spruch darf eine gelassene Lebensweisheit sein.

**Prüfen vor dem Abschicken:**
1. **Hängt der Witz am Wetter?** Würde er bei jedem Wetter genauso funktionieren, ist das Wetter
   nur Kulisse – durchgefallen. Der zweite Satz muss direkt aus dem ersten folgen.
2. **Gibt es eine echte Wendung?** Eine Beobachtung („Leute machen X“), ein bloßes Gegenüber
   („der eine X, der andere Y“) oder etwas Erwartbares (Mütze festhalten bei Wind) ist keine Pointe.
3. **Stimmt der Seitenhieb logisch?** Das Ziel muss sich beim Thema wirklich von Bremern
   unterscheiden. Münchner haben mehr Sonne, Touristen kennen das Wetter nicht – Hamburger haben
   dasselbe Wetter, also nur über Großstadtgehabe, Elbe, Pfeffersäcke. Ziel klar benennen.
4. **Ergibt jeder Satz wörtlich Sinn?** Keine schiefen Bilder, Vermenschlichungen, erzwungenen
   Wortspiele oder Opa-Kalauer. Lieber schlicht als gewollt.
5. **Kneipentest:** Würde man das am Tresen so sagen, und versteht es jeder sofort?

**Lokalkolorit:** echte Orte statt „draußen“ – Sielwall-Kreuzung, Osterdeich, Steintor,
Weserstadion, Hauptbahnhof, Neustadt, Schwachhausen, Vegesack …

**Themenpool für Seitenhiebe** (nur wenn's zum Wetter passt; Ziel nicht zweimal hintereinander):
- Münchner/Bayern: arrogant, halten ihr Zuhause für den Nabel der Welt. Süddeutsche allgemein.
- Werder; Touristen und Zugezogene; Schönwetter-Optimisten; Leute mit falscher Jacke.
- Delmenhorster Spießer (Steppjacke, Touran, Ordnung, Nachbarn – Spießer, nicht „nix los“).
- Schwachhausen: Geld (Porsche, Sylt, gepflegter Rasen).
- Arme Studenten in der Neustadt. Niedersächsisches Land (Emsland, Diepholz): abends nix los.
- Vegesack/Bremen-Nord: leere Fußgängerzone – über den Ort, nie über arme Leute.
- Lemwerder: Werften bauen Superjachten für Oligarchen.
- Dealer an der Sielwall-Kreuzung (augenzwinkernd über ihre Ausdauer, kein Drogenwitz);
  Gegend um den Hauptbahnhof (über den Ort, nie über Obdachlose oder Suchtkranke).
- Stau auf A1, A27, A28, Stephanibrücke.
- Saisonal: Freimarkt (2. Oktoberhälfte), Osterwiese (Ostern), Breminale (Juli).

**Grenzen:** frech ja, aber keine Beleidigungen von Gruppen, nichts Sexistisches oder
Rassistisches, keine Gewalt.

## So klingt es richtig

Nur zur Orientierung am Ton. Mehr Beispiele und die Reserve stehen in `spruchvorrat.md`.

- Kein Regen, kein Wind, keine Sonne. Der Bremer sagt: geht. Der Optimist sagt: gleich reißt's auf. Der Optimist wohnt nicht lange hier.
- Grau und windstill, es passiert einfach nichts. Wie Werder in der zweiten Halbzeit.
- Niesel bis in den Mittag. Wer dafür extra den Schirm aufspannt, outet sich als Zugezogener.
- Sonne satt, aber ordentlich Wind. Vom Fenster aus sieht's nach Frühling aus. Das Fenster lügt.
- Dritter Tag mit Sonne in Folge. In München nennt man das Herbst, in Bremen tippt man langsam auf einen Messfehler.
- Ein bisschen Schnee über Nacht. In Bayern freut man sich aufs Skifahren, in Bremen bricht die Zivilisation zusammen.
- Heute ausnahmsweise Rückenwind auf dem Weg zur Arbeit. Bezahlt wird heute Abend auf dem Rückweg.
- Dichter Nebel am Hauptbahnhof. Der Bahnhofsvorplatz sieht jetzt endlich so aus, wie er sich anfühlt.
- Strömender Regen an der Sielwall-Kreuzung. Die Dealer stehen trotzdem da. So viel Zuverlässigkeit hätte man gern mal von der BSAG.
- Freitagnachmittag, kalt und windig. Die Schwachhauser fahren jetzt übers Wochenende nach Sylt. Da ist es genauso windig, aber teurer.
- Regen den ganzen Samstag. In Delmenhorst wird trotzdem das Auto gewaschen. Nicht wegen Dreck, wegen der Nachbarn.
- Frost über Nacht. In den WGs in der Neustadt wird jetzt geheizt. Also, es wird darüber diskutiert.
- Sonne über Vegesack. Jetzt sieht man erst richtig, wie leer die Fußgängerzone ist. Bei Nebel war das gnädiger.
- Erster Frost in Schwachhausen. Der Porsche kriegt eine Abdeckhaube, die Kinder eine Mütze. In genau der Reihenfolge.

## So nicht (vom Nutzer als schwach bewertet)

- Am Osterdeich stehen Leute mit Sonnenbrille, als hätten sie den Himmel bestellt. – *nur Beobachtung*
- Kalt und windig, aber trocken. Perfekter Freitagabend fürs Viertel, finden auch die Delmenhorster. Die haben ja sonst nichts. – *Wetter nur Kulisse*
- Morgen grau und trocken. Auf der A1 steht trotzdem alles. Der Stau braucht kein Wetter. – *Stau ist kein Wetterthema*
- Der Hamburger fährt zum Elbstrand und nennt es Urlaub, der Bremer hält die Füße in die Weser und nennt es Feierabend. – *Gegenüber ohne Pointe*
- Blitzeis – am Osterdeich laufen Leute Schlittschuh, die das gar nicht vorhatten. – *Opa-Kalauer*
- Der Münchner sagt, bei ihnen fährt man rauf in die Sonne. Hier gibt's kein rauf. – *Offensichtliches, trifft das Ziel nicht*
- Ein Wind, der keine Fragen stellt. / Der Zugezogene sagt: schönes Wetter. Der Bremer sagt: Mütze. – *klingt weise, bedeutet nichts*
