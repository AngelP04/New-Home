from .Config import *
import pygame
import uuid

class Item:
    def __init__(self, nombre, type, id, desc=DESC, materiales=None, obj=None, process=None, progression=0.6, surf=None):
        self.progression = progression
        self.nombre = nombre
        if surf == None:
            self.image = pygame.Surface((30, 30))
            self.image.fill(YELLOW)
        else:
            self.image = surf
        self.is_moving = False
        self.process = process
        self.id = id
        self.id_propio = uuid.uuid4()
        self.type = type
        self.is_acum = False
        self.materiales = materiales
        self.desc = desc
        self.obj = obj
        self.rect = self.image.get_rect()

class Item_acum(Item):
    def __init__(self, nombre, id, max_acum=200, tool="Hacha", process=None, surf=None):
        super(Item_acum, self).__init__(nombre, id=id, type="material", process=process, surf=surf)
        self.max_acum = max_acum
        self.is_acum = True
        self.tool = tool

class Tool(Item):
    def __init__(self, nombre, id, stregth=0, materiales=None, process=None):
        super(Tool, self).__init__(nombre, type="tool", id=id, materiales=materiales, process=process)
        self.streght = stregth
        self.is_acum = False

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

class Craft_Item:
    def __init__(self, material, cantidad):
        self.nombre = material.nombre
        self.id = material.id
        self.id_propio = uuid.uuid4()
        self.cantidad = cantidad
        self.is_acum = True
