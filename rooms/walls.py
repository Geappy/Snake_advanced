"""walls"""

import pygame

from assistent_skripts.color_print import custom_print as cprint, ValidColors as VC


class Wall:
    def __init__(self, x, y, width, height, color=(100, 100, 100), blocks=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.blocks = blocks

    def collides(self, pos: pygame.Vector2) -> bool:
        return self.rect.collidepoint(pos)

    def render(self, screen, origin):
        self.origin = origin
        screen_rect = self.rect.move(self.origin)
        pygame.draw.rect(screen, self.color, screen_rect)
