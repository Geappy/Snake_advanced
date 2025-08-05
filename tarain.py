"""the structure of the tarain"""

import pygame

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC


class Tarain():
    def __init__(self, screen) -> None:
        self.screen: pygame.Surface = screen
