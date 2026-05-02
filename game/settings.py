from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"
SPRITES_DIR = ASSETS_DIR / "sprites"
SOUNDS_DIR = ASSETS_DIR / "sounds"
SAVE_DIR = BASE_DIR / "saves"

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
VIRTUAL_WIDTH = 384
VIRTUAL_HEIGHT = 216
RENDER_SCALE = 3

# Compatibility aliases for older tooling.
SCREEN_WIDTH = WINDOW_WIDTH
SCREEN_HEIGHT = WINDOW_HEIGHT

FPS = 60
TITLE = "Brainrotmon"

VIEWPORT_WIDTH = VIRTUAL_WIDTH * RENDER_SCALE
VIEWPORT_HEIGHT = VIRTUAL_HEIGHT * RENDER_SCALE
VIEWPORT_X = (WINDOW_WIDTH - VIEWPORT_WIDTH) // 2
VIEWPORT_Y = (WINDOW_HEIGHT - VIEWPORT_HEIGHT) // 2

COLORS = {
    "matte": (32, 39, 55),
    "bg_top": (124, 190, 220),
    "bg_bottom": (86, 151, 109),
    "sky": (118, 188, 224),
    "cloud": (242, 244, 225),
    "field_dark": (74, 132, 68),
    "field_mid": (116, 177, 82),
    "field_light": (164, 214, 104),
    "sand": (222, 196, 117),
    "panel": (248, 239, 194),
    "panel_2": (230, 220, 172),
    "panel_3": (91, 117, 176),
    "stroke": (38, 45, 69),
    "stroke_dim": (93, 101, 121),
    "gold": (226, 176, 68),
    "red": (204, 74, 78),
    "green": (78, 157, 75),
    "blue": (70, 126, 203),
    "teal": (65, 160, 170),
    "cream": (255, 248, 215),
    "white": (255, 255, 255),
    "black": (16, 20, 30),
    "shadow": (41, 35, 36),
    "ink": (25, 28, 42),
    "select": (246, 216, 84),
    "signal": (104, 185, 85),
    "violet": (116, 83, 164),
}
