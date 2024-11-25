import pygame, time
from pygame import mixer
from button import Button
from .player import Player
from .healthbar import HealthBar
from .misslight import Misslight
from .conductor import Conductor
from .score import Score
from .letter import Letter
from timer import Timer # type: ignore
from settings import *
from debug import *


playerwidth = 150

mixer.init()

LEVEL_COMPLETE_EVENT = pygame.USEREVENT + 1

class Level:
    def __init__(self, level_data):
        #Get the display surface
        self.display_surface = pygame.display.get_surface()
        self.prev_time = time.time()

        self.visible_sprites = pygame.sprite.Group()
        self.pause_sprites = pygame.sprite.Group()

        self.level_data = level_data

        #Sprites
        self.Conductor = Conductor(self.level_data, self.visible_sprites) #Conductor manages the logic behind the rhythm and components moving according to it
        self.text = self.Conductor.text
        self.playa = Player(BASEPOS, PLAYER_SIZE,  self.visible_sprites) # It's the rectangle box of player
        self.healthbar = HealthBar(((BASEPOS[0]-HEALTH_BAR_SIZE[0] - 10), (BASEPOS[1]+ PLAYER_SIZE[1])), HEALTH_BAR_SIZE, self.visible_sprites)
        self.healthbar.fill_rect_calc()
        self.misslight = Misslight(BASEPOS, PLAYER_SIZE, self.visible_sprites)
        #background_image = pygame.image.load(self.level_data["img"]) 
        background_image = pygame.image.load(self.Conductor.background_path) 
        image_width, image_height = background_image.get_size()
        aspect_ratio = image_width / image_height
        
        self.scaled_image = pygame.transform.scale(background_image, (WIDTH, int(WIDTH / aspect_ratio)))
        
        #Timers
        self.player_state_cooldown = Timer(150, self.playa.defaultstate)
        self.miss_cooldown = Timer(50, self.playa.defaultstate)
        self.timers = [self.miss_cooldown, self.player_state_cooldown] # Timers won't refresh if you don't add them to this group

        self.is_red = False
        self.sprite_pass_count = 0

        self.accuracy_count = {"perfect": 0, "good":0,"ok":0,"meh":0,"miss":0}

        score_pos = ((BASEPOS[0] + PLAYER_SIZE[0]),(BASEPOS[1]/20))
        combo_pos = ((BASEPOS[0] + PLAYER_SIZE[0]), (BASEPOS[1] - PLAYER_SIZE[1]/2))
        percent_pos = ((BASEPOS[0] + PLAYER_SIZE[0]), (BASEPOS[1]/7))
        self.score = Score(score_pos, 60, self.visible_sprites)
        self.combo = Score(combo_pos, 60, self.visible_sprites, "x")
        self.percent = Score(percent_pos, 45, self.visible_sprites, "%")
        self.letter_bool = False
        self.timing = False


        self.pause = False
        self.pause_time = 0
        self.start_time = pygame.time.get_ticks()
        self.complete = False

        # Debug rects
        self.debug_rects = [pygame.Rect(BASEPOS[0], BASEPOS[1], 5, 5)]
        self.press_time = 0
        self.index = 0
        
        #Pause or game over
        self.dead = False
        self.btn_size = ((WIDTH / 4), (HEIGHT / 7))
        self.btn_pos = ((WIDTH / 2 - self.btn_size[0] / 2), self.btn_size[1])
        self.b_continue = Button("Continue", self.btn_pos, self.btn_size, (128, 255, 128), (255, 255, 255))
        self.b_retry = Button("Retry", (self.btn_pos[0], self.btn_pos[1] + self.btn_size[1] * 1.7), self.btn_size, (255, 152, 0), (255, 255, 255))
        self.b_menu = Button("Menu", (self.btn_pos[0], self.btn_pos[1] + self.btn_size[1] * 3.4), self.btn_size, (255, 50, 0), (255, 255, 255))
        self.buttons = []
        self.game_over_screen_fade = pygame.Surface((WIDTH, HEIGHT))
        self.game_over_screen_fade.fill((0, 0, 0))
        self.game_over_screen_fade.set_alpha(160)

        self.game_over_text = Letter((round(WIDTH/2),round(HEIGHT / 8)), 100, "Game Over", [], 2, "../font/Oxanium-VariableFont_wght.ttf", "center")
        self.transparent_surface = pygame.Surface((WIDTH, HEIGHT))

        self.transparent_surface.set_alpha(128)  # 128 is half transparency
        self.transparent_surface.fill((255, 192, 0))



    def restart(self):
        self.__init__(self.level_data)


    def events(self, event):
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)  # Get the name of the key

            if self.pause:
                if key_name == 'return':
                    if self.healthbar.current_health <= 0 or self.complete: #Restart
                        self.restart()
                    else: # Continue
                        self.pause = False
                        self.pause_time += self.Conductor.pause()
                elif key_name == 'escape':
                    custom_event = pygame.event.Event(pygame.USEREVENT, {'action': 'uninitialize_level'})
                    pygame.event.post(custom_event)
            else:
                if key_name == 'escape':

                    self.pause = not self.pause
                    self.pause_time += self.Conductor.pause()
                    self.buttons = [self.b_continue, self.b_retry, self.b_menu]
                    self.position_buttons(self.buttons, 0)
                    if self.game_over_text in self.pause_sprites:
                        self.pause_sprites.remove(self.game_over_text)

                self.player_state_cooldown.activate() # After a while it will change it back to default skin

                
                #Conductor's event part

                press_time = pygame.time.get_ticks() - self.pause_time
                self.press_time = press_time
                index, message, score = self.Conductor.check_accuracy(press_time)
                self.index = index
                
                if index != 2137:

                    if WHATEVER_LETTER and message != "":
                        self.Conductor.map_rect[index].is_visible = False 
                        self.text.letter_update()
                        self.message_routine(score, message, index)
                        self.healthbar.current_health += score / 3

                    elif message == "miss":
                        self.miss()
                        if self.text.first_letter.lower() == key_name:
                            self.message_routine(score, message, index)
                        
                    elif message != "":
                        if self.text.first_letter.lower() == key_name:
                            self.text.letter_update()
                            self.healthbar.current_health += score / 3
                            self.message_routine(score, message, index)
                
                        

                if SPACE_LOCK == 1 and key_name == "space" and self.text.first_letter == key_name: self.text.letter_update()

        elif self.b_continue.is_clicked(event): 
            self.pause = False
            self.pause_time += self.Conductor.pause()

        elif self.b_retry.is_clicked(event):
            self.restart()

        elif self.b_menu.is_clicked(event):
            custom_event = pygame.event.Event(pygame.USEREVENT, {'action': 'uninitialize_level'})
            pygame.event.post(custom_event) # Here it should initialize menu  class and stop level class

        elif event.type == LEVEL_COMPLETE_EVENT:
            self.pause = True
            self.complete = True
            self.buttons = [self.b_retry, self.b_menu]
            self.position_buttons(self.buttons, 1)
            spacing = 50
            table_pos = ((WIDTH / 2), (HEIGHT - spacing * (len(self.accuracy_count) + 1)))
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
            
            Letter(((WIDTH - 50), 50), 60, "Score:  "+str(round(self.score.score)), [self.pause_sprites], anchor = "topright")
            Letter(((WIDTH - 50), 150), 60, "Percent:  "+str(self.percent.score) +"%", [self.pause_sprites], anchor = "topright")
            Letter(((WIDTH - 50), 250), 60, "Highest combo:  x"+str(self.combo.max_combo), [self.pause_sprites], anchor = "topright")


    def run(self):

        dt = time.time() - self.prev_time
        self.prev_time = time.time()

        self.display_surface.fill((255, 192, 0))
        self.display_surface.blit(self.scaled_image, (0, 0))  
        self.display_surface.blit(self.transparent_surface, (0, 0))  
        elapsed_time = pygame.time.get_ticks()
        game_time = elapsed_time - self.pause_time
        debug(f"{game_time} : {self.Conductor.break_sections} : {dt}")
        if not self.pause:
            #debug(f"{self.press_time} : {self.index}")
            if not NO_DEATH:
                self.healthbar.update(dt, game_time, self.Conductor.break_sections)
            #debug(game_time)
            
            #for rect in self.debug_rects:
            #    pygame.draw.rect(self.display_surface, (255, 0, 0), rect) #+====+====+====+====+====+====+====+====+====+====+

            # if self.Conductor.break_sections and not sections_cleared:
            #     for section in self.Conductor.break_sections:
            #         if section[0] < game_time > section[1]:
                        

            


            sorted_sprites = sorted(self.visible_sprites, key=lambda sprite: sprite.z_pos)
            self.box_sprite_logic(game_time)
            pygame.draw.rect(self.display_surface, self.healthbar.fill_color, self.healthbar.fill_rect)

            for sprite in sorted_sprites:
                self.display_surface.blit(sprite.image, sprite.rect)

            for timer in self.timers:
                timer.update()

    
            self.misslight.update(dt)
            if self.healthbar.current_health <= 0:
                self.pause = not self.pause
                self.pause_time += self.Conductor.pause()
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

    #events functions

    def message_routine(self, score, message, index):
        self.accuracy_count[message] += 1
        self.percent.percent(self.accuracy_count)
        self.score.update(round(score + score * self.combo.score * 0.1))
        self.playa.changestate(message)
        self.combo.update(1)
        self.Conductor.map_rect[index].is_visible = False

    # Conductor's update part

    def box_sprite_logic(self, elapsed_time):
        for box in self.Conductor.map_rect: 
            
            #if elapsed_time > (box.initial - 5) and elapsed_time < (box.initial + 5):
            #    self.debug_rects.append(pygame.Rect(box.rect.left, box.rect.bottom, 200, 5))  #+====+====+====+====+====+

            if box.rect.y > -50 and box.rect.y < 20:
                box.is_visible = True

            if box.rect.y > BASEPOS[1] + 200:
                if box.is_visible:
                    box.is_visible = False
                    if KILL_ON_MISS: 
                        self.text.letter_update()
                    self.miss()
                    if box.final_box:
                        pygame.event.post(pygame.event.Event(LEVEL_COMPLETE_EVENT))
                box.kill()
                

            if box.is_visible and not box.appended:
                self.visible_sprites.add(box)
                box.appended = True
            elif not box.is_visible and box.appended:
                self.visible_sprites.remove(box)
            box.update(elapsed_time)
    
    def miss(self):
        self.misslight.image.set_alpha(200)
        self.accuracy_count["miss"] += 1
        self.percent.percent(self.accuracy_count)
        self.playa.changestate("miss")  
        self.combo.reset()
        self.miss_cooldown.activate()
        self.healthbar.current_health -= 10


    # Pause or game over funcs
   
    def position_buttons(self, buttons, instance):
        count = len(buttons)
        if count == 0:
            return
        
        if not instance: # Instance 0 when pausing or losing. Instance 1 when winning which is triggered in conductor
            total_height = sum(button.rect.height for button in buttons)
            spacing = (HEIGHT / count) / 4
            
            total_space = total_height + spacing * (count - 1)
            # Start Y position - centers the buttons on the screen
            start_pos = (HEIGHT - total_space) / 2
            current_y = start_pos
            for button in buttons:
                button.update_pos(button.pos[0], current_y)
                current_y += button.rect.height + spacing 

        else:
            total_height = sum(button.rect.height for button in buttons)
            spacing = (HEIGHT / count) / 10
            
            total_space = total_height + spacing * (count - 1)
            # Start Y position - centers the buttons on the screen
            start_pos = (HEIGHT - total_space * 1.2)
            current_y = start_pos
            current_x = WIDTH - (round(self.btn_size[0] * 1.2))
            for button in buttons:
                button.update_pos(current_x, current_y)
                current_y += button.rect.height + spacing 