from pathlib import Path
import pygame
import os
from assets import settings

abspath = os.path.dirname(os.path.abspath(__file__))

class Falling_box(pygame.sprite.Sprite):
    def __init__(self,x, initial, size, groups, speed = settings.SPEED, z_pos = 1):
        super().__init__(groups)
        self.time = -(initial * speed - settings.PERFECT_LINE_POSITION)
        self.initial = initial
        self.z_pos = z_pos
        self.speed = speed
        self.next_box = False

        original_path = os.path.join(abspath, '..', '..', 'graphics', 'fallingbox.png')
        self.original = pygame.image.load(str(original_path)).convert_alpha()
        self.image = pygame.transform.scale(self.original, size)
        self.rect = self.image.get_rect(bottomleft = (x, self.time))
        self.rect.bottomleft = (x, self.time)
        self.is_visible = False
        self.appended = False


    def update(self, elapsed_time):
        # Calculate the new y position based on the elapsed time
        self.rect.bottom =  self.time + elapsed_time * self.speed

    def reset(self):
        # Reset the attributes to their initial states
        self.rect.y = self.time
        self.is_visible = False
        self.appended = False




