from pathlib import Path
import pygame
import os
from assets import settings

abspath = os.path.dirname(os.path.abspath(__file__))

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups, z_pos=5):
        super().__init__(groups)
        original_path = os.path.join(abspath, '..', '..', 'graphics', 'dam.png')
        original = pygame.image.load(str(original_path)).convert_alpha()
        self.size = size
        self.z_pos = z_pos
        self.image = pygame.transform.scale(original, self.size)
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.topleft = pos

        # For easing
        self.target_pos = pygame.Vector2(pos)  # Target position
        self.current_pos = pygame.Vector2(pos)  # Current position for easing
        self.easing_speed = 0.15  # Adjust to control the easing speed

    def changestate(self, state):
        original_path = os.path.join(abspath, '..', '..', 'graphics', f'dam{state}.png')
        self.original = pygame.image.load(str(original_path)).convert_alpha()
        self.image = pygame.transform.scale(self.original, self.size)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

    def defaultstate(self):
        original_path = os.path.join(abspath, '..', '..', 'graphics', 'dam.png')
        self.original = pygame.image.load(str(original_path)).convert_alpha()
        self.image = pygame.transform.scale(self.original, self.size)
        self.rect = self.image.get_rect(topleft=self.rect.topleft)

    def set_target(self, pos, size):
        """Set a new target position and size for the player."""
        self.target_pos = pygame.Vector2(pos)
        self.size = size

    def update(self):
        # Interpolate position towards the target position
        self.current_pos += (self.target_pos - self.current_pos) * self.easing_speed
        self.rect.topleft = self.current_pos

        # Update image with the new size
        original_path = os.path.join(abspath, '..', '..', 'graphics', 'dam.png')
        original = pygame.image.load(str(original_path)).convert_alpha()
        self.image = pygame.transform.scale(original, self.size)