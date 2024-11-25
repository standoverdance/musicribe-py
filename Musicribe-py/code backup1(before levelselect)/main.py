import pygame, sys
from settings import *
from debug import debug
from level.level import Level
from menu import Menu

class Game:
    def __init__(self):

        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Musicribe")

        self.level = None  # No level initially
        self.menu = Menu()  # Menu is initialized
        self.is_playing = False  # Menu should be active initially

    def initialize_level(self, level_data):
        self.level = Level(level_data)  # Initialize the level
        self.is_playing = True  # Set game state to playing

    def uninitialize_level(self):
        self.level = None  # Remove the current level
        self.is_playing = False  # Switch back to menu
        self.menu.level_selected = False

    def run(self):
        while True:
            for event in pygame.event.get():
                if self.is_playing:
                    self.level.events(event)

                    if event.type == pygame.USEREVENT:
                        if event.action == 'uninitialize_level':
                            self.uninitialize_level()
                else: 
                    self.menu.events(event)
                    if self.menu.level_selected:
                        self.initialize_level(self.menu.selected_level_data)

                      
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            #self.screen.fill((255, 192, 0))
            if self.is_playing:
                self.level.run()
            else:
                debug(self.menu.level_selected)
                self.menu.run()
            pygame.display.update()
            self.clock.tick(FPS)

if __name__== '__main__':
    game = Game()
    game.run()