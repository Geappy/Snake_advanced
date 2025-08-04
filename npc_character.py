"""the structure of NPC characters"""

import pygame

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC


class NPCRegister():
    """a register of all the NPCs"""

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


class NPCCharacter():
    def __init__(self, screen, character: str) -> None:
        self.screen: pygame.display = screen
        self.character: str = character
        self.render: bool = False
