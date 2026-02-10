# 🎓 TIA25 Spotlight

**Interactive Quiz & Learning Session Application**

TIA25 Spotlight is a fullscreen presentation tool for running interactive quiz nights, Tabu-style challenges, and Spotlight discussions in a classroom or lecture hall setting. Built with Python and Pygame for TIA25 course events.

---

## 🎯 Features

- **📋 Quiz Mode** - Display questions prominently with optional moderator notes
- **🚫 Tabu/Explain Mode** - Challenge participants to explain topics without forbidden words
- **💡 Spotlight Discussions** - Facilitate in-depth Q&A sessions with participants
- **💻 Code Analysis** - Show code snippets for bug finding or language identification
- **🎓 Explain-To Challenges** - Explain technical topics to specific audiences (Oma, 5-year-old, etc.)
- **✨ Visual Glow Effects** - Subtle color-coded glow behind content for each task type
- **🎨 Clean, Professional UI** - High-contrast design optimized for projector visibility
- **⌨️ Simple Navigation** - Arrow keys to move between tasks, ESC to quit
- **📁 External Task Storage** - Edit tasks in JSON without touching code
- **🔄 Modular Architecture** - Easy to extend with new task types

---

## 📦 Installation

### Prerequisites

- **Python 3.10 or higher**
- **pip** (Python package manager)

### Setup Steps

1. **Clone or download this project**
   ```bash
   cd tia25-spotlight
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   **Linux/macOS:**
   ```bash
   source venv/bin/activate
   ```
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -e .
   ```
   
   This installs pygame and makes the project editable.

---

## 🚀 Running the Application

### Quick Start

```bash
python main.py
```

The application will:
1. Load tasks from `data/tasks.json`
2. Launch in fullscreen mode
3. Display the first task

### Development Mode

To run in windowed mode (easier for testing):

1. Edit `config/settings.py`
2. Set `FULLSCREEN = False`
3. Run `python main.py`

---

## ⌨️ Keyboard Controls

| Key | Action |
|-----|--------|
| `→` (Right Arrow) | Next task |
| `←` (Left Arrow) | Previous task |
| `ESC` | Exit application |

Navigation wraps around - pressing next on the last task returns to the first.

---

## 📋 Task Structure

Tasks are stored in `data/tasks.json` as a JSON array. Each task has a `type` field that determines its layout and appearance.

### Task Types

#### 1. Quiz Tasks

Display a question with optional moderator notes.

```json
{
  "type": "quiz",
  "question": "Was ist die Zeitkomplexität von QuickSort im Average Case?",
  "note": "Diskutiere die Auswirkung der Pivot-Wahl"
}
```

**Fields:**
- `type` (required): `"quiz"`
- `question` (required): The quiz question text
- `note` (optional): Additional context for moderator or audience

#### 2. Tabu/Explain Tasks

Challenge participants to explain a topic without using forbidden words.

```json
{
  "type": "tabu",
  "topic": "Mengenlehre",
  "forbidden_words": ["Menge", "Gruppe", "Ring", "bijektiv"]
}
```

**Fields:**
- `type` (required): `"tabu"`
- `topic` (required): Subject to explain
- `forbidden_words` (required): Array of words that cannot be used

#### 3. Discussion/Spotlight Tasks

Facilitate open discussions where a participant explains a topic to the group.

```json
{
  "type": "discussion",
  "prompt": "Erkläre den Unterschied zwischen Stack und Queue",
  "spotlight_duration": "5 Minuten"
}
```

**Fields:**
- `type` (required): `"discussion"`
- `prompt` (required): Discussion topic or question
- `spotlight_duration` (optional): Suggested time allocation

#### 4. Code Tasks

Display code snippets with questions like "Find the bug" or "Which programming language is this?". Code is shown in monospace font without syntax highlighting for easy JSON integration.

```json
{
  "type": "code",
  "code": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)",
  "question": "Erkenne den Fehler in diesem Code",
  "note": "Optional: Denk an Randfälle"
}
```

**Fields:**
- `type` (required): `"code"`
- `code` (required): Code snippet (use `\n` for line breaks)
- `question` (required): Question about the code
- `note` (optional): Hint or additional context

**Tips for JSON:**
- Use `\n` for newlines in code
- No special escaping needed for most code
- Escape double quotes inside strings with `\"`

#### 5. Explain-To Tasks

Challenge participants to explain technical topics to specific audiences (grandmother, 5-year-old, insurance agent, etc.).

```json
{
  "type": "explain_to",
  "topic": "Was ist eine API?",
  "audience": "einem 5-Jährigen",
  "note": "Nutze ein alltägliches Beispiel"
}
```

**Fields:**
- `type` (required): `"explain_to"`
- `topic` (required): Technical concept to explain
- `audience` (required): Target audience (e.g., "deiner Oma", "einem 5-Jährigen", "einer Versicherungsmaklerin")
- `note` (optional): Hint about what to focus on

---

## ➕ Adding New Tasks

### Method 1: Edit JSON Directly

1. Open `data/tasks.json` in any text editor
2. Add your task object to the array
3. Save the file
4. Restart the application

**Important:** Validate your JSON syntax! Use a JSON validator if unsure.

### Method 2: Create Alternative Task Files

You can create multiple task files for different events:

```bash
data/
├── tasks.json          # Default
├── tasks_advanced.json # Advanced topics
└── tasks_exam_prep.json # Exam preparation
```

Run with specific file:
```python
# Edit main.py, line 19:
app = Application(task_file="data/tasks_advanced.json")
```

---

## 🎨 Customization

### Colors and Styling

Edit `config/settings.py` to customize:

- **Screen resolution** - `SCREEN_WIDTH`, `SCREEN_HEIGHT`
- **Colors** - Full color palette with semantic names
- **Fonts** - Font families and sizes
- **Spacing** - Padding, margins, layout
- **Glow Effect** - Enable/disable, intensity, radius
  ```python
  GLOW_ENABLED = True      # Set to False to disable
  GLOW_RADIUS = 100        # Size of glow (50-200 recommended)
  GLOW_INTENSITY = 40      # Transparency (20-60 recommended)
  GLOW_LAYERS = 5          # Smoothness (3-7 recommended)
  ```

### Adding New Task Types

1. Create new task dataclass in `src/models/task.py`
2. Add to `TaskFactory._TASK_CLASSES` mapping
3. Create new renderer in `src/views/` (inherit from `BaseRenderer`)
4. Register renderer in `Application._init_renderers()`

Example structure in documentation comments.

---

## 🧑‍🏫 Moderation Tips

### Before the Event

1. **Test your setup** - Run through all tasks in windowed mode
2. **Check visibility** - Ensure text is readable from back of room
3. **Prepare backup** - Have tasks.json on USB drive
4. **Set expectations** - Brief audience on format and rules

### During Quiz Mode

- Read question aloud for clarity
- Use notes as discussion prompts
- Call on volunteers or use random selection
- Encourage debate on complex questions

### During Tabu Mode

- Set a time limit (e.g., 60 seconds)
- Have audience shout if forbidden word is used
- Award points for successful explanations
- Encourage creative descriptions

### During Spotlight Mode

- Invite volunteer to front of room
- Moderate audience questions
- Keep time if duration is specified
- Summarize key points afterward

### General Tips

- **Pace yourself** - Don't rush through tasks
- **Encourage participation** - Create safe environment for wrong answers
- **Mix task types** - Alternate between formats for variety
- **Take breaks** - 10 minutes every 30-45 minutes
- **Capture insights** - Note interesting answers for future discussions

---

## 🏗️ Project Architecture

### Directory Structure

```
tia25-spotlight/
├── main.py                    # Entry point
├── pyproject.toml            # Dependencies
├── README.md                 # This file
│
├── config/                   # Configuration
│   ├── settings.py           # Display, colors, fonts
│   └── keybindings.py        # Keyboard mapping
│
├── data/                     # Task database
│   └── tasks.json            # External tasks
│
└── src/                      # Source code
    ├── models/               # Data structures
    │   ├── task.py           # Task types
    │   └── session.py        # Session state
    │
    ├── services/             # Business logic
    │   ├── task_loader.py    # JSON loading
    │   └── renderer_utils.py # Rendering helpers
    │
    ├── controllers/          # Input handling
    │   └── input_controller.py
    │
    ├── views/                # Rendering
    │   ├── base_renderer.py  # Shared infrastructure
    │   ├── quiz_renderer.py  # Quiz layout
    │   ├── tabu_renderer.py  # Tabu layout
    │   └── discussion_renderer.py # Discussion layout
    │
    └── core/                 # Application core
        └── application.py    # Main loop & orchestration
```

### Design Patterns Used

- **MVC Architecture** - Separation of data, logic, rendering
- **Factory Pattern** - Task creation, renderer selection
- **Template Method** - Base renderer with specialized subclasses
- **Facade Pattern** - Application class as single entry point
- **Dependency Injection** - Configuration passed to components

---

## 🐛 Troubleshooting

### "pygame not found" error

```bash
pip install pygame
```

Or reinstall with:
```bash
pip install -e .
```

### Fonts look wrong

If system fonts fail to load, pygame uses default bitmap fonts. To fix:

1. Install Arial or Roboto on your system
2. Or replace `FONT_FAMILY_PRIMARY` in `config/settings.py` with available font

### Screen is black

Check `data/tasks.json`:
- Must be valid JSON
- Must contain at least one task
- All required fields must be present

Run with:
```bash
python main.py
```
And check terminal for error messages.

### Tasks not updating

After editing `tasks.json`, **restart** the application. Tasks are loaded once at startup.

---

## 🚀 Future Extensions

Ideas for enhancement:

- **Theme System** - Dark mode, high-contrast mode, custom branding
- **Splash Screen** - TIA25 logo on startup
- **Sound Effects** - Transition sounds, timer alerts
- **Timer Display** - Visual countdown for timed tasks
- **Scoring System** - Track points across session
- **Export Session** - Generate report of tasks covered
- **Randomize Mode** - Shuffle task order
- **Remote Control** - Control via mobile app
- **Multiple Choice** - Quiz tasks with answer options

---

## 📄 License

MIT License - Feel free to use and modify for educational purposes.

---

## 🙏 Acknowledgments

Created for **TIA25 course** by the course representatives.

Built with:
- **Python** - Programming language
- **Pygame** - Graphics and input handling
- **Love for teaching** - Making learning interactive and fun

---

## 📞 Support

For questions or issues:
1. Check this README thoroughly
2. Validate your `tasks.json` file
3. Review error messages in terminal
4. Contact course organizers

**Have a great quiz night! 🎉**