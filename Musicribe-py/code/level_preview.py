import pygame
from settings import *

class Preview():
    def __init__(self, audio, image, title, artist):
        #self.path = path
        self.audio = audio
        background_image = pygame.image.load(image)
        self.square_img = self.crop_to_square(background_image)
        self.a = HEIGHT / 5
        print(self.a)
        self.image = pygame.transform.scale(self.square_img, (self.a, self.a))
        self.title = title
        self.artist = artist
        #self.creator = creator
        #self.difficulty = difficulty
        self.title_font = pygame.font.Font(None, 40)
        self.font = pygame.font.Font(None, 24)

    def make_rect(self):
        pass

    def crop_to_square(self, image):
        """
        Crop a rectangular Pygame surface to a square, preserving the center.
        :param image: Pygame Surface object
        :return: Cropped square Pygame Surface object
        """
        width, height = image.get_width(), image.get_height()
        
        # Determine the size of the square (smallest side)
        square_size = min(width, height)
        
        # Calculate cropping coordinates
        x_offset = (width - square_size) // 2
        y_offset = (height - square_size) // 2
        
        # Create a new cropped surface
        cropped_surface = image.subsurface((x_offset, y_offset, square_size, square_size))
        
        # Return a copy of the cropped surface to avoid referencing the original
        return cropped_surface.copy()

    def draw(self, surface, cords):
        surface.blit(self.image, cords)

        # Set the initial y position below the image for text
        x, y = cords[0], cords[1] + self.image.get_height() + 5

        # Render each line of text
        title_text = self.title_font.render(f"{self.title}", True, (255, 255, 255))
        artist_text = self.font.render(f"{self.artist}", True, (255, 255, 255))
        #difficulty_text = self.font.render(f"Difficulty: {self.difficulty}", True, (255, 255, 255))

        # Blit each line of text below the previous one
        surface.blit(title_text, (x + self.a + 10, y - self.a))
        surface.blit(artist_text, (x + self.a + 10, y - self.a + 40))
        #surface.blit(difficulty_text, (x + self.a + 10, y - self.a + 65))

    