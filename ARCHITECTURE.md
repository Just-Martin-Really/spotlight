# TIA25 Spotlight - Architecture Overview

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py                                  │
│                      (Entry Point)                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ Creates & runs
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Application (Facade)                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Responsibilities:                                          │ │
│  │ - Initialize pygame                                        │ │
│  │ - Load tasks via TaskLoader                                │ │
│  │ - Create Session                                           │ │
│  │ - Create InputController                                   │ │
│  │ - Initialize Renderers (Factory)                           │ │
│  │ - Run game loop                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────┬──────────────┬──────────────┬──────────────────────────┘
        │              │              │
        │              │              │
        ▼              ▼              ▼
   ┌────────┐    ┌─────────┐    ┌──────────┐
   │ Session│    │  Input  │    │ Renderer │
   │        │    │Controller│    │ Factory  │
   └────┬───┘    └────┬────┘    └────┬─────┘
        │             │              │
        │             │              │
        ▼             ▼              ▼
```

## Data Flow - Single Frame

```
1. INPUT
   ┌──────────────────┐
   │ User presses →   │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ InputController          │
   │ - Handles pygame events  │
   │ - Maps key to action     │
   └────────┬─────────────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ Session.next_task()      │
   │ - Updates current_index  │
   └────────┬─────────────────┘
            │
2. RENDER  │
            ▼
   ┌──────────────────────────┐
   │ Application._render()    │
   │ - Get current task       │
   │ - Select renderer        │
   └────────┬─────────────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ Renderer (QuizRenderer,  │
   │ TabuRenderer, etc.)      │
   │ - Render task content    │
   │ - Add header/footer      │
   └────────┬─────────────────┘
            │
            ▼
   ┌──────────────────────────┐
   │ pygame.display.flip()    │
   │ - Show on screen         │
   └──────────────────────────┘
```

## Module Responsibilities

```
┌─────────────────────────────────────────────────────────────┐
│                        CONFIG                                │
├─────────────────────────────────────────────────────────────┤
│ settings.py      │ Visual configuration (colors, fonts)     │
│ keybindings.py   │ Keyboard mapping                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                         DATA                                 │
├─────────────────────────────────────────────────────────────┤
│ tasks.json       │ External task database                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        MODELS                                │
├─────────────────────────────────────────────────────────────┤
│ task.py          │ Task data structures (QuizTask, etc.)    │
│ session.py       │ Session state (current index, tasks)     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       SERVICES                               │
├─────────────────────────────────────────────────────────────┤
│ task_loader.py   │ JSON → Task objects                      │
│ renderer_utils.py│ Text wrapping, centering helpers         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     CONTROLLERS                              │
├─────────────────────────────────────────────────────────────┤
│ input_controller.py │ Pygame events → Session actions       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        VIEWS                                 │
├─────────────────────────────────────────────────────────────┤
│ base_renderer.py     │ Shared rendering infrastructure      │
│ quiz_renderer.py     │ Quiz task layout                     │
│ tabu_renderer.py     │ Tabu task layout                     │
│ discussion_renderer.py│ Discussion task layout              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                         CORE                                 │
├─────────────────────────────────────────────────────────────┤
│ application.py   │ Main loop, orchestration                 │
└─────────────────────────────────────────────────────────────┘
```

## Design Patterns Applied

### 1. MVC (Model-View-Controller)
- **Model**: Task dataclasses, Session state
- **View**: Renderer classes
- **Controller**: InputController

### 2. Factory Pattern
- **TaskFactory**: Creates appropriate Task subclass from JSON
- **Renderer Factory**: Maps task type → renderer instance

### 3. Template Method
- **BaseRenderer**: Defines render() skeleton
- **Subclasses**: Override render_content() for custom layout

### 4. Facade Pattern
- **Application**: Single interface to entire system
- Hides complexity of subsystem interactions

### 5. Dependency Injection
- Configuration imported, not hardcoded
- Session passed to InputController
- Screen passed to Renderers

## Adding New Task Types - Step by Step

```
1. DATA MODEL
   └─ src/models/task.py
      └─ Create NewTaskType(BaseTask) dataclass

2. FACTORY REGISTRATION
   └─ src/models/task.py
      └─ Add to TaskFactory._TASK_CLASSES

3. RENDERER
   └─ src/views/new_task_renderer.py
      └─ Create NewTaskRenderer(BaseRenderer)
      └─ Implement render_content()

4. APPLICATION
   └─ src/core/application.py
      └─ Add to _init_renderers() mapping

5. CONFIG (Optional)
   └─ config/settings.py
      └─ Add task-specific colors/settings

6. DATA
   └─ data/tasks.json
      └─ Add example task with "type": "newtype"
```

## File Dependencies

```
main.py
 └─ Application
     ├─ TaskLoader
     │   └─ TaskFactory
     │       └─ Task models
     ├─ Session
     │   └─ Task models
     ├─ InputController
     │   ├─ Session
     │   └─ keybindings
     └─ Renderers
         ├─ BaseRenderer
         │   ├─ settings
         │   └─ renderer_utils
         └─ Task-specific renderers
             └─ Task models
```

## Runtime Flow

```
Startup:
  1. main.py imports Application
  2. Application.__init__()
  3. Application.run()
     ├─ _initialize()
     │   ├─ pygame.init()
     │   ├─ TaskLoader.load_tasks()
     │   ├─ Session(tasks)
     │   ├─ InputController(session)
     │   └─ _init_renderers()
     ├─ _game_loop()
     │   └─ while running:
     │       ├─ InputController.handle_events()
     │       ├─ _render_frame()
     │       │   ├─ session.current_task()
     │       │   ├─ renderers[task.type]
     │       │   └─ renderer.render(task, position)
     │       ├─ pygame.display.flip()
     │       └─ clock.tick(FPS)
     └─ _cleanup()
         └─ pygame.quit()
```

---

This architecture ensures:
- **Separation of Concerns** - Each module has one job
- **Testability** - Components can be tested in isolation
- **Extensibility** - New features plug in cleanly
- **Maintainability** - Clear structure, easy to navigate
