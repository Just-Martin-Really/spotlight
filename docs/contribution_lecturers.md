# Spotlight – Guide für das Erstellen von Aufgaben (für Dozenten)

Dieses Dokument erklärt kurz, wie du neue Aufgaben/Quizfragen für **Spotlight** vorbereitest, ohne Zugriff auf das Projekt zu brauchen.

## Ziel / „Was muss ich tun?“

- Du erstellst Aufgaben **als Text**.
- Du nutzt dafür **einen der Aufgabentypen** unten.
- Du vergibst pro Aufgabe **Punkte** (Schwierigkeit).
- Ich übernehme anschließend deine Inhalte ins nötige Format und teste kurz, ob alles korrekt geladen wird.

---

## Punkte / Schwierigkeit

Jede Aufgabe hat ein Feld **`points`** (Punktwert / Schwierigkeitsstufe).

- Erlaubte Werte: **100, 200, 300, 400, 500**
- Faustregel:
  - **100** = sehr leicht / Warm-up
  - **300** = normal
  - **500** = schwer / Bonus

> Wichtig: Bitte Punkte **immer angeben**. (Fehlt `points`, wird die Aufgabe je nach Setup ggf. abgelehnt.)

---

## So gibst du mir Aufgaben ab

### Format A: „Einfach als Liste“ (am schnellsten)

Bitte pro Aufgabe:
- **Typ**: quiz / discussion / tabu / code / explain_to
- **Inhalt** (je nach Typ)
- **Punkte**: 100 / 200 / 300 / 400 / 500
- Optional: **Notiz** (z. B. Lösung, Tipp)

Beispiel:

```
1) Typ: quiz
   Punkte: 200
   Frage: Was ist die Ableitung von sin(x)?
   Notiz: cos(x)

2) Typ: discussion
   Punkte: 300
   Prompt: Warum darf man durch 0 nicht teilen?

3) Typ: tabu
   Punkte: 400
   Thema: Integral
   Verbotene Wörter: Fläche, Stammfunktion, Grenze
```

### Format B: „Copy‑Paste‑Template“ (noch sauberer, super zum Umwandeln)

Wenn du magst, nutze dieses Mini‑Template pro Aufgabe:

```
TYPE=quiz
POINTS=200
QUESTION=Löse: 2x + 5 = 17
NOTE=x = 6
---
TYPE=discussion
POINTS=300
PROMPT=Erkläre, warum die Summe zweier gerader Zahlen wieder gerade ist.
---
TYPE=tabu
POINTS=400
TOPIC=Ableitung
FORBIDDEN_WORDS=Steigung, Grenzwert, Differentialquotient
---
TYPE=code
POINTS=500
CODE=def f(x):\n    return x^2
QUESTION=Was ist hier falsch (Python)?
NOTE=In Python ist ^ kein Potenz-Operator.
---
TYPE=explain_to
POINTS=100
TOPIC=Was ist ein Bruch?
AUDIENCE=einem 5-jährigen Kind
NOTE=Nutze Pizza- oder Kuchenstücke als Bild.
```

Trenner ist jeweils eine Zeile mit `---`.

---

## Welche Aufgabentypen gibt es? (Schemas + Beispiele)

Spotlight entscheidet über das Layout über das Feld **`type`**.

> Du musst JSON **nicht** selbst schreiben. Die Beispiele unten zeigen aber exakt, welche Inhalte pro Typ erwartet werden.

### 1) Quiz (`type: "quiz"`)
**Klassische Frage**, optional mit Notiz (z. B. Lösung).

Pflichtfelder:
- `type`: `"quiz"`
- `question`: Text der Frage
- `points`: `100 | 200 | 300 | 400 | 500`

Optional:
- `note`: Hinweis/Notiz

Beispiel:
```json
{
  "type": "quiz",
  "points": 200,
  "question": "Was ist die Ableitung von sin(x)?",
  "note": "cos(x)"
}
```

---

### 2) Diskussion (`type: "discussion"`)
**Offene Frage/Prompt** für Erklärungen oder Begründungen.

Pflichtfelder:
- `type`: `"discussion"`
- `prompt`: Prompt/Fragestellung
- `points`: `100 | 200 | 300 | 400 | 500`

Optional:
- `spotlight_duration`: z. B. `"3 Minuten"`

Beispiel:
```json
{
  "type": "discussion",
  "points": 300,
  "prompt": "Erkläre, warum man durch 0 nicht teilen darf.",
  "spotlight_duration": "3 Minuten"
}
```

---

### 3) Tabu (`type: "tabu"`)
Eine Person muss ein Thema erklären, ohne bestimmte Wörter zu benutzen.

Pflichtfelder:
- `type`: `"tabu"`
- `topic`: Thema
- `forbidden_words`: Liste von verbotenen Wörtern
- `points`: `100 | 200 | 300 | 400 | 500`

Beispiel:
```json
{
  "type": "tabu",
  "points": 400,
  "topic": "Ableitung",
  "forbidden_words": ["Steigung", "Grenzwert", "Differentialquotient"]
}
```

---

### 4) Code‑Aufgabe (`type: "code"`)
Für „Finde den Fehler“ oder „Was macht dieser Code?" – Code wird als Text angezeigt.

Pflichtfelder:
- `type`: `"code"`
- `code`: Code‑Text (Zeilenumbrüche als `\n`)
- `question`: Frage zum Code
- `points`: `100 | 200 | 300 | 400 | 500`

Optional:
- `note`: Hinweis

Beispiel:
```json
{
  "type": "code",
  "points": 500,
  "code": "def f(x):\n    return x^2",
  "question": "Was ist hier falsch (Python)?",
  "note": "In Python ist ^ kein Potenz-Operator."
}
```

---

### 5) Explain‑To (`type: "explain_to"`)
Thema so erklären, dass eine bestimmte Zielgruppe es versteht.

Pflichtfelder:
- `type`: `"explain_to"`
- `topic`: Thema
- `audience`: Zielgruppe (z. B. „einem 5‑Jährigen“)
- `points`: `100 | 200 | 300 | 400 | 500`

Optional:
- `note`: Hinweis

Beispiel:
```json
{
  "type": "explain_to",
  "points": 100,
  "topic": "Was ist ein Bruch?",
  "audience": "einem 5-jährigen Kind",
  "note": "Nutze Pizza- oder Kuchenstücke als Bild."
}
```

---

## Wenn du doch selbst JSON schreiben willst (optional)

Dieser Abschnitt ist absichtlich etwas detaillierter, damit du ihn **1:1 in eine KI kopieren** kannst und die KI daraus **korrekt formatierte JSON‑Aufgaben** erzeugt.

Ein paar konkrete Regeln (damit Spotlight sie zuverlässig laden kann):

### Pflichtfelder & Werte
- Jede Aufgabe ist ein JSON‑Objekt: `{ ... }`.
- Eine Aufgabenliste ist ein JSON‑Array: `[ { ... }, { ... } ]`.
- **`type`** ist Pflicht und muss einer der folgenden Strings sein:
  - `"quiz" | "discussion" | "tabu" | "code" | "explain_to"`
- **`points`** ist Pflicht und muss **eine Zahl** sein:
  - `100 | 200 | 300 | 400 | 500`

### String-/Listen-Regeln
- Strings immer in **doppelten** Anführungszeichen: `"Text"` (keine einfachen `'...'`).
- Listen stehen in eckigen Klammern: `[...]`.
  - Beispiel `forbidden_words`: `["Wort1", "Wort2"]`

### Kommas, Quotes, JSON vs. Python
- Nach jedem Feld (außer dem letzten) steht ein Komma.
  - Richtig: `{ "type": "quiz", "points": 200, "question": "..." }`
  - Falsch: `{ "type": "quiz" "points": 200 }` (Komma fehlt)
- JSON kennt nur `true/false/null` (klein geschrieben), **nicht** `True/False/None`.

### Zeilenumbrüche / Sonderzeichen
- Zeilenumbrüche innerhalb eines JSON‑Strings als `\n`.
- Wenn du Backslashes nutzt (z. B. in Regex/Windows‑Pfaden), müssen sie ggf. escaped werden: `\\`.

### Typ-spezifische Pflichtfelder (Kurzform)
- `quiz`: `question`
- `discussion`: `prompt`
- `tabu`: `topic`, `forbidden_words` (Liste)
- `code`: `code`, `question`
- `explain_to`: `topic`, `audience`

> Tipp: Wenn du unsicher bist, nimm ein Beispiel aus diesem Dokument und ändere nur die Inhalte.

Mini‑Beispiel (2 Aufgaben):

```json
[
  { "type": "quiz", "points": 200, "question": "Löse: 2x + 5 = 17", "note": "x = 6" },
  { "type": "discussion", "points": 300, "prompt": "Warum ist 0 eine gerade Zahl?" }
]
```
