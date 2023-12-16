import pygame
from .Tiles import Inside


class Builder(pygame.sprite.Sprite):
    def __init__(self, parent=None, size="small", *, rect, color):
        pygame.sprite.Sprite.__init__(self)
        self.parent = parent
        self.size = size
        if (self.parent is not None):
            self.parent.children.add(self)

        self.image = pygame.surface.Surface(rect.size)
        self.rect = rect
        self.color = color
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

class Estructura(pygame.sprite.Sprite):
    def __init__(self, surf, pos, nombre="Silo", materiales=None, cantidadM=0, size="Large", max_offset_y=-95, min_offset_y=-172):
        pygame.sprite.Sprite.__init__(self)
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.pos_x = self.rect.left
        self.pos_y = self.rect.bottom
        self.min_offset_y = min_offset_y
        self.max_offset_y = max_offset_y
        self.width = self.mask.get_size()[0]
        self.height = self.mask.get_size()[1]
        self.size = size
        self.nombre = nombre
        self.materials = materiales
        self.cantidadM = cantidadM
        self.door = Door(60, 40, self)
        self.enter = False
        self.coll = False
        self.interior = None

    def load_inside(self):
        if self.interior == None:
            self.interior = Inside(self)

    def collide_player(self, event):
        if not self.enter:
            self.coll = True
            return self.coll

class Door:
    def __init__(self, left, bottom, estructura):
        self.parent = estructura

    def collide_player(self, event):
        self.parent.enter = not self.parent.enter




