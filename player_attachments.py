"""Structure of atachments that the Player can add to there Character."""

from __future__ import annotations

import pygame
from typing import Optional, TYPE_CHECKING

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC

if TYPE_CHECKING:
    from player_character import Player

class Weapon:
    def __init__(self, origin: tuple[float, float], pos: tuple[float, float]):
        self.origin = origin
        self.pos = pygame.Vector2(pos)
        self.attached = False
        self.attached_to: Optional[int] = None
        self.size = 15
        self.pickup_range = self.size * 2

        self.dragging = False
        self.drag_offset = pygame.Vector2(0, 0)
                
    def handle_mouse_down(self, mouse_pos: tuple[float, float], origin: tuple[float, float]):
        self.origin = origin
        if self.attached:
            return  # prevent dragging attached weapons (or make detachable if you want)

        mouse_world = pygame.Vector2(mouse_pos) - pygame.Vector2(self.origin)
        if (self.pos - mouse_world).length() <= self.size:
            self.dragging = True
            self.drag_offset = self.pos - mouse_world

    def handle_mouse_up(self, player: Player, origin: tuple[float, float]):
        self.origin = origin
        if not self.dragging:
            return
        self.dragging = False

        # Try to snap to nearest weapon node
        for idx in range(player.weapon_start_index, len(player.snake_pos)-1, player.weapon_interval):
            node_pos = pygame.Vector2(player.snake_pos[idx])
            if (self.pos - node_pos).length() < self.size * 2:
                # Check if slot is available
                existing = player.weapon_slots.get(idx)
                if existing and existing is not self:
                    cprint(f"Node {idx} already has a weapon", VC.RED)
                    return  # prevent overwriting (or handle swap here)

                # Detach from old node if needed
                if self.attached_to is not None:
                    player.weapon_slots[self.attached_to] = None

                # Attach to new node
                self.attached = True
                self.attached_to = idx
                player.weapon_slots[idx] = self
                self.pos = node_pos
                cprint(f"Weapon snapped to node {idx}", VC.GREEN)
                return

        cprint("Dropped weapon without snapping to a node", VC.YELLOW)

    def draw(self, screen: pygame.Surface, origin: tuple[float, float]):
        self.origin = origin
        screen_pos = self.pos + pygame.Vector2(self.origin)

        if self.dragging:
            pygame.draw.circle(screen, (255, 0, 0), screen_pos, self.size + 5, 2)

        color = (255, 0, 255) if self.attached else (0, 0, 255)
        pygame.draw.circle(screen, color, screen_pos, self.size)


    def update(self, origin: tuple[float, float]):
        self.origin = origin
        if self.dragging:
            print(f"Updating weapon at {self.pos}")
            mouse_screen = pygame.Vector2(pygame.mouse.get_pos())
            mouse_world = mouse_screen - pygame.Vector2(self.origin)
            self.pos = mouse_world + self.drag_offset




