import pygame
from .Tiles import Tile
from .map import Cursor_mouse

class Ycamara(pygame.sprite.Group):
    def __init__(self, player, map):
        pygame.sprite.Group.__init__(self)
        self.player = player
        self.screen = pygame.display.get_surface()
        self.half_width = self.screen.get_size()[0] // 2
        self.half_height = self.screen.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        self.lista = []
        self.map = map
        self.moved = False
        self.camera_borders = {"left": 75, "right": 75, "top": 50, "bottom": 50}
        l = self.camera_borders["left"]
        t = self.camera_borders["top"]
        w = self.screen.get_size()[0] - (self.camera_borders["left"] + self.camera_borders["right"])
        h = self.screen.get_size()[1] - (self.camera_borders["top"] + self.camera_borders["bottom"])
        self.camera_rect = pygame.Rect(l, t, w, h)
        self.cont = 0

    def draws_custom(self, *args):
        pass

    def draws(self):
        self.draws_custom()

        for tile in self.sprites():
            if isinstance(tile, Tile):
                offset_rect = tile.rect.move(self.offset.x, self.offset.y)
                self.screen.blit(tile.image, offset_rect)

        self.select_tiles()

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.top, reverse=True):  # Dibujar los sprites de modo que se superpongan entre ellos si la posicion Y es menor
            if not isinstance(sprite, Tile) and not isinstance(sprite, Cursor_mouse):
                offset_rect = sprite.rect.move(self.offset.x, self.offset.y)
                self.screen.blit(sprite.image, offset_rect)

        self.draw_cursor()

    def select_tiles(self):
        self.player.validate_tiles(self.map)
        for tile in self.sprites():
            if isinstance(tile, Tile):
                tile.validate_colision(self.map.mouse)
                if tile.selected:
                    self.screen.blit(self.map.cursor.image, (tile.rect.centerx + self.offset.x - 15, tile.rect.centery + self.offset.y - 15))
                    break


    def draw_cursor(self):
        self.screen.blit(self.map.mouse.image, self.map.mouse.rect.move(self.offset.x, self.offset.y))


    def update(self):
        self.map.update()
        self.map.mouse.update()
        for sprite in self.sprites():
            sprite.update()


'''
Esta es una clase camara que tenia como metodos tipos de camara pero termine usandolo solo como referencia y para obtener algunos valores en la clase map

    def keyboard_control(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: self.camera_rect.x -= 5
        if keys[pygame.K_d]: self.camera_rect.x += 5
        if keys[pygame.K_w]: self.camera_rect.y -= 5
        if keys[pygame.K_s]: self.camera_rect.y += 5

        self.offset.x = self.camera_rect.left - self.camera_borders["left"]
        self.offset.y = self.camera_rect.top - self.camera_borders["top"]

    def box_target_camera(self, target):
        if target.rect.left < self.camera_rect.left:
            self.camera_rect.left = target.rect.left

        if target.rect.right > self.camera_rect.right:
            self.camera_rect.right = target.rect.right

        self.offset.x = self.camera_rect.left - self.camera_borders["left"]
        self.offset.y = self.camera_rect.top - self.camera_borders["top"]

    def center_camera(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

    def draws(self, player):

        self.center_camera(player)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.top, reverse=True):
            offset_rect = sprite.rect.move(self.offset.x, self.offset.y)
            self.screen.blit(sprite.image, offset_rect)
            
'''

class Camera_Center(Ycamara):
    def __init__(self, player, map):
        Ycamara.__init__(self, player, map)


    def draws_custom(self):

        self.offset.x = self.half_width - self.player.rect.centerx
        self.offset.y = self.half_height - self.player.rect.centery

class Box_Camera(Ycamara):
    def __init__(self, player, map):
        Ycamara.__init__(self, player, map)
        self.move = True
        self.in_cinematic = False
        self.cinematica = None

    def draws_custom(self):
        if self.cinematica == None:
            return

        self.in_cinematic = True
        pos = ""
        midpoint_x = ((self.player.rect.x) + (self.cinematica.target.rect.x) // 2)
        midpoint_y = ((self.player.rect.y) + (self.cinematica.target.rect.y) // 2)
        self.temp = pygame.math.Vector2(self.player.rect.centerx + (self.half_width * 2), self.player.rect.centery + (self.half_height // 2))
        self.camera_rect.center = self.temp
        if self.cinematica.target.pos_x < self.player.pos_x and not self.moved:
            pos = "izquierda"
            self.cont += 4
            self.camera_rect.x += self.cont
        elif self.cinematica.target.pos_x > self.player.pos_x and not self.moved:
            pos = "derecha"
            self.cont -= 4
            self.camera_rect.x += self.cont

        if pos == "izquierda":
            if self.offset.x >= abs(midpoint_x) + self.half_width and not self.moved:
                self.moved = True
        elif pos == "derecha":
            if self.offset.x <= abs(midpoint_x) - self.half_width and not self.moved:
                self.moved = True

        if self.cinematica.end_dialogue:
            if self.cinematica.target.pos_x < self.player.pos_x:
                self.cont -= 4
            elif self.cinematica.target.pos_x > self.player.pos_x:
                self.cont += 4
            self.camera_rect.x += self.cont
        if self.cont == 0:
            self.finish_cinematic()
        self.offset.y = self.camera_rect.top - self.camera_borders["top"]
        self.offset.x = self.camera_rect.left - self.camera_borders["left"]
        
    def ajust_cinematic(self, cinematica):
        if cinematica.value:
            self.player.can_move = False
            cinematica.target.can_move = False  # Target es el objeto al que debe dirigirse la camara
            cinematica.begin = True
            self.cinematica = cinematica


    def finish_cinematic(self):
        self.in_cinematic = False

