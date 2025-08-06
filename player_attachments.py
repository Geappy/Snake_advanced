"""Structure of atachments that the Player can add to there Character."""

from __future__ import annotations

import pygame
from typing import Optional, TYPE_CHECKING

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC

if TYPE_CHECKING:
    from player_character import Player


class WeaponBehavior:
    def attack(self):
        raise NotImplementedError

class GunBehavior(WeaponBehavior):
    def attack(self):
        print("Bang!")

class SwordBehavior(WeaponBehavior):
    def attack(self):
        print("Slash!")

class HealingBehavior(WeaponBehavior):
    def attack(self):
        print("Heal +20!")

class WeaponRegister:
    # Weapon types (must match texture file prefixes)
    NAME = 0
    COOLDOWN = 1

    GUN = ("Gun", 100)
    SWORD = ("Sword", 10)
    HEALING = ("Healing", 200)

class Weapons:
    def __init__(self, screen, origin: tuple[float, float], pos: tuple[float, float], weapon_type: tuple[str, int]):
        self.screen: pygame.Surface = screen
        self.origin = origin
        self.pos = pygame.Vector2(pos)
        self.attached = False
        self.attached_to: Optional[int] = None
        self.size = 50
        self.pickup_range = self.size * 2

        self.weapon_name = weapon_type[WeaponRegister.NAME]
        self.texture = self.load_texture(self.weapon_name)

        self.dragging = False
        self.drag_offset = pygame.Vector2(0, 0)

        self.cooldown: int = 0
        self.cooldown_time: int = weapon_type[WeaponRegister.COOLDOWN]

        if weapon_type == WeaponRegister.GUN:
            self.behavior = GunBehavior()
        elif weapon_type == WeaponRegister.SWORD:
            self.behavior = SwordBehavior()
        elif weapon_type == WeaponRegister.HEALING:
            self.behavior = HealingBehavior()
        else:
            raise ValueError(f"Unknown weapon type: {weapon_type}")

    def attack(self):
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        try:
            self.behavior.attack()
        except:
            print("No behavior assigned to this weapon.")
        self.cooldown = self.cooldown_time

    def load_texture(self, weapon_type: str) -> pygame.Surface:
        path = f"textures/player/atachments/{weapon_type}_atachment.png"
        try:
            image = pygame.image.load(path).convert_alpha()

            # Target height (e.g., match weapon size)
            target_height = self.size * 2
            original_width, original_height = image.get_size()

            # Calculate new width while keeping aspect ratio
            aspect_ratio = original_width / original_height
            target_width = int(target_height * aspect_ratio)

            scaled_image = pygame.transform.scale(image, (target_width, int(target_height)))
            return scaled_image

        except Exception as e:
            cprint(f"[ERROR] Failed to load texture: {path}", VC.RED)
            raise e

    def handle_mouse_down(self, mouse_pos: tuple[float, float], origin: tuple[float, float], player: Player):
        self.origin = origin
        mouse_world = pygame.Vector2(mouse_pos) - pygame.Vector2(self.origin)

        # Check if mouse clicked within the weapon hit circle
        if (self.pos - mouse_world).length() <= self.size:
            self.dragging = True
            self.drag_offset = self.pos - mouse_world

            # Detach from player if currently attached
            if self.attached:
                self.attached = False
                if self.attached_to is not None and player.weapon_slots.get(self.attached_to) == self:
                    player.weapon_slots[self.attached_to] = None
                self.attached_to = None

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

    def draw(self, origin: tuple[float, float], angle: float = 0):
        screen_pos = self.pos + pygame.Vector2(origin)

        # Try different correction angles here
        corrected_angle = angle
        if self.attached:
            corrected_angle += 90

        rotated_image = pygame.transform.rotate(self.texture, corrected_angle)
        rect = rotated_image.get_rect(center=screen_pos)
        self.screen.blit(rotated_image, rect)

    def update(self, origin: tuple[float, float]):
        self.origin = origin
        if self.dragging:
            mouse_screen = pygame.Vector2(pygame.mouse.get_pos())
            mouse_world = mouse_screen - pygame.Vector2(self.origin)
            self.pos = mouse_world + self.drag_offset
