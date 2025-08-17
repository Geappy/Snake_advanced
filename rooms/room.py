"""the structure of the tarain"""

import pygame

from assistent_skripts.color_print import custom_print as cprint, ValidColors as VC

from rooms.walls import Wall


class Room:
    def __init__(self, screen: pygame.Surface, origin: tuple[float, float], spawn: tuple[float, float], background_path: str):
        self.screen = screen
        self.origin = origin
        self.pos = spawn

        self.background = self.load_background(background_path)
        image_width, image_height = self.background.get_size()
        self.pos = (self.pos[0] - (image_width * 0.5), self.pos[1] - (image_height * 0.5))

        self.walls: list[Wall] = []

    def load_background(self, path: str) -> pygame.Surface:
        image = pygame.image.load(path).convert_alpha()
        original_width, original_height = image.get_size()
        size = 900
        scale_factor = size / original_height
        new_width = int(original_width * scale_factor)
        return pygame.transform.scale(image, (new_width, size))

    def render(self, origin: tuple[float, float]) -> None:
        self.origin = origin
        draw_pos = (self.origin[0] + self.pos[0], self.origin[1] + self.pos[1])
        self.screen.blit(self.background, draw_pos)

        for wall in self.walls:
            wall.render(self.screen, origin)


class HubRoom(Room):
    def __init__(self, screen, origin, spawn):
        super().__init__(screen, origin, spawn, "textures/tarain/hub/HUB.png")
        self.walls.append(Wall(100, 100, 500, 500))
        self.walls.append(Wall(-500, 400, 60, 200))
