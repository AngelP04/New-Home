import pygame

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
            if self.valid:
                self.selected = True
                self.map.tile_select = self

    def update(self):
        self.selected = False
        if self.state == "arado":
            self.image = pygame.image.load('C:/Users/Familia Perez/Desktop/Angel/Programacion Angel/Pycharm/New Home/Images/tiles/TiledeVerano.png')

