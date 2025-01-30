import pygame
import os
import re
from assets import settings

abspath = os.path.dirname(os.path.abspath(__file__))

class TextInput:
    def __init__(self, pos, size, font_size=32, text_color=(3, 5, 0), bg_color=(255, 255, 240)):
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.color = bg_color
        self.text_color = text_color
        self.font = pygame.font.Font(os.path.join(abspath, '..', 'font', 'bahnschrift.ttf'), font_size)
        self.lines = [""]
        self.active = False
        self.line_surfaces = []
        self.letter_count = 0
        self.cursor_pos = 0

        # Initialize clipboard support
        pygame.scrap.init()


    def resize_font(self, size):
        self.font = pygame.font.Font(settings.UI_Font, size)

    def render_lines(self):
        #self.line_surfaces = [self.font.render(line, True, self.text_color) for line in self.lines]
        self.line_surfaces = [
        self.font.render(line.replace('\0', ''), True, self.text_color) for line in self.lines
    ]
        
    def handle_paste(self):
        """Pastes clipboard content at the current cursor position."""
        if pygame.scrap.get_init():
            # Get clipboard text and decode it
            clipboard_text = pygame.scrap.get(pygame.SCRAP_TEXT)
            if clipboard_text:
                try:
                    clipboard_text = clipboard_text.decode('utf-8')  # Decode from bytes to string
                except UnicodeDecodeError:
                    try:
                        clipboard_text = clipboard_text.decode('windows-1252')
                    except UnicodeDecodeError:
                        # Replace non-decodable characters with a placeholder
                        try:
                            clipboard_text = clipboard_text.decode('windows-1252')
                        except UnicodeDecodeError:
                            # Replace non-decodable characters with a placeholder
                            clipboard_text = clipboard_text.decode('utf-8', errors='replace')

                clipboard_text = re.sub(r'[^\x20-\x7E\n]', '', clipboard_text)

                self.letter_count += len(clipboard_text)
                for char in clipboard_text:
                    if char == '\n':  # Handle newlines in pasted text
                        self.lines.append("")
                    else:
                        self.lines[-1] += char
                        if self.font.size(self.lines[-1])[0] > self.rect.width - 10:
                            # Start a new line if the text exceeds the box width
                            self.lines.append("")
                self.render_lines()
                self.cursor_pos += len(clipboard_text)
                print(clipboard_text)  # Check the output

    def events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state based on mouse click within input box
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            # Handle input while active
            if event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                self.handle_paste()
            elif event.key == pygame.K_RETURN:
                print("Input text:", "".join(self.lines))  # For debugging
                #self.lines = [""]
            elif event.key == pygame.K_BACKSPACE and (pygame.key.get_mods() & pygame.KMOD_LSHIFT):
                if self.letter_count > 100:
                    self.letter_count -= 100
                if self.lines[-1] == "":
                    if len(self.lines) != 1:
                        self.lines.pop()  # Remove empty line if there is one
                elif self.lines[-1]:  # Remove the last character of the last line
                    self.lines[-1] = self.lines[-1][:-100]
            elif event.key == pygame.K_BACKSPACE:
                if self.letter_count > 0:
                    self.letter_count -= 1
                if self.lines[-1] == "":
                    if len(self.lines) != 1:
                        self.lines.pop()  # Remove empty line if there is one
                elif self.lines[-1]:  # Remove the last character of the last line
                    self.lines[-1] = self.lines[-1][:-1]

            elif event.key not in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_LALT, pygame.K_RALT, pygame.K_LCTRL, pygame.K_RCTRL):
                self.lines[-1] += event.unicode  # Add character to the last line
                self.letter_count += 1

                if self.font.size(self.lines[-1])[0] > self.rect.width - 10:
                    self.lines.append("")  # Start a new line if it's too wide
            self.render_lines()

    def update(self):
            # Resize box if needed
            self.rect.h = max(40, len(self.line_surfaces) * (self.font.get_height() + 5))

    def draw(self, screen):
        # Draw background and text on screen
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Draw each line of text, one below the other
        for i, line_surface in enumerate(self.line_surfaces):
            screen.blit(line_surface, (self.rect.x + 5, self.rect.y + 5 + i * (self.font.get_height() + 5)))

        # Draw border
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
