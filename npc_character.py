"""the structure of NPC characters"""

import os
import pygame

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC


class NPCRegister():
    # friendly NPC's
    WORKER = "worker"
    MERCHANT = "merchant"
    GUARD = "guard"

    VILLAGE_NPCS = [
        WORKER,
        MERCHANT,
        GUARD
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
    def __init__(self, screen, character: str, spawn: tuple = (350, 350)) -> None:
        self.screen: pygame.display = screen
        self.active: bool = False
        self.pos: tuple = spawn

        # animation var
        self.animation_state: str = NPCRegister.IDLE
        self.character: str = character
        self.frame: int = 0
        self.animation_sice = self.count_images_in_folder()

    def count_images_in_folder(self, extensions={".png", ".jpg", ".jpeg"}) -> int:
        folder_path = f"textures/npcs/{self.character}/{self.animation_state}"
        return sum(
            1 for file in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, file)) and os.path.splitext(file)[1].lower() in extensions
        )
    
    def change_animation(self, new_state: str) -> None:
        self.animation_state = new_state
        self.animation_sice = self.count_images_in_folder()

    def render(self) -> None:
        if not self.active:
            return
        image_path: str = f"textures/npcs/{self.character}/{self.animation_state}/{self.frame}.png"
        image = pygame.image.load(image_path).convert_alpha()
        self.screen.blit(image, self.pos)
        self.frame += 1
        if self.frame >= self.animation_sice:
            self.frame = 0
