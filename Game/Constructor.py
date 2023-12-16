from .npc import NPC
from .Config import *

class Construtor(NPC):
    def __init__(self, left, bottom):
        NPC.__init__(self, left, bottom, nombre="Roberto", guion=DIALOGOS_ROBERTO, interaccones=INTEREACTUAR_CONSTRUCTOR, dialogos_cinematicas=DIALOGOS_BIOLOGO_CINEMATICA)
        self.can_move = False

class Biologo(NPC):
    def __init__(self, left, bottom):
        NPC.__init__(self, left, bottom, nombre="Roberto", guion=DIALOGOS_ROBERTO, interaccones=INTERACTUAR_BIOLOGO, dialogos_cinematicas=DIALOGOS_BIOLOGO_CINEMATICA)
        self.following = False
        self.wait = False
        self.freedom = True
        self.inter_wait = ["Sigueme", "Regresa al pueblo"]
        self.inter_follow = ["Espera aqui", "Regresa al pueblo"]

    def follow(self, player):
        if self.following:
            self.freedom = False
            self.wait = False
            if player.vista == 1:
                self.pos_x = player.pos_x - 40
                self.pos_y = player.pos_y
            elif player.vista == - 1:
                self.pos_x = player.pos_x + 40
                self.pos_y = player.pos_y
            elif player.vista == 2:
                self.pos_y = player.pos_y - 40
                self.pos_x = player.pos_x
            else:
                self.pos_y = player.pos_y + 40
                self.pos_x = player.pos_x
            self.move(player.vista)

    def waiting(self):
        self.wait = True
        self.can_move = False
        self.following = False

    def free(self):
        self.following = False
        self.wait = False
        self.can_move = True
        self.freedom = True

    def swap_follow(self):
        self.following = not self.following