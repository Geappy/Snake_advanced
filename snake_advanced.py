"""the more advanced snake module to animate a smooth snake that has pysics"""

import pygame
import math


FPS = 60

class FancySnake:
    def __init__(self, screen):
        """
        Initiates the snake class to be redy to work on

        Args:
            screen: The screen to print on
        """
        self.screen = screen

        self.max_speed = 8
        self.acceleration = 1
        self.deceleration = 1

        self.girthness = 50
        self.segment_length = self.girthness * 0.8

        self.snake_pos: dict = {}
        self.snake_pos[0] = ((1200 - 50) // 2,(900 - 50) // 2)
        self.snake_pos[1] = ((1200 - 50) // 2,(900 - 50) // 2 - self.segment_length)
        self.angle = math.atan2(0, - self.segment_length)

        self.physics = {
            'up': 0,
            'down': 0,
            'left': 0,
            'right': 0,
        }

    def add_snake_part(self):
        """
        Add one snake bodaypart to the end of the snake
        """
        x = self.snake_pos[len(self.snake_pos)-2][0] - self.snake_pos[len(self.snake_pos)-1][0]
        y = self.snake_pos[len(self.snake_pos)-2][1] - self.snake_pos[len(self.snake_pos)-1][1]

        angle_rad = math.atan2(x, y)

        x = self.segment_length * math.sin(angle_rad)
        y = self.segment_length * math.cos(angle_rad)

        self.snake_pos[len(self.snake_pos)] = (self.snake_pos[len(self.snake_pos)-1][0] - x, self.snake_pos[len(self.snake_pos)-1][1] - y)

    def check_colition(self, target, points_to_check, range_threshold=25):
        """
        Check if a target (x, y) tuple is within a given range of other (x, y) tuples in a dictionary or list.

        Args:
            target: The target (x, y) tuple to check.
            points_to_check: The dictionary or list containing (x, y) tuples.
            range_threshold: The range threshold for the check.
        Returns:
            tupel: (x, y) coordinates of the colition
        """
        if isinstance(points_to_check, list):
            point_list = points_to_check
        elif isinstance(points_to_check, dict):
            point_list = points_to_check.values()
        else:
            return None

        for x, y in point_list:
            # Calculate the Euclidean distance between the target and each point in the dictionary
            distance = ((target[0] - x) ** 2 + (target[1] - y) ** 2) ** 0.5
            if distance <= range_threshold:
                return (x, y)
        return None
    
    def remove_tail_from_coordinate(self, colition_coords):
        """
        Check if a target (x, y) tuple is within a given range of other (x, y) tuples in a dictionary or list.

        Args:
            colition_coords: the coordinates from where to remove the tail
        Returns:
            list: a list of all the deleated coordinates
        """
        found_index = None
        for key, value in self.snake_pos.items():
            if value == colition_coords:
                found_index = key
                break

        deleate_coods = []
        if found_index is not None:
            keys_to_remove = list(range(found_index, len(self.snake_pos)))
            for key in keys_to_remove:
                deleate_coods.append(self.snake_pos[key])
                del self.snake_pos[key]
        
        return deleate_coods

    def move(self, directions: dict):
        """
        Changes the self.snake_pos to make the snake move

        Args:
            directions: A dict that contains the currently pressed directions
        """
        self.update_speed(directions)
        x_y = self.calculate_new_head_position_coordinates()
        if x_y != (0, 0):
            self.update_new_head_position(x_y)
            self.calculate_and_update_body_positions()

    def update_speed(self, directions: dict):
        """
        Args:
            directions: A dict that contains the currently pressed directions
        """
        for key, value in directions.items():
            if value and self.physics[key] < self.max_speed:
                self.physics[key] += self.acceleration
            elif not value and self.physics[key] > 0:
                self.physics[key] -= self.deceleration
            if self.physics[key] < 0:
                self.physics[key] = 0

    def calculate_new_head_position_coordinates(self):
        """
        Calculates the new x and y positions if the snake is suposed to move

        Returns:
            x: new x position
            y: new y position
        """
        y = self.physics['down']-self.physics['up']
        x = self.physics['right']-self.physics['left']

        # calculate coordinates while keep constant speed
        if x!=0 or y!=0:
            # calculate speed in case we x and y are not equal
            speed = math.sqrt(x**2 + y**2)

            self.angle = math.atan2(x, y)

            self.check_if_head_moves_into_bodey()

            x = speed * math.sin(self.angle)
            y = speed * math.cos(self.angle)
        
        return (x, y)
    
    def check_if_head_moves_into_bodey(self):

        print(self.snake_pos[0][0]-self.snake_pos[1][0], self.snake_pos[0][1]-self.snake_pos[1][1])
        old_angle = math.atan2(self.snake_pos[0][0]-self.snake_pos[1][0], self.snake_pos[0][1]-self.snake_pos[1][1])
        colition_angle = math.asin(self.girthness/2/self.segment_length)

        print(math.degrees(colition_angle))
        print(math.degrees(old_angle))
        print(math.degrees(old_angle+colition_angle), math.degrees(self.angle), math.degrees(old_angle-colition_angle))
        if old_angle+colition_angle > self.angle > old_angle-colition_angle:
            print("Fuck jea?")
    
    def update_new_head_position(self, x_y):
        """
        Adds the new coordinates to the position list,
        and removes the last one

        Args:
            x_y: new x position and new y position
        """
        head_coordinates = self.snake_pos[0]
        new_x = head_coordinates[0] + x_y[0]
        new_y = head_coordinates[1] + x_y[1]
        self.snake_pos[0] = (new_x, new_y)

    def calculate_and_update_body_positions(self):
        """
        Calculate the correcs positions of all the body parts
        """
        for i, bodypart in self.snake_pos.items():
            if i != 0:
                previous_bodypart = self.snake_pos[i - 1]
        
                delta_x = bodypart[0] - previous_bodypart[0]
                delta_y = bodypart[1] - previous_bodypart[1]

                hypotenuse = math.sqrt(delta_x ** 2 + delta_y ** 2)
        
                if hypotenuse > self.segment_length:

                    angle_rad = math.atan2(delta_y, delta_x)
                    
                    new_x = previous_bodypart[0] + self.segment_length * math.cos(angle_rad)
                    new_y = previous_bodypart[1] + self.segment_length * math.sin(angle_rad)
                    
                    self.snake_pos[i] = (new_x, new_y)

    def bezier_curve(self, start_point, end_point, control_point, resolution=5):
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

    def draw(self):
        """
        Draws the snake in the position given by self.snake_pos
        """
        body_to_draw = []
        snake_pos_items = list(self.snake_pos.items())
        for i, body_coords in reversed(snake_pos_items[1:-1]):
            prev_body_coords = (self.snake_pos[i - 1][0] + body_coords[0])/2, (self.snake_pos[i - 1][1] + body_coords[1])/2
            next_body_coords = (self.snake_pos[i + 1][0] + body_coords[0])/2, (self.snake_pos[i + 1][1] + body_coords[1])/2

            for bezier_point in self.bezier_curve(prev_body_coords, next_body_coords, body_coords):
                body_to_draw.append(bezier_point)
        for i, point_to_draw in enumerate(body_to_draw):
            pygame.draw.circle(self.screen, (0, 0, 0), point_to_draw, self.girthness/2)
        pygame.draw.circle(self.screen, (0, 0, 0), (self.snake_pos[0][0], self.snake_pos[0][1]), self.girthness/1.5)
        for point_to_draw in body_to_draw:
            pygame.draw.circle(self.screen, (0, 255, 0), point_to_draw, self.girthness/2.5)
        pygame.draw.circle(self.screen, (100, 255, 100), (self.snake_pos[0][0], self.snake_pos[0][1]), self.girthness/1.75)
        # for i, body_coords in reversed(snake_pos_items):
        #     pygame.draw.circle(self.screen, (255, 0, 0), body_coords, self.girthness/3)


def display_severd_tail(screen, severed_tail: list):
    for severed_tail_list in severed_tail:
        for point_to_draw in severed_tail_list:
            pygame.draw.circle(screen, (0, 0, 0), point_to_draw, 50/2)
        for point_to_draw in severed_tail_list:
            pygame.draw.circle(screen, (0, 255, 0), point_to_draw, 50/2.5)

def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (1200, 900),
    )

    snake = FancySnake(screen)
    clock = pygame.time.Clock()

    directions = {
        'up': False,
        'down': False,
        'left': False,
        'right': False,
    }

    severed_tail = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                chang_value = event.type == pygame.KEYDOWN
                event_key = pygame.key.name(event.key)
                if event_key == "w":
                    directions['up'] = chang_value
                elif event_key == "s":
                    directions['down'] = chang_value
                elif event_key == "a":
                    directions['left'] = chang_value
                elif event_key == "d":
                    directions['right'] = chang_value
            if event.type == pygame.KEYDOWN and pygame.key.name(event.key) == "return":
                    snake.add_snake_part()

        screen.fill((200, 200, 200))

        colition_coords = snake.check_colition(snake.snake_pos[0], list(snake.snake_pos.values())[2:])
        if colition_coords:
            severed_tail.append(snake.remove_tail_from_coordinate(colition_coords))

        if True in directions.values():
            snake.move(directions)
        display_severd_tail(screen, severed_tail)
        snake.draw()
        pygame.display.flip()

        clock.tick(FPS)

if __name__ == "__main__":
    main()

