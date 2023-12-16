from .Boton_Constructor import Button
from .Config import *
from .Menu_Constructor import menu
import pygame

class menu_estructuras(menu):
    def __init__(self, left, bottom, height, interaccion):
        menu.__init__(self, left=left, bottom=bottom, height=height, interaccion=interaccion, width=250, buttom_left=85)