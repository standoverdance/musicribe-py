# /// script
# dependencies = [
#  "pathlib",
#  "pygame-ce",
#  "pyscroll",
#  "mutagen",
#  "time",
#  "re",
# ]
# ///


import pygame, sys
import sys
import os
from os import chdir, path
chdir(path.dirname(path.abspath(__file__)))

abspath = os.path.dirname(os.path.abspath(__file__))
import asyncio
from assets import settings
from assets.debug import debug
from assets.level import Level
from assets.menu import Menu


class Game:
    def __init__(self):

        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Musicrib")
        icon = pygame.image.load(os.path.join(abspath, 'graphics', 'icon.png'))
        pygame.display.set_icon(icon)

        self.level = None  # No level initially
        self.menu = Menu()  # Menu is initialized
        self.level_select = self.menu.lvl_slct
        self.is_playing = False  # Menu should be active initially

    def initialize_level(self, level_data):
        self.level = Level(level_data)  # Initialize the level
        self.is_playing = True  # Set game state to playing

    def uninitialize_level(self):
        self.level = None  # Remove the current level
        self.is_playing = False  # Switch back to menu
        self.level_select.level_selected = False

    async def run(self):
        while True:
            for event in pygame.event.get():
                if self.is_playing:
                    self.level.events(event)

                    if event.type == pygame.USEREVENT:
                        if event.action == 'uninitialize_level':
                            self.uninitialize_level()
                else: 
                    self.menu.events(event)
                    if self.level_select != None and self.level_select.level_selected:
                        print("Initializing level...")
                        self.initialize_level(self.level_select.selected_level_data)

                      
                if event.type == pygame.QUIT:
                    self.cleanup()
                    pygame.quit()
                    sys.exit()
            
            if self.is_playing:
                self.level.run()
            else:
                self.menu.run()
            pygame.display.update()
            self.clock.tick(settings.FPS)
            await asyncio.sleep(0)

    def cleanup(self):
        if self.level:
            self.level.cleanup()

async def main():
    print("Starting game... Initialize pygame")
    pygame.init()
    
    game = Game()
    print("Game initialized")
    await game.run()

if __name__== '__main__': 
    asyncio.run(main())