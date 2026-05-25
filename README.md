# Bone Hunt: Beneath the Surface

A small browser game (single-file HTML/CSS/JS) wrapped by a Python writer script.

Overview
- Control a dog and dig for hidden buried bones.
- Bones are invisible on the map. Use the proximity indicator to find them.
- Win by collecting 10 bones. Touching enemies costs a life.

Files
- `bone_hunt.py` — Python script that writes `bone_hunt.html` and opens it in your browser.
- `bone_hunt.html` — The generated single-file web game (HTML + CSS + JS).

How to run
- Generate and open the game (recommended):

```bash
python3 bone_hunt.py
```

- Or open the generated file directly in a browser:

```bash
open bone_hunt.html   # macOS
# or double-click the file in Finder
```

Controls
- Move: WASD or Arrow keys
- Dig: SPACE (or click/tap on canvas)
- Restart: R

Gameplay details
- Map size: 800 x 500 px
- Bones are placed at random hidden coordinates. Digging (SPACE) near one will reveal and collect it.
- Proximity indicator: shows a status of Far / Close / Very Close and a scent meter to guide you toward bones.
- Enemies (cats/traps) move around; touching one reduces a life. Game over at 0 lives.
- Win condition: collect 10 bones.

CSP programming elements (mapping)
- Arrays used: `bones` (hidden bone objects), `enemies` (moving enemies), and `particles` (dig effects).
- Key functions (present in code):
  - `movePlayer()` — updates player position from input.
  - `digBone()` — handles digging, collection, and particle effects.
  - `spawnBone()` — places a new hidden bone.
  - `updateScentMeter()` — computes nearest bone distance and updates the HUD.
  - `checkCollision()` — checks and responds to collisions with enemies.
  - `restartGame()` — resets game state and spawns initial bones/enemies.
- Variables present: `score`, `playerX`, `playerY`, `lives`, `gameRunning`.
- Loops and conditionals: used throughout for movement, updates, and distance checks (if/else).

Tuning & edits
- To make bones easier/harder: change `BONE_DETECT_DIST` in the JS.
- To change hint cutoffs or colors: edit the `updateScentMeter()` logic.

Troubleshooting
- If the HTML does not open automatically, run `python3 bone_hunt.py` or open `bone_hunt.html` manually.
- If keys don't respond, ensure the page has focus (click the canvas).

License
- Use freely for learning and classroom demonstration.

If you'd like, I can:
- Add sound effects, pause menu, or high-score saving.
- Extract the HTML into separate files instead of a single generated file.
- Tune difficulty or change wording/visuals.

