import pygame
import os
from assets import settings
from pathlib import Path

abspath = os.path.dirname(os.path.abspath(__file__))

class Slider(pygame.sprite.Sprite):
    def __init__(self, x, initial, length, width, groups, speed=settings.SPEED, z_pos=1):
        super().__init__(groups)
        self.time = -(initial * speed - settings.PERFECT_LINE_POSITION)
        self.initial = initial
        self.z_pos = z_pos
        self.speed = speed
        self.next_box = False

        image_path = os.path.join(abspath, '..', '..', 'graphics', 'longbox.png')
        original = pygame.image.load(str(image_path)).convert_alpha()
        self.image = pygame.transform.scale(original, (width, length))
        self.rect = self.image.get_rect(bottomleft=(x, self.time))
        self.rect.bottomleft = (x, self.time)
        self.is_visible = True
        self.appended = False

    def update(self, elapsed_time):
        # Calculate the new y position based on the elapsed time
        self.rect.bottom = self.time + elapsed_time * self.speed

    def reset(self):
        # Reset the attributes to their initial states
        self.rect.y = self.time
        self.is_visible = False
        self.appended = False