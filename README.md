# 📓 Spotlight

**Interactive Quiz & Learning Session Application**

Spotlight is a fullscreen presentation tool for running interactive quiz nights (with teams + scoring), Tabu-style challenges, and Spotlight discussions in a classroom or lecture hall setting. It’s built with Python + Pygame.

---

## 🎯 What Spotlight is good at

- **Teams + scoring** that stays consistent while you loop through tasks
- **Buzzer mechanics** (focus a buzzing team, block them per question on failure)
- **Presenter-safe Tabu** (placeholder slide → reveal later)
- **Big-screen-first UI** (high contrast, tuned font/layout scaling)
- **All content as JSON** (fast to edit, easy to generate with AI)

---

## 📦 Installation

### Prerequisites

- **Python 3.10+**

### Install (recommended)

From the project root:

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

Optional development tools:

```bash
pip install -e ".[dev]"
```

Verify:

```bash
python verify_install.py
```

> If you see **"pygame not found"**, your venv is probably not active, or dependencies weren’t installed into the environment you’re running with.

### Using `uv` (if you prefer)

If you have `uv` installed, you can also sync deps via the lockfile:

```bash
uv sync
```

---

## 🚀 Running

### Run via Python

```bash
python main.py
```

### Run via installed script

After `pip install -e .` you can run:

```bash
spotlight
```

---

## ⌨️ Controls

Spotlight is designed to be operated from the keyboard.

- **← / →**: previous/next task
- **ESC**: quit
- **H**: toggle on-screen help (keybind overlay)

> Tip: The bottom-right hint tells you when help is available.

There are additional controls for team/game flow (buzzer, award points, reveal Tabu, etc.). Those are intentionally shown in-app via the **Help overlay** so the README doesn’t drift.

---

## 🧩 Tasks (`data/tasks.json`)

Tasks live in `data/tasks.json` as a JSON array.

### Important: difficulty/points are required

Every task must have a difficulty / score value.

- Field name: **`points`**
- Allowed values: **100, 200, 300, 400, 500**

Spotlight uses this for scoring and for the roster/overview.

> If `points` is missing, Spotlight will error on load. This is intentional so you don’t end up with “mystery” questions that can’t be scored properly.

### Basic examples

#### Quiz
```json
{
  "type": "quiz",
  "points": 200,
  "question": "Was ist die Zeitkomplexität von QuickSort im Average Case?",
  "note": "Diskutiere die Auswirkung der Pivot-Wahl"
}
```

#### Tabu
```json
{
  "type": "tabu",
  "points": 300,
  "topic": "Mengenlehre",
  "forbidden_words": ["Menge", "Gruppe", "Ring", "bijektiv"]
}
```

#### Discussion
```json
{
  "type": "discussion",
  "points": 100,
  "prompt": "Erkläre den Unterschied zwischen Stack und Queue",
  "spotlight_duration": "5 Minuten"
}
```

#### Code
```json
{
  "type": "code",
  "points": 500,
  "code": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)",
  "question": "Erkenne den Fehler in diesem Code",
  "note": "Optional: Denk an Randfälle"
}
```

#### Explain-To
```json
{
  "type": "explain_to",
  "points": 200,
  "topic": "Was ist eine API?",
  "audience": "einem 5-Jährigen",
  "note": "Nutze ein alltägliches Beispiel"
}
```

---

## 🧑‍🤝‍🧑 Teams, buzzer, scoring (concept)

Spotlight is meant to be used with teams.

- Teams are set up at startup.
- A team can **buzz** to answer.
- After a buzz, the flow is:
  1) **Correct** → award the current question’s `points`
  2) **Fail** → re-open buzzer and **block that team for the current question**

Guards:
- A question’s points can be awarded **only once**.
- A **blocked team** can’t receive points.

---

## 🖥️ Display quality / crispness

Spotlight renders a “logical UI” and can scale it.

In `config/settings.py` you’ll typically find two knobs:

- **Render scale**: affects internal render resolution (higher = crisper but more GPU/CPU)
- **UI scale**: affects text/layout sizing (higher = bigger UI elements)

Practical guidance:

- If everything looks **blurry/low-res** → increase **render scale** slightly.
- If everything becomes **tiny** → increase **UI scale**.
- If performance drops (not ~60fps) → lower **render scale first**.

For 2560×1664 on macOS, a good starting point is often:
- render scale ~ **1.5**
- UI scale ~ **2.0**

If UI scale ≥ 2.5 breaks layout, it usually means some padding/line-wrap limits were tuned for smaller scales. In that case, keep UI scale sane and push crispness via render scale.

---

## 🐛 Troubleshooting

### `ModuleNotFoundError: No module named 'pygame'`

Make sure you’re in the venv you installed into:

```bash
source venv/bin/activate
python -c "import pygame; print(pygame.version.ver)"
```

Then reinstall deps:

```bash
pip install -e .
```

### Tasks fail to load

Common causes:
- invalid JSON
- missing required fields (especially `points`)

---

## 🏗️ Repo map

```
spotlight/
├── main.py
├── config/
│   ├── settings.py
│   └── keybindings.py
├── data/
│   ├── tasks.json
│   └── game_state.json
├── src/
│   ├── core/
│   ├── controllers/
│   ├── models/
│   ├── services/
│   └── views/
└── tests/
```

---

## 📄 License

MIT License.
