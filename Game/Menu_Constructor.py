from .Config import *
from .Widget import Widget
from .Boton_Constructor import Button
import pygame

class menu(Widget):
    def __init__(self, left, bottom, interaccion, height=30, width=100, buttom_left=12):
        Widget.__init__(self, rect=pygame.rect.Rect(left, bottom, width, height), color=GREEN)
        self.lista = []
        Separacion = 10

        for accion in interaccion:
            height += 30
            self.buttom = Button(self, rect=pygame.rect.Rect(buttom_left, Separacion, 75, 15), color=PINK, element=accion, lista=interaccion)
            self.buttom.repaint()
            Separacion += 30
            self.lista.append(self.buttom)