from pathlib import Path
from typing import Dict

import pygame

from .settings import SOUNDS_DIR


class Audio:
    def __init__(self):
        self.available = False
        self.enabled = False
        self.master = 1.0
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        try:
            pygame.mixer.init()
            self.available = True
            self.enabled = True
        except pygame.error:
            self.available = False
            self.enabled = False
        if self.available:
            for path in Path(SOUNDS_DIR).glob("*.wav"):
                try:
                    self.sounds[path.stem] = pygame.mixer.Sound(str(path))
                except pygame.error:
                    pass

    def configure(self, enabled: bool = True, master: float = 1.0):
        self.enabled = self.available and enabled
        self.master = max(0.0, min(1.0, master))
        for sound in self.sounds.values():
            sound.set_volume(self.master)

    def play(self, name: str):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()
