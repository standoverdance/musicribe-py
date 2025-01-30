from pathlib import Path
import pygame
import threading
import multiprocessing
import time
from pygame import mixer
from .player import Player
from .healthbar import HealthBar
from .lights import Misslight, Sliderlight
from .conductor import Conductor
from .score import Score
from .letter import Letter
from ..timer import Timer # type: ignore
from assets import settings
from ..button import Button

# import cProfile
# import pstats



playerwidth = 150

mixer.init()



class Level:
    def __init__(self, level_data):
        #Get the display surface
        self.display_surface = pygame.display.get_surface()
        self.prev_time = time.time()

        # Sprite groups
        self.visible_sprites = pygame.sprite.Group()
        self.pause_sprites = pygame.sprite.Group()

        self.level_data = level_data

        #Player and UI elements
        self.playa = Player(settings.BASEPOS, settings.PLAYER_SIZE,  self.visible_sprites) # It's the rectangle box of player
        self.healthbar = HealthBar(((settings.BASEPOS[0]-settings.HEALTH_BAR_SIZE[0] - 10), (settings.BASEPOS[1]+ settings.PLAYER_SIZE[1])), settings.HEALTH_BAR_SIZE, self.visible_sprites)
        self.healthbar.fill_rect_calc()
        self.misslight = Misslight(settings.BASEPOS, settings.PLAYER_SIZE, self.visible_sprites)
        self.sliderlight = Sliderlight(settings.BASEPOS, settings.PLAYER_SIZE, self.visible_sprites)
        
        
        #Timers
        self.end_timer = None
        self.player_state_cooldown = Timer(150, self.playa.defaultstate)
        self.miss_cooldown = Timer(50, self.playa.defaultstate)
        self.timers = [self.miss_cooldown, self.player_state_cooldown] # Timers won't refresh if you don't add them to this group

        self.is_red = False
        self.accuracy_count = {"perfect": 0, "good":0,"ok":0,"meh":0,"miss":0}

        score_pos = ((settings.BASEPOS[0] + settings.PLAYER_SIZE[0]),(settings.BASEPOS[1]/20))
        combo_pos = ((settings.BASEPOS[0] + settings.PLAYER_SIZE[0]), (settings.BASEPOS[1] - settings.PLAYER_SIZE[1]/2))
        percent_pos = ((settings.BASEPOS[0] + settings.PLAYER_SIZE[0]), (settings.BASEPOS[1]/7))
        self.score = Score(score_pos, 60, self.visible_sprites)
        self.combo = Score(combo_pos, 60, self.visible_sprites, "x")
        self.percent = Score(percent_pos, 45, self.visible_sprites, "%")
        

        # Debug rects
        self.debug_rects = [pygame.Rect(settings.BASEPOS[0], settings.BASEPOS[1], 5, 5)] # Below it's commented with +=======================+ flag
        self.press_time = 0
        self.index = 0
        self.print_limit = 50
        
        #Pause or game over
        self.dead = False
        self.buttons = []

        self.game_over_screen_fade = pygame.Surface((settings.WIDTH, settings.HEIGHT))
        self.game_over_screen_fade.fill((0, 0, 0))
        self.game_over_screen_fade.set_alpha(160)
        
        self.transparent_surface = pygame.Surface((settings.WIDTH, settings.HEIGHT))
        self.transparent_surface.set_alpha(128)  # 128 is half transparency
        self.transparent_surface.fill((255, 192, 0))
        
        self.btn_size = ((settings.WIDTH / 4), (settings.HEIGHT / 7))
        self.btn_pos = ((settings.WIDTH / 2 - self.btn_size[0] / 2), self.btn_size[1])
        self.b_continue = Button("Continue", self.btn_pos, self.btn_size, (128, 255, 128), (255, 255, 255))
        self.b_retry = Button("Retry", (self.btn_pos[0], self.btn_pos[1] + self.btn_size[1] * 1.7), self.btn_size, (255, 152, 0), (255, 255, 255))
        self.b_menu = Button("Menu", (self.btn_pos[0], self.btn_pos[1] + self.btn_size[1] * 3.4), self.btn_size, (255, 50, 0), (255, 255, 255))

        self.game_over_text = Letter(
            (round(settings.WIDTH / 2), round(settings.HEIGHT / 8)),
            100,
            "Game Over",
            [],
            settings.Oxanium_Font, 2,
            "center"
        )

        #Conductor and it's dependencies
        self.Conductor = Conductor(self.level_data, self.visible_sprites) #Conductor manages the logic behind the rhythm and components moving according to it
        self.text = self.Conductor.text
        background_image = pygame.image.load(self.Conductor.background_path) 
        image_width, image_height = background_image.get_size()
        aspect_ratio = image_width / image_height
        self.scaled_image = pygame.transform.scale(background_image, (settings.WIDTH, int(settings.WIDTH / aspect_ratio)))
        self.map_rect = self.Conductor.boxgroup # Now Directibly accessible ###(#(#(#(#))))
        self.sliders = self.Conductor.slidergroup
        self.map_times = self.Conductor.map_times
        self.map_times_length = len(self.map_times)
        self.initial_to_box = {box.initial: box for box in self.map_rect}
        self.index_to_box = {index: box for index, box in enumerate(self.map_rect)}
        self.manager = multiprocessing.Manager()
        self.shared_map_times = self.manager.list(self.map_times)

        self.music_time = multiprocessing.Value('d', 0.0)

        self.letter_bool = False
        self.timing = False
        self.pause = False
        self.complete = False
        self.hold = None # Holds the letter of a slider.
        mixer.music.load(self.Conductor.music_path)
        mixer.music.play()
        self.schedule_end(self.map_times[-1])

        self.process = None
        self.start_process()

        #Anti spamming
        self.last_index = 6969
        self.checkable = True

    def start_process(self):
        if self.process is not None:
            self.process.terminate()
        self.process = multiprocessing.Process(target=self.map_rect_refresh, args=(self.map_times, self.shared_map_times, self.music_time))
        self.process.start()

    # def restart(self):
    #     if self.process is not None:
    #         self.process.terminate()
    #     self.__init__(self.level_data)

    def restart(self):
        self.__init__(self.level_data)

    @staticmethod
    def map_rect_refresh(map_times, shared_map_times, music_time):
        while True:
            time.sleep(1)
            current_music_time = music_time.value
            lower_bound = current_music_time - 400
            upper_bound = current_music_time + settings.LOADING_TIME
            shared_map_times[:] = [timing for timing in map_times if lower_bound <= timing <= upper_bound]
            #print(f"Music time: {current_music_time} Map times: {shared_map_times}")


    def events(self, event):
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)  # Get the name of the key
            if self.pause:
                if key_name == 'return':
                    if self.healthbar.current_health <= 0 or self.complete: #Restart
                        self.restart()
                    else: # Continue
                        self.pausing()
                elif key_name == 'escape':
                    custom_event = pygame.event.Event(pygame.USEREVENT, {'action': 'uninitialize_level'})
                    pygame.event.post(custom_event)
            else:
                if key_name == 'escape':

                    self.pausing()
                    self.buttons = [self.b_continue, self.b_retry, self.b_menu]
                    self.position_buttons(self.buttons, 0)
                    if self.game_over_text in self.pause_sprites:
                        self.pause_sprites.remove(self.game_over_text)
                elif key_name == '`':
                    self.restart()

                self.player_state_cooldown.activate() # After a while it will change it back to default skin

                
                #Conductor's event part
                press_time = mixer.music.get_pos()
                self.press_time = press_time
                index, message, score = self.Conductor.check_accuracy(press_time)
                is_slider = self.Conductor.is_it_slider(press_time)
                self.index = index
                
                if index != 2137:

                    if settings.Modifiers.WHATEVER_LETTER and message != "":
                        self.map_rect[index].is_visible = False 
                        if is_slider:
                            self.hold = key_name
                        else:
                            self.text.letter_update()
                        self.message_routine(score, message, index)
                        self.healthbar.current_health += score / 3

                    elif message == "miss":
                        self.miss()
                        if self.text.first_letter.lower() == key_name:
                            self.message_routine(score, message, index)
                            if is_slider:
                                self.hold = None
                        
                    elif message != "":
                        if self.text.first_letter.lower() == key_name:
                            if is_slider:
                                self.hold = key_name
                                self.sliderlight.changestate(message)
                            else:
                                self.text.letter_update()
                            self.healthbar.current_health += score / 3
                            self.message_routine(score, message, index)
                
                        

                if settings.Modifiers.SPACE_LOCK == 1 and key_name == "space" and self.text.first_letter == key_name: self.text.letter_update()
            
        elif event.type == pygame.KEYUP:
            key_name = pygame.key.name(event.key)  # Get the name of the key
            # Track key release time
            key_up_time = mixer.music.get_pos()
            if self.hold and self.hold == key_name:
                self.hold = None
                index, message, score = self.Conductor.check_slider(key_up_time)
                if message == "miss":
                    self.miss()  
                self.text.letter_update()
                self.message_routine(score, message, index)    
                self.player_state_cooldown.activate() # After a while it will change it back to default skin



        elif self.b_continue.is_clicked(event): 
            self.pause = False
            self.Conductor.pause()

        elif self.b_retry.is_clicked(event):
            self.restart()

        elif self.b_menu.is_clicked(event):
            custom_event = pygame.event.Event(pygame.USEREVENT, {'action': 'uninitialize_level'})
            pygame.event.post(custom_event) # Here it should initialize menu  class and stop level class


    def run(self):
        # profiler = cProfile.Profile()
        # profiler.enable()

        dt = time.time() - self.prev_time
        self.prev_time = time.time()

        self.display_surface.fill((255, 192, 0))
        self.display_surface.blit(self.scaled_image, (0, 0))  
        self.display_surface.blit(self.transparent_surface, (0, 0))  
        self.music_time.value = mixer.music.get_pos()
        if not self.pause:
            #debug(f"{self.press_time} : {self.index}")
            #if self.music_time.value > self.Conductor.break_sections[0][1]:
            if not settings.Modifiers.NO_DEATH:
                self.healthbar.update(dt, self.music_time.value, self.Conductor.break_sections)
            
            # for rect in self.debug_rects:
            #    pygame.draw.rect(self.display_surface, (255, 0, 0), rect) #+====+====+====+====+====+====+====+====+====+====+

            sorted_sprites = sorted(self.visible_sprites, key=lambda sprite: sprite.z_pos)
            self.box_sprite_logic(self.music_time.value)
            pygame.draw.rect(self.display_surface, self.healthbar.fill_color, self.healthbar.fill_rect)

            for sprite in sorted_sprites:
                self.display_surface.blit(sprite.image, sprite.rect)
                
            for timer in self.timers:
                timer.update()

            self.misslight.update(dt)
            self.sliderlight.update(dt)
            if self.hold:
                self.sliderlight.image.set_alpha(300)
            if self.healthbar.current_health <= 0:
                self.pausing()
                self.buttons = [self.b_retry, self.b_menu]
                self.position_buttons(self.buttons, 0)
                self.dead = True
                self.pause_sprites.add(self.game_over_text)
        else:
            #debug(self.accuracy_count)
            sorted_sprites = sorted(self.visible_sprites, key=lambda sprite: sprite.z_pos)
            for sprite in sorted_sprites:
                self.display_surface.blit(sprite.image, sprite.rect)
            pygame.draw.rect(self.display_surface, self.healthbar.fill_color, self.healthbar.fill_rect)
            self.display_surface.blit(self.game_over_screen_fade, (0, 0))
            for sprite in self.pause_sprites:
                self.display_surface.blit(sprite.image, sprite.rect)
            

            for button in self.buttons:
                button.draw(self.display_surface)
        
        # profiler.disable()
        # stats = pstats.Stats(profiler)
        # stats.sort_stats(pstats.SortKey.TIME)
        # stats.print_stats()

    #events functions

    def pausing(self):
        self.pause = not self.pause
        self.Conductor.pause()
        if self.pause:
            if self.process is not None:
                self.process.terminate()
            self.end_timer.cancel()
        else:
            self.start_process()
            self.schedule_end(self.map_times[-1])
            

    def message_routine(self, score, message, index):
        self.accuracy_count[message] += 1
        self.percent.percent(self.accuracy_count)
        self.score.update(round(score + score * self.combo.score * 0.1))
        self.playa.changestate(message)
        self.combo.update(1)
        box = self.index_to_box[index]
        box.is_visible = False

    def schedule_end(self, target_time):
        if self.end_timer is not None:
            self.end_timer.cancel()

        current_position = mixer.music.get_pos()
        delay = (target_time - current_position) / 1000 + 0.2 # Convert milliseconds to seconds
        self.end_timer = threading.Timer(delay, self.trigger_function)
        self.end_timer.start()

    def trigger_function(self):
        self.process.terminate()
        self.buttons = [self.b_retry, self.b_menu]
        self.position_buttons(self.buttons, 1)
        spacing = 50
        table_pos = ((settings.WIDTH / 2), (settings.HEIGHT - spacing * (len(self.accuracy_count) + 1)))
        size = 40
        offset_y = 0
        offset_x = 0
        for line in self.accuracy_count:
            Letter((table_pos[0] + offset_x, table_pos[1] + offset_y), size, line, [self.pause_sprites], anchor = "topright")
            offset_x += spacing
            Letter((table_pos[0] + offset_x, table_pos[1] + offset_y), size, ":", [self.pause_sprites], anchor = "topleft")
            offset_x += spacing
            Letter((table_pos[0] + offset_x, table_pos[1] + offset_y), size, str(self.accuracy_count[line]), [self.pause_sprites], anchor = "topleft")
            offset_x = 0
            offset_y += spacing
        
        Letter(((settings.WIDTH - 50), 50), 60, "Score:  "+str(round(self.score.score)), self.pause_sprites, anchor = "topright")
        Letter(((settings.WIDTH - 50), 150), 60, "Percent:  "+str(self.percent.score) +"%", self.pause_sprites, anchor = "topright")
        Letter(((settings.WIDTH - 50), 250), 60, "Highest combo:  x"+str(self.combo.max_combo), self.pause_sprites, anchor = "topright")

        self.pause = True
        self.complete = True
    # Conductor's update part

    def box_sprite_logic(self, elapsed_time):


        # for box in self.map_rect: ,#+=====+====+=====+=====+=====+====++=====+====+====+
        #     if box.initial == initial:
        #         if elapsed_time > (initial - 5) and elapsed_time < (initial + 5):
        #             self.debug_rects.append(pygame.Rect(box.rect.left, box.rect.bottom, 200, 5))  #+====+====+====+====+====+
        #         break  # Exit the loop once the matching box is found
        # Loop through only those boxes that have initials listed within self.shared_map_times

        if self.sliders:
            for slider in self.sliders:
                if slider.rect.y > -500 and slider.rect.y < 20:
                    slider.is_visible = True
                elif slider.rect.y > settings.BASEPOS[1] + 200:
                    if slider.is_visible:
                        slider.is_visible = False

                if slider.is_visible and not slider.appended:
                    self.visible_sprites.add(slider)
                    slider.appended = True
                elif slider.appended and not slider.is_visible:
                    self.visible_sprites.remove(slider)
                slider.update(elapsed_time)


        for initial in self.shared_map_times:
            box = self.initial_to_box.get(initial)
            if box:
                if box.rect.y > -50 and box.rect.y < 20:
                    box.is_visible = True
                elif box.rect.y > settings.BASEPOS[1] + 200:
                    if box.is_visible:
                        box.is_visible = False
                        if settings.Modifiers.KILL_ON_MISS:
                            self.text.letter_update()
                        self.miss()

                if box.is_visible and not box.appended:
                    self.visible_sprites.add(box)
                    box.appended = True
                elif box.appended and not box.is_visible:
                    self.visible_sprites.remove(box)
                box.update(elapsed_time)

    
    def miss(self):
        self.misslight.image.set_alpha(200)
        self.accuracy_count["miss"] += 1
        self.percent.percent(self.accuracy_count)
        self.playa.changestate("miss")  
        self.combo.reset_combo()
        self.miss_cooldown.activate()
        self.healthbar.current_health -= 10


    # Pause or game over funcs
   
    def position_buttons(self, buttons, instance):
        count = len(buttons)
        if count == 0:
            return
        
        if not instance: # Instance 0 when pausing or losing. Instance 1 when winning which is triggered in conductor
            total_height = sum(button.rect.height for button in buttons)
            spacing = (settings.HEIGHT / count) / 4
            
            total_space = total_height + spacing * (count - 1)
            # Start Y position - centers the buttons on the screen
            start_pos = (settings.HEIGHT - total_space) / 2
            current_y = start_pos
            for button in buttons:
                button.update_pos(button.pos[0], current_y)
                current_y += button.rect.height + spacing 

        else:
            total_height = sum(button.rect.height for button in buttons)
            spacing = (settings.HEIGHT / count) / 10
            
            total_space = total_height + spacing * (count - 1)
            # Start Y position - centers the buttons on the screen
            start_pos = (settings.HEIGHT - total_space * 1.2)
            current_y = start_pos
            current_x = settings.WIDTH - (round(self.btn_size[0] * 1.2))
            for button in buttons:
                button.update_pos(current_x, current_y)
                current_y += button.rect.height + spacing 

    def cleanup(self):
        if self.process is not None:
            self.process.terminate()
            self.process.join()
        if self.end_timer:
            self.end_timer.cancel()