import pygame
from pytmx import load_pygame
from .camaraY import Ycamara

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, map, id_x, id_y, collid=False, cultivable=False):
        pygame.sprite.Sprite.__init__(self, groups)
        self.id_x = id_x
        self.id_y = id_y
        self.dx = 0
        self.dy = 0
        self.cultivable = cultivable
        self.state = "normal"
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
        if self.state == "arado":
            self.image = pygame.image.load('C:/Users/Familia Perez/Desktop/Angel/Programacion Angel/Pycharm/New Home/Images/tiles/TiledeVerano.png')

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
        result = pygame.sprite.collide_mask(self, player)
        if result:
            if not player.colliding:
                return True

