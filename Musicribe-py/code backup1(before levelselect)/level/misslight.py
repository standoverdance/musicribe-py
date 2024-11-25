import pygame

from settings import *

class Misslight(pygame.sprite.Sprite):
    def __init__(self,pos, size, groups, z_pos = 0):
        super().__init__(groups)
        original = pygame.image.load('../graphics/misslight.png')
        self.size = size
        self.z_pos = z_pos
        self.image = pygame.transform.scale(original, self.size)
        self.rect = self.image.get_rect(topleft = pos)
        self.rect.topleft = pos
        self.image.set_alpha(0)

    # def changestate(self, state):
    #     self.original = pygame.image.load('../graphics/dam' + state + '.png')
    #     self.image = pygame.transform.scale(self.original, self.size)
    #     self.rect = self.image.get_rect(topleft = self.rect.topleft)

    # def defaultstate(self):
    #     self.original = pygame.image.load('../graphics/dam.png')
    #     self.image = pygame.transform.scale(self.original, self.size)
    #     self.rect = self.image.get_rect(topleft = self.rect.topleft)

    def update(self, dt):
        alpha = self.image.get_alpha()
        if alpha != 0:
            self.image.set_alpha(alpha - 300 * dt)