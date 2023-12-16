import random

import pygame
from pytmx import load_pygame
from .Config import *
from .camaraY import Ycamara
from .Cinematics import Cinematic
'''
Ycamara es una clase que hereda de pygame.sprite.Group que permite tener el efecto de que el 
jugador se mueve con su función draws
'''

class Cursor_mouse(pygame.sprite.Sprite):
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 20))
        self.image.fill(TEST)
        self.rect = self.image.get_rect()
        self.player = player
        self.rect.center = (pygame.mouse.get_pos()[0] - 650, pygame.mouse.get_pos()[1])
        self.pos_x = self.rect.centerx
        self.pos_y = self.rect.centery
        self.playing = True
        self.can_move = True
        self.initial = False

    def update_pos(self):
        if self.can_move and not self.player.colliding:
            self.pos_x += self.player.vel_x
            self.pos_y += self.player.vel_y

    def update(self):
        self.update_pos()
        if self.initial:
            self.rect.centerx = self.pos_x + pygame.mouse.get_pos()[0]
            self.rect.centery = self.pos_y + pygame.mouse.get_pos()[1]

class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32, 32))
        self.image.fill(PINK)

class Map(Ycamara):
    def __init__(self, player, clase, npc):
        Ycamara.__init__(self)
        self.player = player
        self.tmx = load_pygame('C:/Users/Familia Perez/Desktop/Angel/Tiled-Mapas/Home.tmx')
        self.cursor = Cursor()
        self.lista_valids = []
        self.estructuras = []
        self.areas = []
        self.cinematic = Cinematic(self.player, npc, self, 0)
        self.mouse = Cursor_mouse(self.player)
        self.add(self.mouse)
        self.temp_x = self.camera_rect.x
        for layer in self.tmx.layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    pos = (x * 32, y * 32)
                    self.tile = Tile(pos=pos, surf=surf, groups=self, map=self, id_x=x, id_y=y)
                    self.lista.append(self.tile)

        for obj in self.tmx.objects:
            pos = obj.x, obj.y
            if obj.type in ('Estructuras'):
                surf = pygame.transform.scale(obj.image, (obj.width, obj.height))
                self.estructura = clase(pos=pos, surf=surf, nombre=obj.name)
                self.add(self.estructura)
                self.estructuras.append(self.estructura)

    def custom_draw(self):
        self.offset.x = self.half_width - self.player.rect.centerx
        self.offset.y = self.half_height - self.player.rect.centery
        self.cinematic.ajust_camera()

        for tile in self.lista:
            offset_rect = tile.rect.move(self.offset.x, self.offset.y)
            self.screen.blit(tile.image, offset_rect)
            if tile.selected:
                    self.screen.blit(self.cursor.image, tile.rect.center + self.offset)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.top, reverse=True):
            if not isinstance(sprite, Tile) and not isinstance(sprite, Cursor_mouse):
                offset_rect = sprite.rect.move(self.offset.x, self.offset.y)
                self.screen.blit(sprite.image, offset_rect)

        self.screen.blit(self.mouse.image, (self.mouse.rect.move(self.offset.x, self.offset.y)))

    def update(self):
        for sprite in self.sprites():
            sprite.update()

        tile_collide = self.player.valid_tiles(self)

        for tile in self.lista:
            tile.validate_colision(self.mouse)
            if tile.selected:
                return
            if tile_collide != None:
                if (tile.id_x <= tile_collide.id_x + 2 and tile.id_x >= tile_collide.id_x - 2) and (
                        tile.id_y <= tile_collide.id_y + 2 and tile.id_y >= tile_collide.id_y - 2):
                    if not ((tile.id_x == tile_collide.id_x - 2 and tile.id_y == tile_collide.id_y - 2) or (
                            tile.id_x == tile_collide.id_x - 2 and tile.id_y == tile_collide.id_y + 2)
                            or (tile.id_x == tile_collide.id_x + 2 and tile.id_y == tile_collide.id_y - 2) or (
                                    tile.id_x == tile_collide.id_x + 2 and tile.id_y == tile_collide.id_y + 2)):
                        tile.valid = True

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, map, id_x, id_y, collid=False):
        pygame.sprite.Sprite.__init__(self, groups)
        self.id_x = id_x
        self.id_y = id_y
        self.dx = 0
        self.dy = 0
        self.pos = pos
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.selected = False
        self.valid = False
        self.colid = collid
        self.mask = pygame.mask.from_surface(self.image)
        self.map = map

    def validate_colision(self, cursor):
        result = pygame.sprite.collide_rect(self, cursor)
        if result:
            self.selected = True

    def update(self):
        self.selected = False

class Inside(Ycamara):
    def __init__(self, estructura):
        Ycamara.__init__(self)
        self.surface = pygame.display.get_surface()
        self.tmx = load_pygame('C:/Users/Familia Perez/Desktop/Angel/Tiled-Mapas/capsula_base.tmx')
        doors = self.tmx.get_layer_by_name('Doors')
        self.lista = []
        self.puerta_interior = []
        right_x_colid = 0
        up_y_colid = 0
        self.estructura = estructura

        for layer in self.tmx.layers:
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    if x > right_x_colid:
                        right_x_colid = x
                    if y > up_y_colid:
                        up_y_colid = y
                    pos = (300 + x * 32, 50 + y * 32)
                    if layer != doors:
                        self.tile = Tile(pos=pos, surf=surf, groups=self, map=self, id_x=x, id_y=y)
                        self.lista.append(self.tile)
                    else:
                        self.puerta = Door_interior(pos=pos, surf=surf, groups=self, map=self, id_x=x, id_y=y)
                        self.puerta_interior.append(self.puerta)

        for tile in self.lista:
            if (tile.id_x == 0 or tile.id_y == 0) or (tile.id_x == right_x_colid or tile.id_y == up_y_colid):
                tile.colid = True

class Door_interior(Tile):
    def __init__(self, pos, surf, groups, map, id_x, id_y):
        Tile.__init__(self, pos=pos, surf=surf, groups=groups, map=map, id_x=id_x, id_y=id_y, collid=False)

    def door_colision_player(self, player):
        result = pygame.sprite.collide_rect(self, player)
        if result:
            if not player.colliding:
                return True

