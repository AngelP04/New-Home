from .Recursos import *
import pygame
import math
from .Inventario import *

class Player(pygame.sprite.Sprite):
    def __init__(self, left, bottom):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.bottom = bottom
        self.pos_x = self.rect.left
        self.pos_y = self.rect.bottom
        self.biologo = False
        self.coll = ""
        self.animals_knows = []
        self.speed_x = SPEED
        self.speed_y = SPEED
        self.vel_x = 0
        self.vel_y = 0
        self.temp = self.speed_x
        self.speed_running_x = SPEED_RUNNING
        self.speed_running_y = SPEED_RUNNING
        self.vista = 1
        self.front = False
        self.mask = pygame.mask.from_surface(self.image)
        self.material_mine = None
        self.inventario = Inventario(self, 15, 5, 3)
        self.toolbar = Toolbar(self, 5, 5, 1)
        self.inventario.addItemInv(Tool("hacha", 5, 1))
        self.inventario.addItemInv(Regadera(5))
        self.inventario.addItemInv(Tool("azada", 8, 1))

        self.playing = True
        self.can_move = True
        self.moving = False
        self.colliding = False

    def move(self, value):
        if value == 1:
            self.vel_x += self.speed_x
        elif value == -1:
            self.vel_x -= self.speed_x
        elif value == 2:
            self.vel_y += self.speed_y
        else:
            self.vel_y -= self.speed_y
        self.vista = value

    def run(self, value):
        if value == 1:
            self.vel_x += self.speed_running_x
        elif value == -1:
            self.vel_x -= self.speed_running_x
        elif value == 2:
            self.vel_y += self.speed_running_y
        else:
            self.vel_y -= self.speed_running_y
        self.vista = value

    def collide_with(self, sprites):
       objects = pygame.sprite.spritecollide(self, sprites, False)
       if objects:
           return objects[0]

    def validate_colision_estructura(self, estructura):
        offset_x = estructura.rect.x - self.rect.x
        offset_y = estructura.rect.y - self.rect.y
        enter = False

        overlap = pygame.sprite.collide_mask(self, estructura)
        if overlap:
            self.colliding = True
            if (offset_y > estructura.min_offset_y and offset_y < estructura.max_offset_y):
                enter = True
                if (estructura.pos_x > self.pos_x and self.vel_x > 0):
                    self.pos_x = overlap[0] + self.rect.x - self.image.get_width() + 1.51
                elif (estructura.pos_x < self.pos_x and self.vel_x < 0):
                    self.rect.left = overlap[0] + self.rect.x
                if (self.pos_y > estructura.pos_y and self.vel_y < 0):
                    self.pos_y = estructura.rect.bottom + self.rect.height - 1.51
                elif (self.pos_y < estructura.pos_y and self.vel_y > 0):
                    self.pos_y = estructura.rect.centery + self.rect.height + 10
            elif offset_y > 0:
                enter = False
                if estructura.pos_x > self.pos_x and self.vel_x > 0:
                    self.vel_x *= 0
                elif estructura.pos_x < self.pos_x and self.vel_x < 0:
                    self.vel_x *= 0
            if (estructura.pos_y < self.pos_y and self.vel_y < 0) and not enter:
                self.vel_y *= 0

    def validate_colision(self, recurso):
        result = pygame.sprite.collide_mask(self, recurso)

        if result:
            if (recurso.pos_x > self.pos_x and self.vel_x > 0) or (recurso.pos_x < self.pos_x and self.vel_x < 0):
                self.front = True
                self.pos_x = result[0] + self.pos_x - self.image.get_width() + 1.5
                self.colliding = True
            '''
            if (recurso.pos_y > self.pos_y and self.vel_y > 0) or (recurso.pos_y < self.pos_y and self.vel_y < 0):
                self.speed_y = 0
            '''
        self.coll = result

    def validate_colision_tiles(self, tile):
        result = pygame.sprite.collide_rect(self, tile)
        if result:
            if tile.colid:
                self.colliding = True
                if tile.pos[0] > self.pos_x and self.vel_x > 1:
                    self.vel_x *= 0
                elif tile.pos[0] < self.pos_x and self.vel_x < 0:
                    self.vel_x *= 0
                elif self.pos_y > tile.pos[1] and self.vel_y < 0:
                    self.vel_y *= 0
                elif self.pos_y < tile.pos[1] and self.vel_y > 0:
                    self.vel_y *= 0

    def validate_door(self, door):
        result = pygame.sprite.collide_rect(self, door)
        if result:
            if not self.colliding:
                return True

    def cultive(self, grupo, colision, day):
        posible = True
        good = True
        for tipo in colision:
            for c in tipo:
                if (c.pos_x > self.pos_x and self.vista == 1) or (c.pos_x < self.pos_x and self.vista == -1) or (c.pos_y > self.pos_y and self.vista == 2) or (c.pos_y < self.pos_y and self.vista == -2):
                    dist = math.fabs(pygame.math.Vector2(self.pos_x, self.pos_y).distance_to((c.pos_x, c.pos_y)))
                    if dist > 50:
                        posible = True
                    else:
                        posible = False
                        break
            if posible:
                good = True
                continue
            else:
                good = False
                break

        if self.verify_select_slot().item.nombre == "semilla":
            if good:
                if self.vista == 1:
                    planta = Seed(self.pos_x + 50, self.pos_y, self.material_mine, day)
                elif self.vista == -1:
                    planta = Seed(self.pos_x - 50, self.pos_y, self.material_mine, day)
                elif self.vista == 2:
                    planta = Seed(self.pos_x, self.pos_y + 50, self.material_mine, day)
                else:
                    planta = Seed(self.pos_x, self.pos_y - 50, self.material_mine, day)
                self.check_slot_inventory(Item_acum("semilla", 2)).cant -= 1
                grupo.add(planta)

    def interct(self, grupo):
        for npc in grupo:
            self.dx = abs(self.rect.left - npc.rect.left)
            self.dy = abs(self.rect.bottom - npc.rect.bottom)
            if self.dx < 75 and self.dy < 75:
                return npc.nombre

    def valid_tiles(self, map):
        tile_collide = None

        for tile in map.lista:
            tile.valid = False
            if tile_collide == None:
                if self.rect.collidepoint(tile.rect.center):
                    tile_collide = tile
                    return tile_collide

    def azar(self, tiles):
        for tile in tiles:
            if self.verify_select_slot().item.nombre == "azada":
                if tile.selected:
                    if tile.cultivable:
                        tile.state = "arado"


    def drop(self, item, grupo, cant):
        if item.type == "tool":
            pos = random.randrange(-20, 20)
            if self.vista == 1:
                item_drop = Item_drop(item.image, self.pos_x + 50, self.pos_y + pos, item.nombre, item.id, item.is_acum, item.streght, type="tool")
            elif self.vista == -1:
                item_drop = Item_drop(item.image, self.pos_x - 50, self.pos_y + pos, item.nombre, item.id, item.is_acum, item.streght, type="tool")
            elif self.vista == 2:
                item_drop = Item_drop(item.image, self.pos_x + pos, self.pos_y + 50, item.nombre, item.id, item.is_acum, item.streght, type="tool")
            else:
                item_drop = Item_drop(item.image, self.pos_x + pos, self.pos_y - 50, item.nombre, item.id, item.is_acum, item.streght, type="tool")
            grupo.add(item_drop)
        else:
            for i in range(cant):
                pos = random.randrange(-20, 20)
                if self.vista == 1:
                    item_drop = Item_drop(item.image, self.pos_x + 50, self.pos_y + pos, item.nombre, item.id, item.is_acum, type="material", tool=item.tool)
                elif self.vista == -1:
                    item_drop = Item_drop(item.image, self.pos_x - 50, self.pos_y + pos, item.nombre, item.id, item.is_acum, type="material", tool=item.tool)
                elif self.vista == 2:
                    item_drop = Item_drop(item.image, self.pos_x + pos, self.pos_y + 50, item.nombre, item.id, item.is_acum, type="material", tool=item.tool)
                else:
                    item_drop = Item_drop(item.image, self.pos_x + pos, self.pos_y + 50, item.nombre, item.id, item.is_acum, type="material", tool=item.tool)

                grupo.add(item_drop)

    def update_inventory(self):
        for slot in self.inventario.inventory_slots:
            if slot.item != None:
                if slot.item.is_acum:
                    if slot.cant == 0:
                        slot.item = None

    def check_animals(self, animal): #Funcion del jugaodr
        dx = abs(self.rect.left - animal.rect.left)
        dy = abs(self.rect.top - animal.rect.top)

        if animal.nombre in self.animals_knows:
            return

        if dx < 100 and dy < 100:
            return True

    def stop_move(self):
        if self.vel_x > 0:
            return True

    def update(self):
        if self.playing:
            self.colliding = False
            self.update_pos()
            self.rect.left = self.pos_x
            self.rect.bottom = self.pos_y
            self.update_toolbar()
            self.update_inventory()
            if self.vel_x != 0 or self.vel_y != 0:
                self.moving = True
            else:
                self.moving = False

            if self.coll == None:
                self.front = False

    def collide_items(self, items):
        items = pygame.sprite.spritecollide(self, items, True)
        if items:
            for item in items:
                self.inventario.addItemInv(item)

    def regar(self, semillas):
        for semilla in semillas:
            self.dx = abs(self.pos_x - semilla.pos_x)
            self.dy = abs(self.pos_y - semilla.pos_y)
            if self.dx < 60 and self.dy < 60:
                if self.verify_select_slot().item != None:
                    if self.verify_select_slot().item.nombre == "regadera":
                        semilla.regard = True
                        break

    def mine(self, materials, grupo):
        prob = random.randrange(0, 4)
        for material in materials:
            self.dx = abs(self.pos_x - material.pos_x)
            self.dy = abs(self.pos_y - material.pos_y)
            if self.dx < 45 and self.dy < 45:
                if self.verify_select_slot() != None:
                    if self.verify_select_slot().item.nombre == material.item.tool:
                        if (material.pos_y > self.pos_y and self.vista == 2) or (material.pos_y < self.pos_y and self.vista == -2) or (material.pos_x > self.pos_x and self.vista == 1) or (material.pos_x < self.pos_x and self.vista == -1):
                            if self.verify_inventory(material.item):
                                self.inventario.addItemInv(material.item)
                            else:
                                material.drop(grupo)
                            if material.item_second != None:
                                if prob > 2:
                                    if self.verify_inventory(material.item_second):
                                        self.inventario.addItemInv(material.item_second)
                                    else:
                                        material.drop_second(grupo)
                            self.material_mine = material
                            material.mined()
                            break

    def use_tool(self, semillas, materiales, tiles, grupo=None):
        if self.verify_select_slot().item != None:
            if self.verify_select_slot().item.nombre == "regadera":
                self.regar(semillas)
            elif self.verify_select_slot().item.nombre == "hacha":
                self.mine(materiales, grupo)
            elif self.verify_select_slot().item.nombre == "azada":
                self.azar(tiles)

    def update_pos(self):
        if self.can_move:
            self.pos_x += self.vel_x
            self.pos_y += self.vel_y
        else:
            self.vel_x *= 0
            self.vel_y *= 0

    def stop(self):
        self.playing = False

    def select_slot(self, int=0):
        for slot in self.toolbar.bar_slots:
            slot.select = False
        self.toolbar.bar_slots[int].select = True

    def update_toolbar(self):
        for i in range(0, 5):
            self.toolbar.bar_slots[i].item = self.inventario.inventory_slots[i].item
            self.toolbar.bar_slots[i].cant = self.inventario.inventory_slots[i].cant

    def verify_select_slot(self):
        for slot in self.toolbar.bar_slots:
            if slot.select:
                if slot.item != None:
                    return slot

    def check_slot_inventory(self, item):
        for slot in self.inventario.inventory_slots:
            if slot.item != None:
                if slot.item.id == item.id:
                    return slot

    def verify_inventory(self, item):
        pos = False

        for slot in self.inventario.inventory_slots:
            if slot.item == None:
                pos = True
                break
            elif slot.item.id == item.id:
                if slot.item.is_acum:
                    pos = True
                    break
        return pos

class Raycast(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.image = pygame.Surface((100, 100))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(topleft=self.player.rect.topleft)
        pygame.draw.line(self.image, YELLOW, (self.image.get_width()//2, self.image.get_height()//2), (self.image.get_width()//2 + 50, self.image.get_height()//2), self.player.image.get_height())
        self.image.set_colorkey((0, 0, 0))
        self.collide = False

    def test_raycast(self, recurso):
        hit = pygame.sprite.collide_mask(self, recurso)
        if hit:
            self.collide = True

    def update(self):
        self.rect.center = self.player.rect.center
        self.collide = False

class Regadera(Tool):
    def __init__(self, agua):
        Tool.__init__(self, "regadera", 6, 0)
        self.agua = agua

    def regar(self):
        if self.agua >= 1:
            self.agua -= 1



