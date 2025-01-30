import pygame
from assets import settings
from mutagen.mp3 import MP3

class Preview():
    def __init__(self, audio, image, title, artist, preview_time):
        #self.path = path
        self.preview_time = preview_time
        self.audio = audio
        self.background_image = pygame.image.load(image).convert_alpha()
        self.square_img = self.crop_to_square(self.background_image)
        self.rounded_img = self.round_corners(self.square_img, radius=100)
        self.square_color = (200, 255, 100)
        self.a = settings.HEIGHT / 5
        self.width = settings.WIDTH / 3
        self.image = pygame.transform.scale(self.rounded_img, (int(self.a), int(self.a)))
        self.title = title
        self.artist = artist
        self.title_font = pygame.font.Font(None, 40)
        self.font = pygame.font.Font(None, 24)
        self.selected = False

        self.mutagen_audio = MP3(self.audio)
        self.audio_length = self.mutagen_audio.info.length

        self.overlay_width = int(self.a * 3)  # Much wider than the image
        self.overlay_height = int(self.a * 1.05)
        self.overlay_rect = None
        self.radius = 5

    def is_clicked(self, event):
        # Check if the button is clicked
        if event.type == pygame.MOUSEBUTTONDOWN:  # Only handle mouse button events
            if self.overlay_rect and self.overlay_rect.collidepoint(event.pos):  # Ensure overlay_rect is defined
                self.selected = True
                return True
            return False

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
    
    def create_overlay(self, cords):
        """
        Create a semi-transparent rectangle overlay below the image.
        :param cords: Tuple (x, y) for the top-left corner of the image
        :return: Rect and Surface for the overlay
        """
        x, y = cords
        overlay = pygame.Surface((self.overlay_width, self.overlay_height), pygame.SRCALPHA)

        overlay_color = (132, 28, 0, 200)  # RGBA: dark red with transparency
        pygame.draw.rect(
            overlay, 
            overlay_color, 
            overlay.get_rect(), 
            border_radius=self.radius  # Adjust border radius for roundness
        )

        # Position the overlay slightly below and centered under the image
        overlay_rect = overlay.get_rect(center=(x + self.overlay_width / 2 - 5, y + self.a / 2))
        return overlay, overlay_rect
    

    def draw(self, surface, cords):

        overlay, self.overlay_rect = self.create_overlay(cords)
        surface.blit(overlay, self.overlay_rect.topleft)
        surface.blit(self.image, cords)

        # Set the initial y position below the image for text
        x, y = cords[0], cords[1] + self.image.get_height() + 5

        # Render each line of text
        title_text = self.title_font.render(f"{self.title}", True, (255, 255, 255))
        artist_text = self.font.render(f"{self.artist}", True, (255, 255, 255))
        audio_length_info = self.font.render(f"Audio length: {int(self.audio_length)}", True, (255, 255, 255))
        #difficulty_text = self.font.render(f"Difficulty: {self.difficulty}", True, (255, 255, 255))

        # Blit each line of text below the previous one
        surface.blit(title_text, (x + self.a + 10, y - self.a))
        surface.blit(artist_text, (x + self.a + 10, y - self.a + 40))
        surface.blit(audio_length_info, (x + self.a + 10, y - self.a + 65))
        #surface.blit(difficulty_text, (x + self.a + 10, y - self.a + 65))

    def round_corners(self, image, radius):
        """
        Rounds the corners of a Pygame surface.
        :param image: Pygame surface to modify
        :param radius: Radius of the rounded corners
        :return: Pygame surface with rounded corners
        """
        # Create a rounded rectangle surface
        width, height = image.get_size()
        corner_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(corner_surface, (255, 255, 255, 255), (0, 0, width, height), border_radius=radius)



        # Apply the mask to the image
        rounded_image = image.copy()
        rounded_image.blit(corner_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        return rounded_image