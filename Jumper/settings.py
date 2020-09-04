# game options/settings
TITLE = "Save Bertrand !"
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'arial'
HS_FILE = 'highscore.txt'
SPRITESHEET = 'spritesheet_jumper.png'

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)
BGCOLOR = LIGHTBLUE

# Player properties
PLAYER_ACC = .5
PLAYER_FRICTION = -.12
PLAYER_GRAVITY = .8
PLAYER_JUMP = 18.5

# Game properties
SPRING_BOOST = 50
JETPACK_BOOST = 18
JETPACK_DURABILITY = 3000
SHIELD_DURABILITY = 6000
MOB_SPAWN = 5000
CLOUD_SPAWN = 15
PLAYER_LAYER = 6
PLATFORM_LAYER = 2
POW_LAYER = 1
ACTIVATED_POW_LAYER = 4
MOB_LAYER = 3
CLOUD_LAYER = 0

# Starting platforms
PLATFORM_LIST = [(0, HEIGHT - 60), (WIDTH / 2 -50, HEIGHT * 3 / 4 - 50),
                 (125, HEIGHT - 350), (350, 200), (175, 100)]
