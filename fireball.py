import pygame
import math

class Fireball:
    def __init__(self, x, y):
        # determines original/base radius of fireball
        self.baseRadius = 10
        self.radius = self.baseRadius
        # determines position of fireball
        self.x = x
        self.y = y
        # controls pulsing
        self.pulseSpeed = 0.08
        self.pulseAmount = 3
        # sine wave animation used for pulse - timer
        self.time = 0
        self.updateRect()

    def updateRect(self):
        # updates collision rectangle (based on current radius)
        self.rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def update(self):
        # Timer increased each frame for animation
        self.time += self.pulseSpeed
        self.radius = self.baseRadius + math.sin(self.time) * self.pulseAmount
        self.updateRect()

    def draw(self, screen):
        # Outer glow effect
        glowRadius = int(self.radius + 6)
        glowSurface = pygame.Surface((glowRadius*2, glowRadius*2), pygame.SRCALPHA)
        pygame.draw.circle(
            glowSurface,
            (255, 100, 0, 70),
            (glowRadius, glowRadius),
            glowRadius
        )
        screen.blit(glowSurface, (self.x - glowRadius, self.y - glowRadius))

        # Draw fireball with radial colour gradient
        for r in range(int(self.radius), 0, -1):
            colour = (
                255,
                int(120 - (r/self.radius)*60),
                0
            )
            pygame.draw.circle(
                screen,
                colour,
                (int(self.x), int(self.y)),
                r
            )
