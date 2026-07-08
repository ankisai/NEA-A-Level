import pygame
import os

# jewel class is collectible item 
class Jewel:
    def __init__(self, x, y):
        self.size = 28
        # rectangle for position & collision detection around jewel
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = (x, y) # sets position using centre point

        imagePath = 'assets/Tiles/tile_0067.png'

        # checks image file exists to avoid runtime error
        if not os.path.isfile(imagePath):
            raise FileNotFoundError('Cannot find jewel image')
        # loads image with transparency support
        image = pygame.image.load(imagePath).convert_alpha()
        # resize image to match jewel size
        self.image = pygame.transform.scale(image, (self.size, self.size))

    # moves jewel left when game world scrolls
    def move(self, scrollAmount):
        self.rect.x -= scrollAmount

    # draws jewel sprite onto game screen
    def draw(self, screen):
        screen.blit(self.image, self.rect)


