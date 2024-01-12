import pygame
from pytmx import load_pygame
from .Config import *
from .Tiles import Tile
from .camaraY import Ycamara
from .Estructuras import Estructura, Silo

class Cursor_mouse(pygame.sprite.Sprite): #Este es un mouse falso que toma en cuenta el offset del mapa
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

class Cursor(pygame.sprite.Sprite): #Esto solo es una imagen que sera eliminada
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 30))
        self.image.fill(PINK)

class Map(Ycamara): #Este mapa es una camara en la cual se dibujan todos los tiles
    def __init__(self, player, cinematicas=None):
        Ycamara.__init__(self)
        self.player = player
        self.tmx = load_pygame(HOME)
        self.cursor = Cursor()
        self.estructuras = []
        self.estructuras_disp = []
        self.speed_x = 1
        self.speed_y = 1
        self.vel_x = 0
        self.vel_y = 0
        self.box = Box_camera()
        self.mouse = Cursor_mouse(self.player)
        self.add(self.mouse)
        self.cinematicas = cinematicas
        self.cinematica_now = cinematicas[0]
        self.camera_can_move = True
        self.temp_x = self.camera_rect.x
        self.pos_x = self.camera_rect.centerx
        self.pos_y = self.camera_rect.centery
        for layer in self.tmx.layers: #Bucle for para agregar todos los tiles al map
            if hasattr(layer, 'data'):
                for x, y, surf in layer.tiles():
                    cultivable = self.tmx.get_tile_properties(x, y, layer.id - 1)["cultivable"]
                    pos = (x * 32, y * 32)
                    self.tile = Tile(pos=pos, surf=surf, groups=self, map=self, id_x=x, id_y=y, cultivable=cultivable)
                    self.lista.append(self.tile)


        for obj in self.tmx.objects:  #Bucle for para agregar todos los objetos al map
            pos = obj.x, obj.y
            if obj.type in ('Estructuras'):
                if obj.visible:
                    surf = pygame.transform.scale(obj.image, (obj.width, obj.height))
                    self.estructura = Estructura(pos=pos, surf=surf, nombre=obj.name, id=obj.id)
                    self.add(self.estructura)
                    self.add(self.estructura.door)
                    self.estructuras.append(self.estructura)
                else:
                    surf = pygame.transform.scale(obj.image, (obj.width, obj.height))
                    self.estructura = Silo(pos=pos, surf=surf, id=obj.id)
                    self.estructuras_disp.append(self.estructura)

    def update_pos(self):
        if self.camera_can_move:
            self.pos_x += self.vel_x
            self.pos_y += self.vel_y

    def custom_draw(self):
        self.offset.x = self.half_width - self.player.rect.centerx
        self.offset.y = self.half_height - self.player.rect.centery
        self.vel_x = 0
        self.vel_y = 0
        self.temp_x = self.offset.x
        for cinematica in self.cinematicas:
            if cinematica.value:
                self.ajust_camera(cinematica)

        for tile in self.lista: #Los tiles se dibujan por separado de los demas sprites para que no se superpongan
            offset_rect = tile.rect.move(self.offset.x, self.offset.y)
            self.screen.blit(tile.image, offset_rect)
            if tile.selected:
                self.screen.blit(self.cursor.image, (tile.rect.centerx + self.offset.x - 15, tile.rect.centery + self.offset.y - 15))

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.top, reverse=True): #Dibujar los sprites de modo que se superpongan entre ellos si la posicion Y es menor
            if not isinstance(sprite, Tile) and not isinstance(sprite, Cursor_mouse):
                offset_rect = sprite.rect.move(self.offset.x, self.offset.y)
                self.screen.blit(sprite.image, offset_rect)

        self.screen.blit(self.mouse.image, (self.mouse.rect.move(self.offset.x, self.offset.y)))
        pygame.draw.rect(self.screen, YELLOW, self.camera_rect, 10)

    def ajust_camera(self, cinematica): #Funcion para mover la camara cuando se activa una cinematica, aun esta en proceso

        pos = ""
        midpoint_x = ((self.player.rect.x) + (cinematica.target.rect.x) + self.offset.x) // 2
        self.camera_can_move = False

        if cinematica.value and not cinematica.end_dialogue:
            self.player.can_move = False
            cinematica.target.can_move = False #Target es el objeto al que debe dirigirse la camara
            cinematica.begin = True

        if cinematica.begin:
            self.cinematica_now = cinematica
            if self.cinematica_now.target.pos_x > self.player.pos_x:
                pos = "derecha"
                if self.camera_rect.centerx <= midpoint_x and not self.cinematica_now.moved:
                    temp = 0
                    self.cinematica_now.moved = True
                    self.offset.x = self.camera_rect.left - self.camera_borders["left"]
                elif self.camera_rect.centerx > midpoint_x and not self.cinematica_now.moved:
                    temp = 4
                    self.camera_rect.left -= temp
                    self.offset.x = self.camera_rect.left - self.camera_borders["left"]
            elif self.cinematica_now.target.pos_x < self.player.pos_x:
                pos = "izquierda"
                self.camera_rect.x = self.player.pos_x + self.offset
                if self.camera_rect.centerx >= midpoint_x + 600 and not self.cinematica_now.moved:
                    temp = 0
                    self.cinematica_now.moved = True
                    self.offset.x = self.camera_rect.left - self.camera_borders["left"]
                elif self.camera_rect.centerx < midpoint_x + 600 and not self.cinematica_now.moved:
                    temp = 4
                    self.camera_rect.centerx += temp
                    self.offset.x = self.camera_rect.left - self.camera_borders["left"]


        if self.cinematica_now.end_dialogue:
            if pos == "derecha":
                temp = 4
                self.camera_rect.x += temp
                self.offset.x = self.camera_rect.left - self.camera_borders["left"]
                if not self.offset.x < self.temp_x:
                    self.offset.x = self.temp_x
                    self.player.can_move = True
                    self.cinematica_now.begin = False
                    self.cinematica_now.moved = False
                    self.cinematica_now.finish = True
                    self.camera_can_move = True

            elif pos == "izquierda":
                temp = 4
                self.camera_rect.x -= temp
                self.offset.x = self.camera_rect.left - self.camera_borders["left"]
                if not self.camera_rect.x > self.temp_x - 100:
                    self.offset.x = self.temp_x
                    self.player.can_move = True
                    self.cinematica_now.begin = False
                    self.cinematica_now.moved = False
                    self.cinematica_now.finish = True
                    self.camera_can_move = True

    def update(self):
        for sprite in self.sprites():
            sprite.update()

        for cinematica in self.cinematicas:
            cinematica.update()

        self.update_pos()
        if self.camera_can_move:
            self.camera_rect.centerx = self.pos_x
            self.camera_rect.centery = self.pos_y

        tile_collide = self.player.valid_tiles(self)

        for obj in self.tmx.objects: #Bucle for para saber si se ha construido alguna estructura y agregarla al map
            if obj.type in ('Estructuras'):
                for estructura in self.estructuras_disp:
                    if estructura.id == obj.id:
                        if estructura.builded:
                            obj.visible = True
                            self.add(estructura)
                            self.estructuras.append(estructura)

        for tile in self.lista:
            tile.validate_colision(self.mouse)
            if tile.selected:
                break
            if tile_collide != None: #Se crea el y actualiza el area en el cual es valido seleccionar ciertos tiles dependiendo del tile que esta tocando el jugador
                if (tile.id_x <= tile_collide.id_x + 2 and tile.id_x >= tile_collide.id_x - 2) and (
                        tile.id_y <= tile_collide.id_y + 2 and tile.id_y >= tile_collide.id_y - 2):
                    if not ((tile.id_x == tile_collide.id_x - 2 and tile.id_y == tile_collide.id_y - 2) or (
                            tile.id_x == tile_collide.id_x - 2 and tile.id_y == tile_collide.id_y + 2)
                            or (tile.id_x == tile_collide.id_x + 2 and tile.id_y == tile_collide.id_y - 2) or (
                                    tile.id_x == tile_collide.id_x + 2 and tile.id_y == tile_collide.id_y + 2)):
                        tile.valid = True

class Box_camera(Ycamara):
    def __init__(self):
        Ycamara.__init__(self)

    def box_target_camera(self, target):
        if target.rect.centerx < self.camera_rect.centerx:
            self.camera_rect.centerx = target.rect.centerx

        if target.rect.centerx > self.camera_rect.centerx:
            self.camera_rect.centerx = target.rect.centerx

        self.offset.x = self.camera_rect.left - self.camera_borders["left"]
        self.offset.y = self.camera_rect.top - self.camera_borders["top"]