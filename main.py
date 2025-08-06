"""Main game loop and setup for Snakes and Guns.dinemum"""

import sys
import pygame
from typing import Optional

from assistent_skripts.color_print import custom_print as cprint
from assistent_skripts.color_print import ValidColors as VC

from player_character import Player
from npc_character import NPCCharacter, NPCRegister, NamedNPCs
from hub import HUB
from player_attachments import Attachment, WeaponRegister, Projectile, SwordSwingProjectile
from player_hud import PlayerHUD, HUDRegister


class Game:
    def __init__(self) -> None:
        """Initialize the game window, characters, HUD, and game state."""
        pygame.init()
        pygame.display.set_caption("Snakes and Guns.dinemum")
        self.screen = pygame.display.set_mode()
        cprint("Game setup successful", VC.MAGENTA)

        self.origin = self.get_screen_center()

        self.clock = pygame.time.Clock()
        self.running = True
        self.move_enabled = False

        # Game Systems
        self.hub = HUB(self.screen, self.origin, (0, 0))
        self.player = self._init_player()
        self.npc_characters = self._init_npcs()
        self.ground_weapons = self._init_ground_weapons()
        self.player_hud = PlayerHUD(self.screen, self.player)

        # Interaction and state
        self.dragging_weapon: Optional[Attachment] = None
        self.projectiles: list[Projectile] = []

        self.tick_counter = 0
        cprint("Character setup successful", VC.MAGENTA)

    def _init_player(self) -> Player:
        """Create the player and their initial body segments."""
        player = Player(self.screen, self.origin, (0, 0))
        for _ in range(3):
            player.add_snake_part()
        return player

    def _init_npcs(self) -> dict[str, NPCCharacter]:
        """Spawn initial NPC characters."""
        return {
            NamedNPCs.NIBBIN: NPCCharacter(
                self.screen,
                self.origin,
                NPCRegister.WIZARD,
                spawn=(-600, -200),
                active=True
            )
        }

    def _init_ground_weapons(self) -> list[Attachment]:
        """Create a list of weapons lying on the ground."""
        return [
            Attachment(self.screen, self.player, self.origin, (100, 200), WeaponRegister.GUN),
            Attachment(self.screen, self.player, self.origin, (300, 400), WeaponRegister.SWORD),
            Attachment(self.screen, self.player, self.origin, (500, 300), WeaponRegister.HEALING),
        ]

    def get_screen_center(self) -> tuple[float, float]:
        width, height = self.screen.get_size()
        return width * 0.5, height * 0.5

    # ─────────────────────────────────────────────────────────────
    # Game Loop Parts
    # ─────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Start and run the main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(60)
            self.tick_counter += 1
            self._npc_test_movement()

    def update(self) -> None:
        """Update game logic and world state."""
        if self.move_enabled:
            self.player.set_target_pos()

        self.player.update_body_positions()

        for weapon in self.ground_weapons:
            weapon.update(self.origin)

        for projectile in self.projectiles:
            projectile.update()

        self.attack()

        self._handle_collition()

        # Remove projectiles that are no longer alive
        self.projectiles = [p for p in self.projectiles if p.alive]

    def render(self) -> None:
        """Draw everything to the screen."""
        self.screen.fill((0, 0, 0))

        # Update camera origin based on player's head
        head = self.player.snake_pos[0]
        screen_w, screen_h = self.screen.get_size()
        self.origin = (screen_w * 0.5 - head[0], screen_h * 0.5 - head[1])

        self.hub.render(self.origin)
        self.player.render(self.origin)

        if self.dragging_weapon:
            self.player.draw_attachment_nodes(self.dragging_weapon)

        self._render_weapons()
        self._render_npcs()

        self.player_hud.update()
        self.player_hud.render()

        pygame.display.flip()

    def _handle_collition(self) -> None:
        """Handle collisions between projectiles (including melee) and NPCs."""

        for projectile in self.projectiles:
            if not projectile.alive:
                continue

            for npc_name, npc in self.npc_characters.items():
                if not npc.active:
                    continue

                npc_center = pygame.Vector2(npc.pos)

                # Projectile logic
                if isinstance(projectile, Projectile):
                    if (projectile.pos - npc_center).length() < npc.size * 0.5:
                        npc.change_health(projectile.damage)
                        projectile.alive = False

                # Melee swing logic
                elif isinstance(projectile, SwordSwingProjectile):
                    if npc_name in projectile.hit_npcs:
                        continue  # Prevent multiple hits

                    if (projectile.pos - npc_center).length() < projectile.range_radius:
                        npc.change_health(projectile.damage)
                        projectile.hit_npcs.add(npc_name)

            # Update projectile lifespan
            if isinstance(projectile, SwordSwingProjectile):
                projectile.lifespan -= 1
                if projectile.lifespan <= 0:
                    projectile.alive = False

    def _render_weapons(self) -> None:
        """Update and render unattached weapons and projectiles."""
        for weapon in self.ground_weapons:
            if weapon.attached:
                continue

            angle = 0
            if weapon.dragging:
                mouse_world = pygame.Vector2(pygame.mouse.get_pos()) - pygame.Vector2(self.origin)
                direction = mouse_world - weapon.pos
                if direction.length_squared() > 0:
                    angle = direction.angle_to(pygame.Vector2(1, 0))

            weapon.draw(self.origin, angle)

        for projectile in self.projectiles:
            projectile.draw(self.origin)

    def _render_npcs(self) -> None:
        """Render all active NPC characters."""
        for npc in self.npc_characters.values():
            npc.render(self.origin)

    def attack(self) -> None:
        """Trigger all attached weapons to attack."""
        for weapon in self.ground_weapons:
            if weapon.attached:
                weapon.attack(self.projectiles)

    def _npc_test_movement(self) -> None:
        """Temporary movement logic to demonstrate NPC animation."""
        if self.tick_counter == 300:
            self.npc_characters[NamedNPCs.NIBBIN].set_target_pos((1000, 600))
        elif self.tick_counter == 600:
            self.npc_characters[NamedNPCs.NIBBIN].set_target_pos((-1000, -600))
            self.tick_counter = 0

    # ─────────────────────────────────────────────────────────────
    # Input Handling
    # ─────────────────────────────────────────────────────────────

    def handle_input(self) -> None:
        """Handle all input from keyboard and mouse."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

            elif event.type == pygame.KEYDOWN:
                self._handle_key(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up(event)

    def _handle_key(self, event) -> None:
        """Process key presses."""
        key = pygame.key.name(event.key)
        if key == "s":
            cprint("s", VC.YELLOW)
        self.player.add_snake_part()

    def _handle_mouse_down(self, event) -> None:
        if event.button == 1:  # Left click
            click = self.player_hud.get_clicked()
            if click == "":
                self.dragging_weapon = None
                for weapon in self.ground_weapons:
                    weapon.handle_mouse_down(pygame.mouse.get_pos(), self.origin, self.player)
                    if weapon.dragging:
                        self.dragging_weapon = weapon
                        break
            elif click == HUDRegister.OPTIONS:
                cprint("options", VC.MAGENTA)

        elif event.button == 3:  # Right click
            self.move_enabled = True

    def _handle_mouse_up(self, event) -> None:
        if event.button == 1:
            for weapon in self.ground_weapons:
                weapon.handle_mouse_up(self.player, self.origin)
            self.dragging_weapon = None

        elif event.button == 3:
            self.move_enabled = False
            self.player.target_pos = self.player.snake_pos[0]

    def quit(self) -> None:
        """End the game gracefully."""
        self.running = False
        pygame.quit()
        sys.exit()
        cprint("Game closed", VC.MAGENTA)


# ─────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────

def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
