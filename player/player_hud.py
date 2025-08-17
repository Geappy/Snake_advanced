"""hud for displaying player information"""

import pygame

from assistent_skripts.color_print import custom_print as cprint, ValidColors as VC

from player.player_character import Player


class HUDRegister():
    OPTIONS = "options"

class PlayerHUD():
    def __init__(self, screen, player_snake: Player) -> None:
        self.screen: pygame.Surface = screen
        self.size = self.screen.get_size()
        self.player_snake = player_snake

        # options
        self.burger_img = self.load_image("textures/player/hud/Apo_burgy.png", self.size[1] * 0.1)
        burger_size = self.burger_img.get_size()
        self.burger_pos = (self.size[0] * 0.01, self.size[1] * 0.99 - burger_size[1])

        # player
        self.max_health = self.player_snake.max_HP
        self.max_armor = 10
        self.max_mana = 100
        self.max_length = 50

        self.health: int = self.player_snake.HP
        self.armor: int = 10
        self.mana: int = 100
        self.length: int = len(self.player_snake.snake_pos)

        self.player_img = self.load_image("textures/player/hud/defult.jpeg", self.size[1] * 0.2)
        # player_size = self.player_img.get_size()
        self.player_pos = (self.size[0] * 0.01, self.size[1] * 0.01)

        # map
        self.map_img = self.load_image("textures/player/hud/reymen.png", self.size[1] * 0.3)
        map_size = self.map_img.get_size()
        self.map_pos = (self.size[0] * 0.99 - map_size[0], self.size[1] * 0.01)

        # items
        self.item_list: list = []
        self.items_img = self.load_image("textures/player/hud/defult.jpeg", self.size[1] * 0.1)
        items_size = self.items_img.get_size()
        self.items_pos = (self.size[0] * 0.99 - items_size[0], self.size[1] * 0.99 - items_size[1])

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

        burger_rect = self.burger_img.get_rect(topleft=self.burger_pos)
        if burger_rect.collidepoint(mouse_pos):
            return HUDRegister.OPTIONS

        return ""
    
    def draw_bar(self, value: int, max_value: int, x: int, y: int, width: int, height: int, fill_color: tuple, outline: int):
        # Outline
        pygame.draw.rect(self.screen, (0, 0, 0), (x - 1, y - 1, width + 2, height + 2), outline)

        # Background
        pygame.draw.rect(self.screen, (40, 40, 40), (x, y, width, height), outline)

        # Filled section
        fill_width = int((value / max_value) * width)
        if fill_width > 0:
            pygame.draw.rect(self.screen, fill_color, (x, y, fill_width, height), outline)
    
    def player(self) -> None:
        # Get player icon rect
        icon_rect = self.player_img.get_rect(topleft=self.player_pos)

        # Layout settings
        base_bar_width = icon_rect.width - 20
        base_bar_height = int(self.size[1] * 0.02)
        bar_x = icon_rect.left + 10
        start_y = icon_rect.top + 10
        spacing = base_bar_height + 4

        # Track vertical offset
        y_offset = start_y

        # ─ Armor bar ─ (slightly bigger, rendered first)
        armor_bar_padding = 7
        armor_bar_height = base_bar_height + 2 * armor_bar_padding

        # Draw armor bar (behind HP)
        armor_x = bar_x - armor_bar_padding
        armor_y = y_offset - armor_bar_padding
        armor_width = base_bar_width + 2 * armor_bar_padding
        self.draw_bar(self.armor, self.max_armor, armor_x, armor_y, armor_width, armor_bar_height, (130, 120, 150), 5 + armor_bar_padding)

        # ─ HP bar ─ (same size as others)
        self.draw_bar(self.health, self.max_health, bar_x, y_offset, base_bar_width, base_bar_height, (255, 50, 50), 5)
        y_offset += base_bar_height + spacing

        # ─ Mana bar ─
        self.draw_bar(self.mana, self.max_mana, bar_x, y_offset, base_bar_width, base_bar_height, (50, 255, 255), 5)
        y_offset += base_bar_height + spacing

        # ─ Length bar ─
        self.draw_bar(self.length, self.max_length, bar_x, y_offset, base_bar_width, base_bar_height, (0, 255, 0), 5)

    def update(self) -> None:
        self.health = self.player_snake.HP
        self.length = len(self.player_snake.snake_pos)

    def render(self) -> None:
        self.update()
        self.size = self.screen.get_size()
        self.screen.blit(self.burger_img, self.burger_pos)
        self.player()
        self.screen.blit(self.map_img, self.map_pos)
        self.screen.blit(self.items_img, self.items_pos)
