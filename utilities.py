from math import sqrt
import pygame
from pygame import Vector2

import pytmx

from settings import *

def returnFadeSurface(size):
    """Return a circular fade of size: size x size"""
    # Create the surface onto which the fade will be drawn
    fade = pygame.Surface((size, size))

    # For every pixel on the surface
    for y in range(size):
        for x in range(size):
            # Calculate the distance to the center of the surface
            distanceToCenter = sqrt((x - size/2) ** 2 + (y - size/2) ** 2)
            # Turn it into a fraction from 0 up, invert it and set the values lower than 0 to 0. Multiply this by 255 to get a value from 0 to 255
            brightness = max(1 - (distanceToCenter / (size/2)), 0) * 255
            # Set that pixel to that brightness
            fade.set_at((x, y), (brightness, brightness, brightness))

    return fade

class TileMap:
    def __init__(self, filename, scale):
        self.scale = scale

        tm = pytmx.load_pygame(filename, pixelalpha=True)

        self.width = tm.width * tm.tilewidth * scale
        self.height = tm.height * tm.tileheight * scale

        self.tmxdata = tm

        # Generate the background image
        self.backgroundImg, self.topImg, self.wallMask = self.make_map()

        self.topImg.set_colorkey(BLACK)
        self.wallMask.set_colorkey(BLACK)

        self.rect = self.backgroundImg.get_rect()
    
    def render(self, bg_surface, top_surface, wall_mask_surface):
        """A function that draws the map onto a surface"""

        tile_image = self.tmxdata.get_tile_image_by_gid
        tile_prop = self.tmxdata.get_tile_properties_by_gid

        # For every visible layer
        for layer in self.tmxdata.visible_layers:
            # If the layer is a tile layer
            if isinstance(layer, pytmx.TiledTileLayer):
                # For every position on that layer
                for x, y, gid in layer:
                    # Get the tile image
                    tile = tile_image(gid)
                    
                    # If there is a tile in that spot
                    if tile:
                        # Scale the image and draw it onto the surface
                        tile = pygame.transform.scale(tile, (int(self.tmxdata.tilewidth * self.scale), int(self.tmxdata.tileheight * self.scale)))
                        if layer.name == "Above":
                            top_surface.blit(tile, (x * self.tmxdata.tilewidth * self.scale, y * self.tmxdata.tileheight * self.scale))
                        else:
                            bg_surface.blit(tile, (x * self.tmxdata.tilewidth * self.scale, y * self.tmxdata.tileheight * self.scale))


                        if tile_prop(gid)["isWall"]:
                            pygame.draw.rect(wall_mask_surface, WHITE, (x * self.tmxdata.tilewidth * self.scale, y * self.tmxdata.tileheight * self.scale, int(self.tmxdata.tilewidth * self.scale), int(self.tmxdata.tileheight * self.scale)), 0)


        return bg_surface, top_surface, wall_mask_surface

    def make_map(self):
        # Make a surface for the map to be drawn onto
        temp_bg_surface = pygame.Surface((self.width, self.height))
        temp_top_surface = pygame.Surface((self.width, self.height))
        temp_wall_surface = pygame.Surface((self.width, self.height))

        # Draw the map onto the surface and return it
        return self.render(temp_bg_surface, temp_top_surface, temp_wall_surface)

class Camera:
    def __init__(self, width, height):
        # Uses a rect to keep track of the camera
        self.camera =pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Moves the rect of the entity
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        # Calculate the map offset so it will follow the player sprite
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # Limit scrolling to map size
        x = min(0, x) # left
        y = min(0, y) # top
        x = max(-(self.width - WIDTH), x) # right
        y = max(-(self.height - HEIGHT), y) # bottom
        self.camera = pygame.Rect(x, y, self.width, self.height)
    
    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)