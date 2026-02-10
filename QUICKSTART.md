# 🚀 Quick Start Guide - TIA25 Spotlight

## Installation (5 Minuten)

### Step 1: Extract the Project
Unzip `tia25-spotlight` to your desired location.

### Step 2: Open Terminal/Command Prompt
Navigate to the project folder:
```bash
cd path/to/tia25-spotlight
```

### Step 3: Create Virtual Environment
```bash
python -m venv venv
```

### Step 4: Activate Virtual Environment

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### Step 5: Install Dependencies
```bash
pip install -e .
```

### Step 6: Verify Installation
```bash
python verify_install.py
```

If all checks pass ✓, you're ready!

---

## Running the Application

### Start in Fullscreen (Presentation Mode)
```bash
python main.py
```

### Start in Windowed Mode (Testing)
1. Edit `config/settings.py`
2. Change `FULLSCREEN = True` to `FULLSCREEN = False`
3. Run `python main.py`

---

## Controls

- **→** (Right Arrow) - Next task
- **←** (Left Arrow) - Previous task
- **ESC** - Exit

---

## Customizing Tasks

Edit `data/tasks.json` in any text editor:

```json
[
  {
    "type": "quiz",
    "question": "Your question here?",
    "note": "Optional hint"
  },
  {
    "type": "tabu",
    "topic": "Topic to explain",
    "forbidden_words": ["word1", "word2", "word3"]
  },
  {
    "type": "discussion",
    "prompt": "Discussion topic",
    "spotlight_duration": "5 minutes"
  }
]
```

Save and restart the app.

---

## Troubleshooting

**"pygame not found"**
```bash
pip install pygame
```

**"tasks.json not found"**  
Make sure you're running from the project root directory.

**Fonts look wrong**  
Install Arial or change `FONT_FAMILY_PRIMARY` in `config/settings.py`.

---

## Full Documentation

See **README.md** for complete guide including:
- Architecture details
- Adding new task types
- Moderation tips
- Customization options

---

**Ready to start your quiz night! 🎉**
