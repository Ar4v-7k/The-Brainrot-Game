# Brainrotmon

A retro dark-modern monster RPG set in Rotria, with overworld exploration, story chapters, badges, quests, berries, trainer battles, wild encounters, bosses, and a full Brainrotmon roster.

## Run

```bash
cd "/Users/aravsharma/Documents/New project/brainrotmon"
python3 -m pip install -r requirements.txt
python3 main.py
```

Run `python3 tools/generate_assets.py` after roster or asset-pipeline changes.

## Controls

- Arrow keys or WASD: move/select
- Enter or Space: confirm
- Escape or C: back/open adventure menu
- M: zoomable Rotria map
- B: bag
- P: party
- D: Brainrotdex
- Q: quests
- J: badges/journal
- On the map: +/- zoom, arrows/WASD pan, Tab cycles POIs, R resets
- In the overworld, Enter/Space interacts with NPCs, signs, berry trees, shops, healers, and visible Brainrotmon.

## Notes

The new adventure path uses `adventure_slot_*.json` saves. Old wave-run saves are left alone for backup/debug compatibility.

`tools/generate_assets.py` also builds the retro overworld runtime set: a 1024-tile `assets/sprites/overworld/tileset.png`, `tileset_index.json`, and player/NPC walking sprites.
