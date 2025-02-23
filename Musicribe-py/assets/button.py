from pathlib import Path
import pygame
import os
from assets import settings

abspath = os.path.dirname(os.path.abspath(__file__))

class Button:
    def __init__(self, text, pos, size, bg_color, text_color, selector = False):
        self.size = size
        self.pos = pos
        self.rect = pygame.Rect(pos, size)  # Button rectangle
        self.font = pygame.font.Font(os.path.join(abspath, '..', 'font', 'bahnschrift.ttf'), round(settings.HEIGHT / 18))  # Font size 
        self.bg_color = bg_color  # Button background color
        self.text = text
        self.text_color = text_color
        self.render_text(self.text, self.text_color) 
        self.selector = selector
        # Usable - If it turns into selector:
        self.selected = False
        self.dropdown_rects = []
        self.objects = []
        #self.letter_type = LetterType(size, text, ) 
        self.radius = 8

    def change_text(self, text, text_color = (255, 255, 255)):
            self.text = text
            self.text_color = text_color

    def render_text(self, text, text_color = (255,255,255)):
        self.text = text
        self.text_color = text_color
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update_pos(self,pos_x, pos_y):
        self.pos = (pos_x, pos_y)
        self.rect = pygame.Rect(self.pos, self.size)
        self.render_text(self.text, self.text_color)

    def update_size(self, size_x, size_y):
        self.rect = pygame.Rect(self.pos, (size_x, size_y))
        self.render_text(self.text, self.text_color)
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.radius)
        surface.blit(self.text_surface, self.text_rect)

    def is_clicked(self, event):
        # Check if the button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.selector:
                if self.selected:
                    for i, rect in enumerate(self.dropdown_rects):
                        if rect.collidepoint(event.pos):
                            self.text = self.objects[i]  # Update the selected object
                            self.selected = False  # Close the dropdown
                            return True
                if self.rect.collidepoint(event.pos):
                    self.selected = not self.selected  # Toggle dropdown state
                    return True
            elif self.rect.collidepoint(event.pos):
                return True
        return False
    
    def draw_selector(self, surface, selection):
        # Draw the main button
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.radius)
        self.render_text(self.text, self.text_color)
        surface.blit(self.text_surface, self.text_rect)
        self.objects = selection

        # If dropdown is open, show all options
        if self.selected:
            self.dropdown_rects = [pygame.Rect(self.rect[0], self.rect[1] + i * 60, self.rect[2], self.rect[3]) for i in range(1, len(selection) + 1)] 
            for i, obj in enumerate(selection):
                pygame.draw.rect(surface, (200,200,200), self.dropdown_rects[i], border_radius=self.radius)
                text_surface = self.font.render(obj, True, (0,0,0))
                surface.blit(text_surface, (self.dropdown_rects[i].x + 10, self.dropdown_rects[i].y + 5))