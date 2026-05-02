from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from .settings import SAVE_DIR
from .state import AdventureState, ProfileState, RunState, SaveBundle, SettingsState


class Storage:
    def __init__(self, save_dir: Path = SAVE_DIR):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.profile_path = self.save_dir / "profile.json"

    def slot_path(self, slot: int) -> Path:
        return self.save_dir / f"slot_{slot}.json"

    def adventure_slot_path(self, slot: int) -> Path:
        return self.save_dir / f"adventure_slot_{slot}.json"

    def load_bundle(self) -> SaveBundle:
        if not self.profile_path.exists():
            return SaveBundle()
        payload = json.loads(self.profile_path.read_text())
        return SaveBundle(
            settings=SettingsState.from_dict(payload.get("settings")),
            profile=ProfileState.from_dict(payload.get("profile")),
        )

    def save_bundle(self, bundle: SaveBundle) -> None:
        self.profile_path.write_text(json.dumps(bundle.to_dict(), indent=2))

    def load_run(self, slot: int) -> Optional[RunState]:
        path = self.slot_path(slot)
        if not path.exists():
            return None
        payload = json.loads(path.read_text())
        return RunState.from_dict(payload)

    def save_run(self, run: RunState) -> None:
        run.normalize()
        self.slot_path(run.slot).write_text(json.dumps(run.to_dict(), indent=2))

    def delete_run(self, slot: int) -> None:
        path = self.slot_path(slot)
        if path.exists():
            path.unlink()

    def list_slots(self) -> Dict[int, Optional[RunState]]:
        return {slot: self.load_run(slot) for slot in (1, 2, 3)}

    def load_adventure(self, slot: int) -> Optional[AdventureState]:
        path = self.adventure_slot_path(slot)
        if not path.exists():
            return None
        payload = json.loads(path.read_text())
        return AdventureState.from_dict(payload)

    def save_adventure(self, adventure: AdventureState) -> None:
        adventure.normalize()
        self.adventure_slot_path(adventure.slot).write_text(json.dumps(adventure.to_dict(), indent=2))

    def delete_adventure(self, slot: int) -> None:
        path = self.adventure_slot_path(slot)
        if path.exists():
            path.unlink()

    def list_adventure_slots(self) -> Dict[int, Optional[AdventureState]]:
        return {slot: self.load_adventure(slot) for slot in (1, 2, 3)}
