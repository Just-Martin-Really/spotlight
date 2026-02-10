"""
Spotlight - Entry Point

Interactive quiz and learning session application for TIA25 course.
Displays tasks fullscreen for audience participation.

Usage:
    python main.py

Controls:
    → : Next task
    ← : Previous task
    ESC : Quit
"""

from src.core.application import Application


def main():
    """
    Application entry point.

    Creates and runs the Application instance.
    All initialization and error handling is delegated to Application class.
    """
    app = Application(task_file="data/tasks.json")
    app.run()


if __name__ == "__main__":
    main()