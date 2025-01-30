from pathlib import Path
import pygame
import os

from assets import settings

abspath = os.path.dirname(os.path.abspath(__file__))

class Misslight(pygame.sprite.Sprite):
    def __init__(self,pos, size, groups, z_pos = 2):
        super().__init__(groups)
        original_path = os.path.join(abspath, '..', '..', 'graphics', 'misslight.png')
        original = pygame.image.load(str(original_path)).convert_alpha()
        self.size = size
        self.z_pos = z_pos
        self.image = pygame.transform.scale(original, self.size)
        self.rect = self.image.get_rect(topleft = pos)
        self.rect.topleft = pos
        self.image.set_alpha(0)

    def update(self, dt):
        alpha = self.image.get_alpha()
        if alpha != 0:
            self.image.set_alpha(alpha - 300 * dt)

class Sliderlight(pygame.sprite.Sprite):
    def __init__(self,pos, size, groups, z_pos = 2):
        super().__init__(groups)
        original_path = os.path.join(abspath, '..', '..', 'graphics', 'sliderlight.png')
        original = pygame.image.load(str(original_path)).convert_alpha()
        self.size = size
        self.z_pos = z_pos
        self.image = pygame.transform.scale(original, self.size)
        self.rect = self.image.get_rect(topleft = pos)
        self.rect.topleft = pos
        self.image.set_alpha(0)

    def changestate(self, state):
        original_path = os.path.join(abspath, '..', '..', 'graphics', f'sliderlight{state}.png')
        self.original = pygame.image.load(str(original_path)).convert_alpha()
        self.image = pygame.transform.scale(self.original, self.size)
        self.rect = self.image.get_rect(topleft = self.rect.topleft)

    def update(self, dt):
        alpha = self.image.get_alpha()
        if alpha != 0:
            self.image.set_alpha(alpha - 1200 * dt)