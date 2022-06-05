import pygame
from pygame import Vector2

from math import cos, sin, atan2, pi

from settings import *

def collide_rect(player, wall):
    return player.col_rect.colliderect(wall.rect)

def rotateVector2(vector2, angle):
    vector2 = Vector2(vector2)
    passedVector2 = Vector2(vector2)

    angle *= pi/180

    vector2.x = passedVector2.x * cos(angle) - passedVector2.y * sin(angle)
    vector2.y = passedVector2.x * sin(angle) + passedVector2.y * cos(angle)

    return vector2

class Character(pygame.sprite.Sprite):
    def __init__(self, game, position, characterImages, characterName):
        pygame.sprite.Sprite.__init__(self, game.all_sprites, game.all_characters)

        self.characterImages = characterImages
        self.characterName = characterName
        self.imageKey = "stand"

        self.image = self.characterImages[self.characterName][self.imageKey]
        self.rect = self.image.get_rect()
        self.rect.center = position

        self.col_rect = CHARACTER_COL_RECT.copy()
        self.col_rect.center = position

        self.position = Vector2(position)
        self.velocity = Vector2()

        self.bulletOffset = Vector2(19, 15)
        self.fireRate = 1000
        self.lastFireTime = 0

        self.angle = 0

        self.game = game

        self.health = 100

    def update(self):
        self.updateVelocity()
        self.velocity *= FLOOR_FRICTION

        self.position += self.velocity * self.game.deltaT

        self.rect = self.image.get_rect()
        self.rect.center = self.position

        self.col_rect.centerx = self.position.x
        self.wall_collision('x')

        self.col_rect.centery = self.position.y
        self.wall_collision('y')

        self.rotate()

        if self.health <= 0:
            self.kill()

    def wall_collision (self, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.all_obsticles, False, collide_rect)
            # For every wall im colliding with
            for hit in hits:
                # If im moving right
                if self.velocity.x > 0:
                    # Put me on the left of the object
                    self.position.x = hit.rect.left - self.col_rect.width / 2
                # If im moving left
                if self.velocity.x < 0:
                    # Put me on the right of the object
                    self.position.x = hit.rect.right + self.col_rect.width / 2
                # Set the players velocity to zero and move their collision rect
                self.velocity.x = 0
                # Set the rect
                self.rect.centerx = self.position.x
                self.col_rect.centerx = self.position.x
                # Stop the loop
                break
        elif direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.all_obsticles, False, collide_rect)
            for hit in hits:
                if self.velocity.y > 0:
                    self.position.y = hit.rect.top - self.col_rect.height / 2
                if self.velocity.y < 0:
                    self.position.y = hit.rect.bottom + self.col_rect.height / 2
                self.velocity.y = 0
                self.rect.centery = self.position.y
                self.col_rect.centery = self.position.y
                break

    def rotate(self, angle=None, smoothing=True):
        self.previousAngle = self.angle
        
        if not angle:
            self.angle = self.getCharacterRotation()
        else:
            self.angle = angle

        if smoothing:
            self.angle = (self.angle + self.previousAngle*4) / 5

        self.image = pygame.transform.rotate(self.characterImages[self.characterName][self.imageKey], self.angle)

    def shoot(self):
        if pygame.time.get_ticks() > self.lastFireTime + self.fireRate:
            self.lastFireTime = pygame.time.get_ticks()
            Bullet(self.game, self, self.position + rotateVector2(self.bulletOffset, -self.angle), self.angle, 400)

    def getCharacterRotation(self):
        return atan2(-self.velocity.y, self.velocity.x) * 180/pi

    def updateVelocity(self):
        pass

class Player(Character):
    def __init__(self, game, position, characterImages, character="manBlue"):
        super().__init__(game, position, characterImages, character)

        self.input = []
        self.prevInput = []

        self.holdingObject = None

    def get_input(self, input):
        self.input = input

    def updateVelocity(self):
        if self.input:
            speedMultiplier = 1.5 if self.input[5] else 1

            # Forward
            if any(self.input[1]):
                self.velocity += rotateVector2(Vector2(CHARACTER_SPEED, 0), -self.angle) * speedMultiplier

            # Backward
            if any(self.input[2]):
                self.velocity += rotateVector2(Vector2(-CHARACTER_SPEED, 0), -self.angle) * speedMultiplier

            # Left
            if any(self.input[3]):
                self.velocity += rotateVector2(Vector2(0, -CHARACTER_SPEED*3/4), -self.angle) * speedMultiplier

            # Right
            if any(self.input[4]):
                self.velocity += rotateVector2(Vector2(0, CHARACTER_SPEED*3/4), -self.angle) * speedMultiplier

    def getCharacterRotation(self):
        if not self.input:
            return 0

        return atan2(-self.input[0][0][1], self.input[0][0][0]) * 180/pi

    def isCloseToObjects(self, distance, objects) -> bool:
        for object in objects:
            if (self.position - object.position).magnitude() < distance:
                return True

        return False

    def pickupClosestObject(self):
        # Get the closest object
        closestObject = None
        closestDistance = 0
        for object in self.game.all_objects:
            if not closestObject or (self.position - Vector2(object.rect.center)).magnitude() < closestDistance:
                closestObject = object
                closestDistance = (self.position - Vector2(object.rect.center)).magnitude()

        if closestDistance > 40:
            return

        self.holdingObject = closestObject

        self.holdingObject.pickup(self)

        self.imageKey = "hold"

    def update(self):
        super().update()

        # Check if your item hasn't been stolen
        if self.holdingObject and self.holdingObject.heldBy != self:
            self.holdingObject = None
            self.imageKey = "stand"

        if self.input:
            # Pickup and put down objects
            if self.input[6] and not self.prevInput[6]:
                if not self.holdingObject:
                    self.pickupClosestObject()
                else:
                    self.holdingObject.putDown()
                    self.holdingObject = None
                    self.imageKey = "stand"

            # Pull out gun if not holding object
            if not self.holdingObject and self.input[7] and not self.prevInput[7]:
                if self.imageKey != "gun":
                    self.imageKey = "gun"
                else:
                    self.imageKey = "stand"

            # Shoot bullet
            if self.imageKey == "gun":
                if self.input[0][1][0] and not self.prevInput[0][1][0]:
                    self.shoot()

        self.prevInput = self.input.copy()

class Guard(Character):
    def __init__(self, game, points, characterImages):
        self.points = [Vector2(point)*game.scale for point in points]

        super().__init__(game, self.points[0], characterImages, "hitman1")

        self.currentPoint = 0

        self.sightRange = 200

        self.game = game

    def getClosestCharacterDistance(self) -> None or Vector2:
        closestOffset = None
        for character in self.game.all_characters:
            if type(character) == Player:

                # If the offset is closes, save it as the closest
                offset = self.position - character.position
                if not closestOffset or offset.magnitude() < closestOffset.magnitude():
                    closestOffset = offset

        if closestOffset and closestOffset.magnitude() > self.sightRange:
            closestOffset = None

        return closestOffset

    def updateVelocity(self):
        pointOffset = self.position - self.points[self.currentPoint]

        # If the guard is within half a tile of the current point
        if pointOffset.length() < TILESIZE/2:
            # Change the current point
            self.currentPoint += 1

            # If the guard is at the end of the path, go back to the start
            self.currentPoint %= len(self.points)

        nearestCharacter = self.getClosestCharacterDistance()

        # Change the image and chase player if near enough to one
        self.imageKey = "stand"
        if nearestCharacter:
            pointOffset = nearestCharacter
            self.imageKey = "gun"
            self.shoot()

        # Allow even a vector of (0, 0) to be normalised
        if pointOffset.magnitude() == 0:
            pointOffset.x += 1

        self.velocity += pointOffset.normalize() * -CHARACTER_SPEED

class Obsticle(pygame.sprite.Sprite):
    def __init__(self, game, position, size, isTransparent):
        pygame.sprite.Sprite.__init__(self, [game.all_sprites, game.all_obsticles])
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])

        self.size = Vector2(size)
        self.position = Vector2(position)
        self.centerPosition = Vector2(position) + Vector2(size)/2

        self.isTransparent = isTransparent

        # Calculate the positions of all the corners
        self.cornerPositions = [
            self.position,
            self.position + Vector2(self.size.x, 0),
            self.position + self.size,
            self.position + Vector2(0, self.size.y),
            self.position,
        ]

        if self.size.x > game.sightRange:
            Obsticle(game, self.position, (self.size.x/2, self.size.y), self.isTransparent)
            Obsticle(game, (self.position.x + self.size.x/2, self.position.y), (self.size.x/2, self.size.y), self.isTransparent)
            self.kill()
        elif self.size.y > game.sightRange:
            Obsticle(game, self.position, (self.size.x, self.size.y/2), self.isTransparent)
            Obsticle(game, (self.position.x, self.position.y + self.size.y/2), (self.size.x, self.size.y/2), self.isTransparent)
            self.kill()

    def returnShaddowPolygons(self, lightPos, lightRange):
        """Returns the polygons of shaddows from a light source"""

        shaddowDistance = lightRange

        polygons = []
        for i in range(4):
            # Add a corner to the polygon
            polygon = [Vector2(self.cornerPositions[i]), Vector2(self.cornerPositions[i+1])]

            # If the any of the corners are within the lights range
            if (polygon[0] - lightPos).length() < lightRange or (polygon[1] - lightPos).length() < lightRange:
                relativeVector = (polygon[1] - lightPos).normalize()
                positionVector = relativeVector * shaddowDistance
                polygon.append(polygon[1] + positionVector)

                self.lockToGrid(relativeVector)
                positionVector = relativeVector * shaddowDistance
                polygon.append(polygon[1] + positionVector)

                relativeVector = (polygon[0] - lightPos).normalize()
                self.lockToGrid(relativeVector)
                positionVector = relativeVector * shaddowDistance
                polygon.append(polygon[0] + positionVector)

                relativeVector = (polygon[0] - lightPos).normalize()
                positionVector = relativeVector * shaddowDistance
                polygon.append(polygon[0] + positionVector)

                polygons.append(polygon)

        return polygons

    def lockToGrid(self, vector2):
        vector2.x = self.isPositive(vector2.x)
        vector2.y = self.isPositive(vector2.y)
        vector2.normalize()

    def isPositive(self, number):
        if number > 0:
            return 1
        elif number < 0:
            return -1
        else:
            return 0

class Object(pygame.sprite.Sprite):
    def __init__(self, game, position, angle, image, imageName):
        pygame.sprite.Sprite.__init__(self, [game.all_sprites, game.all_objects])

        self.position = Vector2(position)
        self.angle = angle

        self.imageName = imageName

        self.originalImage = image
        self.generateImage()

        # Create a collision object for the object
        self.collider = Obsticle(game, (self.position.x - 5, self.position.y - 5), (10, 10), False)

        self.heldBy = None

        self.game = game

    def generateImage(self):
        self.image = pygame.transform.rotate(self.originalImage, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def update(self):
        if self.heldBy:
            self.position = Vector2(self.heldBy.position)
            self.position += Vector2(cos(self.heldBy.angle*pi/180), -sin(self.heldBy.angle*pi/180)) * 20

            self.angle = self.heldBy.angle - 90
            self.generateImage()

        self.rect.center = self.position

    def pickup(self, character):
        self.heldBy = character

        self.collider.kill()
    
    def putDown(self):
        self.heldBy = None

        self.collider = Obsticle(self.game, (self.position.x - 5, self.position.y - 5), (10, 10))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, parent, startPos, angle, range):
        pygame.sprite.Sprite.__init__(self, [game.all_sprites, game.all_projectiles])

        self.game = game
        self.parent = parent
        self.startPos = startPos
        self.position = Vector2(startPos)
        self.direction = rotateVector2(Vector2(0, 1), -angle - 90)
        self.range = range

        self.angle = angle
        self.imageName = "bullet"

        self.image = game.spriteImgs["bullet"]
        self.rect = self.image.get_rect()
        self.rect.center = self.startPos

        self.speed = 1000

    def update(self):
        self.position += self.direction * self.speed * self.game.deltaT

        self.rect.center = self.position

        # Kill if touching a wall
        hits = pygame.sprite.spritecollide(self, self.game.all_obsticles, False)
        if hits:
            self.kill()

        # Do damage to characters
        hits = pygame.sprite.spritecollide(self, self.game.all_characters, False)
        for hit in hits:
            if hit != self.parent:
                hit.health -= 25
                self.kill()
                break

        if (self.position - self.startPos).magnitude() >= self.range:
            self.kill()