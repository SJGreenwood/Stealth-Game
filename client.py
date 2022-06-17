from time import time
import pygame

from os import path

from playerLighting import returnPlayerSight
from utilities import *
from sprites import *
from UI import *
from server import *
from network import *
from settings import *

class Client:
    def __init__(self):
        """Initialise game window, mixer and clock"""

        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Stealth game (client)")
        self.clock = pygame.time.Clock()

        self.scriptDir = path.dirname(__file__)

        self.scale = 0.5
        self.spriteImages = self.loadSpriteImages()

        self.charaterSize = self.spriteImages["manBlue_stand"].get_size()

        self.mask = pygame.Surface((WIDTH, HEIGHT))

        self.sightRange = 400
        self.sightFade = returnFadeSurface(self.sightRange * 2)
        self.wallSightRange = WIDTH
        self.wallFade = pygame.Surface((self.wallSightRange*2, self.wallSightRange*2))
        self.wallFade.blit(returnFadeSurface(self.wallSightRange), (self.wallSightRange/2, self.wallSightRange/2))

        self.lastFramerates = [0 for _ in range(FPS)]

    def new(self):
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.all_obsticles = pygame.sprite.Group()

        # Generate the map
        self.mapInfo = TileMap(path.join(path.join(self.scriptDir, "maps"), "main map.tmx"), self.scale)

        self.wholeSightMask = pygame.Surface((int(self.mapInfo.width), int(self.mapInfo.height)))

        self.minimap = Minimap(self.mapInfo.backgroundImg, 200, 0.15, BLUE, 3, ORANGE, 5, (39, 174, 96))

        # Spawn all the obsticles
        self.loadWalls()

        self.network = Network()

        self.playerPos = [0, 0]
        self.cameraPos = [0, 0]

    def run(self):
        """The client's game loop"""

        self.running = True
        while self.running:
            # Keep loop running at the right speed and get the time since the last frame
            self.deltaT = self.clock.tick(FPS) / 1000
            
            self.lastFramerates.append(1/self.deltaT)
            del self.lastFramerates[0]
            print(sum(self.lastFramerates)/FPS)

            self.events()
            self.update()
            self.draw()

    def events(self):
        """Handle input"""

        for event in pygame.event.get():
            # Check for closing window
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pos()
        mouseButtons = pygame.mouse.get_pressed()

        self.importantKeys = [
            [
                [mouse[0] - self.playerPos[0] + self.cameraPos[0], mouse[1] - self.playerPos[1] + self.cameraPos[1]],
                mouseButtons,
            ],
            [keys[pygame.K_w], keys[pygame.K_UP]],
            [keys[pygame.K_s], keys[pygame.K_DOWN]],
            [keys[pygame.K_a], keys[pygame.K_LEFT]],
            [keys[pygame.K_d], keys[pygame.K_RIGHT]],
            keys[pygame.K_LSHIFT],
            keys[pygame.K_e],
            keys[pygame.K_f],
            keys[pygame.K_b],
        ]

    def update(self):
        # Send keyboard input to the server
        self.objectInfo = readInfo(self.network.send(makeInfo(self.importantKeys)))

        # Get the character the client is controlling
        self.getPlayerInfo()

        self.minimap.update(self.playerPos)

    def draw(self):
        self.screen.fill(BLACK)

        # Draw the map
        self.screen.blit(self.mapInfo.backgroundImg, -self.cameraPos)

        # Draw all sprites if they have an image
        for sprite in self.objectInfo:
            if sprite["image"] != "None":
                image = self.spriteImages[sprite["image"]]
                image = pygame.transform.rotate(image, sprite["angle"])
                self.screen.blit(image, Vector2(sprite["position"])-self.cameraPos)

        self.screen.blit(self.mapInfo.topImg, -self.cameraPos)

        # Create and draw the player lighting
        self.createScreenMask(self.playerPos, self.cameraPos)

        self.screen.blit(self.mask, pygame.Rect(0, 0, WIDTH, HEIGHT), special_flags=pygame.BLEND_MULT)

        self.minimap.draw(self.screen)

        pygame.display.flip()

    def getPlayerInfo(self):
        """Get the player's new position and the camera poition"""
        for character in self.objectInfo:
            if character["focus"]:
                self.playerPos = Vector2(character["position"])

        self.playerPos += Vector2(self.charaterSize, self.charaterSize)/2
        self.cameraPos = self.playerPos - Vector2(WIDTH, HEIGHT)/2

        self.cameraPos.x = max(self.cameraPos.x, 0)
        self.cameraPos.y = max(self.cameraPos.y, 0)

        self.cameraPos.x = min(self.cameraPos.x, self.mapInfo.width - WIDTH)
        self.cameraPos.y = min(self.cameraPos.y, self.mapInfo.height - HEIGHT)

        return self.cameraPos, self.playerPos

    def createScreenMask(self, playerPos, cameraPos):
        """A method that creates a lighting mask for the screen"""
        # Clear the mask
        self.mask.fill(BLACK)

        # Create the light mask
        playerLight = returnPlayerSight(playerPos, self.all_obsticles, self.sightRange, WHITE)
        # Add the light fade ontop of the light
        playerLight.blit(self.sightFade, pygame.Rect(0, 0, self.sightRange, self.sightRange), special_flags=pygame.BLEND_MULT)

        # Draw the player light onto the screen mask
        self.mask.blit(playerLight, Vector2(playerPos) - Vector2(cameraPos) - Vector2(self.sightRange, self.sightRange))

        # Make a copy of the walls mask and draw the walls fade onto it
        fadedWallMask = self.mapInfo.wallMask.copy()
        fadedWallMask.blit(self.wallFade, playerPos - Vector2(self.wallSightRange, self.wallSightRange), special_flags=pygame.BLEND_MULT)
        # Draw the faded walls mask onto the final mask
        self.mask.blit(fadedWallMask, -cameraPos)

    def loadSpriteImages(self):
        """Load all character images"""
        characters = ["hitman1", "manBlue", "manBrown", "manOld", "soldier1", "survivor1", "womanGreen"]
        variations = ["gun", "hold", "machine", "reload", "silencer", "stand"]

        objects = ["flatScreen", "moniter", "oldTV_beige", "oldTV_black", "oldTV_wood", "bullet", "bag"]

        imageDirectory = path.join(self.scriptDir, "images")

        characterImages = path.join(imageDirectory, "characters")
        objectImages = path.join(imageDirectory, "objects")

        allImages = {}

        for character in characters:
            for variation in variations:
                filename = f"{character}_{variation}.png"

                image = pygame.image.load(path.join(characterImages, filename)).convert_alpha()
                image = pygame.transform.scale(image, (int(image.get_width()*self.scale*2), int(image.get_height()*self.scale*2)))

                allImages[f"{character}_{variation}"] = image

        for imgName in objects:
            filename = f"{imgName}.png"

            image = pygame.image.load(path.join(objectImages, filename)).convert_alpha()
            image = pygame.transform.scale(image, (int(image.get_width()*self.scale*2), int(image.get_height()*self.scale*2)))

            allImages[imgName] = image

        return allImages

    def loadWalls(self):
        for tile_object in self.mapInfo.tmxdata.objects:
            if tile_object.name == "solid":
                # Spawn an obsticle
                Obsticle(self, (tile_object.x*self.scale, tile_object.y*self.scale), (tile_object.width*self.scale, tile_object.height*self.scale), tile_object.properties["isTransparent"])

client = Client()

while True:
    client.new()
    client.run()