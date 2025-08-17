"""the structure of the tarain"""

import pygame

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC


class HUB():
    def __init__(self, screen, origin: tuple[float, float], spawn: tuple[float, float]) -> None:
        self.screen: pygame.Surface = screen
        self.pos = spawn
        self.origin = origin

        self.hub_image = self.hub_background()
        image_width, image_height = self.hub_image.get_size()
        self.pos = (self.pos[0] - (image_width * 0.5), self.pos[1] - (image_height * 0.5))

    def hub_background(self) -> pygame.surface.Surface:
        image_path: str = f"textures/tarain/hub/HUB.png"
        image = pygame.image.load(image_path).convert_alpha()
        original_width, original_height = image.get_size()
        sice = 900
        scale_factor = sice / original_height
        new_width = int(original_width * scale_factor)
        return pygame.transform.scale(image, (new_width, sice))

    def render(self, origin: tuple[float, float]) -> None:
        """render the HUB"""
        self.origin = origin
        origin_pos = (self.origin[0] + self.pos[0], self.origin[1] + self.pos[1])
        self.screen.blit(self.hub_image, origin_pos)
