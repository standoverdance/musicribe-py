from pathlib import Path
import pygame
from assets import settings
from .button import Button
import zipfile
import os
from tkinter import filedialog
from .debug import debug
from .level.letter import Letter
from .level_preview import Preview
from .difficulty_preview import Difficulty
from .input import TextInput
from .musicrimage import Musicrimage
from .level_select import Level_select
from pygame import mixer

abspath = os.path.dirname(os.path.abspath(__file__))

class Menu():
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        
        self.visible_sprites = pygame.sprite.Group()
        audio_path = os.path.join(abspath, '..', 'audio', 'Master.wav')
        mixer.music.load(str(audio_path))
        mixer.music.play()
        self.init_buttons()
        self.load_levels()

        #Edit section
        #======----=========
        self.object_count = 0
        self.input_box = TextInput((self.select_pos[0], 140), (self.select_size[0], 400))
        self.musicrimage = Musicrimage((self.btn_pos[0] + self.btn_size[0] + settings.WIDTH / 3, settings.HEIGHT/2 + 50), (600, settings.HEIGHT + 100), self.visible_sprites)

        self.osu_files = []
        self.osz_file = None
        self.can_input = False

        self.count_down = None
        self.message = None
        self.warning = None

        self.edit = False
        self.levels = {}

        self.sounds = {
            "edit_button": pygame.mixer.Sound(os.path.join(abspath, '..', 'audio', 'opening-software-interface.wav')),
            "page_back": pygame.mixer.Sound(os.path.join(abspath, '..', 'audio', 'page-back-chime.wav')),
            "quit": pygame.mixer.Sound(os.path.join(abspath, '..', 'audio', 'back.wav')),
            "play": pygame.mixer.Sound(os.path.join(abspath, '..', 'audio', 'select-click.wav'))
        }

    def init_buttons(self):
        #Buttons
        self.btn_size = ((settings.WIDTH / 4), (settings.HEIGHT / 7))
        self.btn_pos = ((settings.WIDTH / 5 - self.btn_size[0] / 2), self.btn_size[1])
        self.b_play = Button("Play", self.btn_pos, self.btn_size, (128, 255, 128), (255, 255, 255))
        self.b_edit = Button("Edit", (self.btn_pos[0], self.btn_pos[1] + self.btn_size[1] * 1.7), self.btn_size, (255, 152, 0), (255, 255, 255))
        self.b_quit = Button("Quit", (self.btn_pos[0], self.btn_pos[1] + self.btn_size[1] * 3.4), self.btn_size, (255, 50, 0), (255, 255, 255))
        self.select_size = ((settings.WIDTH - 200), (settings.HEIGHT / 10))
        self.select_pos = ((settings.WIDTH / 2 - self.select_size[0] / 2), 20)
        self.b_select = Button("Select an .osz file", self.select_pos, self.select_size, (88, 88, 128), (255, 255, 255))
        self.b_convert = Button("Convert", ((settings.WIDTH - self.btn_size[0] /1.5 - 50), (settings.HEIGHT - self.btn_size[1]/1.5 - 50)), ((self.btn_size[0] / 1.5), (self.btn_size[1] /1.5)), (128, 255, 128), (255, 255, 255))
        
        self.buttons = [self.b_play, self.b_edit, self.b_quit]
        self.position_buttons(self.buttons)

    def events(self, event):

        if not self.lvl_slct.selecting_level:
            self.input_box.events(event)

            if event.type == pygame.KEYDOWN and self.input_box.active and self.osz_file and self.osu_files:
                self.visible_sprites.remove(self.count_down)
                self.count_down = Letter((self.select_pos[0], 570), 20, f"Characters to fill  {self.input_box.letter_count}/{self.object_count}", self.visible_sprites)
            
            for button in self.buttons:  # Only check for buttons in the active list
                if button.is_clicked(event):
                    # Perform the action based on which button was clicked
                    if button == self.b_play:
                        self.sounds["play"].play()
                        self.lvl_slct.select()

                    elif button == self.b_convert:

                        if self.osz_file:
                            self.visible_sprites.remove(self.warning)
                            if self.input_box.letter_count == self.object_count:
                                self.convert(f"{self.specific_path}/{self.b_select.text}", "".join(self.input_box.lines))
                                self.sounds["play"].play()
                            elif self.input_box.letter_count > self.object_count:
                                self.warning = Letter((self.select_pos[0], 590), 20, f"Warning! You've input too many letters. The text can't be completed during normal gameplay.", self.visible_sprites)
                                self.convert(f"{self.specific_path}/{self.b_select.text}", "".join(self.input_box.lines))
                                self.sounds["play"].play()
                                #print(f"{self.specific_path}/{self.b_select.text}")
                            else:
                                self.warning = Letter((self.select_pos[0], 590), 20, f"There is too few letters. Add text to convert!", self.visible_sprites)
                        else:
                            self.warning = Letter((self.select_pos[0], 590), 20, f"You didn't even select any files to convert!", self.visible_sprites)

                    elif button == self.b_quit:
                        self.sounds["quit"].play()
                        if self.edit:
                            self.reset_edit_state()
                        else:
                            pygame.quit()


                    elif button == self.b_edit:
                        self.visible_sprites.empty()
                        self.sounds["edit_button"].play()
                        self.b_select.render_text(self.b_select.text)
                        self.edit = True
                        self.buttons = [self.b_convert, self.b_select, self.b_quit]
                        self.edit_buttons()

                    elif button == self.b_select:
                        self.sounds["page_back"].play()
                        self.b_select_event()
        else:
            self.lvl_slct.events(event)



    def run(self):
        if self.lvl_slct.selecting_level:
            self.lvl_slct.run()
        else:
            if self.edit:
                self.display_surface.fill((232, 128, 0))
                self.input_box.draw(self.display_surface)
            else:
                self.display_surface.fill((255, 192, 0))
                self.musicrimage.update()

            for button in self.buttons:
                if button.selector:
                    button.draw_selector(self.display_surface, self.osu_files)
                else:
                    button.draw(self.display_surface)
            
            for sprite in self.visible_sprites:
                    self.display_surface.blit(sprite.image, sprite.rect)



    def position_buttons(self, buttons):
        count = len(buttons)
        if count == 0:
            return
        
        total_height = sum(button.rect.height for button in buttons)
        spacing = (settings.HEIGHT / count) / 4
        
        total_space = total_height + spacing * (count - 1)
        # Start Y position - centers the buttons on the screen
        start_pos = (settings.HEIGHT - total_space) / 2
        current_y = start_pos
        for button in buttons:
            button.update_size(self.btn_size[0],self.btn_size[1])
            button.update_pos(self.btn_pos[0], current_y)
            current_y += button.rect.height + spacing 

    def edit_buttons(self):
        self.b_quit.update_pos(50, (settings.HEIGHT - self.btn_size[1] / 1.5 - 50))
        self.b_quit.update_size((self.btn_size[0]/1.5),(self.btn_size[1]/1.5))

    def open_osz_file(self):
        # Open file dialog and select .osz file
        file_path = filedialog.askopenfilename(filetypes=[("OSZ Files", "*.osz")])
        if file_path:
            return file_path
        return None
    
    def reset_edit_state(self):
        """Resets the edit mode state and related button texts."""
        self.osz_file = None
        self.osu_files = []
        self.b_select.text = "Select an .osz file"
        self.b_select.change_text(self.b_select.text)
        self.b_select.selector = False
        self.can_input = False
        self.edit = False
        self.buttons = [self.b_play, self.b_edit, self.b_quit]
        self.position_buttons(self.buttons)
        self.visible_sprites.empty()
        self.visible_sprites.add(self.musicrimage)
        self.input_box.lines = [""]
        self.input_box.letter_count = 0
        self.input_box.render_lines()


    
    def b_select_event(self):
        if not self.osz_file:  # If no .osz file is selected, select it first
            self.osu_files = []  # Clear previous osu files list
            self.osz_file = self.open_osz_file()  # Function to open .osz file
            self.b_select.selector = True
            if self.osz_file:
                if zipfile.is_zipfile(self.osz_file):
                    try:
                        part = self.osz_file.split("/")
                        last_part = part[-1].split('.')[0]
                        self.specific_path = Path(__file__).parent.parent / 'data' / last_part
        
                        if not self.specific_path.exists():
                            with zipfile.ZipFile(self.osz_file, 'r') as osz_file:
                                osz_file.extractall(self.specific_path)
                                for file_name in osz_file.namelist():
                                    if file_name.endswith('.osu'):
                                        self.osu_files.append(file_name)
                                if self.osu_files:
                                    # Change button text to allow selecting .osu file
                                    self.b_select.text = self.osu_files[0]
                                    self.file_open_and_rmv(self.specific_path / self.osu_files[0])
                                
                                    self.message = Letter((self.select_pos[0], 140), 20, f"Number of HitObjects in {self.osu_files[0]}: {self.object_count}", self.visible_sprites)
                        else:
                            #print(f"Directory '{specific_path}' already exists.")
                            list_data = os.listdir(self.specific_path)
                            for file_name in list_data:
                                if file_name.endswith('.osu'):
                                    self.osu_files.append(file_name)
                            #print(self.osu_files)
                            if self.osu_files:
                                # Change button text to allow selecting .osu file
                                self.b_select.text = self.osu_files[0]
                                self.file_open_and_rmv(self.specific_path / self.osu_files[0])
                            
                                self.message = Letter((self.select_pos[0], 140), 20, f"Number of HitObjects in {self.osu_files[0]}: {self.object_count}", self.visible_sprites)
                                
                    #except FileExistsError:
                    #    print(f"Directory '{specific_path}' already exists.")
                    except PermissionError:
                        print(f"Permission denied: Unable to create '{self.specific_path}'.")
                    except Exception as e:
                        print(f"An error occurred: {e}")
        else:  # If .osz is already selected, allow selecting specific .osu file
            if self.osz_file and self.osu_files:
                hit_objects = []  
                object_count = 0
                selected_osu_file = self.b_select.text
                self.file_open_and_rmv(self.specific_path / selected_osu_file)
                self.visible_sprites.remove(self.message)
                if not self.b_select.selected:
                    self.message = Letter((self.select_pos[0], 140), 20, f"Number of HitObjects in {selected_osu_file}: {self.object_count}", self.visible_sprites)
                self.b_select.text = selected_osu_file
                self.can_input = True

    def load_levels(self):
        self.lvl_slct = None
        base_dir = os.path.join(abspath, '..', 'data')
        if not os.path.exists(base_dir):
            print(f"Directory '{base_dir}' does not exist.")
            return
        self.levels = {}
        section = None
        audio = None
        bgimage = None
        for folder_path in os.listdir(base_dir):
            folder_full_path = os.path.join(base_dir, folder_path)
            if os.path.isdir(folder_full_path):
                for file_path in os.listdir(folder_full_path):
                    if file_path.endswith('.osu'):
                        with open(os.path.join(folder_full_path, file_path), 'r', encoding='utf-8') as file:
                            self.osu_data = file.read()
                            lines = self.osu_data.splitlines()

                            # Initialize variables to store metadata
                            section = None
                            audio = None
                            bgimage = None
                            title = None
                            artist = None
                            creator = None
                            difficulty = None
                            preview_time = None
                            text_exist = False

                            for line in lines:
                                line = line.strip()
                                if line.startswith('[') and line.endswith(']'):
                                    section = line[1:-1]
                                elif section == "General" and line:
                                    if line.startswith("AudioFilename"):
                                        audio = line.split(":")[1].strip()
                                    if line.startswith("PreviewTime"):
                                        preview_time = int(line.split(":")[1].strip())
                                elif section == "Events" and line:
                                    events = line.split(',')
                                    if events[0] == '0':  # 0 indicates background image in Events
                                        bgimage = events[2].replace('"', '').strip()
                                elif section == "Metadata" and line:
                                    if line.startswith("Title"):
                                        title = line.split(":")[1].strip()
                                    elif line.startswith("Artist"):
                                        artist = line.split(":")[1].strip()
                                    elif line.startswith("Creator"):
                                        creator = line.split(":")[1].strip()
                                elif section == "Difficulty" and line:
                                    if line.startswith("OverallDifficulty"):
                                        difficulty = line.split(":")[1].strip()
                                elif section == "Text" and line:
                                    text_exist = True
                            if text_exist and audio and bgimage and title and artist and creator and difficulty:
                                key = (audio, title, artist)
                                audio_path = os.path.join(folder_full_path, audio)
                                image_path = os.path.join(folder_full_path, bgimage)

                                if key not in self.levels:
                                    self.levels[key] = {
                                        "preview": Preview(str(audio_path), str(image_path), title, artist, preview_time),
                                        "difficulties": []
                                    }

                                self.levels[key]["difficulties"].append(
                                    Difficulty(str(os.path.join(folder_full_path, file_path)), creator, difficulty)
                                )
        if self.levels:
            self.lvl_slct = Level_select(self.levels)

    def interate_on_osu(self, file):
        self.osu_data = file.read()

        lines = self.osu_data.splitlines()
        section = None
        hit_objects = []
        object_count = 0    
        previous_time = None
        updated_lines = []  # Create a list to hold the lines to keep
        line_count = 0

        #_text_exists = False
        text_exists = False
        self.map_text_exists = False
        mode = None
        audio = None
        bgimage = None

        for line in lines:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                section = line[1:-1]
                updated_lines.append(line)
            
            elif section == "General" and line:
                updated_lines.append(line)
                if line.startswith("Mode:"):
                    mode = line.split(":")[1].strip()

            elif section == "HitObjects" and line:
                parts = line.split(',')
                x, y, time, hit_type = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                if hit_type & 2:  # Slider
                    path = parts[5]
                    repeat = int(parts[6])
                    length = float(parts[7])
                    hit_objects.append(time)
                else:  # Hit circle or other types
                    hit_objects.append(time)

                if previous_time is None or previous_time != time:
                    updated_lines.append(line)  # Keep this line since it's not a duplicate
                    previous_time = time  # Update previous_time for the next iteration
                    object_count += 1  # Only increment count if the line is kept
            elif section == "Text" and line:
                self.map_text_exists = True
                updated_lines.append(line)
            else:
                updated_lines.append(line)

        return object_count, mode, updated_lines
    
    def file_open_and_rmv(self, path): # Removes the possible duplicates
        with open(path, 'r', encoding='utf-8') as file:
            self.object_count, mode, updated_lines = self.interate_on_osu(file)
            #Here close, open for writing. Then open for reading to continue the rest
        if mode == 3:
            with open(path, 'w', encoding='utf-8') as file:
                # Write the updated lines back to the file
    
                file.write('\n'.join(updated_lines))
            with open(path, 'r', encoding='utf-8') as file:
                self.object_count, _, _ = self.interate_on_osu(file)  # Get the updated count

        if self.object_count > 720:
            self.input_box.resize_font(12)
        else:
            self.input_box.resize_font(32)

    def convert(self, path, text):
        with open(path, 'r', encoding='utf-8') as file:
            self.object_count, mode, updated_lines = self.interate_on_osu(file)
        if self.map_text_exists:
            updated_lines.pop()
            updated_lines.pop()
            updated_lines.append("[Text]")
            updated_lines.append(text)
        else:
            updated_lines.append("[Text]")
            updated_lines.append(text)
        with open(path, 'w', encoding='utf-8') as file:
                # Write the updated lines back to the file
                file.write('\n'.join(updated_lines))

        self.load_levels()