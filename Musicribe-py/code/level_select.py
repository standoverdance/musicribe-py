import pygame
from settings import *

class Level_select():
    def __init__(self, levels):
        self.display_surface = pygame.display.get_surface()
        
        self.visible_sprites = pygame.sprite.Group()

        self.levels = levels
        
        self.level_selected = False
        self.selected_level_data = None

    def events(self, event):
        pass

    def run(self):
        self.display_surface.fill((255, 192, 0))
        y = 20

        for level_data in self.levels.values():
            preview = level_data["preview"]
            preview.draw(self.display_surface, (10, y))

            y += preview.a + 10

        # for level in self.levels:
        #     level.draw(self.display_surface, (10, y))
        #     y += level.a + 10

        