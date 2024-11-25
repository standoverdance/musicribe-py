import pygame
import os
from pygame import mixer
from .fallingbox import Falling_box
from settings import *
from mutagen import mp3
from .lettertype import LetterType

LEVEL_COMPLETE_EVENT = pygame.USEREVENT + 1

class Conductor():
    def __init__(self, pathtomap, spritegroup):
        self.visible_sprites = spritegroup   
        self.boxgroup = pygame.sprite.Group()     
        self.mappath = pathtomap

        map_times, audio_file, text, bgimg, font = self.parse_osu_file(pathtomap)
        music_path = self.get_full_path(pathtomap, audio_file)
        self.background_path = self.get_full_path(pathtomap, bgimg)
            

        mixer.music.load(music_path)
        self.start_time = pygame.time.get_ticks()
        mixer.music.play()


        self.count = len(map_times)
        self.this_time, self.break_sections = self.current_times(map_times)
        self.final_box = len(self.this_time) - 1
        self.map_rect = self.rectify_times(self.this_time, self.boxgroup)

        
        #Anti spamming
        self.pressed_or_missed_list = []
        self.last_index = 6969
        self.checkable = True

        self.pause_start = 0
        self.pause_end = 0

        if font:
            font_path = self.get_full_path(pathtomap, font)
            self.text = LetterType(100, text, self.visible_sprites, font_path) #Rhythmless typing game part 
        else:
            self.text = LetterType(100, text, self.visible_sprites)

    def parse_osu_file(self, file_path):
        font = None
        with open(file_path, 'r', encoding='utf-8') as file:
            section = None
            hit_objects = [0] #The zero here is so that hitobjects starts with index 1. 
            #If you remove it. You will always miss the first note. 
            # But now I've changed current_times function based on it. If you delete it it will create a domino of errors. 
            # Good luck. That's a challange.
            object_count = 0
            for line in file:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    section = line[1:-1]
                elif section == "HitObjects" and line:
                    parts = line.split(',')
                    object_count += 1
                    x, y, time, hit_type = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
                    if hit_type & 2:  # Slider
                        path = parts[5]
                        repeat = int(parts[6])
                        length = float(parts[7])
                        hit_objects.append(time)
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
                elif section == "Difficulty" and line:
                    if line.startswith("OverallDifficulty"):
                        self.difficulty = line.split(":")[1].strip()
                elif section == "Text" and line:
                    text = line
                    #print(len(text))
            #print(object_count)
                

        return hit_objects, audio_file, text, bgimage, font

    def get_full_path(self, pathtomap, file):
        # Get the directory of the .osu file
        map_directory = os.path.dirname(pathtomap)
        
        # Combine it with the relative audio filename from the .osu file
        music_path = os.path.join(map_directory, file)
        return music_path

    def current_times(self, times):
        current_time = []
        last_time = 0
        break_section = []
        wait = []
        for index, time in enumerate(times):
            if time - last_time - 2500 > 0:
                break_section.append(index)
            last_time = time
            current_time.append(time + self.start_time)
        if break_section:
            for index in break_section:
                wait.append((current_time[index-1], current_time[index]))

        return current_time, wait

    def rectify_times(self, times, spritegroup):
        rects = []
        for index, time in enumerate(times):
            if index == self.final_box:
                rects.append(Falling_box(BASEPOS[0] + 4, time - (int(BASEPOS[1]) + PLAYER_SIZE[1] / 1.17), (150,31), time, spritegroup, SPEED, time, True))
            else:
                rects.append(Falling_box(BASEPOS[0] + 4, time - (int(BASEPOS[1]) + PLAYER_SIZE[1] / 1.17), (150,31), time, spritegroup, SPEED, time, False))
        return rects
    

    def get_timing_data(file_path):
        with open(file_path, 'r') as file:
            section = None
            TimingPoint = []
            TimingPoints = []

            for line in file:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    section = line[1:-1]
                elif section == "TimingPoints" and line:
                    parts = line.split(',')
                    offset, miliseconds_per_beat, meter = int(parts[0]), parts[1], int(parts[2])
                    TimingPoint = []
                    TimingPoint.append(offset, miliseconds_per_beat, meter)
                    TimingPoints.append(TimingPoint)
        return TimingPoints
    
    def get_mp3_length_in_miliseconds(file_path):
        audio = mp3(file_path)
        length_in_seconds = audio.info.length
        length_in_milliseconds = int(length_in_seconds * 1000)
        return length_in_milliseconds
    

    def check_accuracy(self, press_time):
        closest_index = min(range(len(self.this_time)), key=lambda i: abs(self.this_time[i] - press_time))

        if closest_index == self.final_box:#len(self.this_time) - 1:
            pygame.event.post(pygame.event.Event(LEVEL_COMPLETE_EVENT))

        if closest_index == self.last_index:
            self.checkable = False
        else:
            self.checkable = True


        
        if self.checkable:
            difficulty = self.difficulty
            if self.this_time[closest_index - 1] not in self.pressed_or_missed_list and self.this_time[closest_index - 1] > press_time - (141 - 3 * difficulty): #Wasn't pressed and within "meh" range.
                correct_timing = self.this_time[closest_index - 1]
            else:
                correct_timing = self.this_time[closest_index]  
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
        self.pressed_or_missed_list.append(closest_index)

    def pause(self):
        if pygame.mixer.music.get_busy():  # Check if music is currently playing
            pygame.mixer.music.pause()
            self.pause_start = pygame.time.get_ticks()
            #print(str(self.pause_start) + "<-----Pause start")
            pause_time = 0

        else:
            pygame.mixer.music.unpause()
            self.pause_end = pygame.time.get_ticks()
            pause_time = self.pause_end - self.pause_start
            self.adjust_map(pause_time)
            #print(str(pause_time) + "<-----Pause time")
            #print(self.break_sections)
            self.break_sections = self.adjust_breaks(pause_time, self.break_sections)
            #print(self.break_sections)
        return pause_time
    
    def load(self):
        pygame.mixer.music.pause()

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
