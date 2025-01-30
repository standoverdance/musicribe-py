import pygame 
from assets import settings
from .letter import Letter

class LetterType():
    def __init__(self, size, input_text, spritegroup, font = settings.UI_Font):
        self.spritegroup = spritegroup
        
        self.letter_sprites = pygame.sprite.Group()
        self.initial_text = input_text
        self.size = size
        self.font = font
        self.first_letter = self.letters_to_sprites(input_text, size, font)

        self.width_limit = 200 if settings.Modifiers.HIDDEN_LETTERS else settings.WIDTH - int(settings.BASEPOS[0])
    
    def reset(self):
        for sprite in self.letter_sprites:
            self.spritegroup.remove(sprite)
        self.letter_sprites.empty()
        self.first_letter = self.letters_to_sprites(self.initial_text, self.size, self.font)

    def single_letters(self, text):
        result = []
        for i in range(len(text)):
            if settings.Modifiers.SPACE_LOCK > 1:
                if str(text[i]) != " ":
                    result.append(str(text[i]))
            else:
                result.append(str(text[i]))
        return result
    
    def letters_to_sprites(self, text, size, font):
        letter_list = self.single_letters(text)

        x_pos = settings.BASEPOS[0]
        prev_width = 0
        for index, letter in enumerate(letter_list):
            if index == 0:
                x_pos = settings.BASEPOS[0] +  (settings.PLAYER_SIZE[0] / 2)
                y_pos = settings.BASEPOS[1] + settings.PLAYER_SIZE[1]
                position = (x_pos, y_pos)
                letter_sprite = Letter(position, size, letter, [self.spritegroup, self.letter_sprites], font)
                first_letter = letter_sprite.letter_txt
                x_pos = settings.BASEPOS[0] +  ((settings.PLAYER_SIZE[0] - letter_sprite.width) / 2)
                position = (x_pos, y_pos)
                letter_sprite.update(position)
            elif index == 1:
                x_pos = settings.BASEPOS[0] + settings.PLAYER_SIZE[0] 
                position = (x_pos, y_pos)
                letter_sprite = Letter(position, size, letter, [self.spritegroup, self.letter_sprites], font)
                prev_width = letter_sprite.width
            else:
                x_pos += prev_width
                position = (x_pos, y_pos)
                letter_sprite = Letter(position, size, letter, [self.spritegroup, self.letter_sprites], font)
                prev_width = letter_sprite.width
        return first_letter

    def letter_update(self):
        prev_width = 0
        if self.letter_sprites:
            for index, sprite in enumerate(self.letter_sprites):
                if index != 0:
                    aggregate_width += sprite.width
                
                if index == 0:
                    sprite.kill()
                    aggregate_width = 0
                elif index == 1:
                    x_pos = settings.BASEPOS[0] +  ((settings.PLAYER_SIZE[0] - sprite.width) / 2)
                    y_pos = settings.BASEPOS[1] + settings.PLAYER_SIZE[1]
                    pos = (x_pos, y_pos)
                    sprite.update(pos)
                    self.first_letter = sprite.letter_txt
                elif index == 2:
                    x_pos = settings.BASEPOS[0] + settings.PLAYER_SIZE[0] 
                    pos = (x_pos, y_pos)
                    sprite.update(pos)
                    prev_width = sprite.width
                else:
                    if aggregate_width > self.width_limit:
                        sprite.remove(self.spritegroup)
                    else:
                        sprite.add(self.spritegroup)
                        x_pos += prev_width
                        pos = (x_pos, y_pos)
                        sprite.update(pos)
                        prev_width = sprite.width