import pygame
import os
from .fallingbox import Falling_box
from .slider import Slider
from assets import settings
from mutagen import mp3
from .lettertype import LetterType
from ..button import Button



class Conductor():
    def __init__(self, pathtomap, spritegroup, map_times = None, map_rect = None, texte = None, fonte = None):
        self.visible_sprites = spritegroup   
        self.boxgroup = pygame.sprite.Group() 
        self.slidergroup = pygame.sprite.Group()    

        self.base_slider_velocity = 0.2198
        self.map_times, audio_file, text, bgimg, font, self.sliders = self.parse_osu_file(pathtomap)
        self.music_path = self.get_full_path(pathtomap, audio_file)
        self.background_path = self.get_full_path(pathtomap, bgimg)

        #Anti spamming
        self.last_index = 6969
        self.checkable = True

        self.break_sections = self.breaks(self.map_times)
        self.up_times = []
        for time in self.map_times: Falling_box(settings.BASEPOS[0] + 4, time, (150,31), self.boxgroup)
        for slider in self.sliders: 
            Slider(settings.BASEPOS[0] + 4, slider[0], slider[1], 150, self.slidergroup)
            slider_up_time = slider[0] + slider[1]
            self.up_times.append(slider_up_time)

        if font:
            font_path = self.get_full_path(pathtomap, font)
            self.text = LetterType(100, text, self.visible_sprites, font_path) #Rhythmless typing game part 
        else:
            self.text = LetterType(100, text, self.visible_sprites)

    


    def breaks(self, times):
        last_time = 0
        break_section = []
        wait = []
        for index, time in enumerate(times):
            if index == 1:
                wait.append((0, time))
            if time - last_time - 2500 > 0:
                break_section.append(index)
            last_time = time
        if break_section:
            for index in break_section:
                wait.append((times[index-1], times[index]))

        return wait

    def parse_osu_file(self, file_path):
        font = None
        with open(file_path, 'r', encoding='utf-8') as file:
            section = None
            hit_objects = [0] #The zero here is so that hitobjects starts with index 1. 
            #If you remove it. You will always miss the first note. 
            # But now I've changed current_times function based on it. If you delete it it will create a domino of errors. 
            # Good luck.
            sliders = []
            object_count = 0
            first_timing = False
            turn_off_sliders = False
            for line in file:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    section = line[1:-1]
                elif section == "Difficulty" and line:
                    if line.startswith("OverallDifficulty"):
                        self.difficulty = float(line.split(":")[1].strip())
                    if line.startswith("SliderMultiplier"):
                        self.slider_multiplier = float(line.split(":")[1].strip())
                    if line.startswith("TurnOffSliders"):
                        turn_off_sliders = bool(line.split(":")[1].strip())
                elif section == "TimingPoints" and line and not first_timing:
                    parts = line.split(',')
                    offset, miliseconds_per_beat, meter = int(parts[0]), parts[1], int(parts[2])
                    first_timing = True
                    self.base_slider_velocity = 100 * self.slider_multiplier / float(miliseconds_per_beat)
                elif section == "HitObjects" and line:
                    parts = line.split(',')
                    object_count += 1
                    x, y, time, hit_type = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                    if hit_type & 2 and not turn_off_sliders:  # Slider
                        path = parts[5]
                        repeat = int(parts[6])
                        length = float(parts[7])
                        slider_duration = round((length / self.base_slider_velocity) * repeat)
                        hit_objects.append(time)
                        sliders.append((hit_objects[-1], slider_duration))
                    elif hit_type & 128 and not turn_off_sliders:  # Mania Slider
                        end_time = int(parts[5].split(':')[0])
                        slider_duration = end_time - time
                        hit_objects.append(time)
                        sliders.append((hit_objects[-1], slider_duration))
                    else:  # Hit circle or other types
                        hit_objects.append(time)
                elif section == "General" and line:
                    if line.startswith("AudioFilename:"):
                        audio_file = line.split(":")[1].strip()
                    if line.startswith("Font:"):
                        font = line.split(":")[1].strip()
                elif section == "Events" and line:
                    events = line.split(',')
                    if events[0] == '0':  # 0 indicates background image in Events
                        bgimage = events[2].replace('"', '').strip()
                elif section == "Text" and line:
                    text = line

        return hit_objects, audio_file, text, bgimage, font, sliders

    def get_full_path(self, pathtomap, file):
        # Get the directory of the .osu file
        map_directory = os.path.dirname(pathtomap)
        
        # Combine it with the relative audio filename from the .osu file
        music_path = os.path.join(map_directory, file)
        return music_path
    
    
    def check_slider(self, up_time):
        closest_index = min(range(len(self.up_times)), key=lambda i: abs(self.up_times[i] - up_time))
        ms_difference = abs(self.up_times[closest_index] - up_time)
        difficulty = self.difficulty / 2
        if ms_difference <= 16:
            message = "perfect"
            score = 32
            return closest_index, message, score
        elif ms_difference <= 64 - 3 * difficulty:
            message = "perfect"
            score = 30
            return closest_index, message, score
        elif ms_difference <= 97 - 3 * difficulty:
            message = "good"
            score = 20
            return closest_index, message, score
        elif ms_difference <= 127 - 3 * difficulty:
            message = "ok"
            score = 10
            return closest_index, message, score
        elif ms_difference <= 151 - 3 * difficulty:
            message = "meh"
            score = 5
            return closest_index, message, score
        else:
            message = "miss"
            score = 0
            return closest_index, message, score
        
    def is_it_slider(self, press_time):
        closest_index = min(range(len(self.map_times)), key=lambda i: abs(self.map_times[i] - press_time))
        is_slider = False
        for slider in self.sliders:
            if slider[0] == self.map_times[closest_index]:
                is_slider = True
        return is_slider
    
    def check_accuracy(self, press_time):
        closest_index = min(range(len(self.map_times)), key=lambda i: abs(self.map_times[i] - press_time))

        if closest_index == self.last_index:
            self.checkable = False
        else:
            self.checkable = True
        
        if self.checkable:

            difficulty = self.difficulty

            #This checks if there the box before the closest index is still within "meh" range
            if closest_index - 1 != self.last_index and self.map_times[closest_index - 1] > press_time - (141 - 3 * difficulty):
                closest_index -= 1

            correct_timing = self.map_times[closest_index]  
            ms_difference = abs(correct_timing - press_time)

            if ms_difference <= 16:
                message = "perfect"
                score = 32
                self.box_routine(closest_index)
                return closest_index, message, score
            elif ms_difference <= 64 - 3 * difficulty:
                message = "perfect"
                score = 30
                self.box_routine(closest_index)
                return closest_index, message, score
            elif ms_difference <= 97 - 3 * difficulty:
                message = "good"
                score = 20
                self.box_routine(closest_index)
                return closest_index, message, score
            elif ms_difference <= 127 - 3 * difficulty:
                message = "ok"
                score = 10
                self.box_routine(closest_index)
                return closest_index, message, score
            elif ms_difference <= 151 - 3 * difficulty:
                message = "meh"
                score = 5
                self.box_routine(closest_index)
                return closest_index, message, score
            elif ms_difference <= 188 - 3 * difficulty:
                message = "miss"
                score = 0
                self.box_routine(closest_index)
                return closest_index, message, score
            else:
                message = ""
                score = 0
                closest_index = 2137
                return closest_index, message, score
        else:
            message = ""
            score = 0
            closest_index = 2137
        return closest_index, message, score

    def box_routine(self, closest_index):
        self.last_index = closest_index
        self.checkable = True

    def pause(self):
        if pygame.mixer.music.get_busy():  # Check if music is currently playing
            pygame.mixer.music.pause()

        else:
            pygame.mixer.music.unpause()
            self.pause_end = pygame.time.get_ticks()

    def adjust_map(self, time):
        for sprite in self.map_rect:
            sprite.rect.y - time
    
    def adjust_breaks(self, time, breaks):
        new_list = []
        for start, end in breaks:
            start + time
            end + time
            new_list.append((start, end))
        return new_list