from pathlib import Path
import pygame
import os
from assets import settings

abspath = os.path.dirname(os.path.abspath(__file__))

class Score(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups, optional_front_text ="", z_pos = 1): 
        super().__init__(groups)   
        self.score = 0
        self.pos = pos
        self.font = pygame.font.Font(os.path.join(abspath, '..', '..', 'font', 'bahnschrift.ttf'), size)
        self.image = self.font.render(optional_front_text + str(self.score), True, (255, 255, 255))
        self.rect = self.image.get_rect(topleft = pos)
        self.z_pos = z_pos
        self.front = optional_front_text

        self.scoring = {"perfect": 30, "good":20, "ok":10,"meh":5,"miss":0}

        self.max_combo = 0


    def update(self, add_score):
        self.score += add_score
        if self.max_combo < self.score:
            self.max_combo = self.score
        self.image  = self.font.render(self.front + str(round(self.score)), True, (255, 255, 255))

    def reset_combo(self):
        if self.score > self.max_combo:
            self.max_combo = self.score
        self.score = 0
        self.image = self.font.render(self.front + str(self.score), True, (255, 255, 255))

    def update_pos(self, pos):
        self.rect = self.image.get_rect(bottomleft = pos)

    # Function only used in percent calculations instead of update and reset above for combo and score
    def percent(self, accuracy_liabrary):
        self.score = 100
        aggregate = 0
        sum = 0
        for x in accuracy_liabrary:
            aggregate += accuracy_liabrary[x]*self.scoring[x]
            sum += self.scoring["perfect"]* accuracy_liabrary[x]
        self.score = round(100*aggregate/ sum, 1)
        self.image = self.font.render(self.front + str(self.score), True, (255, 255, 255))

    def reset(self):
        self.score = 0
        self.image = self.font.render(self.front + str(self.score), True, (255, 255, 255))
