from pathlib import Path
import pygame
import os
import math

abspath = os.path.dirname(os.path.abspath(__file__))

class Musicrimage(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups, z_pos=0):
        super().__init__(groups)
        self.original_path = os.path.join(abspath, '..', 'graphics', 'musicrimage.png')
        self.original = pygame.image.load(str(self.original_path)).convert_alpha()
        self.size = size
        self.z_pos = z_pos
        self.image = pygame.transform.scale(self.original, self.size)
        self.rect = self.image.get_rect(center=pos)
        self.center = pos

        # Animation attributes
        self.scale_factor = 1.0
        self.scale_direction = 1
        self.scale_speed = 0.02
        self.min_scale = 0.8
        self.max_scale = 1
        self.time = 0

    def update(self):
        # Update the time
        self.time += self.scale_speed

        # Calculate the new scale factor using a sinusoidal function
        self.scale_factor = self.min_scale + (self.max_scale - self.min_scale) * (0.5 * (1 + math.sin(self.time)))

        # Scale the image
        new_size = (int(self.size[0] * self.scale_factor), int(self.size[1] * self.scale_factor))
        self.image = pygame.transform.scale(self.original, new_size)

        # Reposition the image to keep the center point fixed
        self.rect = self.image.get_rect(center=self.center)