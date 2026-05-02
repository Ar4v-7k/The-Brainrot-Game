# Brainrotmon Handoff: Chat History + Pain Points

## Purpose

This file is big on purpose.

User wants open new chat and keep most useful history, especially:
- what was asked
- what was tried
- what kept going wrong
- what quality bar user actually wants
- what current live state is
- what future agent should preserve

This file should let another agent jump in without reading whole old thread.

## Core User Taste / Quality Bar

User wants game art and animation to feel closer to:
- Instagram reference they kept mentioning earlier
- later: official GitHub/game reference feel
- most importantly for current roster style: close to quality/vibe of these 4 brainrots:
  - `Bombardiro Crocodilo`
  - `Frigo Camelo`
  - `Brr Brr Patapim`
  - `Chimpanzini Bananini`

When user says:
- "like before"
- "same quality"
- "same style"

they usually mean:
- chunky crisp pixel art
- cleaner silhouette
- less obvious AI-smear
- more premium meme-monster finish
- stable anatomy across frames
- not blurry
- not muddy
- not weirdly over-rendered

## Communication Preference

User often asks for:
- caveman mode
- less tokens
- fast work

So terse updates good.

But actual implementation should still be careful.

## Big Repeated User Requirements

These came up many times:

1. **Each brainrot needs custom idle animation**
   - not only float up/down
   - real frame-based idle
   - around `4 fps`
   - clear at gameplay size

2. **Each brainrot needs 4 unique moves**
   - not generic move pool feel
   - move names tied to creature identity

3. **Each move needs its own custom attack animation**
   - user means actual sprite frames, not only code motion
   - not shared generic slash/burst only

4. **If move shoots projectile, projectile also needs custom animation**
   - user explicitly repeated this many times
   - projectile should not be generic fallback if avoidable

5. **Move body animation must actually show in game**
   - major prior bug: assets existed on disk but not shown live

6. **No blur**
   - user very sensitive to blurry creatures

7. **No obvious AI-generated feel**
   - user dislikes smeary, muddy, over-detailed, unstable outputs

8. **Auto-open / relaunch game after changes**
   - user repeatedly asked for this

## Very Important User Frustrations

These were pain points that caused repeated dissatisfaction:

### A. Fake animation vs real animation

User often rejected:
- code-only bobbing
- lunge motion without real sprite changes
- generic shared fx reused across many moves

User wanted:
- real frame sequences
- per-move sprite art
- per-projectile sprite art

### B. “You only changed idle”

This happened multiple times.

Pattern:
- new brainrot art got upgraded
- but move body/projectile art stayed old or procedural
- user noticed immediately

Lesson:
- if adding/reworking a brainrot, verify:
  - portrait
  - idle frames
  - move body frames
  - projectile frames where needed
  - live code path actually uses them

### C. Assets existed but game still did not show them

Happened on new move anim pass.

Root cause:
- move body frames were present in `assets/sprites/move_anim`
- but battle scene was not passing those frames into `draw_creature`
- result: user saw no custom attack animation in-game

Fix that was made:
- `game/scenes.py` now passes per-move `body` frames into creature attack draw path
- old duplicate body overlay path removed because it caused ghost/trail issues

### D. Wrong-facing and bad lunge behavior

User repeatedly complained:
- some creatures faced wrong direction
- contact moves did not get close enough
- lunges looked fake or stood still

Important history:
- several fixes tried
- eventually per-creature facing map / lunge tuning added
- but this area remains sensitive; verify in live game after any major move-art change

### E. Cutout / hole / black box issues

Several image pipeline bugs happened:
- internal holes in creatures
- neighboring-frame bleed
- black opaque box during attacks

Known causes and fixes:

1. **Cutout holes / missing parts**
   - caused by aggressive bg removal and big-frame downscaling artifacts
   - improved via:
     - safer flood-fill bg removal
     - gap-aware slicing
     - hole fill
     - prebaked battle-sized sprites

2. **Black box around attacker**
   - attack-body frames were generated from portraits carrying opaque black background
   - cleaned in move anim generation pipeline

### F. Old save/profile data still showing removed creatures

At one point user asked remove 5 brainrots.
Code refs were removed, but they still appeared in game because:
- `saves/profile.json` still contained them in `seen` / `unlocked`

Lesson:
- roster removals may need both:
  - code/data removal
  - save/profile cleanup

## Current Project Location

Main workspace:
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon`

## Current Important Files

Gameplay / runtime:
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/main.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/scenes.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/battle.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/assets.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/creatures.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/idle_manifest.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/move_anim_manifest.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/state.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/game/storage.py`

Save/profile:
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/saves/profile.json`

Important tooling:
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/process_idle_strip.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/process_anim_strip.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/generate_assets.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/generate_move_anims.py`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/tools/import_custom_assets.py`

## Important Asset Buckets

Source sheets:
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/source_sheets/brainrot_idles_v7`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/source_sheets/custom_v1/attacks`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/source_sheets/move_anims_v1/body`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/source_sheets/move_anims_v1/projectile`

Live assets:
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/creatures`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/creature_anim`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/creature_battle`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/move_anim`

## Current Roster History

### Original 3 polished core

These were early focus creatures:
- `spaghettimon`
- `tungtungsahur`
- `ballerinacappuccina`

These got lots of polishing first:
- portrait
- idle
- moves
- custom move fx

### Later popular additions

Added later:
- `tralalerotralala`
- `cappuccinoassassino`
- `vaccasaturnosaturnita`
- `bombardirocrocodilo`
- `frigocamelo`
- `brrbrrpatapim`
- `chimpanzinibananini`
- `raviolord`
- `salsicciator`
- `crostinoboss`
- `bruschettank`
- `mozzarellion`
- `pizzaratto`
- `lasagnaconda`
- `gelatitan`
- `polentazilla`
- `macaronocchio`

### Removal + restore history

At one point user asked remove:
- `pizzaratto`
- `lasagnaconda`
- `gelatitan`
- `polentazilla`
- `macaronocchio`

They were removed from:
- code data
- manifests
- battle timings

Then user asked bring them back, but with art quality closer to:
- `Bombardiro Crocodilo`
- `Frigo Camelo`
- `Brr Brr Patapim`
- `Chimpanzini Bananini`

So they were restored with:
- new idle strips
- new portraits
- later new move body strips
- later new projectile strips

## Current Most Important Style References

These files are good practical style anchors:

Source idle sheets:
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/source_sheets/brainrot_idles_v7/bombardirocrocodilo.png`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/source_sheets/brainrot_idles_v7/frigocamelo.png`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/source_sheets/brainrot_idles_v7/brrbrrpatapim.png`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/source_sheets/brainrot_idles_v7/chimpanzinibananini.png`

Portrait refs:
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/creatures/bombardirocrocodilo.png`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/creatures/frigocamelo.png`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/creatures/brrbrrpatapim.png`
- `/Users/aravsharma/Documents/The Brainrot Game/brainrotmon/assets/sprites/creatures/chimpanzinibananini.png`

These are what user meant when saying:
- “make 5 now in that style”
- “same quality”
- “like before”

## Current State of 5 Restored Brainrots

These 5 now exist again:
- `pizzaratto`
- `lasagnaconda`
- `gelatitan`
- `polentazilla`
- `macaronocchio`

They currently have:
- restored creature defs
- restored idle manifest entries
- restored move anim manifest entries
- restored move visuals
- restored battle timing entries
- restored profile unlock/seen entries
- fresh imagegen idle strips in style closer to good reference 4
- live portraits rebuilt from new idle strips
- battle idle frames rebuilt
- fresh per-move `body` strips
- fresh projectile strips for projectile moves

Projectile moves for those 5:
- `crust_comet`
- `mozza_mob`
- `ricotta_rattle`
- `bake_coil`
- `frost_swirl`
- `brain_freeze`
- `golden_roar`
- `polenta_meteor`
- `ganache_glint`
- `marzipan_mirage`

Non-projectile moves for those 5:
- `scurry_slice`
- `oven_ambush`
- `layer_lash`
- `coil_crush`
- `scoop_smack`
- `sundae_slide`
- `kernel_kick`
- `corn_quake`
- `string_sting`
- `puppet_pivot`

## Current Pain Point Likely Still Relevant

Very likely next pain point:
- user may still dislike these `5` if only body/projectile changed but effect strips still older/generic

Important nuance:
- in latest fast pass, fresh move **body** strips and fresh **projectile** strips were generated for restored 5
- existing **effect** frames for these 5 were kept

If user says:
- still not like before
- effects wrong
- still generic

then likely next step:
- regenerate fresh `effect` strips too for those `5`

## Timeline of Big Technical Changes

### 1. Evolution scaffolding

Added earlier:
- `EvolutionDef`
- optional evolution on creatures
- state hooks for evolved forms

Mostly not active yet.

### 2. Huge asset/style pass

Non-brainrot UI / tiles / player art got reworked earlier.

### 3. Brainrot portrait pass

Lots of creature portraits remade over time.

### 4. Idle animation rebuild

Eventually moved from:
- fake bobbing

to:
- real idle frame strips

Then:
- battle-sized prebaked sprites introduced to avoid downscale artifacts / tiny holes

### 5. Move animation system

Move pipeline evolved from:
- generic fx
- code motion only

to:
- `move_anim/<move_key>_body_*.png`
- `move_anim/<move_key>_effect_*.png`
- `move_anim/<move_key>_projectile_*.png`

### 6. Battle render bug fix

Important fix:
- `game/scenes.py` now passes current move body frames into `draw_creature`
- before this, custom move body anims could exist but never render

### 7. Roster save cleanup

Important save fix:
- `saves/profile.json` can preserve removed creatures in `seen`/`unlocked`

## Current Known Good Commands

Compile:
```bash
python3 -m py_compile /Users/aravsharma/Documents/The\ Brainrot\ Game/brainrotmon/game/creatures.py /Users/aravsharma/Documents/The\ Brainrot\ Game/brainrotmon/game/idle_manifest.py /Users/aravsharma/Documents/The\ Brainrot\ Game/brainrotmon/game/move_anim_manifest.py /Users/aravsharma/Documents/The\ Brainrot\ Game/brainrotmon/game/scenes.py /Users/aravsharma/Documents/The\ Brainrot\ Game/brainrotmon/game/battle.py
```

Launch:
```bash
python3 /Users/aravsharma/Documents/The\ Brainrot\ Game/brainrotmon/main.py
```

## Important Processing Caveats

### `process_anim_strip.py` / `process_idle_strip.py`

These use pygame display init internally.

In long scripts:
- pygame display state may die between calls
- needed workaround was often:
  - `pygame.init()`
  - `pygame.display.init()`
  - `pygame.display.set_mode((1,1))`
  - re-run between processing calls

### Large scripts

Long monolithic scripts sometimes felt stuck.

Safer:
- staged scripts
- visible progress prints

## Generated Image Path Convention

Built-in `image_gen` outputs defaulted under:
- `/Users/aravsharma/.codex/generated_images/...`

Important:
- project-bound assets should be copied into repo afterward
- do not leave only in generated_images path

## Latest Fast Workflow That Worked

For speed while keeping decent quality:

1. Generate fresh idle strip per creature with `image_gen`
2. Copy into:
   - `assets/source_sheets/brainrot_idles_v7/<key>.png`
3. Process into live idle frames with `process_idle_strip.py`
4. Rebuild portrait from `idle_0`
5. Rebuild battle idle bakes
6. Generate 4-row move body sheet per creature
7. Slice rows into per-move body source strips
8. Process into:
   - `assets/sprites/move_anim/<move>_body_0..5.png`
9. Generate 2-row projectile sheets for projectile moves
10. Slice and process into:
   - `assets/sprites/move_anim/<move>_projectile_0..5.png`

This was much faster than fully custom one-call-per-move asset generation.

## Current Likely Future Requests

Based on history, user may soon ask for one of:

1. Make move **effect** strips fresh too for restored 5
2. Polish one ugly move one-by-one
3. Add more brainrots
4. Remove some again
5. Match style even more tightly to specific favorites
6. Fix any live combat bug after new asset wiring

## If New Agent Continues Work

Best default assumptions:

- user values speed but hates fake shortcuts
- if you say custom animation, user expects actual sprite frames
- projectile moves need projectile frames
- if move art exists but not visible in-game, user will catch it fast
- user dislikes blur
- user dislikes AI-smear
- user wants game relaunched after edits

## Most Recent Important Change Before This File

Restored `5` removed brainrots with:
- fresh idle art in better style
- fresh move body strips
- fresh projectile strips
- live game relaunched

Those 5:
- `Pizzaratto`
- `Lasagnaconda`
- `Gelatitan`
- `Polentazilla`
- `Macaronocchio`

If user says “still wrong” next, first check:
- are fresh body strips actually visible in-game
- are projectile strips visible in-game
- are effect strips still older generic ones
- does save/profile roster reflect intended live roster

## Short Summary For New Agent

User wants premium meme-monster pixel battler.

Biggest repeated pain:
- fake/shared animation instead of true per-move sprite animation
- blurry / AI-looking art
- assets generated but not wired live
- roster removal not reflected in saves

Current good style anchors:
- Bombardiro / Frigo / Brr / Chimp source sheets and portraits

Current live work hotspot:
- battle animation pipeline in `game/scenes.py`
- creature/move data in manifests
- source sheet processing scripts

