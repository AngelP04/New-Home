import pygame
from .Tiles import Inside
from .Config import *


class Builder(pygame.sprite.Sprite):
    def __init__(self, image, pos, parent=None):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        if (self.parent is not None):
            self.parent.children.add(self)

        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.pos_x = self.rect.left
        self.pos_y = self.rect.bottom
        self.playing = True

        self.children = pygame.sprite.OrderedUpdates()

    def stop(self):
        self.playing = False

    def update(self):
        if self.playing:
            self.children.update()

    def repaint(self):
        self.image.fill(self.color)
        self.children.draw(self.image)

        if (self.parent is not None):
            self.parent.repaint()

    def collide_player(self, event):
        pass

    def _collide_player(self, event):
        event.x -= self.rect.left
        event.y -= self.rect.top

        for sprite in self.children:
            if isinstance(sprite, Builder):
                if sprite.rect.collidepoint(event.x, event.y):
                    sprite.collide_player(event)
                    break
            else:
                self.collide_player(event)

class Estructura(Builder):
    def __init__(self, surf, pos, id, nombre="Silo", materiales=None, size="small", max_offset_y=-95, min_offset_y=-172, desc="Refugio para los habitantes"):
        Builder.__init__(self, surf, pos)
        self.id = id
        self.image = surf
        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.icon = pygame.transform.scale(self.image, (120, 140))
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.desc = desc
        self.pos_x = self.rect.left
        self.pos_y = self.rect.bottom
        self.min_offset_y = min_offset_y
        self.max_offset_y = max_offset_y
        self.width = self.mask.get_size()[0]
        self.height = self.mask.get_size()[1]
        self.builded = False
        self.size = size
        self.nombre = nombre
        self.materials = materiales
        self.enter = False
        self.door = Door((self.pos_x + 86, self.pos_y - 28), self)
        self.coll = False
        self.interior = None

    def load_inside(self):
        if self.interior == None:
            self.interior = Inside(self)

    def collide_player(self, event):
        if not self.enter:
            self.coll = True
            return self.coll

class Door(Builder):
    def __init__(self, pos, estructura):
        Builder.__init__(self, pygame.Surface((30, 60)), pos, estructura)
        self.image.fill((60, 100, 78))
        self.image.set_colorkey((0, 0, 0))

    def collide_player(self, event):
        return True


class Silo(Estructura):
    def __init__(self, surf, pos, id):
        Estructura.__init__(self, surf, pos, id, materiales={"Madera": 5}, desc="Almacena alimento")
        self.state = "vacio"

    def update(self):
        if self.state == "vacio":
            image = pygame.image.load(silo_vacio)
            self.image = pygame.transform.scale(image, (self.image_width, self.image_height))
        elif self.state == "lleno":
            image = pygame.image.load(silo_lleno)
            self.image = pygame.transform.scale(image, (self.image_width, self.image_height))
        else:
            image = pygame.image.load(silo_con_espacio)
            self.image = pygame.transform.scale(image, (self.image_width, self.image_height))




