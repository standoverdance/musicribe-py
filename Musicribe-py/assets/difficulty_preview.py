from pathlib import Path
import pygame
import os
from assets import settings

abspath = os.path.dirname(os.path.abspath(__file__))

class Difficulty():
    def __init__(self, osu_path, creator, how_hard):
        self.path = osu_path
        self.square_color = (200, 255, 100)
        self.width = settings.WIDTH / 3
        self.difficulty = how_hard
        self.creator = creator
        self.font = pygame.font.Font(None, 24)

        star_scale = (20, 20)
        star_path = os.path.join(abspath, '..', 'graphics', 'star.png')
        self.star = pygame.image.load(str(star_path)).convert_alpha()
        self.icon_image = pygame.transform.scale(self.star, star_scale)

        self.overlay_height = 40
        self.overlay_rect = None

        self.selectable = False
        self.selected = False

        self.radius = 5

    def is_clicked(self, event):
        # Check if the button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN:  # Only handle mouse button events
            if self.overlay_rect and self.overlay_rect.collidepoint(event.pos):  # Ensure overlay_rect is defined
                return self.path

    
    def create_overlay(self, cords):
        """
        Create a semi-transparent rectangle overlay below the image.
        :param cords: Tuple (x, y) for the top-left corner of the image
        :return: Rect and Surface for the overlay
        """
        x, y = cords
        overlay = pygame.Surface((self.width, self.overlay_height), pygame.SRCALPHA)
        overlay.fill((232, 128, 0, 200))  # RGBA: black with 50% transparency

        overlay_color = (232, 128, 0, 200)
        pygame.draw.rect(
            overlay, 
            overlay_color, 
            overlay.get_rect(), 
            border_radius=self.radius  # Adjust border radius for roundness
        )

        # Position the overlay slightly below and centered under the image
        overlay_rect = overlay.get_rect(center=(x + self.width / 2, y + self.overlay_height / 2))
        return overlay, overlay_rect
    

    def draw(self, surface, cords):

        overlay, self.overlay_rect = self.create_overlay(cords)
        surface.blit(overlay, self.overlay_rect.topleft)
        # Set the initial y position below the image for text
        x, y = cords[0], cords[1]

        # Blit each line of text below the previous one
        creator_text = self.font.render(f"{self.creator}:", True, (255, 255, 255))
        surface.blit(creator_text, (x + 10, y + 10))
        # Render each line of text
        x += self.width - 5
        difficulty = float(self.difficulty)
        star_width, star_height = self.icon_image.get_size()
        full_stars = int(difficulty)
        for i in range(full_stars):
            surface.blit(self.icon_image, (x - self.icon_image.get_width(), y + 10))
            x -= (self.icon_image.get_width() + 5)

        fractional_part = difficulty - full_stars
        if fractional_part > 0:  # Only draw if there's a fractional part
            # Calculate the width of the fractional star
            fractional_width = int(star_width * fractional_part)
            x_offset = int(star_width * (1-fractional_part))

            # Create a subsurface for the fractional star
            fractional_star = self.icon_image.subsurface((x_offset, 0, fractional_width, star_height))
            surface.blit(fractional_star, (x - fractional_width, y + 10))
