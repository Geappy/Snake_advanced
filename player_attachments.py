"""Structure of atachments that the Player can add to there Character."""

from __future__ import annotations

import pygame
from typing import Optional, TYPE_CHECKING

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC

if TYPE_CHECKING:
    from player_character import Player

class Weapon:
    def __init__(self, pos: tuple[float, float]):
        self.pos = pygame.Vector2(pos)
        self.attached = False
        self.attached_to: Optional[int] = None
        self.size = 15

    def draw(self, screen: pygame.Surface, origin: tuple[float, float]):
        screen_pos = self.pos + pygame.Vector2(origin)
        
        if not self.attached:
            # Optional: draw pickup area outline
            pygame.draw.circle(screen, (100, 100, 100), screen_pos, self.size * 2, 3)
        
        color = (255, 0, 255) if self.attached else (0, 0, 255)
        pygame.draw.circle(screen, color, screen_pos, self.size)


    def try_pickup(self, player: Player, mouse_pos: tuple[float, float]):
        if self.attached:
            return

        # Convert mouse to world space
        mouse_world_pos = pygame.Vector2(mouse_pos) - pygame.Vector2(player.origin)

        # Check if mouse clicked within this weapon's pickup area
        if (self.pos - mouse_world_pos).length() <= self.size * 2:
            # Find the first available segment to attach to
            for idx in range(0, len(player.snake_pos), player.weapon_interval):
                if player.weapon_slots.get(idx) is None:
                    self.attached = True
                    self.attached_to = idx
                    player.weapon_slots[idx] = self
                    cprint(f"Weapon picked up and attached to segment {idx}", VC.YELLOW)
                    return

