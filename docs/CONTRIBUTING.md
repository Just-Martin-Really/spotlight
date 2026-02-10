# 🤝 Contributing to Spotlight

Willkommen! Dieses Projekt ist für Studierende gedacht und wir freuen uns über Beiträge.

---

## 🎯 Wie du helfen kannst

### 1. Neue Tasks hinzufügen
Die einfachste Art beizutragen:
- Bearbeite `data/tasks.json`
- Füge interessante Quiz-Fragen, Tabu-Themen oder Diskussionsthemen hinzu
- Stelle einen Pull Request

### 2. Bugs finden und melden
- Teste die Anwendung mit verschiedenen Setups
- Dokumentiere Probleme mit genauen Schritten zur Reproduktion
- Erstelle ein Issue auf GitHub

### 3. Dokumentation verbessern
- README klarer machen
- Beispiele hinzufügen
- Übersetzungen

### 4. Neue Features entwickeln
Siehe "Feature-Ideen" unten!

---

## 🛠️ Development Setup

### Voraussetzungen
- Python 3.10+
- Git (für Versionskontrolle)
- Code-Editor (VS Code, PyCharm, etc.)

### Setup-Schritte

1. **Projekt klonen/forken**
   ```bash
   git clone <repository-url>
   cd spotlight
   ```

2. **Virtual Environment erstellen**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # oder
   venv\Scripts\activate  # Windows
   ```

3. **Dependencies installieren (editable mode)**
   ```bash
   pip install -e ".[dev]"
   ```
   
   Dies installiert:
   - pygame (Hauptdependency)
   - pytest (Testing)
   - black (Code Formatting)
   - mypy (Type Checking)

4. **Verifizieren**
   ```bash
   python verify_install.py
   python main.py
   ```

---

## 📝 Code Style Guidelines

### Python Code
- **PEP 8** Standard befolgen
- **Type Hints** nutzen wo möglich
- **Docstrings** für alle Klassen und Funktionen
- **Englische Kommentare** (Code ist international lesbar)

### Formatierung
Wir nutzen **Black** für automatische Formatierung:
```bash
black src/ config/
```

### Type Checking
```bash
mypy src/
```

### Naming Conventions
```python
# Classes: PascalCase
class QuizRenderer:
    pass

# Functions/Methods: snake_case
def load_tasks(filepath: str) -> List[Task]:
    pass

# Constants: UPPER_SNAKE_CASE
COLOR_BACKGROUND = (15, 23, 42)

# Private members: _leading_underscore
def _render_footer(self):
    pass
```

---

## 🏗️ Architektur-Prinzipien

Beim Hinzufügen neuer Features, beachte:

### 1. Separation of Concerns
- **Models**: Nur Daten, keine Logik
- **Services**: Business-Logik, kein UI
- **Views**: Rendering, keine Zustandsänderungen
- **Controllers**: Input → Aktionen, kein Rendering

### 2. Single Responsibility
Jede Klasse hat **genau eine** Aufgabe:
- `TaskLoader` lädt Tasks (nicht: rendert sie)
- `Session` verwaltet State (nicht: lädt Tasks)
- `QuizRenderer` rendert Quiz (nicht: andere Task-Typen)

### 3. Dependency Injection
Keine globalen Variablen! Übergib Dependencies:
```python
# ✓ Gut
class Renderer:
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config

# ✗ Schlecht
class Renderer:
    def __init__(self):
        import config  # Tight coupling!
        self.config = config
```

---

## 🎨 Feature-Ideen für Contributions

### 🟢 Einfach (Guter Einstieg)
- [ ] **Multiple Choice Quiz**: Quiz mit Antwortoptionen A/B/C/D
- [ ] **Timer Display**: Visueller Countdown für Diskussionen
- [ ] **Custom Fonts**: Mehr Font-Optionen in Settings
- [ ] **Sound Effects**: Transition-Sounds (optional aktivierbar)
- [ ] **Dark/Light Theme**: Theme-Switcher in Settings

### 🟡 Mittel
- [ ] **Scoring System**: Punktevergabe und Anzeige
- [ ] **Session Export**: Markdown-Report nach Session
- [ ] **Random Mode**: Tasks in zufälliger Reihenfolge
- [ ] **Splash Screen**: TIA25 Logo beim Start
- [ ] **Animation Transitions**: Fade-Effekte zwischen Tasks

### 🔴 Fortgeschritten
- [ ] **Remote Control**: Steuerung per Handy-App
- [ ] **Audience Voting**: Live-Umfragen via QR-Code
- [ ] **Plugin System**: Dynamisches Laden von Task-Typen
- [ ] **Multi-Language**: i18n für DE/EN
- [ ] **Web Interface**: Browser-basierte Alternative zu Desktop

---

## 📋 Pull Request Checklist

Bevor du einen PR einreichst:

- [ ] Code läuft ohne Errors (`python main.py`)
- [ ] Neue Funktionen dokumentiert (Docstrings + README)
- [ ] Code formatiert (`black src/`)
- [ ] Type Hints hinzugefügt
- [ ] Keine Breaking Changes (außer explizit besprochen)
- [ ] Beispiel-Tasks aktualisiert (falls relevant)
- [ ] CHANGELOG.md aktualisiert

---

## 🧪 Testing (Optional, aber empfohlen)

Falls du Tests schreiben möchtest:

```bash
# Test-Datei erstellen: tests/test_task_loader.py
import pytest
from src.services.task_loader import TaskLoader

def test_load_valid_tasks():
    tasks = TaskLoader.load_tasks("data/tasks.json")
    assert len(tasks) > 0
    assert tasks[0].type in ["quiz", "tabu", "discussion"]

# Tests ausführen
pytest tests/
```

---

## 💡 Best Practices für neue Task-Typen

Beispiel: **Multiple Choice Quiz**

### 1. Datenmodell
```python
# src/models/task.py
@dataclass
class MultipleChoiceTask(BaseTask):
    question: str
    options: List[str]  # ["A) ...", "B) ...", "C) ...", "D) ..."]
    correct_answer: str  # "B"
    explanation: Optional[str] = None
```

### 2. Factory Registration
```python
# src/models/task.py
class TaskFactory:
    _TASK_CLASSES = {
        # ... existing ...
        "multiple_choice": MultipleChoiceTask,
    }
```

### 3. Renderer
```python
# src/views/multiple_choice_renderer.py
class MultipleChoiceRenderer(BaseRenderer):
    def render_content(self, task: MultipleChoiceTask) -> None:
        # 1. Render question
        # 2. Render options in columns/list
        # 3. Use appropriate colors
        pass
```

### 4. Application Integration
```python
# src/core/application.py
def _init_renderers(self):
    self.renderers = {
        # ... existing ...
        "multiple_choice": MultipleChoiceRenderer(self.screen),
    }
```

### 5. JSON Beispiel
```json
{
  "type": "multiple_choice",
  "question": "Welche Datenstruktur ist am besten für LIFO?",
  "options": [
    "A) Queue",
    "B) Stack",
    "C) Array",
    "D) HashMap"
  ],
  "correct_answer": "B",
  "explanation": "LIFO = Last In, First Out → Stack"
}
```

---

## 🐛 Debugging-Tipps

### Pygame-Fenster bleibt schwarz
```python
# Füge Debug-Output hinzu:
print(f"Current task: {self.session.current_task()}")
print(f"Renderer: {renderer}")
```

### Tasks laden nicht
```python
# In task_loader.py, füge hinzu:
print(f"Loading from: {path.absolute()}")
print(f"Task data: {data}")
```

### Schriftarten fehlen
```python
# base_renderer.py
pygame.font.get_fonts()  # Liste aller verfügbaren Fonts
```

---

## 📞 Fragen?

- **Code-Fragen**: Schau in ARCHITECTURE.md
- **Setup-Probleme**: Siehe README.md Troubleshooting
- **Feature-Diskussionen**: Erstelle ein Issue/öffne Discussion

---

## 🙏 Code of Conduct

- Sei respektvoll und konstruktiv
- Hilf Anfängern
- Dokumentiere deine Änderungen
- Teste vor dem Commit
- Hab Spaß beim Programmieren! 🎉

---

**Danke, dass du Spotlight besser machst!**
