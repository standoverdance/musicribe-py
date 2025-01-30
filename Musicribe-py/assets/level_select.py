from pathlib import Path
import pygame
import os
from assets import settings
from .level.player import Player
from .debug import debug
from .timer import Timer
from .button import Button

abspath = os.path.dirname(os.path.abspath(__file__))

class Level_select():
    def __init__(self, levels):
        self.display_surface = pygame.display.get_surface()
        
        self.visible_sprites = pygame.sprite.Group()
        self.a = settings.HEIGHT / 5 + 4
        self.preview_spacing = 10
        self.player = Player((8, 18), (self.a, self.a), self.visible_sprites)
        self.scroll_timer = Timer(9)

        self.levels = levels
        self.selecting_level = False
        self.selecting_difficulty = False
        self.selected_index = 0
        self.selected_difficulty_index = 0
        self.max_diff_index = 69
        self.max_lvl_index = len(self.levels) - 2 # -2 Because the self.selected_index is buggin. :)

        self.audio_length = 0

        self.level_selected = False
        self.selected_level_data = None

        self.selectable_difficulties = []
        self.scroll_offset = 0
        self.max_scroll = self.adjust_max_scroll()
        self.scroll_speed = 20
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

        self.background = None

        self.sounds = {
            "tap": pygame.mixer.Sound(os.path.join(abspath, '..', 'audio', 'tap.wav')),
            "select": pygame.mixer.Sound(os.path.join(abspath, '..', 'audio', 'select-click.wav'))
        }
        button_pos = (settings.WIDTH /2, settings.HEIGHT - 60)

        self.settings_button = Button("Settings", button_pos, (450, 50), (50, 50, 50), (255, 255, 255), selector=False)

        # Create the toggle buttons
        self.toggles = [
            Button(f"No Death:{settings.Modifiers.NO_DEATH}", (button_pos[0], button_pos[1] - 60), (450, 50), (50, 50, 50), (255, 255, 255), selector=False),
            Button(f"Hide Letters:{settings.Modifiers.HIDDEN_LETTERS}", (button_pos[0], button_pos[1] - 120), (450, 50), (50, 50, 50), (255, 255, 255), selector=False),
            Button(f"Kill letters on miss:{settings.Modifiers.KILL_ON_MISS}", (button_pos[0], button_pos[1] - 180), (450, 50), (50, 50, 50), (255, 255, 255), selector=False),
            Button(f"Whatever letter:{settings.Modifiers.WHATEVER_LETTER}", (button_pos[0], button_pos[1] - 240), (450, 50), (50, 50, 50), (255, 255, 255), selector=False)
            
        ]
        self.show_toggles = False

    def toggle_settings(self):
        self.show_toggles = not self.show_toggles

    def events(self, event):
        if self.settings_button.is_clicked(event):
            self.toggle_settings()
        if self.show_toggles:
            for toggle in self.toggles:
                if toggle.is_clicked(event):
                    if toggle.text.startswith("No Death"):
                        settings.Modifiers.NO_DEATH = not settings.Modifiers.NO_DEATH
                        toggle.render_text(f"No Death: {settings.Modifiers.NO_DEATH}")
                    elif toggle.text.startswith("Hide Letters"):
                        settings.Modifiers.HIDDEN_LETTERS = not settings.Modifiers.HIDDEN_LETTERS
                        toggle.render_text(f"Hide Letters: {settings.Modifiers.HIDDEN_LETTERS}")
                    elif toggle.text.startswith("Kill letters on miss"):
                        settings.Modifiers.KILL_ON_MISS = not settings.Modifiers.KILL_ON_MISS
                        toggle.render_text(f"Kill letters on miss: {settings.Modifiers.KILL_ON_MISS}")
                    elif toggle.text.startswith("Whatever letter"):
                        settings.Modifiers.WHATEVER_LETTER = not settings.Modifiers.WHATEVER_LETTER
                        toggle.render_text(f"Whatever letter: {settings.Modifiers.WHATEVER_LETTER}")

        if event.type == pygame.MOUSEBUTTONDOWN: 
            if event.button == 1:
                pygame.mixer.init()
                for prime_index, level_data in enumerate(self.levels.values()):
                    preview = level_data["preview"]
                    if preview.overlay_rect and preview.overlay_rect.collidepoint(event.pos):
                        if preview.selected: preview.selected = False
                        else:
                            self.image_and_audio(preview)
                            self.selected_index = prime_index - 1 #I genuenly don't know why the hell it should be -1. It came out that way when I was debugging. It will probably create problems in the future
                            #Deselect
                            for index, level_data in enumerate(self.levels.values()):
                                inner_preview = level_data["preview"]
                                if index != prime_index:
                                    inner_preview.selected = False
                                    inner_difficulties = level_data["difficulties"]
                                    for difficulty in inner_difficulties:
                                        if difficulty.selectable:
                                            difficulty.selectable = False
                    if preview.selected:
                        difficulties = level_data["difficulties"]
                        for difficulty in difficulties:
                            if not difficulty.selectable: difficulty.selectable = True
                            if difficulty.selectable:
                                path = difficulty.is_clicked(event)
                                if path != None:
                                    self.run_level(difficulty.path)
            elif event.button == 4:  # Scroll up
                bottom_bound = self.display_surface.get_height() - 95
                if self.player.rect.bottom > bottom_bound and not self.scroll_timer.active:
                    self.scroll_timer.activate()
                    self.selected_index -= 1
                    self.preview_selected()
                self.scroll_offset = max(self.scroll_offset - self.scroll_speed, 0)
            elif event.button == 5:  # Scroll down
                if self.scroll_offset < self.max_scroll:
                    self.scroll_offset += self.scroll_speed
                    if self.player.rect.top < 55 and not self.scroll_timer.active:
                        self.scroll_timer.activate()
                        self.selected_index += 1
                        self.preview_selected()

        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            if key_name == "down" or key_name == "s":
                if self.selecting_difficulty:
                    if self.selected_difficulty_index < self.max_diff_index - 1:
                        self.selected_difficulty_index += 1
                        self.difficulty_selected(True)
                    else:
                        self.selected_difficulty_index = 0
                        self.selecting_difficulty = False
                        self.difficulty_selected(False)
                        self.selected_index += 1
                        self.preview_selected()

                else:
                    if self.selected_index < self.max_lvl_index:
                        self.selected_index += 1
                        self.preview_selected()
            
            if key_name == "up" or key_name == "w":
                if self.selecting_difficulty:
                    if self.selected_difficulty_index > 0:
                        self.selected_difficulty_index -= 1
                        self.difficulty_selected(True)
                    else:
                        self.selected_difficulty_index = 0
                        self.selecting_difficulty = False
                        self.difficulty_selected(False)
                        self.selected_index -= 1
                        self.preview_selected()
                else:
                        
                    if self.selected_index >= 0: 
                        self.selected_index -= 1
                        self.preview_selected()

            if key_name == "escape":
                self.selecting_level = False
                pygame.mixer.music.stop()
                pygame.mixer.music.load("../audio/Master.wav")
                pygame.mixer.music.play()
            
            if key_name == "return":
                if self.selecting_difficulty:
                    for prime_index, level_data in enumerate(self.levels.values()):
                        difficulties = level_data["difficulties"]
                        if prime_index == self.selected_index + 1:
                            for difficulty in difficulties:
                                if difficulty.selected:
                                    self.run_level(difficulty.path)
                else:
                    hah = self.selected_index + 1
                    for prime_index, level_data in enumerate(self.levels.values()):
                            if prime_index == hah:
                                difficulties = level_data["difficulties"]
                                diff_count = len(difficulties)
                                if diff_count == 1:
                                        for difficulty in difficulties:
                                            self.run_level(difficulty.path)
                                else:
                                    self.selecting_difficulty = True
                                    self.max_diff_index = diff_count
                                    for index, difficulty in enumerate(difficulties):
                                        if index == self.selected_difficulty_index:
                                            difficulty.selected = True
                                        else:
                                            difficulty.selected = False

                                
    def adjust_max_scroll(self):
        max_scroll = 0
        for level_data in self.levels.values():
            preview = level_data["preview"]
            max_scroll += preview.overlay_height + self.preview_spacing
        max_scroll -= self.display_surface.get_height() - 200
        return max_scroll


    def select(self):
        self.selecting_level = True
        for index, level_data in enumerate(self.levels.values()):
            preview = level_data["preview"]
            if index == 1:
                try:
                    pygame.mixer.music.load(preview.audio)
                    preview_time_seconds = preview.preview_time / 1000
                    pygame.mixer.music.play(start=preview_time_seconds)
                except Exception as e:
                    print(f"Error loading or playing music: {e}")

                image_width, image_height = preview.background_image.get_size()
                aspect_ratio = image_width / image_height
                
                self.background = pygame.transform.scale(preview.background_image, (settings.WIDTH, int(settings.WIDTH / aspect_ratio)))

    def difficulty_selected(self, bool):
        for prime_index, level_data in enumerate(self.levels.values()):
            hah = self.selected_index + 1
            if prime_index == hah:
                difficulties = level_data["difficulties"]
                for index, difficulty in enumerate(difficulties):
                    if bool:
                        if index == self.selected_difficulty_index:
                            difficulty.selected = True
                        else:
                            difficulty.selected = False
                    else:
                        difficulty.selected = False
        self.sounds["tap"].play()

    def preview_selected(self):
        self.max_scroll = self.adjust_max_scroll()
        xd = self.selected_index + 1
        for prime_index, level_data in enumerate(self.levels.values()):
            preview = level_data["preview"]
            if prime_index != xd: preview.selected = False
            else: self.image_and_audio(preview)
        self.sounds["tap"].play()

    def run_level(self, path):
        self.sounds["select"].play()
        self.selected_level_data = path
        self.level_selected = True
        self.player.set_target(settings.BASEPOS, settings.PLAYER_SIZE)
                

    def image_and_audio(self, preview):
        preview.selected = True
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(preview.audio)
            preview_time_seconds = preview.preview_time / 1000
            pygame.mixer.music.play(start=preview_time_seconds)
        except Exception as e:
            print(f"Error loading or playing music: {e}")
        image_width, image_height = preview.background_image.get_size()
        aspect_ratio = image_width / image_height
        
        self.background = pygame.transform.scale(preview.background_image, (settings.WIDTH, int(settings.WIDTH / aspect_ratio)))
                

    def run(self):
        self.display_surface.fill((255, 192, 0))
        if self.background: self.display_surface.blit(self.background, (0,0))

        top_bound = 50
        bottom_bound = self.display_surface.get_height() - 100

        y = 50 - self.scroll_offset
        if self.scroll_offset > self.max_scroll:
            self.scroll_offset = self.max_scroll

        self.settings_button.draw(self.display_surface)
        if self.show_toggles:
            for toggle in self.toggles:
                toggle.draw(self.display_surface)
        for index, level_data in enumerate(self.levels.values()):
            preview = level_data["preview"]
            preview.draw(self.display_surface, (10, y))
            y += preview.a + self.preview_spacing
            bruv = index - 1
            if bruv == self.selected_index:
                player_y = int(y - 5 - preview.overlay_height)
                self.player.set_target((8, player_y), (self.a, self.a))
            if preview.selected:
                difficulties = level_data["difficulties"]
                for difficulty in difficulties:
                    if difficulty.selected:
                        difficulty.draw(self.display_surface, (50, y))
                        y += 50
                    else:
                        difficulty.draw(self.display_surface, (25, y))
                        y += 50

        player_top = self.player.rect.top
        player_bottom = self.player.rect.bottom

        if player_top + 20 < top_bound:
            self.scroll_offset = max(self.scroll_offset - self.scroll_speed, 0)
        elif player_bottom - 20 > bottom_bound:
            self.scroll_offset = min(self.scroll_offset + self.scroll_speed, self.max_scroll)

        self.player.update()
        self.display_surface.blit(self.player.image, self.player.rect)

        self.scroll_timer.update()

