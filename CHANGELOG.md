# Changelog

All notable changes to TIA25 Spotlight will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-02-10

### Initial Release

#### Features
- **Three Task Types**
  - Quiz questions with optional notes
  - Tabu/Explain challenges with forbidden words
  - Discussion/Spotlight sessions with time allocations

- **Professional UI**
  - Fullscreen presentation mode
  - High-contrast colors optimized for projectors
  - Task-specific color coding (blue/red/green)
  - Responsive text wrapping and centering

- **Simple Navigation**
  - Arrow key navigation (← →)
  - Circular task progression
  - Position indicator
  - ESC to quit

- **External Task Management**
  - JSON-based task storage
  - No code changes needed to add tasks
  - Validation and error handling

- **Modular Architecture**
  - MVC-inspired design
  - Factory pattern for renderers
  - Easy to extend with new task types
  - Clean separation of concerns

#### Technical
- Python 3.10+ support
- Pygame 2.5.0+ integration
- Modern pyproject.toml configuration
- Comprehensive inline documentation
- Type hints for better IDE support

#### Documentation
- Complete README with installation guide
- Quick start guide
- Moderation tips and best practices
- Architecture overview
- Task format examples
- Troubleshooting section

---

## Future Roadmap

### Planned Features
- [ ] Theme system (Dark mode, TIA25 branding)
- [ ] Splash screen with logo
- [ ] Sound effects for transitions
- [ ] Visual timer for timed tasks
- [ ] Scoring system
- [ ] Session export (Markdown report)
- [ ] Task randomization mode
- [ ] Multiple choice quiz option

### Under Consideration
- Remote control via mobile app
- Audience response system integration
- Custom fonts and styling
- Animation transitions
- Background music support

---

*For detailed changes in future releases, see git commit history.*
