"""the structure of the tarain"""

import pygame

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC


class HUB():
    def __init__(self, screen, spawn: tuple) -> None:
        self.screen: pygame.display = screen
        self.pos = spawn

        self.hub_image = self.hub_background()

        image_width, image_height = self.hub_image.get_size()
        self.pos = (self.pos[0] - (image_width // 2), self.pos[1] - (image_height // 2))

    def hub_background(self) -> pygame.surface.Surface:
        image_path: str = f"textures/tarain/hub/HUB.png"
        image = pygame.image.load(image_path).convert_alpha()
        original_width, original_height = image.get_size()
        sice = 900
        scale_factor = sice / original_height
        new_width = int(original_width * scale_factor)
        return pygame.transform.scale(image, (new_width, sice))

    def render(self, offset: tuple) -> None:
        """render the HUB"""
        self.pos = (self.pos[0] + offset[0], self.pos[1] + offset[1])
        self.screen.blit(self.hub_image, self.pos)
