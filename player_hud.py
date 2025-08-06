"""hud for displaying player information"""

import pygame

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC


class HUDRegister():
    OPTIONS = "options"

class PlayerHUD():
    def __init__(self, screen) -> None:
        self.screen: pygame.Surface = screen
        self.size = self.screen.get_size()

        # options
        self.burger = self.load_image("textures/player/hud/Apo_burgy.png", self.size[1] * 0.1)
        self.burger_pos = (self.size[0] * 0.01, self.size[1] * 0.9,)

        # player
        self.health: int = 10
        self.mana: int = 100
        self.length: int = 3

        self.player = self.load_image("textures/player/hud/Apo_burgy.png", self.size[1] * 0.1)
        self.player_pos = (self.size[0] * 0.01, self.size[1] * 0.9,)

        # map
        self.map = self.load_image("textures/player/hud/Apo_burgy.png", self.size[1] * 0.1)
        self.map_pos = (self.size[0] * 0.01, self.size[1] * 0.9,)

        # items
        self.item_list: list = []
        self.items = self.load_image("textures/player/hud/Apo_burgy.png", self.size[1] * 0.1)
        self.items_pos = (self.size[0] * 0.01, self.size[1] * 0.9,)

    def load_image(self, path: str, target_height: int) -> pygame.Surface:
        """returns a scaled image"""
        try:
            image = pygame.image.load(path).convert_alpha()

            original_width, original_height = image.get_size()
            aspect_ratio = original_width / original_height
            target_width = int(target_height * aspect_ratio)

            scaled_image = pygame.transform.scale(image, (target_width, int(target_height)))
            return scaled_image

        except Exception as e:
            cprint(f"[ERROR] Failed to load texture: {path}", VC.RED)
            raise e
        
    def get_clicked(self) -> str:
        mouse_pos = pygame.mouse.get_pos()

        burger_rect = self.burger.get_rect(topleft=self.burger_pos)
        if burger_rect.collidepoint(mouse_pos):
            return HUDRegister.OPTIONS

        return ""
        
    def update(self) -> None:
        pass

    def render(self) -> None:
        self.size = self.screen.get_size()
        self.screen.blit(self.burger, self.burger_pos)
        self.screen.blit(self.player, self.player_pos)
        self.screen.blit(self.map, self.map_pos)
        self.screen.blit(self.items, self.items_pos)
