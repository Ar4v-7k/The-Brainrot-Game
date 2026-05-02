# AI HELP HERE

If you are another coding agent opening this project, read this file first.

Project path:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon`

Main run command:

```bash
python3 main.py
```

Main asset regen command:

```bash
python3 tools/generate_assets.py
```

## What this game is right now

This is a heavily reworked Pygame monster-battler prototype called **Brainrotmon**.

The user wanted it pushed toward:

- Instagram-style premium monster game feel
- MoggMon / monster battler energy
- darker cleaner UI
- custom monster art
- idle animation
- custom move FX and projectiles
- less AI-smear, less blur, less broken cutouts

This copy is **not** a git repo right now, so this file is the project memory.

## Live roster right now

Only 3 brainrots are active on purpose:

1. `spaghettimon`
2. `tungtungsahur`
3. `ballerinacappuccina`

Creature data:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/creatures.py`

Do **not** bring back the old larger roster unless the user explicitly asks.

## Their 4 moves

### Spaghettimon

- `Fork Flick` -> `fork_flick`
- `Sauce Splash` -> `sauce_splash`
- `Al Dente Slam` -> `al_dente_slam`
- `Meatball Panic` -> `meatball_panic`

### Tungtung Sahur

- `Drum Knock` -> `drum_knock`
- `Sahur Burst` -> `sahur_burst`
- `Tung Roll` -> `tung_roll`
- `Midnight March` -> `midnight_march`

### Ballerina Cappuccina

- `Pirouette Pour` -> `pirouette_pour`
- `Foam Ribbon` -> `foam_ribbon`
- `Arabesque Roast` -> `arabesque_roast`
- `Finale Froth` -> `finale_froth`

## Important game files

Runtime:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/scenes.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/assets.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/battle.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/state.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/settings.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/idle_manifest.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/move_anim_manifest.py`

Tooling / asset pipeline:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/generate_assets.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/generate_move_anims.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/process_idle_strip.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/process_anim_strip.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/import_custom_assets.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/validate_battle_sprites.py`

## Asset buckets that matter

### Portraits

High-res cleaned portraits used in menus / roster:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/creatures`

Raw portrait sources:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/source_sheets/custom_v1/portraits`

### Idle strips

Processed idle frames:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/creature_anim`

Raw idle sources:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/source_sheets/custom_v1/idles`

Old archive:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/source_sheets/brainrot_idles_v7`

### Battle-sized idle sprites

These were added specifically to fix tiny-hole artifacts caused by shrinking giant idle frames at runtime:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/creature_battle`

Format:

- `{creature_key}_enemy_0..5.png`
- `{creature_key}_player_0..5.png`

### Move animation sprites

Processed move anim frames:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/move_anim`

These include:

- body frames
- effect frames
- projectile frames

Raw move strips:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/source_sheets/move_anims_v1`

### Runtime UI

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/runtime_ui`

## What was already fixed

### 1. The game structure

The project was pushed toward a battle-first runtime.

### 2. The UI

The battle UI was reworked to look more like a retro monster battler and less like a rough prototype.

### 3. Idle animation

All 3 live brainrots have 6-frame idle strips with 4 fps ping-pong timing.

### 4. Projectile art

Projectile move visuals were partially replaced using AI-generated image sheets, then sliced into per-move strips.

### 5. Bad cutouts / missing parts / random holes

This was a huge issue and several pipeline fixes were added:

- safer background flood fill
- gap-aware strip slicing
- edge-leak cleanup
- enclosed-hole filling
- battle-sized prebaked idle sprites

Core files for that work:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/process_idle_strip.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/process_anim_strip.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/import_custom_assets.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/generate_assets.py`

## Important visual truth

### Ballerina handle gap

Ballerina Cappuccina has a large cup-handle opening that is **intentional**.

Do not treat that as a cutout defect.

### Tiny hole bug

Most of the old random tiny holes were reduced by moving battle idle rendering onto prebaked battle-size sprites.

## Current known likely remaining problem

The user reported:

- when the player or enemy attacks, there is a black box around the character

Important:

- idle in battle now uses prebaked battle sprites from `assets/sprites/creature_battle`
- attack still uses move body frames from `assets/sprites/move_anim/*_body_*.png`

That means idle and attack are currently using different render paths.

This is the most likely reason the user still sees attack-time boxy / bad rendering.

## Most likely next fix

Create a new prebaked battle-sized **attack body** bucket too.

Recommended folder:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/move_body_battle`

Recommended format:

- `{move_key}_enemy_0..5.png`
- `{move_key}_player_0..5.png`

Then:

1. bake those from `move_anim/*_body_*.png`
2. load them in `game/assets.py`
3. use them in `game/scenes.py` during attack body playback

Keep effect/projectile render path unchanged unless needed.

## Current debug files worth checking

Folder:

- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tmp_debug`

Useful examples:

- `battle_sprite_preview.png`
- `roster_ballerinacappuccina.png`
- `spaghettimon_fork_flick_attack.png`
- `tungtungsahur_tung_roll_attack.png`
- move animation verification folders

## Useful commands

Regenerate assets:

```bash
python3 tools/generate_assets.py
```

Compile check:

```bash
python3 -m py_compile game/assets.py game/scenes.py tools/generate_assets.py
```

Battle sprite preview:

```bash
python3 tools/validate_battle_sprites.py
```

Launch game:

```bash
python3 main.py
```

## What the user cares about most

The user is very sensitive to:

- blurry sprites
- broken cutouts
- black boxes
- reused generic animation
- things still looking AI-generated in a bad way

The user likes:

- Instagram reference feel
- cleaner high-quality monster art
- custom animation identity
- agents leaving detailed context for future agents

## Short next-agent checklist

If you are taking over:

1. reproduce the current issue in battle
2. inspect attack body render path
3. prebake attack body frames at battle size
4. route attack playback to those baked frames
5. re-run asset generation
6. re-launch and save new debug previews

