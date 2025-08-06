"""the main entry function of the game"""

import sys
import pygame
from typing import Optional

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC

from player_character import Player
from npc_character import NPCCharacter, NPCRegister, NamedNPCs
from hub import HUB
from player_attachments import Weapons, WeaponRegister


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

        self.dragging_weapon: Optional[Weapons] = None
        self.ground_weapons = [
            Weapons(self.origin, (100, 200), weapon_type=WeaponRegister.GUN),
            Weapons(self.origin, (300, 400), weapon_type=WeaponRegister.SWORD),
            Weapons(self.origin, (500, 300), weapon_type=WeaponRegister.HEALING),
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
                    self.dragging_weapon = None  # Reset

                    for weapon in self.ground_weapons:
                        weapon.handle_mouse_down(pygame.mouse.get_pos(), self.origin, self.player)
                        if weapon.dragging:
                            self.dragging_weapon = weapon
                            break

                elif event.button == 3: # right click
                    self.move = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # left click
                    for weapon in self.ground_weapons:
                        weapon.handle_mouse_up(self.player, self.origin)
                        self.dragging_weapon = None

                elif event.button == 3: # right click
                    self.move = False
                    # set target to zero
                    self.player.target_pos = self.player.snake_pos[0]

    def render(self) -> None:
        """Render all important game objects each frame."""
        
        # Update target position if the player is moving
        if self.move:
            self.player.set_target_pos()

        # Clear screen
        self.screen.fill((0, 0, 0))

        # Update player position (but not origin yet)
        self.player.update_body_positions()

        # Calculate world-to-screen origin based on player head position
        player_head = self.player.snake_pos[0]
        screen_w, screen_h = self.screen.get_size()
        self.origin = (
            screen_w * 0.5 - player_head[0],
            screen_h * 0.5 - player_head[1]
        )

        # Render HUB
        self.hub.render(self.origin)

        # Render Player
        self.player.render(self.origin)

        # Draw possible attachment nodes (if dragging a weapon)
        if self.dragging_weapon:
            self.player.draw_attachment_nodes(self.dragging_weapon)

        # Update and draw all weapons
        for weapon in self.ground_weapons:
            if weapon.dragging or not weapon.attached:
                weapon.update(self.origin)
            weapon.draw(self.screen, self.origin)

        # Render NPCs
        for npc in self.npc_characters.values():
            npc.render(self.origin)

        # Flip display
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
