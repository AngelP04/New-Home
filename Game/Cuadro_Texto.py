from .Config import *
import pygame

class Text_Rect(pygame.sprite.Sprite):
    def __init__(self, width=WIDTH, height=150, left=0, bottom=HEIGHT-150):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()
        self.rect.x = left
        self.rect.y = bottom
        self.text = ""
        self.font = pygame.font.match_font(FONT)

    def display_text(self, surface, text, size, color, pos_x, pos_y):
        font = pygame.font.Font(self.font, size)

        text = font.render(text, True, color)
        rect = text.get_rect()
        rect.midtop = (pos_x, pos_y)

        surface.blit(text, rect)

    def draw_text(self, frase, pos_x, pos_y=50):
        self.display_text(self.image, self.text_format(frase), 14, WHITE, pos_x, pos_y)

    def check_distance(self, pos_x):
        if self.rect.left - pos_x <= 100:
            return True

    def text_format(self, letra):
        self.text = letra
        return self.text

class TextRectInv(Text_Rect):
    def __init__(self, slot):
        Text_Rect.__init__(self, 400, 200, slot.x + 20, slot.y)
        self.text_nombre = ""
        self.display = False
        self.slot = slot
        self.width = 400
        self.height = 200

    def add_text(self, text):
        self.image.fill(GREEN_LIGHT)
        font = pygame.font.Font(self.font, 18)
        collection = [word.split(' ') for word in text.splitlines()]
        space = font.size(' ')[0]
        x = 20
        y = 20
        for line in collection:
            for word in line:
                word_surface = font.render(word, True, WHITE)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= 400:
                    x = 20
                    y += word_height
                if y > 200:
                    self.image = pygame.transform.scale(self.image, [self.width, self.height + word_height])
                    self.rect.x = self.slot.x + 20
                    self.rect.y = self.slot.y
                self.image.blit(word_surface, (x, y))
                x += word_width + space
            x = 20
            y += word_height


    def draw(self, screen):
        if self.display:
            screen.blit(self.image, self.rect)

    def show_info(self):
        self.display = not self.display

    def update(self):
        if self.slot.item != None:
            for palabra in self.slot.item.desc:
                if palabra != " ":
                    continue
            self.add_text(self.slot.item.desc)