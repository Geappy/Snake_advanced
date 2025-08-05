"""the main entry function of the game"""

import pygame
import sys

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC

from player_character import Player
from npc_character import NPCCharacter, NPCRegister
from hub import HUB


class MainGameOBJ():
    def __init__(self) -> None:
        # setup the game using pygame
        pygame.init()
        pygame.display.set_caption("Smakes and guns.dinemum")
        # pygame.display.set_icon(pygame.image.load('textures/icon.png'))
        self.screen = pygame.display.set_mode()
        cprint("game setup sucsessful", VC.MAGENTA)

        width, height = self.screen.get_size()
        self.hub = HUB(self.screen, (0,0))

        self.move: bool = False

        # setup all the characters
        self.player = Player(self.screen)
        self.npc_characters: dict[str, NPCCharacter] = {}

        self.npc_characters[NPCRegister.WIZARD] = NPCCharacter(self.screen, NPCRegister.WIZARD)
        self.npc_characters[NPCRegister.WIZARD].active = True

        cprint("character setup sucsessful ", VC.MAGENTA)

    def handle_input(self):
        """loocks for player input and handles it"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.kill_game()

            elif event.type == pygame.KEYDOWN:
                event_key = pygame.key.name(event.key)
                if event_key == "s":
                    cprint("s", VC.YELLOW)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # left click
                    self.move = True

                elif event.button == 3: # right click
                    self.player.add_snake_part()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # left click
                    self.move = False
                    # set target to zero
                    self.player.target_pos = self.player.snake_pos[0]

                elif event.button == 3: # right click
                    pass

    def render(self) -> None:
        """render all the importaint stuff"""
        if self.move:
            # self.npc_characters[NPCRegister.WIZARD].set_target_pos(pygame.mouse.get_pos())
            self.player.set_target_pos(pygame.mouse.get_pos())

        self.screen.fill((0, 0, 0))
        self.player.update_body_positions()

        player_x, player_y = self.player.snake_pos[0]
        width, height = self.screen.get_size()
        center_x = width // 2
        center_y = height // 2
        offset = (center_x - player_x, center_y - player_y)

        self.hub.render(offset)
        self.player.render(offset)
        for obj in self.npc_characters.values():
            obj.render(offset)
        pygame.display.flip()

    def kill_game(self) -> None:
        """ends the game"""
        pygame.quit()
        sys.exit()
        cprint("Game destroyed", VC.MAGENTA)

def main() -> None:
    game = MainGameOBJ()
    clock = pygame.time.Clock()

    while True:
        game.handle_input()
        game.render()
        clock.tick(60)

if __name__ == "__main__":
    main()
