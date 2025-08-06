"""Structure of Player characters with movement and visual rendering."""

import pygame
from typing import Optional

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC

from player_attachments import Weapon

# === Color Constants ===
GREEN = (0, 255, 0)
LIGHT_GREEN = (100, 255, 100)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Player:
    def __init__(self, screen: pygame.Surface, origin: tuple[float, float], spawn: tuple[float, float]) -> None:
        """
        Initializes the player snake with movement and rendering properties.

        Args:
            screen: The Pygame surface to draw on.
            origin: The local origin offset for positioning.
            spawn: The initial spawn position of the snake.
        """
        self.screen = screen

        # Movement properties
        self.max_speed = 8
        self.acceleration = 1
        self.deceleration = 1
        self.move_speed = 15
        self.target_pos = spawn

        # Geometry
        self.girthness = 60
        self.segment_length = self.girthness * 0.8
        self.origin = origin
        self.snake_pos: list[tuple[float, float]] = [
            spawn,
            (spawn[0], spawn[1] - self.segment_length)
        ]

        # Atachments
        self.weapon_start_index = 1
        self.weapon_interval = 3
        self.weapon_slots: dict[int, Optional[Weapon]] = {}

        # Cached values
        self.radius_outer = self.girthness / 2
        self.radius_inner = self.girthness / 2.5
        self.radius_head_outer = self.girthness / 1.5
        self.radius_head_inner = self.girthness / 1.75
        self.radius_eye = self.girthness / 5
        self.radius_pupil = self.radius_eye * 0.5
        self.eye_distance = self.girthness * 0.3

    # ──────────────────────────────────────────────────────────────
    # Input & State Update
    # ──────────────────────────────────────────────────────────────

    def set_target_pos(self) -> None:
        """
        Updates the target position based on current mouse position.
        """
        mouse_pos = pygame.mouse.get_pos()
        self.target_pos = (mouse_pos[0] - self.origin[0], mouse_pos[1] - self.origin[1])

    def calc_move_pos(self) -> None:
        """
        Moves the snake head toward the target position using capped movement speed.
        """
        head = pygame.Vector2(self.snake_pos[0])
        target = pygame.Vector2(self.target_pos)
        direction = target - head
        distance = direction.length()

        if distance < self.move_speed:
            self.snake_pos[0] = self.target_pos
        else:
            direction.scale_to_length(self.move_speed)
            self.snake_pos[0] = (head + direction).xy

    def update_weapons(self):
        for idx, weapon in self.weapon_slots.items():
            if weapon:
                weapon.pos = pygame.Vector2(self.snake_pos[idx])

    def update_body_positions(self) -> None:
        """
        Updates positions of body segments to follow the segment before them.
        """
        self.calc_move_pos()
        for i in range(1, len(self.snake_pos)):
            current = self.snake_pos[i]
            prev = self.snake_pos[i - 1]

            delta = pygame.Vector2(current) - pygame.Vector2(prev)
            distance = delta.length()

            if distance > self.segment_length:
                delta.scale_to_length(self.segment_length)
                new_pos = pygame.Vector2(prev) + delta
                self.snake_pos[i] = new_pos.xy
        self.update_weapons()

    # ──────────────────────────────────────────────────────────────
    # Snake Structure
    # ──────────────────────────────────────────────────────────────

    def add_snake_part(self) -> None:
        """
        Appends a new body segment at the end of the snake.
        """
        tail = pygame.Vector2(self.snake_pos[-1])
        before_tail = pygame.Vector2(self.snake_pos[-2])
        direction = (tail - before_tail).normalize()
        new_segment = tail - direction * self.segment_length
        self.snake_pos.append(new_segment.xy)

    # ──────────────────────────────────────────────────────────────
    # Rendering Helpers
    # ──────────────────────────────────────────────────────────────

    def bezier_curve(self, start_point, end_point, control_point, resolution: int) -> list:
        """
        Generates a quadratic Bezier curve through three points.

        Args:
            start_point: The first anchor point.
            end_point: The second anchor point.
            control_point: The midpoint control point.
            resolution: Number of interpolated points.

        Returns:
            List of curve points.
        """
        points = []
        for i in range(resolution + 1):
            t = i / resolution
            x = (1 - t) ** 2 * start_point[0] + 2 * (1 - t) * t * control_point[0] + t ** 2 * end_point[0]
            y = (1 - t) ** 2 * start_point[1] + 2 * (1 - t) * t * control_point[1] + t ** 2 * end_point[1]
            points.append((x, y))
        return points

    def player_eyes(self) -> None:
        """
        Draws two forward-facing eyes on the snake's head using direction vector.
        """
        head = self.snake_pos[0]
        neck = self.snake_pos[1]
        direction = pygame.Vector2(head) - pygame.Vector2(neck)

        if direction.length_squared() == 0:
            return

        dir_norm = direction.normalize()
        perp = pygame.Vector2(-dir_norm.y, dir_norm.x)

        forward_offset = self.girthness * 0.2
        head_screen = pygame.Vector2(self.origin) + pygame.Vector2(head) + dir_norm * forward_offset

        left_eye_pos = head_screen + perp * self.eye_distance
        right_eye_pos = head_screen - perp * self.eye_distance

        pygame.draw.circle(self.screen, WHITE, left_eye_pos, self.radius_eye)
        pygame.draw.circle(self.screen, WHITE, right_eye_pos, self.radius_eye)

        pupil_offset = dir_norm * (self.girthness * 0.1)
        pygame.draw.circle(self.screen, BLACK, left_eye_pos + pupil_offset, self.radius_pupil)
        pygame.draw.circle(self.screen, BLACK, right_eye_pos + pupil_offset, self.radius_pupil)

    def draw_attachment_nodes(self, dragging_weapon: Optional[Weapon] = None) -> None:
        """
        Draws visual markers for possible weapon attachment nodes.
        Highlights the closest one if dragging a weapon.
        """

        closest_idx = None
        min_distance = float('inf')

        if dragging_weapon:
            for idx in range(self.weapon_start_index, len(self.snake_pos), self.weapon_interval):
                segment_pos = pygame.Vector2(self.snake_pos[idx])
                dist = (segment_pos - dragging_weapon.pos).length()
                if dist < min_distance:
                    min_distance = dist
                    closest_idx = idx

        for idx in range(self.weapon_start_index, len(self.snake_pos)-1, self.weapon_interval):
            segment_pos = pygame.Vector2(self.snake_pos[idx])
            screen_pos = pygame.Vector2(self.origin) + segment_pos

            if idx == closest_idx and dragging_weapon:
                # Highlight closest node in yellow
                pygame.draw.circle(self.screen, (255, 255, 0), screen_pos, 10)
            else:
                # Normal available node in cyan
                pygame.draw.circle(self.screen, (0, 255, 255), screen_pos, 5)
        print(f"Weapon world pos: {dragging_weapon.pos}")
        print(f"Segment world pos: {segment_pos}")
        print(f"Distance: {(segment_pos - dragging_weapon.pos).length()}")

    # ──────────────────────────────────────────────────────────────
    # Drawing & Rendering
    # ──────────────────────────────────────────────────────────────

    def draw(self) -> None:
        """
        Renders the snake using Bezier curves and overlapping colored circles.
        """
        body_to_draw = []

        for i in reversed(range(1, len(self.snake_pos) - 1)):
            body_coords = self.snake_pos[i]
            screen_pos = pygame.Vector2(self.origin) + pygame.Vector2(body_coords)
            if not self.screen.get_rect().collidepoint(screen_pos):
                continue

            prev_body_coords = (
                (self.snake_pos[i - 1][0] + body_coords[0]) / 2,
                (self.snake_pos[i - 1][1] + body_coords[1]) / 2
            )
            next_body_coords = (
                (self.snake_pos[i + 1][0] + body_coords[0]) / 2,
                (self.snake_pos[i + 1][1] + body_coords[1]) / 2
            )
            body_to_draw.extend(self.bezier_curve(prev_body_coords, next_body_coords, body_coords, 5))

        # Offset all points to screen coordinates
        screen_points = [(self.origin[0] + p[0], self.origin[1] + p[1]) for p in body_to_draw]

        for p in screen_points:
            pygame.draw.circle(self.screen, BLACK, p, self.radius_outer)
        pygame.draw.circle(self.screen, BLACK, pygame.Vector2(self.origin) + pygame.Vector2(self.snake_pos[0]), self.radius_head_outer)

        for p in screen_points:
            pygame.draw.circle(self.screen, GREEN, p, self.radius_inner)
        pygame.draw.circle(self.screen, LIGHT_GREEN, pygame.Vector2(self.origin) + pygame.Vector2(self.snake_pos[0]), self.radius_head_inner)

        self.player_eyes()

    def render(self, origin: tuple[float, float]) -> None:
        """
        Public method to update the snake's origin and draw it to the screen.
        """
        self.origin = origin
        self.draw()
        for weapon in self.weapon_slots.values():
            if weapon:
                weapon.draw(self.screen, self.origin)
