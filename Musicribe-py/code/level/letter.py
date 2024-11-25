import pygame
from settings import *

class Letter(pygame.sprite.Sprite):
    def __init__(self, pos, size, letter_txt, groups, z_pos = 1, fonte = UI_Font, anchor = "bottomleft"):
        super().__init__(groups)
        if letter_txt == " ":
            self.letter_txt = "space"
        else:
            self.letter_txt = letter_txt

        font = pygame.font.Font(fonte, size)
        if letter_txt and '\0' not in letter_txt:
            self.image = font.render(letter_txt, True, (255, 255, 255))
        else:
            self.image = font.render(" ", True, (255, 255, 255))
        self.rect = self.image.get_rect(bottomleft = pos)
        if anchor == 'center':
            self.rect.center = pos
        elif anchor == 'topleft':
            self.rect.topleft = pos
        elif anchor == 'bottomleft':
            self.rect.bottomleft = pos
        elif anchor == 'bottomright':
            self.rect.bottomright = pos
        elif anchor == 'topright':
            self.rect.topright = pos
        self.z_pos = z_pos

        # Get the width and height of the rendered letter
        self.width, self.height = self.image.get_size()
        

    def update(self, pos):
        self.rect = self.image.get_rect(bottomleft = pos)