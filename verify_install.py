#!/usr/bin/env python3
"""
Installation verification script for Spotlight.

Run this after installation to verify everything is set up correctly.
"""

import sys


def check_python_version():
    """Check if Python version is 3.10 or higher."""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"  ✗ Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    print(f"  ✓ Python {version.major}.{version.minor} - OK")
    return True


def check_pygame():
    """Check if pygame is installed."""
    print("✓ Checking pygame installation...")
    try:
        import pygame
        print(f"  ✓ pygame {pygame.version.ver} - OK")
        return True
    except ImportError:
        print("  ✗ pygame not found")
        print("  → Install with: pip install pygame")
        return False


def check_task_file():
    """Check if tasks.json exists and is valid."""
    print("✓ Checking task file...")
    from pathlib import Path
    from src.services.task_loader import TaskLoader
    
    task_file = Path("data/tasks.json")
    
    if not task_file.exists():
        print("  ✗ data/tasks.json not found")
        return False
    
    try:
        tasks = TaskLoader.load_tasks(str(task_file))
        print(f"  ✓ Loaded {len(tasks)} tasks - OK")
        return True
    except Exception as e:
        print(f"  ✗ Error loading tasks: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Spotlight - Installation Verification")
    print("=" * 60)
    print()
    
    checks = [
        check_python_version(),
        check_pygame(),
        check_task_file(),
    ]
    
    print()
    print("=" * 60)
    
    if all(checks):
        print("✓ All checks passed! Ready to run.")
        print()
        print("Start the application with:")
        print("  python main.py")
    else:
        print("✗ Some checks failed. Please fix issues above.")
        sys.exit(1)
    
    print("=" * 60)


if __name__ == "__main__":
    main()
