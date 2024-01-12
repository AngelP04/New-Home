from .Config import *
from .Widget import Widget
from .Boton_Constructor import Button
import pygame

class menu(Widget):
    def __init__(self, left, bottom, interaccion, height=30, width=100, buttom_left=12, buttom_width=75, buttom_height=15, config="vertical"):
        Widget.__init__(self, rect=pygame.rect.Rect(left, bottom, width, height), color=GREEN)
        self.lista = []
        self.repaint()
        Separacion_vertical = 10
        separacion_horizontal = 10

        if config == "vertical":
            for accion in interaccion:
                height += 30
                self.buttom = Button(self, rect=pygame.rect.Rect(buttom_left, Separacion_vertical, buttom_width, buttom_height), color=PINK, element=accion, lista=interaccion)
                self.buttom.repaint()
                Separacion_vertical += 30
                self.lista.append(self.buttom)
        else:
            for accion in interaccion:
                height += 30
                if self.rect.width - separacion_horizontal < 35:
                    print(self.rect.width - separacion_horizontal)
                    separacion_horizontal = 10
                    Separacion_vertical += 40
                self.buttom = Button(self, rect=pygame.rect.Rect(separacion_horizontal, Separacion_vertical, buttom_width, buttom_height), color=PINK, element=accion, lista=interaccion)
                self.buttom.repaint()
                separacion_horizontal += 50
                self.lista.append(self.buttom)
