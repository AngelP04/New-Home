import pygame
import random
import datetime
from .Config import *

class NPC(pygame.sprite.Sprite):
    def __init__(self, left, bottom, nombre=None, guion=DIALOGOS_NPC, interaccones=None, dialogos_cinematicas=None):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 30))
        self.image.fill(MAGENTA)
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.bottom = bottom
        self.pos_x = self.rect.left
        self.pos_y = self.rect.bottom
        self.mask = pygame.mask.from_surface(self.image)
        self.guion = guion
        self.guion_cinematica = dialogos_cinematicas
        self.nombre = nombre
        self.vel_x = 0
        self.vel_y = 0
        self.in_cinematic = False
        self.cant_in_cinematic = 0
        self.playing = False
        self.time_move = 10
        self.time_stop = 60
        self.moving = False
        self.can_move = True
        self.clock_stop = datetime.timedelta(seconds=40)
        self.cont_stop = self.clock_stop
        self.clock_move = datetime.timedelta(seconds=5)
        self.cont_move = self.clock_move
        self.cant_in = 0
        self.talking = False
        self.interacciones = interaccones

    def move(self, dire):
        self.vel_x = 0
        self.vel_y = 0
        if dire == 1:
            self.vel_x += 1.5
        elif dire == -1:
            self.vel_x -= 1.5
        elif dire == 2:
            self.vel_y += 1.5
        elif dire == -2:
            self.vel_y -= 1.5

    def collide_with(self, sprites):
       objects = pygame.sprite.spritecollide(self, sprites, False)
       if objects:
           return objects[0]

    def validate_colision(self, recurso):
        result = pygame.sprite.collide_rect(self, recurso)
        if result:
            if recurso.pos_x > self.pos_x + 4 and self.vel_x > 1:
                self.vel_x *= 0
            elif recurso.pos_x < self.pos_x - 4 and self.vel_x < 0:
                self.vel_x *= 0
            elif recurso.pos_y < self.pos_y - 4 and self.vel_y < 0:
                self.vel_y *= 0
            elif recurso.pos_y > self.pos_y + 4 and self.vel_y > 0:
                self.vel_y *= 0

    def update_pos(self):
        if self.can_move:
            if not self.moving:
                self.cont_stop -= datetime.timedelta(milliseconds=500)
                dire = random.randrange(-3, 3)
                if self.cont_stop <= datetime.timedelta(seconds=0) and not self.moving:
                    self.move(dire)
                    self.cont_stop = self.clock_stop
                    self.moving = True
            else:
                self.cont_move -= datetime.timedelta(milliseconds=200)
                if self.cont_move <= datetime.timedelta(seconds=0) and self.moving:
                    self.move(0)
                    self.cont_move = self.clock_move
                    self.moving = False

            self.pos_x += self.vel_x
            self.pos_y += self.vel_y

    def stop(self):
        self.playing = False

    def update(self):
        if self.playing:
            self.update_pos()
            self.rect.left = self.pos_x
            self.rect.bottom = self.pos_y
        else:
            self.vel_x *= 0
            self.vel_y *= 0

    def update_conv(self):
        self.frase = self.guion[self.cant_in]
        if self.guion_cinematica != None:
            self.frase_cinematic = self.guion_cinematica[self.cant_in_cinematic]