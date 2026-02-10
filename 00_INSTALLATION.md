# 📦 Spotlight - Alle Dateien

## ✅ Heruntergeladene Dateien

### 📄 Haupt-Dateien (Root)
- `pyproject.toml` - Projekt-Konfiguration & Dependencies
- `main.py` - Einstiegspunkt der Anwendung
- `verify_install.py` - Installations-Check-Script
- `.gitignore` - Git-Ausschlüsse

### 📚 Dokumentation
- `README.md` - Vollständige Dokumentation (Installation, Usage, etc.)
- `QUICKSTART.md` - 5-Minuten-Schnellstart
- `ARCHITECTURE.md` - Architektur-Diagramme und Design-Patterns
- `CONTRIBUTING.md` - Contribution-Guide für Studierende
- `CHANGELOG.md` - Versionshistorie

### ⚙️ Configuration (config/)
- `config/settings.py` - Display, Farben, Fonts
- `config/keybindings.py` - Tastatur-Mapping
- `config/__init__.py` - Python-Package-Marker

### 📊 Data
- `data/tasks.json` - 12 Beispiel-Tasks (Quiz, Tabu, Diskussion)

### 🏗️ Source Code (src/)

#### Models (src/models/)
- `task.py` - Task-Datenklassen (QuizTask, TabuTask, DiscussionTask)
- `session.py` - Session-State-Management
- `__init__.py`

#### Services (src/services/)
- `task_loader.py` - JSON → Task-Objekte
- `renderer_utils.py` - Text-Rendering-Helpers
- `__init__.py`

#### Controllers (src/controllers/)
- `input_controller.py` - Keyboard-Event-Handling
- `__init__.py`

#### Views (src/views/)
- `base_renderer.py` - Basis-Renderer mit shared logic
- `quiz_renderer.py` - Quiz-Task-Renderer
- `tabu_renderer.py` - Tabu-Task-Renderer
- `discussion_renderer.py` - Discussion-Task-Renderer
- `__init__.py`

#### Core (src/core/)
- `application.py` - Hauptloop & Orchestrierung
- `__init__.py`

---

## 🚀 Installation auf deinem System

### 1. Ordnerstruktur erstellen

Erstelle einen Ordner `spotlight` und lege alle Dateien in der richtigen Struktur ab:

```
spotlight/
├── main.py
├── pyproject.toml
├── verify_install.py
├── .gitignore
├── README.md
├── QUICKSTART.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── CHANGELOG.md
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── keybindings.py
│
├── data/
│   └── tasks.json
│
└── src/
    ├── __init__.py
    ├── models/
    │   ├── __init__.py
    │   ├── task.py
    │   └── session.py
    ├── services/
    │   ├── __init__.py
    │   ├── task_loader.py
    │   └── renderer_utils.py
    ├── controllers/
    │   ├── __init__.py
    │   └── input_controller.py
    ├── views/
    │   ├── __init__.py
    │   ├── base_renderer.py
    │   ├── quiz_renderer.py
    │   ├── tabu_renderer.py
    │   └── discussion_renderer.py
    └── core/
        ├── __init__.py
        └── application.py
```

### 2. Terminal öffnen

```bash
cd tia25-spotlight
```

### 3. Virtual Environment erstellen

```bash
python -m venv venv
```

### 4. Virtual Environment aktivieren

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 5. Dependencies installieren

```bash
pip install -e .
```

Dies installiert:
- pygame (2.5.0+)
- Optional: pytest, black, mypy für Development

### 6. Installation verifizieren

```bash
python verify_install.py
```

Erwartete Ausgabe:
```
============================================================
TIA25 Spotlight - Installation Verification
============================================================

✓ Checking Python version...
  ✓ Python 3.X - OK
✓ Checking pygame installation...
  ✓ pygame 2.X.X - OK
✓ Checking task file...
  ✓ Loaded 12 tasks - OK

============================================================
✓ All checks passed! Ready to run.

Start the application with:
  python main.py
============================================================
```

### 7. Starten! 🎉

```bash
python main.py
```

---

## 🎮 Steuerung

- **→** (Rechte Pfeiltaste) - Nächste Task
- **←** (Linke Pfeiltaste) - Vorherige Task
- **ESC** - Beenden

---

## 🛠️ Erste Schritte

### Tasks anpassen

Bearbeite `data/tasks.json`:

```json
[
  {
    "type": "quiz",
    "question": "Deine Frage hier?",
    "note": "Optional: Hinweis"
  },
  {
    "type": "tabu",
    "topic": "Thema erklären",
    "forbidden_words": ["Wort1", "Wort2", "Wort3"]
  },
  {
    "type": "discussion",
    "prompt": "Diskussionsthema",
    "spotlight_duration": "5 Minuten"
  }
]
```

Speichern und App neu starten.

### Farben anpassen

Bearbeite `config/settings.py`:

```python
# Beispiel: Hintergrundfarbe ändern
COLOR_BACKGROUND = (0, 0, 0)  # Schwarz
```

### Windowed Mode (zum Testen)

In `config/settings.py`:

```python
FULLSCREEN = False  # Statt True
```

---

## 📋 Checkliste

- [ ] Alle Dateien heruntergeladen
- [ ] Ordnerstruktur korrekt erstellt
- [ ] Virtual Environment erstellt
- [ ] Dependencies installiert
- [ ] Verification erfolgreich
- [ ] App startet im Fullscreen
- [ ] Navigation funktioniert (← →)
- [ ] Tasks werden angezeigt

---

## 🐛 Probleme?

### "pygame not found"
```bash
pip install pygame
```

### "ModuleNotFoundError: No module named 'src'"
- Stelle sicher, dass du im Projekt-Root bist
- `__init__.py` Dateien vorhanden?

### "tasks.json not found"
- Datei muss in `data/tasks.json` liegen
- Pfad relativ zum Projekt-Root

### Fonts sehen komisch aus
- Installiere Arial auf deinem System
- Oder ändere `FONT_FAMILY_PRIMARY` in `config/settings.py`

---

## 📚 Weiterführende Dokumentation

- **README.md** - Vollständige Anleitung
- **ARCHITECTURE.md** - Code-Struktur verstehen
- **CONTRIBUTING.md** - Features hinzufügen
- **QUICKSTART.md** - Schnelle Übersicht

---

**Viel Erfolg mit deinem interaktiven Lernabend! 🎓**
