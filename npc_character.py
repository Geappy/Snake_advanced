"""the structure of NPC characters"""

import os
import math
import pygame

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC


class NPCRegister():
    # friendly NPC's
    WIZARD = "wizard"

    VILLAGE_NPCS = [
        WIZARD,
    ]

    # hostile NPC's
    VAMPIRE = "vampire"

    ENEMY_NPCS = [
        VAMPIRE,
    ]

    # animation states
    IDLE = "idle"
    RUNNING = "running"
    DEAD = "dead"


class NPCCharacter():
    def __init__(self, screen, character: str, spawn: tuple, origin: tuple) -> None:
        self.screen: pygame.display = screen
        self.active: bool = False
        self.pos: tuple = spawn
        self.origin: tuple = origin
        self.target_pos: tuple = self.pos
        self.move_speed: int = 8
        self.sice: int = 200

        # animation var
        self.animation_state: str = NPCRegister.IDLE
        self.character: str = character
        self.frame: int = 0
        self.frame_timer: int = 0
        self.frame_delay: int = 10
        self.animation_sice = self.count_images_in_folder()

    def count_images_in_folder(self, extensions={".png", ".jpg", ".jpeg"}) -> int:
        folder_path = f"textures/npcs/{self.character}/{self.animation_state}"
        return sum(
            1 for file in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, file)) and os.path.splitext(file)[1].lower() in extensions
        )
    
    def change_animation(self, new_state: str) -> None:
        if self.animation_state == new_state:
            return
        self.animation_state = new_state
        self.animation_sice = self.count_images_in_folder()
        self.frame = 0
        self.frame_timer = 0

    def set_target_pos(self, new_pos) -> None:
        self.target_pos = (self.pos[0] + new_pos[0], self.pos[1] + new_pos[1])
        self.change_animation(NPCRegister.RUNNING)
        self.frame_delay = 3

    def calc_move_pos(self) -> None:
        """to set new position for fluid movement"""
        # get the lengths of the right triangle
        delta_x = self.target_pos[0] - self.pos[0]
        delta_y = self.target_pos[1] - self.pos[1]

        hypotenuse = math.sqrt(delta_x ** 2 + delta_y ** 2)

        # if we are close to the target, snap to the target
        if hypotenuse < self.move_speed:
            self.pos = self.target_pos
            self.change_animation(NPCRegister.IDLE)
            self.frame_delay = self.move_speed * 2

        # calsculate the new animated pos
        else:
            angle_rad = math.atan2(delta_y, delta_x)
            new_x = self.pos[0] + self.move_speed * math.cos(angle_rad)
            new_y = self.pos[1] + self.move_speed * math.sin(angle_rad)

            self.pos = (new_x, new_y)

    def render(self, origin: tuple) -> None:
        self.origin = origin
        if not self.active:
            self.pos = self.target_pos
            return
        if self.target_pos != self.pos:
            self.calc_move_pos()

        image_path: str = f"textures/npcs/{self.character}/{self.animation_state}/{self.frame}.png"
        image = pygame.image.load(image_path).convert_alpha()

        # deal with sice and right positioning
        original_width, original_height = image.get_size()
        scale_factor = self.sice / original_height
        new_width = int(original_width * scale_factor)
        centered_pos = (self.pos[0] - new_width * 0.5, self.pos[1] - self.sice * 0.8)
        origin_pos = (self.origin[0] + centered_pos[0], self.origin[1] + centered_pos[1])

        scaled_image = pygame.transform.scale(image, (new_width, self.sice))
        self.screen.blit(scaled_image, origin_pos)

        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame += 1
            self.frame_timer = 0
            if self.frame >= self.animation_sice:
                self.frame = 0

