import pygame
from settings import *

class HealthBar(pygame.sprite.Sprite):
    def __init__(self,pos, size, groups, max_health=100, current_health=100, z_pos = 2):
        super().__init__(groups)
        original = pygame.image.load('../graphics/healthframe.png')
        self.size = size
        self.z_pos = z_pos
        self.image = pygame.transform.scale(original, self.size)
        self.rect = self.image.get_rect(bottomleft = pos)
        self.rect.bottomleft = pos
        
        self.max_health = max_health
        self.current_health = current_health

        self.fill_color = (127, 158, 217)

        self.fill_rect = pygame.Rect(0,0,0,0)


        

    def changestate(self, new_health):
        self.current_health = max(0, min(new_health, self.max_health))

    def fill_rect_calc(self):
        
        fill_height = int((self.current_health / self.max_health) * (self.rect.height - (self.rect.height / 30)))
        fill_width = int(self.rect.width - self.rect.width / 3.75)
        fill_left = int(self.rect.left + (self.rect.width / 7.5))
        fill_top = int(self.rect.top + self.rect.height / 60) + (self.rect.height - self.rect.height / 30 - fill_height)

        self.fill_rect = pygame.Rect(fill_left, fill_top, fill_width, fill_height)
    


    def update(self, dt, game_time, break_sections):
        for start, end in break_sections:
            if start <= game_time <= end:
                return 
        if self.current_health > 0:
            self.current_health -= 10 * dt
        if self.current_health > self.max_health:
            self.current_health = self.max_health
        self.fill_rect_calc()