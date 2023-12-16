import random
from .Inventario import Item
import pygame
from .Config import *

class Recurso(pygame.sprite.Sprite):
    def __init__(self, left, bottom, aguante, nombre, item=None, item_second=None):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 30))
        self.image.fill(PINK)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.left = left
        self.rect.bottom = bottom
        self.pos_x = self.rect.centerx
        self.pos_y = self.rect.centery
        self.aguante = aguante
        self.nombre = nombre
        self.item = item
        self.playing = True
        self.is_moving = False
        self.item_second = item_second

    def mined(self):
        self.aguante -= 1
        if self.aguante == 0:
            self.kill()

    def drop(self, grupo):
        dir_x = random.randrange(-50, 50)
        dir_y = random.randrange(-50, 50)
        item_drop = Item_drop(self.item.image, self.pos_x + dir_x, self.pos_y + dir_y, self.item.nombre, self.item.id, is_acum=self.item.is_acum, tool=self.item.tool)
        grupo.add(item_drop)

    def drop_second(self, grupo):
        dir_x = random.randrange(-50, 50)
        dir_y = random.randrange(-50, 50)
        item_second_drop = Item_drop(self.item_second.image, self.pos_x + dir_x, self.pos_y + dir_y,
                                     self.item_second.nombre, self.item_second.id,
                                     is_acum=self.item_second.is_acum, tool=self.item_second.tool)
        grupo.add(item_second_drop)

    def stop(self):
        self.playing = False

    def update(self):
        if self.playing:
            self.rect.centerx = self.pos_x
            self.rect.centery = self.pos_y

class Item_drop(pygame.sprite.Sprite, Item):
    def __init__(self, img, left, bottom, nombre, id, is_acum=True, tool=None, strenght=0, type=None):
        pygame.sprite.Sprite.__init__(self)
        Item.__init__(self, nombre, id, type)
        self.image = img
        self.rect = self.image.get_rect()
        self.pos_x = left
        self.pos_y = bottom
        self.rect.left = self.pos_x
        self.rect.bottom = self.pos_y
        self.playing = True
        self.is_acum = is_acum
        self.tool = tool
        self.streght = strenght

    def update(self):
        self.rect.left = self.pos_x
        self.rect.bottom = self.pos_y

class Seed(pygame.sprite.Sprite):
    def __init__(self, left, bottom, parent, planted):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((15, 15))
        self.image.fill(PINK)
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.bottom = bottom
        self.pos_x = self.rect.left
        self.pos_y = self.rect.bottom
        self.parent = parent
        self.day_planted = planted
        self.days_grow = self.day_planted + 5
        self.playing = True
        self.day_no_regard = 0
        self.regard = False
        self.marchite = False

    def update_day(self, grupo):
        if not self.marchite:
            self.day_planted += 1
            if self.regard:
                self.day_no_regard = 0
                if self.day_planted >= self.days_grow:
                    planta = self.parent
                    planta.pos_x = self.pos_x
                    planta.pos_y = self.pos_y
                    self.kill()
                    grupo.add(planta)
                else:
                    self.regard = False
                    return
            else:
                self.day_no_regard += 1
                if self.day_no_regard > 1:
                    self.marchite = True
        else:
            self.kill()

    def stop(self):
        self.playing = False

    def update(self):
        if self.playing:
            self.rect.centerx = self.pos_x
            self.rect.centery = self.pos_y
