import os
from pathlib import Path

abspath = os.path.dirname(os.path.abspath(__file__))

WIDTH   = 1280
HEIGHT  = 720
FPS     = 50

OFFSET_Y = 200
BASEPOS = (WIDTH / 15, HEIGHT - OFFSET_Y)

PLAYER_SIZE = (158, 158)
HEALTH_BAR_SIZE = (30, HEIGHT - OFFSET_Y)
KEY_COOLDOWN = 5
SPEED = 1

# Dependencies (Based on the playersize, basepos etc.)
PERFECT_LINE_POSITION = int(BASEPOS[1]) + int(PLAYER_SIZE[1])

if SPEED < 1:
    LOADING_TIME = 1750 * (1/SPEED) # In milliseconds, block of rhythm objects that should load.
else:
    LOADING_TIME = 1750

# Paths to fonts
UI_Font = os.path.join(abspath, '..', 'font', 'bahnschrift.ttf')
Oxanium_Font = os.path.join(abspath, '..', 'font', 'Oxanium-VariableFont_wght.ttf')

# Variables for the game modifiers.
class Modifiers:
    DEATH_MATCH = False
    NO_DEATH = False
    HIDDEN_LETTERS = False
    KILL_ON_MISS = False
    WHATEVER_LETTER = False
    SPACE_LOCK = 0
    SLIDERS_TURNED_ON = True
