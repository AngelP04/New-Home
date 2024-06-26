import pygame
import uuid
from pytmx import load_pygame
from .Config import *
from .Tiles import Tile
from .Estructuras import Estructura, Silo
from .Recursos import Recurso
from .Items import Item_acum

class Cursor_mouse(pygame.sprite.Sprite): #Este es un mouse falso que toma en cuenta el offset del mapa
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 20))
        self.image.fill(DARK_GREEN_TWO)
        self.rect = self.image.get_rect()
        self.player = player
        self.rect.center = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
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

class Cursor(pygame.sprite.Sprite): #Esto solo es una imagen que sera eliminada
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 30))
        self.image.fill(PINK)

class Map(pygame.sprite.Group): #Este mapa es una camara en la cual se dibujan todos los tiles
    def __init__(self, player, tmx=HOME):
        pygame.sprite.Group.__init__(self)
        self.player = player
        self.tmx = load_pygame(tmx)
        self.offset = pygame.math.Vector2()
        self.estructuras = []
        self.estructuras_disp = []
        self.minerales = []
        self.in_cinematic = False
        self.tile_select = None
        self.moved = False
        self.screen = pygame.display.get_surface()
        self.half_width = self.screen.get_size()[0] // 2
        self.half_height = self.screen.get_size()[1] // 2
        self.camera_borders = {"left": 75, "right": 75, "top": 50, "bottom": 50}
        l = self.camera_borders["left"]
        t = self.camera_borders["top"]
        w = self.screen.get_size()[0] - (self.camera_borders["left"] + self.camera_borders["right"])
        h = self.screen.get_size()[1] - (self.camera_borders["top"] + self.camera_borders["bottom"])
        self.camera_rect = pygame.Rect(l, t, w, h)
        self.cursor = Cursor()
        self.mouse = Cursor_mouse(self.player)
        self.add(self.mouse)
        self.tiles = []
        self.load_tiles_and_objects()

    def load_tiles_and_objects(self):
        for layer in self.tmx.layers: #Bucle for para agregar todos los tiles al map
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    cultivable = self.tmx.get_tile_properties(x, y, layer.id - 1)["cultivable"]
                    pos = (x * 32, y * 32)
                    tile = Tile(pos=pos, surf=surf, groups=self, map=self, id_x=x, id_y=y, cultivable=cultivable)
                    self.add(tile)
                    self.tiles.append(tile)


        for obj in self.tmx.objects:  #Bucle for para agregar todos los objetos al map
            pos = obj.x, obj.y
            if obj.type in ('Estructuras'):
                if obj.visible:
                    surf = pygame.transform.scale(obj.image, (obj.width, obj.height))
                    estructura = Estructura(pos=pos, surf=surf, nombre=obj.name, id=obj.id)
                    self.estructuras.append(estructura)
                else:
                    surf = pygame.transform.scale(obj.image, (obj.width, obj.height))
                    estructura = Silo(pos=pos, surf=surf, id=obj.id)
                    self.estructuras_disp.append(estructura)
            elif obj.type in ('Minerales'):
                if obj.visible:
                    print(obj.name)
                    surf = pygame.transform.scale(obj.image, (obj.width, obj.height))
                    mineral = Recurso(surf, pos, nombre=obj.name, aguante=5)
                    self.minerales.append(mineral)



    def custom_draw(self):
        for tile in self.sprites():
            if isinstance(tile, Tile):
                offset_rect = tile.rect.move(self.offset.x, self.offset.y)
                self.screen.blit(tile.image, offset_rect)

    def valid_tiles(self):
        for tile in self.sprites():
            if isinstance(tile, Tile):
                tile.validate_colision(self.mouse)
                if tile.selected:
                    break

    def update(self):

        for obj in self.tmx.objects: #Bucle for para saber si se ha construido alguna estructura y agregarla al map
            if obj.type in ('Estructuras'):
                for estructura in self.estructuras_disp:
                    if estructura.id == obj.id:
                        if estructura.builded:
                            obj.visible = True
                            self.estructuras.append(estructura)
                            self.estructuras_disp.remove(estructura)

    def finish_cinematic(self):
        self.in_cinematic = False

class Inside(Map):
    def __init__(self, player, tmx=INTERIOR):
        self.puerta_interior = []
        Map.__init__(self, player, tmx)

    def load_tiles_and_objects(self):
        right_x_colid = 0
        up_y_colid = 0
        doors = self.tmx.get_layer_by_name('Doors')
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
                        self.tiles.append(self.tile)
                    else:
                        self.puerta = Door_interior(pos=pos, surf=surf, groups=self, map=self, id_x=x, id_y=y)
                        self.puerta_interior.append(self.puerta)

        for tile in self.tiles:
            if (tile.id_x == 0 or tile.id_y == 0) or (tile.id_x == right_x_colid or tile.id_y == up_y_colid):
                tile.colid = True

class Door_interior(Tile):
    def __init__(self, pos, surf, groups, map, id_x, id_y):
        Tile.__init__(self, pos=pos, surf=surf, groups=groups, map=map, id_x=id_x, id_y=id_y, collid=False)

    def door_colision_player(self, player):
        result = pygame.sprite.collide_mask(self, player)
        if result:
            if not player.colliding:
                return True