"""Structure of NPC characters with movement and visual rendering."""

import os
import pygame

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC


class NamedNPCs:
    NIBBIN = "Nibbin"  # Wizard


class NPCRegister:
    # Friendly NPCs
    WIZARD = "wizard"
    VILLAGE_NPCS = [WIZARD]

    # Hostile NPCs
    VAMPIRE = "vampire"
    ENEMY_NPCS = [VAMPIRE]

    # Animation states
    IDLE = "idle"
    RUNNING = "running"
    DEAD = "dead"


class NPCCharacter:
    def __init__(self, screen: pygame.Surface, origin: tuple[float, float], character: str,
                 spawn: tuple[float, float], active: bool = False) -> None:
        """
        Initializes an animated NPC character.

        Args:
            screen: The Pygame surface to draw on.
            origin: The screen offset (e.g. camera offset).
            character: The NPC identifier (used for folder paths).
            spawn: The world position to spawn the character.
            active: Whether this NPC is currently active.
        """
        self.screen = screen
        self.active = active
        self.origin = origin
        self.pos = pygame.Vector2(spawn)
        self.target_pos = pygame.Vector2(spawn)

        # Movement
        self.move_speed = 8
        self.size = 200

        # Animation
        self.character = character
        self.animation_state = NPCRegister.IDLE
        self.frame = 0
        self.frame_timer = 0
        self.frame_delay = 10
        self.animation_count = self._count_animation_frames()

    # ──────────────────────────────────────────────────────────────
    # Animation Handling
    # ──────────────────────────────────────────────────────────────

    def _count_animation_frames(self, extensions={".png", ".jpg", ".jpeg"}) -> int:
        """Counts the number of frames in the current animation folder."""
        folder_path = f"textures/npcs/{self.character}/{self.animation_state}"
        try:
            return sum(
                1 for file in os.listdir(folder_path)
                if os.path.isfile(os.path.join(folder_path, file)) and os.path.splitext(file)[1].lower() in extensions
            )
        except FileNotFoundError:
            cprint(f"Missing animation folder: {folder_path}", VC.RED)
            return 0

    def change_animation(self, new_state: str) -> None:
        """
        Changes the animation state if different from current one.

        Args:
            new_state: One of NPCRegister.IDLE, RUNNING, DEAD, etc.
        """
        if self.animation_state == new_state:
            return

        self.animation_state = new_state
        self.animation_count = self._count_animation_frames()
        self.frame = 0
        self.frame_timer = 0

        # Optional tweak: adjust frame speed per animation
        if new_state == NPCRegister.RUNNING:
            self.frame_delay = 3
        else:
            self.frame_delay = self.move_speed * 2

    # ──────────────────────────────────────────────────────────────
    # Movement
    # ──────────────────────────────────────────────────────────────

    def set_target_pos(self, offset: tuple[float, float]) -> None:
        """
        Sets a new movement target based on an offset from current position.
        """
        self.target_pos = self.pos + pygame.Vector2(offset)
        self.change_animation(NPCRegister.RUNNING)

    def _move_toward_target(self) -> None:
        """
        Smoothly moves the character toward its target position.
        """
        direction = self.target_pos - self.pos
        distance = direction.length()

        if distance < self.move_speed:
            self.pos = self.target_pos
            self.change_animation(NPCRegister.IDLE)
        else:
            direction.scale_to_length(self.move_speed)
            self.pos += direction

    # ──────────────────────────────────────────────────────────────
    # Rendering
    # ──────────────────────────────────────────────────────────────

    def render(self, origin: tuple[float, float]) -> None:
        """
        Renders the NPC sprite to the screen at the correct position.

        Args:
            origin: The current screen offset (e.g. camera position).
        """
        self.origin = origin

        if not self.active:
            self.pos = self.target_pos  # snap to destination when inactive
            return

        if self.pos != self.target_pos:
            self._move_toward_target()

        # Load current frame
        image_path = f"textures/npcs/{self.character}/{self.animation_state}/{self.frame}.png"
        try:
            image = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            cprint(f"Missing image: {image_path}", VC.RED)
            return

        # Scale image
        original_width, original_height = image.get_size()
        scale_factor = self.size / original_height
        new_width = int(original_width * scale_factor)
        scaled_image = pygame.transform.scale(image, (new_width, self.size))

        # Position image
        centered_pos = pygame.Vector2(self.pos.x - new_width * 0.5, self.pos.y - self.size * 0.8)
        screen_pos = pygame.Vector2(self.origin) + centered_pos

        self.screen.blit(scaled_image, screen_pos)

        # Advance frame if needed
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % self.animation_count if self.animation_count > 0 else 0
