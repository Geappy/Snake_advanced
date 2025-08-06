"""Structure of attachments that the Player can add to their character."""

from __future__ import annotations

import math
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

    def __init__(self, weapon: Attachment):
        self.weapon = weapon

    def attack(self, projectiles: list):
        base_pos = pygame.Vector2(self.weapon.pos)
        angle = self.weapon.last_angle

        offset_distance = 80
        damage = self.weapon.weapon_type[WeaponRegister.DAMAGE]

        # Linear movement of the weapon
        linear_velocity = self.weapon.pos - self.weapon.previous_pos

        # Angular velocity (converted to radians)
        d_angle = self.weapon.last_angle - self.weapon.previous_angle
        d_angle_rad = -math.radians(d_angle)

        # Fire two projectiles at ±90° from the current angle
        for offset in [-90, 90]:
            fire_angle = angle + offset
            direction = pygame.Vector2(1, 0).rotate(-fire_angle).normalize()
            spawn_pos = base_pos + direction * offset_distance

            # Tangential velocity due to rotation
            tangential_velocity = pygame.Vector2(-direction.y, direction.x) * offset_distance * d_angle_rad
            total_velocity = linear_velocity + tangential_velocity

            # Create projectile
            projectile = Projectile(
                screen=self.weapon.screen,
                origin=self.weapon.origin,
                pos=spawn_pos,
                direction=direction,
                damage=damage,
                inherited_velocity=total_velocity
            )

            projectiles.append(projectile)

class SwordBehavior(WeaponBehavior):
    def __init__(self, weapon: Attachment):
        self.weapon = weapon

    def attack(self, projectiles: list):
        base_pos = pygame.Vector2(self.weapon.pos)
        base_angle = self.weapon.last_angle

        offset_distance = 80
        range_radius = 60
        damage = self.weapon.weapon_type[WeaponRegister.DAMAGE]

        for offset in [-90, 90]:  # Two swings on opposite sides
            angle = base_angle + offset
            direction = pygame.Vector2(1, 0).rotate(-angle).normalize()
            slash_pos = base_pos + direction * offset_distance

            swing = SwordSwingProjectile(
                screen=self.weapon.screen,
                origin=self.weapon.origin,
                pos=slash_pos,
                direction=direction,
                damage=damage,
                range_radius=range_radius,
                lifespan=2
            )

            projectiles.append(swing)

class HealingBehavior(WeaponBehavior):
    """Healing weapon restores player health."""
    def __init__(self, weapon: Attachment):
        self.weapon = weapon

    def attack(self, projectiles: list):
        healing = self.weapon.weapon_type[WeaponRegister.DAMAGE]
        self.weapon.player.change_health(healing, reduce=False)


# -------------------------------
# Weapon Register
# -------------------------------

class WeaponRegister:
    """Weapon type metadata (name and cooldown)."""
    NAME = 0
    COOLDOWN = 1
    DAMAGE = 2

    GUN = ("Gun", 100, 1)
    SWORD = ("Sword", 10, 1)
    HEALING = ("Healing", 200, 1)

    ATTACHED = "atachment"
    DETACHED = "card"

# -------------------------------
# Attachment Class
# -------------------------------

class Attachment:
    """Attachable weapon component for the player character."""

    def __init__(self, screen: pygame.Surface, player: Player, origin: tuple[float, float], pos: tuple[float, float], weapon_type: tuple[str, int]):
        self.screen = screen
        self.player = player
        self.origin = origin
        self.pos = pygame.Vector2(pos)
        self.previous_pos = pygame.Vector2(pos)

        self.size = 50
        self.pickup_range = self.size * 2
        self.last_angle = 0
        self.previous_angle = self.last_angle 

        self.attached = False
        self.attached_to: Optional[int] = None

        self.dragging = False
        self.drag_offset = pygame.Vector2(0, 0)

        self.weapon_type = weapon_type
        self.cooldown = 0
        self.cooldown_time = weapon_type[WeaponRegister.COOLDOWN]

        self.texture_detached = self.load_texture(self.weapon_type[WeaponRegister.NAME], WeaponRegister.DETACHED)
        self.texture_attached = self.load_texture(self.weapon_type[WeaponRegister.NAME], WeaponRegister.ATTACHED)

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

    def load_texture(self, weapon_type: str, state: str) -> pygame.Surface:
        """Load and scale weapon texture based on type."""
        path = f"textures/player/atachments/{weapon_type}_{state}.png"
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
                    del player.weapon_slots[self.attached_to]
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
        if self.attached:
            rotated_image = pygame.transform.rotate(self.texture_attached, corrected_angle)
        else:
            rotated_image = pygame.transform.rotate(self.texture_detached, corrected_angle)
        rect = rotated_image.get_rect(center=screen_pos)
        self.screen.blit(rotated_image, rect)

    def update(self, origin: tuple[float, float]):
        """Update weapon position either by drag or attachment."""
        self.origin = origin
        if self.attached:
            self.previous_pos = self.pos
            self.previous_angle = getattr(self, "last_angle", 0)
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
        screen: pygame.Surface,
        origin: tuple[float, float],
        pos: pygame.Vector2,
        direction: pygame.Vector2,
        damage: int,
        inherited_velocity: pygame.Vector2 = pygame.Vector2(0, 0),
        speed: float = 15,
    ):
        self.screen = screen
        self.origin = origin
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

    def draw(self, origin: tuple[float, float]):
        """Render the projectile."""
        self.origin = origin
        screen_pos = self.pos + pygame.Vector2(origin)
        pygame.draw.circle(self.screen, (255, 200, 200), screen_pos, self.radius)

class SwordSwingProjectile:
    def __init__(
        self,
        screen: pygame.Surface,
        origin: tuple[float, float],
        pos: pygame.Vector2,
        direction: pygame.Vector2,
        damage: int,
        range_radius: float = 60,
        lifespan: int = 2
    ):
        self.screen = screen
        self.origin = origin
        self.pos = pygame.Vector2(pos)
        self.direction = direction.normalize()
        self.damage = damage
        self.range_radius = range_radius
        self.lifespan = lifespan
        self.hit_npcs = set()
        self.alive = True

    def update(self):
        """Move the projectile forward."""
        pass

    def draw(self, origin: tuple[float, float]):
        self.origin = origin
        # world_pos = self.pos + pygame.Vector2(self.origin)
        # pygame.draw.circle(self.screen, (255, 255, 100), world_pos, self.range_radius, 2)

