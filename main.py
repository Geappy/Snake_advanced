"""the main entry function of the game"""

import pygame
import sys

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC

from player_character import Player
from npc_character import NPCCharacter, NPCRegister, NamedNPCs
from hub import HUB
from player_attachments import Weapon


class MainGameOBJ():
    def __init__(self) -> None:
        # setup the game using pygame
        pygame.init()
        pygame.display.set_caption("Smakes and guns.dinemum")
        # pygame.display.set_icon(pygame.image.load('textures/icon.png'))
        self.screen = pygame.display.set_mode()
        cprint("game setup sucsessful", VC.MAGENTA)

        width, height = self.screen.get_size()
        self.origin: tuple[float, float] = (width * 0.5, height * 0.5)

        self.hub = HUB(self.screen, self.origin, (0, 0))

        self.move: bool = False

        self.ground_weapons = [
            Weapon((100, 200)),
            Weapon((300, 400)),
        ]

        # setup all the characters
        self.player = Player(self.screen, self.origin, (0, 0))
        for _ in range(3):
            self.player.add_snake_part()
        self.npc_characters: dict[str, NPCCharacter] = {}

        self.npc_characters[NamedNPCs.NIBBIN] = NPCCharacter(
            self.screen,
            self.origin,
            NPCRegister.WIZARD,
            spawn=(-600, -200),
            active=True
        )

        cprint("character setup sucsessful ", VC.MAGENTA)

    def handle_input(self):
        """loocks for player input and handles it"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.kill_game()

            elif event.type == pygame.KEYDOWN:
                self.player.add_snake_part()
                event_key = pygame.key.name(event.key)
                if event_key == "s":
                    cprint("s", VC.YELLOW)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # left click
                    self.move = True

                elif event.button == 3: # right click
                    for weapon in self.ground_weapons:
                        weapon.try_pickup(self.player, pygame.mouse.get_pos())

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
            self.player.set_target_pos()

        self.screen.fill((0, 0, 0))

        # Let player update itself (but not calculate origin)
        self.player.update_body_positions()

        # Calculate origin based on player head position
        player_head = self.player.snake_pos[0]
        screen_w, screen_h = self.screen.get_size()
        self.origin = (
            screen_w * 0.5 - player_head[0],
            screen_h * 0.5 - player_head[1]
        )

        # Pass the origin to all renderable objects
        self.hub.render(self.origin)
        for weapon in self.ground_weapons:
            if not weapon.attached:
                weapon.draw(self.screen, self.origin)
        self.player.render(self.origin)
        for npc in self.npc_characters.values():
            npc.render(self.origin)

        pygame.display.flip()

    def kill_game(self) -> None:
        """ends the game"""
        pygame.quit()
        sys.exit()
        cprint("Game destroyed", VC.MAGENTA)

def main() -> None:
    game = MainGameOBJ()
    clock = pygame.time.Clock()

    counter: int = 0
    while True:
        game.handle_input()
        game.render()
        clock.tick(60)
        counter += 1
        if counter == 300:
            game.npc_characters[NamedNPCs.NIBBIN].set_target_pos((1000, 600))
        elif counter == 600:
            game.npc_characters[NamedNPCs.NIBBIN].set_target_pos((-1000, -600))
            counter = 0

if __name__ == "__main__":
    main()
