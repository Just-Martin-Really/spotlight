# Spotlight — WOW Mode TODO (Game Show Edition)

> Status: **Planning + in-progress** (do not commit yet)
> Goal: Make Spotlight *obviously* better than PowerPoint by turning it into a live game show runner.

---

## Definition of WOW (what the audience/presenter sees)

### Always-on overlays
- [ ] **Scoreboard overlay** (teams + scores) visible on every task screen
- [ ] **Buzz-in overlay** (OPEN / LOCKED + winner highlight)
- [ ] **Round timer overlay** (stopwatch + optional countdown)

### Controls (single laptop)
- [ ] `1..4`: add points to team
- [ ] `SHIFT+1..4`: subtract points
- [ ] `B`: open buzz-in
- [ ] `1..4` while open: buzz (locks to first)
- [ ] `R`: reset buzz
- [ ] `SPACE`: start/pause timer
- [ ] `BACKSPACE`: reset timer
- [ ] `C`: clear all scores (confirm?)
- [ ] `S`: save snapshot to disk
- [ ] `L`: load snapshot from disk
- [ ] `H`: show help overlay (controls cheat-sheet)

### Visual flair
- [ ] Score pop animation when changed
- [ ] Winner highlight pulse / glow
- [ ] Optional sound effects (buzz, score +, score -) — behind a setting flag
- [ ] “Round summary” interstitial screen (optional)

---

## Non-functional requirements
- [ ] **Deterministic core tests**: scoring rules, timer math, buzz lock logic, persistence
- [ ] UI rendering changes should be minimal and centralized (prefer BaseRenderer overlays)
- [ ] No network required (offline reliability). No secrets.

---

## Architecture sketch (contracts)

### New model: `GameState`
- Inputs:
  - key commands (score +/-, buzz controls, timer controls)
  - time source (injectable for tests; default pygame ticks)
- Outputs:
  - team scores (list[int])
  - buzz state: CLOSED/OPEN/LOCKED + winning team idx
  - timer state: running/paused + elapsed_ms (+ optional target_ms)
- Error modes:
  - invalid team index → ignore
  - persistence read errors → keep current state and show status

### Persistence
- File: `data/game_state.json` (or `data/snapshots/game_state.json`)
- Save shape:
  - teams: [{name, score}]
  - timer: {mode, elapsed_ms, running}
  - buzz: {state, locked_team}
  - version

---

## Implementation milestones

### Milestone 1 — Core state + tests (no UI yet)
- [ ] Add `src/models/game_state.py`
- [ ] Add unit tests `tests/test_game_state.py`
  - [ ] score add/subtract
  - [ ] buzz open/lock/reset
  - [ ] timer start/pause/reset with injected clock
  - [ ] persistence serialize/deserialize

### Milestone 2 — Input routing
- [ ] Extend `config/keybindings.py` with game-show keys
- [ ] Update `src/controllers/input_controller.py` to emit command objects (not just bool)
  - [ ] Keep backward compat: still allow quit/prev/next

### Milestone 3 — Overlay rendering
- [ ] Add overlay renderer helper: `src/views/overlays.py`
  - [ ] scoreboard
  - [ ] timer
  - [ ] buzz state
  - [ ] transient status messages (e.g., "Saved")
- [ ] Hook overlay rendering into `BaseRenderer.render()` or `BaseRenderer._render_footer()`
  - [ ] Prefer drawing overlays *after* `render_content()` so they’re always visible

### Milestone 4 — Application integration
- [ ] `Application` owns `GameState` instance
- [ ] Apply input commands each frame
- [ ] Force redraw/transition consistency when overlay changes

### Milestone 5 — Polish / wow
- [ ] Animations for score changes / buzz lock
- [ ] Sounds (optional)
- [ ] Help overlay on `H`

---

## Files likely touched
- `src/models/game_state.py` (new)
- `src/models/__init__.py` (maybe export)
- `src/controllers/input_controller.py`
- `config/keybindings.py`
- `src/views/base_renderer.py`
- `src/views/*_renderer.py` (minimal or none; prefer central overlay)
- `src/core/application.py`
- `tests/test_game_state.py` (new)
- `tests/test_renderer_utils.py` (keep existing)

---

## Open decisions (default assumptions)
- Teams default: 4 teams: A/B/C/D
- Point delta default: +1 / -1 (might add +/-5 keys later)
- Timer default: stopwatch
- Persistence default file: `data/game_state.json`

---

## Verification commands
```zsh
python -m pytest -q
python main.py
```

