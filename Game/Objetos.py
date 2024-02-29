from .Items import *
import pygame
from .Config import *

class Regadera(Tool):
    def __init__(self, agua):
        Tool.__init__(self, "regadera", 6, 0)
        self.agua = agua

    def regar(self):
        if self.agua >= 1:
            self.agua -= 1

class Object(pygame.sprite.Sprite):
    def __init__(self, nombre, id, element=None):
        self.nombre = nombre
        self.id = id
        self.element = element
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.image.fill(PINK)
        self.rect = self.image.get_rect()

    def get_pos(self, pos):
        self.rect.center = pos

    def on_click(self):
        pass

class Horno(Object):
    def __init__(self):
        Object.__init__(self, nombre="Horno", id=20)

    def on_click(self):
        print(1)

#OBJETOS ACUMULABLES
SEMILLA = Item_acum("semilla", 2)
MADERA = Item_acum("Madera", 1)
PIEDRA = Item_acum("Piedra", 3)

#HERRAMIENTAS
AZADA = Tool("Azada", 8, 1, materiales=[Craft_Item(PIEDRA, 5), Craft_Item(MADERA, 10)],image=pygame.image.load('Images/Objetos/Pico.png'))
HACHA = Tool("Hacha", 5, 1, image=pygame.image.load('Images/Objetos/Azada.png'))
REGADERA = Regadera(5)

