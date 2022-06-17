import pygame

from sprites import *
from UI import *
from utilities import *
from playerLighting import returnPlayerSight
from settings import *

from os import path

class Game:
    def __init__(self):
        """Initialise game window, mixer and clock"""

        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("server")
        self.clock = pygame.time.Clock()

        self.mask = pygame.Surface((WIDTH, HEIGHT))

        self.scriptDir = path.dirname(__file__)

        self.scale = 0.5

        self.sightRange = 400

        self.characterImgs = self.loadPlayerImages()
        self.spriteImgs = self.loadOtherImages()
        
    def new(self):
        print("New game created")
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.all_obsticles = pygame.sprite.Group()

        self.all_characters = pygame.sprite.Group()
        self.all_objects = pygame.sprite.Group()
        self.all_projectiles = pygame.sprite.Group()

        # Generate the map
        self.mapInfo = TileMap(path.join(path.join(self.scriptDir, "maps"), "main map.tmx"), self.scale)

        # Spawn all the obsticles
        self.loadObjects()

    def run(self):
        """The game's game loop"""

        self.running = True
        while self.running:
            # Keep loop running at the right speed and get the time since the last frame
            self.deltaT = self.clock.tick(FPS) / 1000
            # print(1/self.deltaT)
            self.events()
            self.update()
            self.draw()

    def events(self):
        """Process input"""

        for event in pygame.event.get():
            # Check for closing window
            if event.type == pygame.QUIT:
                quit()

    def update(self):
        """Update all the sprites"""
        self.all_sprites.update()
        
    def loadObjects(self):
        for tile_object in self.mapInfo.tmxdata.objects:
            if tile_object.name == "solid":
                # Spawn an obsticle
                Obsticle(self, (tile_object.x*self.scale, tile_object.y*self.scale), (tile_object.width*self.scale, tile_object.height*self.scale), tile_object.properties["isTransparent"])
            elif tile_object.name == "guard":
                # Spawn a guard
                Guard(self, tile_object.points, self.characterImgs)
            elif tile_object.name == "player":
                # Spawn the player and remeber the spawn position
                self.spawnPoint = list(Vector2(tile_object.x, tile_object.y)*self.scale)
            elif tile_object.name == "object":
                Object(self, (tile_object.x*self.scale, tile_object.y*self.scale), tile_object.properties["objectRotation"], self.spriteImgs[tile_object.properties["objectImg"]], tile_object.properties["objectImg"])

    def loadPlayerImages(self):
        """Load all character images"""
        characters = ["hitman1", "manBlue", "manBrown", "manOld", "soldier1", "survivor1", "womanGreen"]
        variations = ["gun", "hold", "machine", "reload", "silencer", "stand"]

        imageDirectory = path.join(self.scriptDir, "images")

        characterImages = path.join(imageDirectory, "characters")

        allCharacterImgs = {}

        for character in characters:
            characterImgs = {}
            for variation in variations:
                filename = f"{character}_{variation}.png"

                image = pygame.image.load(path.join(characterImages, filename)).convert_alpha()
                image = pygame.transform.scale(image, (int(image.get_width()*self.scale*2), int(image.get_height()*self.scale*2)))

                characterImgs[variation] = image

            allCharacterImgs[character] = characterImgs

        return allCharacterImgs

    def loadOtherImages(self):
        objects = ["flatScreen", "moniter", "oldTV_beige", "oldTV_black", "oldTV_wood", "bullet", "bag"]


        imageDirectory = path.join(self.scriptDir, "images")

        objectImages = path.join(imageDirectory, "objects")

        allImages = {}

        for imgName in objects:
            filename = f"{imgName}.png"

            image = pygame.image.load(path.join(objectImages, filename)).convert_alpha()
            image = pygame.transform.scale(image, (int(image.get_width()*self.scale*2), int(image.get_height()*self.scale*2)))

            allImages[imgName] = image

        return allImages

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.mapInfo.backgroundImg, (0, 0))

        for sprite in self.all_sprites:
            if type(sprite) not in [Obsticle]:
                self.screen.blit(sprite.image, sprite.rect.topleft)

        pygame.display.flip()