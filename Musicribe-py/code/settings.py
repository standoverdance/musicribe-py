
WIDTH   = 1280
HEIGHT  = 720
FPS     = 50

OFFSET_Y = 200
BASEPOS = (WIDTH / 15, HEIGHT - OFFSET_Y)



PLAYER_SIZE = (158, 158)
HEALTH_BAR_SIZE = (30, HEIGHT - OFFSET_Y)
KEY_COOLDOWN = 5

UI_Font = '../font/bahnschrift.ttf'

SPEED = 1
#DEATH_MATCH = True
NO_DEATH = False
HIDDEN_LETTERS = False
KILL_ON_MISS = False
NO_BOX_NO_KILL = False
WHATEVER_LETTER = False
SPACE_LOCK = 0 #Space 0: Spaces have to be pressed to the rhythm. Space 1: (Does not add combo if without rhythm) But without rhythm is allowable  Space: 2 or above the spaces are automatically skipped 
#/// Space 0 no code. / Space 1 in level press event / Space > 1 in lettertype

# /// Accuracy in conductor.checkaccuracy()
