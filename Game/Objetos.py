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
    def __init__(self, nombre, load_bar=None):
        self.nombre = nombre
        self.id = uuid.uuid4()
        self.load_bar = load_bar
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.image.fill(PINK)
        self.rect = self.image.get_rect()

    def get_pos(self, pos):
        self.rect.center = pos

    def on_click(self):
        pass

    def update(self):
        pass

#OBJETOS ACUMULABLES
SEMILLA = Item_acum("semilla", 11)
MADERA_PROCESADA = Item_acum("Madera Procesada", 28)
MADERA = Item_acum("Madera", 1, process=MADERA_PROCESADA)
PIEDRA = Item_acum("Piedra", 2)

#HERRAMIENTAS
HACHA_PROCESADA = Tool("Hacha Procesada", 15)
AZADA = Tool("Azada", 8, materiales=[Craft_Item(PIEDRA, 5), Craft_Item(MADERA, 10)])
HACHA = Tool("Hacha", 5, process=HACHA_PROCESADA)
REGADERA = Regadera(5)

