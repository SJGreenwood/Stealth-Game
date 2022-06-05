import pygame

# Window variables setup
FPS = 60

# Basic colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (47, 149, 208)
ORANGE = (166, 74, 15)

# Use the display resolution to size the window
pygame.init()
displayInfo = pygame.display.Info()
WIDTH = int(displayInfo.current_w * 2 / 3)
HEIGHT = int(displayInfo.current_h * 2 / 3)

TILESIZE = 64
CHARACTER_SPEED = 75
FLOOR_FRICTION = 0.6

CHARACTER_COL_RECT = pygame.Rect(0, 0, TILESIZE*3/4, TILESIZE*3/4)