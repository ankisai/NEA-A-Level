import pygame

class Spike():
    def __init__(self, x, y):
        self.width = 26
        self.height = 16

        # Align bottom of spike exactly to platform top
        self.rect = pygame.Rect(
            x,
            y + (20 - self.height),  # compensate for smaller height
            self.width,
            self.height
        )

        self.colour = (10, 70, 30)

    def draw(self, screen):
        pygame.draw.polygon(
            screen,
            self.colour,
            [
                (self.rect.left, self.rect.bottom),
                (self.rect.centerx, self.rect.top),
                (self.rect.right, self.rect.bottom)
            ]
        )


