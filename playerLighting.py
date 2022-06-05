import pygame

from math import sin, cos, pi

from settings import *

def returnPlayerSight(playerPos, obsticles, sightRange, colour):
    # Create a new surface and set the black to transparent
    light = pygame.Surface((2*sightRange, 2*sightRange))
    light.fill(colour)

    center = pygame.Vector2(sightRange, sightRange)

    polygons = []

    # For every object
    for obsticle in obsticles:
        if not obsticle.isTransparent:
            shaddows = obsticle.returnShaddowPolygons(playerPos, sightRange)

            # For every shaddow
            for s in range(len(shaddows)):
                for p in range(len(shaddows[s])):
                    # Move it so that the light position is at (0, 0)
                    shaddows[s][p] -= playerPos
                    shaddows[s][p] += center

            # Add the shaddow polygons to a list
            polygons.extend(shaddows)

    for polygon in polygons:
        pygame.draw.polygon(light, BLACK, polygon, 0)

    # Return the surface
    return light