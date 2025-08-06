"""Structure of attachments that the Player can add to their character."""

from __future__ import annotations

import pygame
from typing import Optional, TYPE_CHECKING

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC

if TYPE_CHECKING:
    from player_character import Player


# -------------------------------
# Weapon Behavior Base & Subtypes
# -------------------------------

class WeaponBehavior:
    """Base class for defining weapon-specific behaviors."""
    def __init__(self, weapon: Attachment):
        self.weapon = weapon

    def attack(self, projectiles: list):
        raise NotImplementedError("Weapon behavior must implement 'attack'")


class GunBehavior(WeaponBehavior):
    """Gun weapon shoots two projectiles in opposite directions."""
    def attack(self, projectiles: list):
        base_pos = pygame.Vector2(self.weapon.pos)
        angle = getattr(self.weapon, "last_angle", 0)

        # Directions offset by ±90 degrees from weapon's angle
        direction1 = pygame.Vector2(1, 0).rotate(-angle - 90).normalize()
        direction2 = pygame.Vector2(1, 0).rotate(-angle + 90).normalize()

        offset_distance = 80
        spawn1 = base_pos + direction1 * offset_distance
        spawn2 = base_pos + direction2 * offset_distance

        inherited_velocity = self.weapon.pos - self.weapon.previous_pos
        projectiles.append(Projectile(spawn1, direction1, inherited_velocity))
        projectiles.append(Projectile(spawn2, direction2, inherited_velocity))


class SwordBehavior(WeaponBehavior):
    """Sword weapon for close combat."""
    def attack(self, projectiles: list):
        print("Slash!")


class HealingBehavior(WeaponBehavior):
    """Healing weapon restores player health."""
    def attack(self, projectiles: list):
        print("Heal +20!")


# -------------------------------
# Weapon Register
# -------------------------------

class WeaponRegister:
    """Weapon type metadata (name and cooldown)."""
    NAME = 0
    COOLDOWN = 1

    GUN = ("Gun", 100)
    SWORD = ("Sword", 10)
    HEALING = ("Healing", 200)


# -------------------------------
# Attachment Class
# -------------------------------

class Attachment:
    """Attachable weapon component for the player character."""

    def __init__(self, screen, player: Player, origin: tuple[float, float], pos: tuple[float, float], weapon_type: tuple[str, int]):
        self.screen: pygame.Surface = screen
        self.player = player
        self.origin = origin
        self.pos = pygame.Vector2(pos)
        self.previous_pos = pygame.Vector2(pos)

        self.size = 50
        self.pickup_range = self.size * 2
        self.last_angle = 0

        self.attached = False
        self.attached_to: Optional[int] = None

        self.dragging = False
        self.drag_offset = pygame.Vector2(0, 0)

        self.weapon_name = weapon_type[WeaponRegister.NAME]
        self.cooldown = 0
        self.cooldown_time = weapon_type[WeaponRegister.COOLDOWN]

        self.texture = self.load_texture(self.weapon_name)

        # Assign behavior based on weapon type
        if weapon_type == WeaponRegister.GUN:
            self.behavior = GunBehavior(self)
        elif weapon_type == WeaponRegister.SWORD:
            self.behavior = SwordBehavior(self)
        elif weapon_type == WeaponRegister.HEALING:
            self.behavior = HealingBehavior(self)
        else:
            raise ValueError(f"Unknown weapon type: {weapon_type}")

    def attack(self, projectiles: list):
        """Trigger the weapon's attack behavior."""
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        try:
            self.behavior.attack(projectiles)
        except Exception as e:
            print(f"[ERROR] Failed to attack: {e}")

        self.cooldown = self.cooldown_time

    def load_texture(self, weapon_type: str) -> pygame.Surface:
        """Load and scale weapon texture based on type."""
        path = f"textures/player/atachments/{weapon_type}_atachment.png"
        try:
            image = pygame.image.load(path).convert_alpha()
            target_height = self.size * 2
            aspect_ratio = image.get_width() / image.get_height()
            target_width = int(target_height * aspect_ratio)
            return pygame.transform.scale(image, (target_width, int(target_height)))
        except Exception as e:
            cprint(f"[ERROR] Failed to load texture: {path}", VC.RED)
            raise e

    def handle_mouse_down(self, mouse_pos: tuple[float, float], origin: tuple[float, float], player: Player):
        """Start dragging the weapon if clicked within hit circle."""
        self.origin = origin
        mouse_world = pygame.Vector2(mouse_pos) - pygame.Vector2(origin)

        if (self.pos - mouse_world).length() <= self.size:
            self.dragging = True
            self.drag_offset = self.pos - mouse_world

            if self.attached:
                self.attached = False
                if self.attached_to is not None and player.weapon_slots.get(self.attached_to) == self:
                    player.weapon_slots[self.attached_to] = None
                self.attached_to = None

    def handle_mouse_up(self, player: Player, origin: tuple[float, float]):
        """Stop dragging and try to attach to a node if nearby."""
        self.origin = origin
        if not self.dragging:
            return
        self.dragging = False

        for idx in range(player.weapon_start_index, len(player.snake_pos) - 1, player.weapon_interval):
            node_pos = pygame.Vector2(player.snake_pos[idx])
            if (self.pos - node_pos).length() < self.size * 2:
                existing = player.weapon_slots.get(idx)
                if existing and existing is not self:
                    cprint(f"Node {idx} already has a weapon", VC.RED)
                    return

                if self.attached_to is not None:
                    player.weapon_slots[self.attached_to] = None

                self.attached = True
                self.attached_to = idx
                player.weapon_slots[idx] = self
                self.pos = node_pos
                cprint(f"Weapon snapped to node {idx}", VC.GREEN)
                return

        cprint("Dropped weapon without snapping to a node", VC.YELLOW)

    def draw(self, origin: tuple[float, float], angle: float = 0):
        """Draw the weapon at its current position."""
        screen_pos = self.pos + pygame.Vector2(origin)
        self.last_angle = angle

        corrected_angle = angle + 90 if self.attached else angle
        rotated_image = pygame.transform.rotate(self.texture, corrected_angle)
        rect = rotated_image.get_rect(center=screen_pos)
        self.screen.blit(rotated_image, rect)

    def update(self, origin: tuple[float, float]):
        """Update weapon position either by drag or attachment."""
        self.origin = origin
        if self.attached:
            self.previous_pos = self.pos
            self.pos = self.player.snake_pos[self.attached_to]
        elif self.dragging:
            mouse_screen = pygame.Vector2(pygame.mouse.get_pos())
            mouse_world = mouse_screen - pygame.Vector2(self.origin)
            self.pos = mouse_world + self.drag_offset


# -------------------------------
# Projectile Class
# -------------------------------

class Projectile:
    """Simple projectile shot by weapons."""
    def __init__(
        self,
        pos: pygame.Vector2,
        direction: pygame.Vector2,
        inherited_velocity: pygame.Vector2 = pygame.Vector2(0, 0),
        speed: float = 15,
        damage: int = 10
    ):
        self.pos = pygame.Vector2(pos)
        self.velocity = direction.normalize() * speed + inherited_velocity
        self.radius = 6
        self.damage = damage
        self.alive = True

    def update(self):
        """Move the projectile forward."""
        self.pos += self.velocity

        # Deactivate if out of bounds
        if not (-3000 < self.pos.x < 3000 and -3000 < self.pos.y < 3000):
            self.alive = False

    def draw(self, screen: pygame.Surface, origin: tuple[float, float]):
        """Render the projectile."""
        screen_pos = self.pos + pygame.Vector2(origin)
        pygame.draw.circle(screen, (255, 200, 200), screen_pos, self.radius)
