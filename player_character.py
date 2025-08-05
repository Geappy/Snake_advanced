"""the structure of NPC characters"""

import math
import pygame

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC


class Player():
    def __init__(self, screen, spawn: tuple, origin: tuple) -> None:
        """
        Initiates the snake class to be redy to work on

        Args:
            screen: The screen to print on
        """
        self.screen: pygame.display = screen

        self.max_speed: int = 8
        self.acceleration: int = 1
        self.deceleration: int = 1

        self.girthness: int = 60
        self.segment_length: float = self.girthness * 0.8

        self.move_speed: int = 15
        self.target_pos: tuple = spawn

        self.origin: tuple = origin
        self.snake_pos: list[tuple] = []
        self.snake_pos.append(spawn)
        self.snake_pos.append((spawn[0], spawn[1] - self.segment_length))

    def add_snake_part(self):
        """
        Add one snake bodaypart to the end of the snake
        """
        x = self.snake_pos[len(self.snake_pos)-2][0] - self.snake_pos[len(self.snake_pos)-1][0]
        y = self.snake_pos[len(self.snake_pos)-2][1] - self.snake_pos[len(self.snake_pos)-1][1]

        angle_rad = math.atan2(x, y)

        x = self.segment_length * math.sin(angle_rad)
        y = self.segment_length * math.cos(angle_rad)

        last_x, last_y = self.snake_pos[-1]
        self.snake_pos.append((last_x - x, last_y - y))


    def calc_move_pos(self) -> None:
        """to set new position for fluid movement"""
        # get the lengths of the right triangle
        delta_x = self.target_pos[0] - self.snake_pos[0][0]
        delta_y = self.target_pos[1] - self.snake_pos[0][1]

        hypotenuse = math.sqrt(delta_x ** 2 + delta_y ** 2)

        # if we are close to the target, snap to the target
        if hypotenuse < self.move_speed:
            self.snake_pos[0] = self.target_pos

        # calsculate the new animated pos
        else:
            angle_rad = math.atan2(delta_y, delta_x)
            new_x = self.snake_pos[0][0] + self.move_speed * math.cos(angle_rad)
            new_y = self.snake_pos[0][1] + self.move_speed * math.sin(angle_rad)

            self.snake_pos[0] = (new_x, new_y)

    def update_body_positions(self) -> None:
        """
        Calculate the correcs positions of all the body parts
        """
        self.calc_move_pos()
        for i, bodypart in enumerate(self.snake_pos):
            if i == 0:
                continue
            previous_bodypart = self.snake_pos[i - 1]
    
            delta_x = bodypart[0] - previous_bodypart[0]
            delta_y = bodypart[1] - previous_bodypart[1]

            hypotenuse = math.sqrt(delta_x ** 2 + delta_y ** 2)
    
            if hypotenuse <= self.segment_length:
                continue

            angle_rad = math.atan2(delta_y, delta_x)
            
            new_x = previous_bodypart[0] + self.segment_length * math.cos(angle_rad)
            new_y = previous_bodypart[1] + self.segment_length * math.sin(angle_rad)
            
            self.snake_pos[i] = (new_x, new_y)

    def bezier_curve(self, start_point, end_point, control_point, resolution=5) -> list:
        """
        Compute points on a Bezier curve defined by start_point, end_point, and control_point.

        Args:
            start_point: Tuple (x, y) of the starting point
            end_point: Tuple (x, y) of the ending point
            control_point: Tuple (x, y) of the control point
            resolution: How manny points are returned

        Returns:
            points: List of tuples representing points on the Bezier curve
        """
        points = []
        for i in range(resolution + 1):
            t = i / resolution
            x = (1 - t) ** 2 * start_point[0] + 2 * (1 - t) * t * control_point[0] + t ** 2 * end_point[0]
            y = (1 - t) ** 2 * start_point[1] + 2 * (1 - t) * t * control_point[1] + t ** 2 * end_point[1]
            points.append((x, y))
        return points
    
    def set_target_pos(self) -> None:
        """sets coordinates to move towards"""
        mouse_pos = pygame.mouse.get_pos()  # screen position
        self.target_pos = (mouse_pos[0] - self.origin[0], mouse_pos[1] - self.origin[1])

    def draw(self) -> None:
        """
        Draws the snake in the position given by self.snake_pos
        """
        body_to_draw = []

        for i in reversed(range(1, len(self.snake_pos) - 1)):
            body_coords = self.snake_pos[i]
            prev_body_coords = (
                (self.snake_pos[i - 1][0] + body_coords[0]) / 2,
                (self.snake_pos[i - 1][1] + body_coords[1]) / 2
            )
            next_body_coords = (
                (self.snake_pos[i + 1][0] + body_coords[0]) / 2,
                (self.snake_pos[i + 1][1] + body_coords[1]) / 2
            )
            for bezier_point in self.bezier_curve(prev_body_coords, next_body_coords, body_coords):
                body_to_draw.append(bezier_point)

        for point_to_draw in body_to_draw:
            point_fom_origin = (self.origin[0] + point_to_draw[0], self.origin[1] + point_to_draw[1])
            pygame.draw.circle(self.screen, (0, 0, 0), point_fom_origin, self.girthness / 2)
        point_fom_origin = (self.origin[0] + self.snake_pos[0][0], self.origin[1] + self.snake_pos[0][1])
        pygame.draw.circle(self.screen, (0, 0, 0), point_fom_origin, self.girthness / 1.5)

        for point_to_draw in body_to_draw:
            point_fom_origin = (self.origin[0] + point_to_draw[0], self.origin[1] + point_to_draw[1])
            pygame.draw.circle(self.screen, (0, 255, 0), point_fom_origin, self.girthness / 2.5)
        point_fom_origin = (self.origin[0] + self.snake_pos[0][0], self.origin[1] + self.snake_pos[0][1])
        pygame.draw.circle(self.screen, (100, 255, 100), point_fom_origin, self.girthness / 1.75)

        # for i, body_coords in enumerate(reversed(self.snake_pos)):
        #     pygame.draw.circle(self.screen, (255, 0, 0), body_coords, self.girthness/3)

    def render(self, origin: tuple) -> None:
        """renders and updates the plaxer character"""
        self.origin = origin
        self.draw()
