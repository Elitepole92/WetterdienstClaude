# WetterdienstClaude

Erzeugt 3× täglich (5:45, 11:45, 17:45 Uhr Europe/Berlin) einen frechen norddeutschen
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
  - Dritter Tag mit Sonne in Folge. In München nennt man das Herbst, in Bremen tippt man langsam auf einen Messfehler.
  - Kräftiger Wind übers Weserstadion. Bei dem Wetter geht jeder Ball ins Aus. Beim Werder-Training merkt das keiner.
  - Endlich Sommer, richtig heiß. Der Bremer hält das genau zwei Tage aus, dann will er seinen Nieselregen zurück.
  - Ein bisschen Schnee über Nacht. In Bayern freut man sich aufs Skifahren, in Bremen bricht die Zivilisation zusammen.
  - Gewitter über der Breminale. Die Auswärtigen flüchten ins Zelt, die Bremer holen sich noch ein Bier, solange die Schlange kurz ist.
  - Aprilwetter: Sonne, Hagel, Sonne, Regen. Im Viertel trägt man deshalb einfach alles gleichzeitig, und keiner guckt komisch.
  - Nebel so dick, dass man das Weserstadion von der Brücke aus nicht mehr sieht. Werder-Fans sagen: ist auch besser so.
  - Erster Tag, an dem man die Jacke offen lassen könnte. Der Bremer macht nur den obersten Knopf auf. Man weiß ja nie.
  - Seit einer Woche keine Sonne gesehen. Im Solarium im Viertel gibt's jetzt Wartenummern.
  - Heute ausnahmsweise Rückenwind auf dem Weg zur Arbeit. Bezahlt wird heute Abend auf dem Rückweg.
  - Der Schnee ist über Nacht zu Matsch geworden. Hält ungefähr so lange wie der Vorsatz, mal wieder in die Kunsthalle zu gehen.
  - Strömender Regen an der Sielwall-Kreuzung. Die Dealer stehen trotzdem da. So viel Zuverlässigkeit hätte man gern mal von der BSAG.
  - Dichter Nebel am Hauptbahnhof. Der Bahnhofsvorplatz sieht jetzt endlich so aus, wie er sich anfühlt.
  - Regen, und auf der A28 aus Delmenhorst steht alles. Gut so, dann bleibt das Viertel heute Abend mal unter sich.
  - Sonne am Nachmittag. In der Neustadt sitzen die Studenten mit Dosenbier auf dem Bordstein. Mehr Urlaub gibt das Bafög nicht her.
  - Ordentlich Sturm heute Nacht. In Schwachhausen liegen morgen Äste auf dem Rasen, und zwar welche, die vorher keiner genehmigt hat.
  - Frostiger Freitagmorgen. Die Studenten aus der Neustadt gehen heute freiwillig in die Vorlesung. Da ist wenigstens geheizt.
  - Kräftiger Wind von der Küste. Am Bahnhofsvorplatz riecht's heute ausnahmsweise mal nach Nordsee.
  - Freitagnachmittag, kalt und windig. Die Schwachhauser fahren jetzt übers Wochenende nach Sylt. Da ist es genauso windig, aber teurer.
  - Ordentlich Sturm über Bremen-Nord. In der Vegesacker Fußgängerzone fliegen trotzdem keine Schilder weg. Da hängen ja kaum noch welche.
  - Freitagabend, kalt und windig, alle stehen vor der Kneipe. Die Delmenhorster erkennt man an der Steppjacke. Passend zum Touran.
  - Grau ohne Ende. Ein Münchner im Steintor fragt, wie man das hier aushält. Ging eigentlich ganz gut, bis er kam.
  - Sonne über Vegesack. Jetzt sieht man erst richtig, wie leer die Fußgängerzone ist. Bei Nebel war das gnädiger.
  - Regen den ganzen Samstag. In Delmenhorst wird trotzdem das Auto gewaschen. Nicht wegen Dreck, wegen der Nachbarn.
  - Frost über Nacht. In den WGs in der Neustadt wird jetzt geheizt. Also, es wird darüber diskutiert.
  - Erster Frost in Schwachhausen. Der Porsche kriegt eine Abdeckhaube, die Kinder eine Mütze. In genau der Reihenfolge.
  - Grau und kalt, aber trocken. Am Osterdeich sind alle spazieren. Wer in Bremen auf Sonne wartet, kommt nie vor die Tür.
  - Windstill und trocken, ideales Laubbläserwetter. Leider Sonntag. In Schwachhausen stehen sie jetzt am Fenster und warten auf Montag.
  - Kalt, trocken, kaum Wind. Perfektes Fußballwetter. Werder muss sich für heute eine neue Ausrede suchen.
- **Themenpool für Seitenhiebe** (zusätzlich zu den Zielen oben; nur wenn's zum Wetter passt):
  - *Freimarkt* (zweite Oktoberhälfte, Bürgerweide) und *Osterwiese* (um Ostern) – nur in der
    Saison erwähnen. *Breminale* (Juli, Osterdeich) – nur im Sommer.
  - Die Dealer an der Sielwall-Kreuzung – augenzwinkernd über ihre Ausdauer, nicht als Drogenwitz.
  - Die Gegend um den Hauptbahnhof, die manchmal ein bisschen gruselig ist – über den Ort,
    nie auf Kosten von Obdachlosen oder Suchtkranken.
  - Stau auf den Zufahrten nach Bremen (A1, A27, A28, Stephanibrücke …).
  - Spießer aus Delmenhorst (Mittelklasse: Steppjacke, Touran, Fiat Multipla, Ordnung, Nachbarn – *Spießer*, nicht
    „da ist nix los“, und kein Porsche) und Schwachhausen (Geld: Porsche, Sylt, gepflegter Rasen).
  - Niedersächsische Landbevölkerung (Emsland, Landkreis Diepholz …): da ist abends nichts los.
  - Bremen-Nord/Vegesack: Strukturschwäche, leere Fußgängerzone – über den Ort, nie über arme Leute.
  - Lemwerder (nicht Lemwerden): Werften, die Superjachten für Oligarchen bauen.
  - Bayern/Münchner: arrogant und überheblich, halten ihr Zuhause für den Nabel der Welt und gucken mit Scheuklappen auf alles andere.
  - Arme Studenten in der Neustadt.
- **Die Beispiele oben zeigen nur den Ton.** Die Beispiele unter *Hauptstil* und
  *Lebensweisheit* nie übernehmen, auch nicht abgewandelt. Sprüche aus *So klingt es richtig*
  und alle eigenen früheren Sprüche dürfen nach **zwei Wochen** wörtlich wiederkommen, wenn sie
  genau zum aktuellen Wetter passen (siehe *Nicht wiederholen*). Sonst gilt: eigene, neue Idee.
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
  Zugezogene sagt: schönes Wetter. Der Bremer sagt: Mütze.“; „alle in kurzen Hosen, nur die
  Beine haben das noch nicht mitbekommen“ – zu großer Gedankensprung). Jeder Satz muss
  wörtlich Sinn ergeben, und der Vergleich muss in sich stimmen (in Bayern fährt man nicht
  *in der Stadt* Ski, also nicht „in Bayern fährt man damit Ski, in Bremen fällt der Bus aus“).
- **Der Seitenhieb hängt am Wetter.** Prüffrage: Funktioniert der Witz bei jedem Wetter genauso? Dann ist das Wetter
  nur Kulisse und der Spruch durchgefallen (schwach: „Kalt und windig, aber trocken. Perfekter Freitagabend fürs Viertel,
  finden auch die Delmenhorster. Die haben ja sonst nichts.“).
  Auch kein Trick ist: „trotz des Wetters passiert X“, wenn X sowieso nichts mit Wetter zu tun hat (schwach: „Morgen
  grau und trocken. Auf der A1 steht trotzdem alles. Der Stau braucht kein Wetter.“ – Stau ist kein Wetterthema).
- **Die Pointe hängt am Bild.** Der zweite Teil muss direkt aus dem ersten folgen, nicht ein
  neues Thema aufmachen (schwach: Scheibe freikratzen … und abends keinen Parkplatz finden –
  das hat mit dem Kratzen nichts zu tun; besser: erst bis Hastedt zum Auto laufen, *dann* kratzen).
- **Zwei Seiten sind noch kein Witz.** Ein Gegenüber „der eine macht X, der andere Y“ braucht
  eine Pointe, sonst ist es nur eine Aufzählung (schwach: „Der Hamburger fährt zum Elbstrand und
  nennt es Urlaub, der Bremer hält die Füße in die Weser und nennt es Feierabend“).
- **Keine Opa-Kalauer.** Abgegriffene Witze, die man schon hundertmal gehört hat, wirken
  boomerig (schwach: „Blitzeis – am Osterdeich laufen Leute Schlittschuh, die das gar nicht
  vorhatten“). Lieber eine Beobachtung, die frisch und konkret ist.
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
- **Wiederholen ist okay, unlustig nicht.** Vorher `git log --since='14 days ago' -p -- spruch.json`
  ansehen. Lieber ab und zu einen bewährten Spruch wiederbringen als zwanghaft etwas Neues
  bauen, das dann nicht zündet. Faustregeln: denselben Spruch nicht innerhalb von zwei Wochen
  wörtlich wiederholen; das Ziel des Seitenhiebs möglichst nicht direkt hintereinander gleich.
  Besteht kein neuer Spruch den Kneipentest, einen passenden aus *So klingt es richtig* oder
  aus der Historie nehmen, der älter als zwei Wochen ist.
