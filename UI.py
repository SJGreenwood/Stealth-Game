import pygame

from settings import *

class Minimap:
    def __init__(self, mapImg, size, scale, playerColour, playerSize, outlineColour, outlineSize, bgColour):
        self.minimap = mapImg.copy()

        self.mapSize = mapImg.get_size()

        self.minimap = pygame.transform.scale(self.minimap, (int(self.mapSize[0]*scale), int(self.mapSize[1]*scale)))

        self.circleMask = pygame.Surface((size, size))
        pygame.draw.circle(self.circleMask, WHITE, (size/2, size/2), size/2)

        self.minimapFrame = pygame.Surface((size, size))
        self.minimapFrame.set_colorkey(BLACK)

        self.size = size
        self.scale = scale

        self.playerColour = playerColour
        self.playerSize = playerSize

        self.outlineColour = outlineColour
        self.outlineSize = outlineSize

        self.bgColour = bgColour

        self.screenPosition = (WIDTH - size - 20, 15)

    def update(self, playerPos):
        """Assemble the minimap for this frame"""

        offset = [(playerPos[0] * self.scale), (playerPos[1] * self.scale)]

        # Clear the previous frame
        self.minimapFrame.fill(BLACK)
        # Draw the map onto the minimap
        self.minimapFrame.blit(self.minimap, (self.size/2 - offset[0], self.size/2 - offset[1]))
        # Turn the square surface into a circle
        self.minimapFrame.blit(self.circleMask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # Draw the character onto the minimap
        pygame.draw.circle(self.minimapFrame, self.playerColour, (self.size/2, self.size/2), self.playerSize)

        # Draw a 10px outline onto the minimap
        pygame.draw.circle(self.minimapFrame, self.outlineColour, (self.size/2, self.size/2), self.size/2, self.outlineSize)

    def draw(self, surface):
        # Draw the minimap backing onto the screen
        pygame.draw.circle(surface, self.bgColour, (self.screenPosition[0] + self.size/2, self.screenPosition[1] + self.size/2), self.size/2)

        # Draw the minimap onto the screen
        surface.blit(self.minimapFrame, self.screenPosition)

class Text:
    def __init__(self, text, size):
        # Segoe UI
        font = pygame.font.SysFont("Segoe UI", size)
        self.image = font.render(text, True, WHITE)
        self.rect = self.image.get_rect()

        self.active = False

    def draw(self, surface, position):
        if self.active:
            self.rect.center = position
            surface.blit(self.image, self.rect)