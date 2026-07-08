import pygame
import os

class Platform():
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.baseX = x

        imagePath = 'assets/Tiles/tile_0022.png'
        if not os.path.isfile(imagePath):
            raise FileNotFoundError('Cannot find platform image')

        image = pygame.image.load(imagePath).convert_alpha()
        self.image = pygame.transform.scale(image, (width, height)) 

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        return 0
