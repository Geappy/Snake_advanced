"""Structure of NPC characters with movement and visual rendering."""

import os
import pygame

from assistent_skripts.color_print import custom_print as cprint, ValidColors as VC


class NamedNPCs:
    NIBBIN = "Nibbin"  # Wizard


class NPCRegister:
    NAME = 0
    HP = 1

    # Friendly NPCs
    WIZARD = ("wizard", 5)
    VILLAGE_NPCS = [WIZARD]

    # Hostile NPCs
    VAMPIRE = ("vampire", 10)
    ENEMY_NPCS = [VAMPIRE]

    # Animation states
    IDLE = "idle"
    RUNNING = "running"
    DEAD = "dead"


class NPCCharacter:
    def __init__(self, screen: pygame.Surface, origin: tuple[float, float], character: tuple[str, int],
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

        self.max_HP: int = self.character[NPCRegister.HP]
        self.HP: int = self.max_HP

    def change_health(self, amount: int, reduce: bool = True):
        """Reduces the NPC's HP and handles death."""
        if reduce:
            self.HP -= amount
            cprint(f"{self.character[NPCRegister.NAME]} took {amount} damage. Remaining HP: {self.HP}", VC.YELLOW)

            if self.HP <= 0:
                self.HP = 0
                self.change_animation(NPCRegister.DEAD)
                self.target_pos = self.pos
                cprint(f"{self.character[NPCRegister.NAME]} has died!", VC.RED)
        else:
            self.HP += amount
            print(f"{self.character[NPCRegister.NAME]} heald {amount}. HP: {self.HP}", VC.YELLOW)

            if self.HP >= self.max_HP:
                self.HP = self.max_HP
                self.change_animation(NPCRegister.IDLE)

    # ──────────────────────────────────────────────────────────────
    # Animation Handling
    # ──────────────────────────────────────────────────────────────

    def _count_animation_frames(self, extensions={".png", ".jpg", ".jpeg"}) -> int:
        """Counts the number of frames in the current animation folder."""
        folder_path = f"textures/npcs/{self.character[NPCRegister.NAME]}/{self.animation_state}"
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

    def health_bar(self, screen_pos: pygame.Vector2, bar_width: int):
        """
        Displays the NPC's health bar above its head.

        Args:
            screen_pos: The top-left position of the NPC sprite on screen.
            bar_width: The width of the health bar (usually matches sprite width).
        """
        bar_height = 10
        bar_offset_y = 20  # Vertical offset above the sprite

        # Calculate health bar position
        bar_x = screen_pos.x
        bar_y = screen_pos.y - bar_offset_y

        # Draw red background bar
        pygame.draw.rect(
            self.screen,
            (200, 50, 50),
            (bar_x, bar_y, bar_width, bar_height),
            border_radius=3
        )

        # Draw green foreground based on HP
        if self.max_HP > 0:
            hp_ratio = max(0, min(self.HP / self.max_HP, 1))  # Clamp between 0 and 1
            green_width = int(bar_width * hp_ratio)
            pygame.draw.rect(
                self.screen,
                (50, 200, 50),
                (bar_x, bar_y, green_width, bar_height),
                border_radius=3
            )

    # ──────────────────────────────────────────────────────────────
    # Movement
    # ──────────────────────────────────────────────────────────────

    def set_target_pos(self, offset: tuple[float, float]) -> None:
        """
        Sets a new movement target based on an offset from current position.
        """
        if self.animation_state == NPCRegister.DEAD:
            return
        self.target_pos = self.pos + pygame.Vector2(offset)
        self.change_animation(NPCRegister.RUNNING)

    def _move_toward_target(self) -> None:
        """
        Smoothly moves the character toward its target position.
        """
        if self.animation_state == NPCRegister.DEAD:
            return
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
            self.pos = self.target_pos
            return

        if self.pos != self.target_pos:
            self._move_toward_target()

        # Load current frame
        image_path = f"textures/npcs/{self.character[NPCRegister.NAME]}/{self.animation_state}/{self.frame}.png"
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

        if self.HP < self.max_HP:
            self.health_bar(screen_pos, new_width)

        # Advance frame if needed
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % self.animation_count if self.animation_count > 0 else 0
