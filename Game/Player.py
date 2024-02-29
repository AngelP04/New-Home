import pygame.image

from .Recursos import *
from .Inventario import *

class Player(pygame.sprite.Sprite):
    def __init__(self, left, bottom):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(JUGADOR_M)
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.walk_front = [pygame.image.load(f'Images/Jugador/Movimiento/Jugador_M_Frente_{i}.png') for i in range(1, 3)]
        self.walk_back = [pygame.image.load(f'Images/Jugador/Movimiento/Jugador_M_Espalda_{i}.png') for i in range(1, 3)]
        self.walk_right = [pygame.image.load(f'Images/Jugador/Movimiento/Jugador_M_Derecha_{i}.png') for i in range(1, 3)]
        self.walk_left = [pygame.image.load(f'Images/Jugador/Movimiento/Jugador_M_Izquierda_{i}.png') for i in range(1, 3)]
        self.rect = self.image.get_rect()
        self.rect.left = left
        self.rect.bottom = bottom
        self.frame = 1
        self.pos_x = self.rect.left
        self.pos_y = self.rect.bottom
        self.biologo = False
        self.coll = ""
        self.last_direction = ""
        self.animals_knows = []
        self.objetos_crafteables = []
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
        self.inventario.addItemInv(AZADA)
        self.inventario.addItemInv(HACHA)

        self.playing = True
        self.can_move = True
        self.moving = False
        self.colliding = False

    def put_item(self, tile, group): #Funcion para colocar items como decoraciones, cofres, entre otros que se vayan añadiendo
        if self.verify_select_slot().item.obj != None:
            obj = self.verify_select_slot().item.obj
            obj.get_pos(tile.pos)
            self.inventario.removeItemInv(self.verify_select_slot().item)
            self.groups()[0].add(obj)
            group.add(obj)

    def handle_event(self): #Funcion para manejar los eventos
        key = pygame.key.get_pressed()
        mods = pygame.key.get_mods()
        self.vel_x = 0
        self.vel_y = 0
        match self.last_direction:
            case 'left':
                self.image = self.walk_left[0]
            case 'right':
                self.image = self.walk_right[0]
            case 'up':
                self.image = pygame.image.load('Images/Jugador/Movimiento/Jugador_M_Espalda_Quieto.png')
            case 'down':
                self.image = pygame.image.load('Images/Jugador/Movimiento/Jugador_M_Frente_Quieto.png')

        if key[pygame.K_d]:
            self.frame += 0.1
            if self.frame >= len(self.walk_right):
                self.frame = 0
            self.image = self.walk_right[int(self.frame)]
            if mods & pygame.KMOD_CTRL:
                self.run('right')
            else:
                self.move('right')
            self.last_direction = 'right'
        if key[pygame.K_a]:
            self.frame += 0.1
            if self.frame >= len(self.walk_left):
                self.frame = 0
            self.image = self.walk_left[int(self.frame)]
            if mods & pygame.KMOD_CTRL:
                self.run('left')
            else:
                self.move('left')
            self.last_direction = 'left'
        if key[pygame.K_s]:
            self.frame += 0.1
            if self.frame >= len(self.walk_front):
                self.frame = 0
            self.image = self.walk_front[int(self.frame)]
            if mods & pygame.KMOD_CTRL:
                self.run('down')
            else:
                self.move('down')
            self.last_direction = 'down'
        if key[pygame.K_w]:
            self.frame += 0.1
            if self.frame >= len(self.walk_front):
                self.frame = 0
            self.image = self.walk_back[int(self.frame)]
            if mods & pygame.KMOD_CTRL:
                self.run('up')
            else:
                self.move('up')
            self.last_direction = 'up'

        self.image = pygame.transform.scale(self.image, (64, 64))

    def move(self, direction):
        if direction == 'left':
            self.vel_x -= self.speed_x
        if direction == 'right':
            self.vel_x += self.speed_x
        if direction == 'up':
            self.vel_y -= self.speed_y
        if direction == 'down':
            self.vel_y += self.speed_y

    def run(self, direction):
        if direction == 'right':
            self.vel_x += self.speed_running_x
        if direction == 'left':
            self.vel_x -= self.speed_running_x
        if direction == 'down':
            self.vel_y += self.speed_running_y
        if direction == 'up':
            self.vel_y -= self.speed_running_y

    def collide_with(self, sprites):
       objects = pygame.sprite.spritecollide(self, sprites, False)
       if objects:
           return objects[0]

    def validate_colision_estructura(self, estructura): #Funcion para detectar colisiones con estructuras, funciona distinto a validate_colision
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

    def validate_colision(self, recurso): #Funcion para verificar la colision con objetos como arboles o piedras
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

    def validate_door(self, door): #Funcion para detectar si el jugador entra por una puerta mientras no este colisionando con algo mas
        result = pygame.sprite.collide_rect(self, door)
        if result:
            if not self.colliding:
                return True

    def cultive(self, tile, grupo, day):
        '''
        Funcion similar a put_item, pero que necesita la variable del dia
        porque el proceso de la semilla depende de eso
        '''
        if self.verify_select_slot().item.nombre == "semilla":
            planta = Seed(tile.pos[0], tile.pos[1], self.material_mine, day)
            self.check_slot_inventory(SEMILLA).cant -= 1
            grupo.add(planta)

    def interct(self, grupo): #Funcion para saber la distancia de los npcs saber si se puede hablar con alguno
        for npc in grupo:
            self.dx = abs(self.rect.left - npc.rect.left)
            self.dy = abs(self.rect.bottom - npc.rect.bottom)
            if self.dx < 75 and self.dy < 75:
                return npc.nombre

    def valid_tiles(self, map):
        tile_collide = None

        for tile in map.tiles:
            tile.valid = False
            if tile_collide == None:
                if pygame.sprite.collide_mask(self, tile):
                    tile_collide = tile
                    return tile_collide

    def azar(self, tiles):
        for tile in tiles:
            if self.verify_select_slot().item.nombre == "azada":
                if tile.selected:
                    if tile.cultivable:
                        tile.state = "arado"

    def drop(self, item, grupo, cant):
        '''
        Funcion para desechar los items desde el inventario
        '''
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
        self.inventario.update_crafting()
        for slot in self.inventario.inventory_slots:
            if slot.item != None:
                if slot.item.is_acum:
                    if slot.cant == 0:
                        slot.item = None

    def check_cant(self, cantidades, slot):
        suficiente = False
        for cantidad in cantidades:
            if slot.cant >= cantidad:
                suficiente = True
            else:
                suficiente = False
                break
        return suficiente

    def check_animals(self, animal): #Funcion similar a interct pero con animales
        dx = abs(self.rect.left - animal.rect.left)
        dy = abs(self.rect.top - animal.rect.top)

        if animal.nombre in self.animals_knows:
            return

        if dx < 200 and dy < 200:
            return True

    def stop_move(self):
        if self.vel_x > 0:
            return True

    def update(self):
        self.update_inventory()
        if self.playing:
            self.colliding = False
            self.update_pos()
            self.rect.left = self.pos_x
            self.rect.bottom = self.pos_y
            self.update_toolbar()
            if self.vel_x != 0 or self.vel_y != 0:
                self.moving = True
            else:
                self.moving = False

            if self.coll == None:
                self.front = False

    def collide_items(self, items):
        '''
        Funcion para recoger items del suelo
        '''
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
            if self.dx < 75 and self.dy < 75:
                if self.verify_select_slot() != None:
                    if self.verify_select_slot().item.nombre == material.item.tool:
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
            elif self.verify_select_slot().item.nombre == "Hacha":
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
        if type(item) == dict:
            items = item["item"]
            for item in items:
                for slot in self.inventario.inventory_slots:
                    if slot.item != None:
                        if slot.item.id == item.id:
                            return slot
        else:
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



