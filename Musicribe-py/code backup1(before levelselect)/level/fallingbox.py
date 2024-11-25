import pygame
from settings import *
from timer import Timer

class Falling_box(pygame.sprite.Sprite):
    def __init__(self,x, y_miliseconds, size, value, groups, speed, initial, final_box, z_pos = 0):
        super().__init__(groups)
        self.time = -y_miliseconds
        self.initial = initial
        self.value = value
        self.z_pos = z_pos
        self.speed = speed
        self.next_box = False
        self.final_box = final_box

        self.original = pygame.image.load('../graphics/fallingbox.png')
        self.image = pygame.transform.scale(self.original, size)
        self.rect = self.image.get_rect(topleft = (x, self.time))
        self.rect.topleft = (x, self.time)
        self.is_visible = False
        self.appended = False


    def update(self, elapsed_time):
        # Calculate the new y position based on the elapsed time
        speed = self.speed  # Speed factor, adjust as needed
        self.rect.y =  self.time * speed + (elapsed_time * speed)


