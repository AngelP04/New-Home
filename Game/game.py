import os
import sys
import datetime

from .Player import Player
from .Recursos import *
from .npc import NPC, Biologo
from .Menu_Constructor import menu
from .Event import *
from .Cuadro_Texto import Text_Rect
from .menu_estructuras import menu_estructuras
from .Inventario import *
from .camaraY import Camera_Center, Box_Camera
from .map import Map, Inside
from .Cinematics import Cinematic, Cinematic_manager
from .Animales import Animal

npc_basico = {"left": 200, "bottom": 300, "nombre": "Fernan", "guion": DIALOGOS_NPC, "interactuar": INTERACTUAR_NPC, "dialogos_cinematicas": DIALOGOS_BIOLOGO_CINEMATICA}
npc_constructor = {"left": 750, "bottom": 100, "nombre":"Roberto", "guion": DIALOGOS_ROBERTO, "interactuar": INTEREACTUAR_CONSTRUCTOR, "dialogos_cinematicas": DIALOGO_ROBERTO_CINEMATIC}
lista_npcs = [NPC(**npc_basico), NPC(**npc_constructor)]

class game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))  # Crea la ventana
        pygame.display.set_caption(TITLE)  # Le da sombre de la ventana
        pygame.mouse.set_visible(True)

        self.running = True  # Permit saber si el program se esta cutaneous

        self.clock = pygame.time.Clock()

        self.listas_cinematicas = []

        self.font = pygame.font.match_font(FONT)

        self.dir = os.path.dirname(__file__)

        self.build_enter = None

        self.obj = None

        self.slot_select = 0

        self.day = 1
        self.day_time = datetime.timedelta(minutes=TIEMPO_DIA)
        self.drawing = True

    def start(self):
        self.new()

    def update_day(self):
        self.day_time -= datetime.timedelta(seconds=5)
        if self.day_time <= datetime.timedelta(seconds=0):
            self.day += 1
            for seed in self.seeds:
                seed.update_day(self.recursos)
            self.day_time = datetime.timedelta(minutes=TIEMPO_DIA)

    def add_sprites(self, camera, map):
        for sprite in map.sprites():
            if sprite != map.mouse and sprite not in camera:
                camera.add(sprite)

    def generate_elements(self):

        self.player = Player(100, 300)

        self.animal = Animal(-200, 100, "Señor de la montaña")

        self.animals = pygame.sprite.Group()

        self.animals.add(self.animal)

        self.npcs = pygame.sprite.Group()

        self.fernan = Biologo(200, 50)

        self.arbol = Recurso(200, 70, 10, "Arbol", item=MADERA, item_second=SEMILLA)

        self.roca = Recurso(200, 120, 5, "Roca", item=PIEDRA)

        self.sprites_inside = pygame.sprite.Group()

        self.Cursor = pygame.sprite.Group()

        self.recursos = pygame.sprite.Group()

        self.estructuras = pygame.sprite.Group()

        self.items = pygame.sprite.Group()

        self.seeds = pygame.sprite.Group()

        self.doors = pygame.sprite.Group()

        self.objects = pygame.sprite.Group()

        self.create_cinematic()

        self.map = Map(self.player)

        self.camera = Camera_Center(self.player, self.map)

        self.camera_cinematicas = Box_Camera(self.player, self.map)

        self.manager_cinematic = Cinematic_manager(self.listas_cinematicas, self.camera_cinematicas, self.map)
        self.add_sprites(self.camera, self.map)
        self.add_sprites(self.camera_cinematicas, self.map)

        for estructura in self.map.estructuras:
            self.camera.add(estructura)
            self.camera.add(estructura.door)
            self.doors.add(estructura.door)
            self.estructuras.add(estructura)
            estructura.load_inside(Inside, self.player)

        for npc in lista_npcs:
            self.npcs.add(npc)
            self.camera.add(npc)
            self.camera_cinematicas.add(npc)

        self.camera.add(self.player)
        self.camera.add(self.fernan)
        self.camera.add(self.animal)
        self.camera.add(self.arbol)
        self.camera.add(self.roca)
        self.recursos.add(self.arbol)
        self.recursos.add(self.roca)
        self.npcs.add(self.fernan)

        self.current_camera = self.camera
        self.cursor = self.current_camera.map.mouse

    def new(self):
        self.state = "Playing"
        self.cantidadM = 0
        self.cantidadComida = 0
        self.playing = True
        self.pause = False

        self.generate_elements()
        self.run()

    def run(self):  # Ejecta las functionless metas el program se execute
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def display_text(self, surface, text, size, color, pos_x, pos_y):
        font = pygame.font.Font(self.font, size)

        text = font.render(text, True, color)
        rect = text.get_rect()
        rect.midtop = (pos_x, pos_y)

        surface.blit(text, rect)

    def filter_animals(self):
        if isinstance(self.manager_cinematic.cinematic_now.target, Animal):
            return True

    def update(self):
        if not self.playing:
            return

        self.update_day()

        for animal in self.player.animals_knows:
            if animal not in self.fernan.animals:
                self.fernan.animals.append(animal)

        if self.current_camera.moved:
            self.state = "Cinematic"

        self.manager_cinematic.update()

        if self.manager_cinematic.in_cinematic:
            self.map.in_cinematic = True
            self.current_camera = self.manager_cinematic.camera

        self.fernan.follow(self.player)


        build = self.player.collide_with(self.estructuras)
        if build:
            for estructura in self.estructuras:
                event = Collision_event(self.player, estructura)
                estructura.collide_player(event)
                if pygame.sprite.collide_mask(self.player, estructura.door):
                    estructura.enter = True
                if estructura.collide_player(event):
                    self.player.validate_colision_estructura(estructura)

        for estructura in self.estructuras:
            if estructura.enter:
                self.build_enter = estructura
                if estructura.size == "small":
                    self.sprites_inside.add(self.player)
                    self.sprites_inside.add(self.cursor)
                self.state = "inside-build"
                break

        for seed in self.seeds:
            self.camera.add(seed)

        for slot in self.player.toolbar.bar_slots:
            slot.update(self.surface)

        for item in self.items:
            if item not in self.current_camera.sprites():
                self.current_camera.add(item)
            if self.player.verify_inventory(item):
                self.player.collide_items(self.items)

        for recurso in self.recursos:
            if recurso not in self.current_camera.sprites():
                self.current_camera.add(recurso)
            self.player.validate_colision(recurso)

        for npc in self.npcs:
            for estructura in self.estructuras:
                npc.validate_colision(estructura)
            for recurso in self.recursos:
                npc.validate_colision(recurso)

        if self.state == "Talking":
            self.text_rect()
        elif self.state == "Playing":
            self.current_camera.update()
        elif self.state == "menu_npc":
            self.create_menu_npc()
        elif self.state == "Cinematic":
            self.text_rect_cinematic()
            self.current_camera.update()
        elif self.state == "Building":
            self.menu_build()
        elif self.state == "Inventario":
            self.create_inventario()
        elif self.state == "Cofre":
            self.create_inventario_cofre()
        elif self.state == "inside-build":
            self.inside_build()
        elif self.state == "menu_fernan":
            self.create_menuBiologist()
        elif self.state == "Tienda":
            self.create_menu_tienda()
        elif self.state == "crafting":
            self.crafting()

    def draw(self):
        if self.drawing:
            self.surface.fill(BLACK)
            self.current_camera.draws()
            self.player.toolbar.draw(self.surface)
            for slot in self.player.toolbar.bar_slots:
                slot.update(self.surface)
            self.player.inventario.draw(self.surface)
            if self.obj != None:
                self.obj.inventario.draw(self.surface)
        else:
            self.surface.fill(BLACK)
            if self.build_enter.size == "small":
                self.build_enter.interior.draw(self.surface)
                self.sprites_inside.draw(self.surface)
            else:
                self.current_camera.draws()
            self.player.toolbar.draw(self.surface)
            for slot in self.player.toolbar.bar_slots:
                slot.update(self.surface)
            self.player.inventario.draw(self.surface)

        pygame.display.flip()

    def stop_draw(self):
        self.drawing = not self.drawing

    def inside_build(self):
        self.player.pos_x = 400
        self.player.pos_y = 200
        self.cursor.pos_x = self.player.pos_x
        self.cursor.pos_y = self.player.pos_y
        if self.build_enter.size == "small":
            self.sprites_inside.add(self.player)
            self.cursor.can_move = False
        else:
            self.camera_interiores = Camera_Center(self.player, self.build_enter.interior)
            self.camera_interiores.add(self.player)
            self.add_sprites(self.camera_interiores, self.build_enter.interior)
            self.current_camera = self.camera_interiores
        self.stop_draw()
        inside = True

        while inside:
            self.clock.tick(FPS)
            self.draw()
            self.current_camera.update()
            if self.build_enter.size == "small":
                self.cursor.pos_x = pygame.mouse.get_pos()[0]
                self.cursor.pos_y = pygame.mouse.get_pos()[1]
            self.events()

            for door in self.build_enter.interior.puerta_interior:
                salida = self.player.validate_door(door)
                if salida:
                    break

            if salida:
                self.player.valid_tiles(self.map)
                self.build_enter.enter = False
                if self.player in self.sprites_inside and self.cursor in self.sprites_inside:
                    self.sprites_inside.remove(self.player)
                    self.sprites_inside.remove(self.cursor)
                else:
                    self.camera_interiores.remove(self.player)
                    self.camera_interiores.remove(self.cursor)
                    self.current_camera = self.camera
                self.cursor.can_move = True
                self.player.pos_x = self.build_enter.pos_x + 60
                self.player.pos_y = self.build_enter.pos_y + 60
                self.cursor.pos_x = self.player.pos_x
                self.cursor.pos_y = self.player.pos_y
                self.build_enter = None
                inside = False
                self.state = "Playing"
                self.stop_draw()

            pygame.display.flip()

    def create_menu_tienda(self):
        self.cuadro_animales = Text_Rect(width=300, height=200, left=400, bottom=20)
        self.menu_animals = menu(left=100, bottom=20, width=205, height=200, interaccion=self.fernan.animals, buttom_left=43, buttom_width=35, buttom_height=35, config="horizontal")
        self.buttom_salir = Button_parent(rect=pygame.rect.Rect(110, 200, 70, 40), color=PINK, element="Salir")
        self.buttom_buy = Button_parent(rect=pygame.rect.Rect(225, 200, 70, 40), color=BLUE_Light, element="Comprar")
        self.buttom_salir.repaint()
        self.buttom_buy.repaint()

        self.stop_characters()

        distancia_letras_x = 60
        temp = None
        found = False
        tiempo_letras = datetime.timedelta(seconds=Tiempo_dialogos)
        cont_letras = tiempo_letras
        cont = 0
        texto = ""

        Distancia = 10

        self.surface.blit(self.menu_animals.image, self.menu_animals.rect)
        self.surface.blit(self.cuadro_animales.image, self.cuadro_animales.rect)
        self.surface.blit(self.buttom_salir.image, self.buttom_salir.rect)
        self.surface.blit(self.buttom_buy.image, self.buttom_buy.rect)

        buiying = True

        while buiying:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    buiying = False
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.menu_animals._on_click(Event(event))
                    if self.menu_animals.element != None and self.menu_animals.element != temp:
                        distancia_letras_x = 60
                        cont = 0

                    if self.buttom_salir.rect.collidepoint(pygame.mouse.get_pos()):
                        self.player.vel_x = 0
                        self.player.vel_y = 0
                        self.back_game()
                        self.stop_characters()
                        self.state = "Playing"
                        buiying = False

                    elif self.buttom_buy.rect.collidepoint(pygame.mouse.get_pos()):
                        pass

            pygame.display.flip()

    def create_menu_npc(self):
        alto = 30
        for npc in self.npcs:
            if npc.talking:
                for interaccion in npc.interacciones:
                    alto += 22
                self.menu_npc = menu(npc.pos_x + self.current_camera.offset.x + 15, npc.pos_y + self.current_camera.offset.y - 90, npc.interacciones, height=alto)
                break
            else:
                continue

        group = pygame.sprite.GroupSingle(self.menu_npc)
        self.stop_characters()
        Distancia = 10
        for button in self.menu_npc.lista:
            self.display_text(self.menu_npc.image, button.element, 10, WHITE, 50, Distancia)
            Distancia += 30

        self.surface.blit(self.menu_npc.image, self.menu_npc.rect)

        pause = True

        while pause:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pause = False
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.menu_npc._on_click(Event(event))
                    if self.menu_npc.element == "Hablar":
                        pause = False
                        self.back_game()
                        self.stop_characters()
                        self.state = "Talking"

                    elif self.menu_npc.element == "Construir":
                        pause = False
                        self.back_game()
                        self.stop_characters()
                        self.state = "Building"

                    elif self.menu_npc.element == "Seguir":
                        pause = False
                        self.back_game()
                        self.stop_characters()
                        self.fernan.swap_follow()
                        self.state = "Playing"
                    elif self.menu_npc.element == "Tienda":
                        pause = False
                        self.back_game()
                        self.stop_characters()
                        self.state = "Tienda"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for npc in self.npcs:
                            npc.talking = False
                        pause = False
                        self.back_game()
                        self.stop_characters()
                        self.state = "Playing"

            pygame.display.flip()

    def crafting(self):
        Distancia = 8
        self.cuadro_objetos = Text_Rect(width=300, height=200, left=400, bottom=20)
        interaccion = self.player.inventario.objetos
        menu_craft = menu(left=100, bottom=20, width=200, height=200, interaccion=interaccion, config="vertical", buttom_left=65, selections=self.player.objetos_crafteables)
        for button in menu_craft.lista:
            self.display_text(menu_craft.image, button.element.nombre, 15, WHITE, 103, Distancia)
            Distancia += 30
        self.buttom_salir = Button_parent(rect=pygame.rect.Rect(90, 200, 70, 40), color=PINK, element="Salir")
        self.buttom_build = Button_parent(rect=pygame.rect.Rect(250, 200, 70, 40), color=BLUE_Light, element="Craft")
        self.buttom_salir.repaint()
        self.buttom_build.repaint()

        self.stop_characters()

        self.surface.blit(menu_craft.image, menu_craft.rect)
        self.surface.blit(self.cuadro_objetos.image, self.cuadro_objetos.rect)
        self.surface.blit(self.buttom_salir.image, self.buttom_salir.rect)
        self.surface.blit(self.buttom_build.image, self.buttom_build.rect)

        crafting = True

        while crafting:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    crafting = False
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    menu_craft._on_click(Event(event))
                    Distancia = 10
                    for obj in self.player.inventario.objetos:
                        if menu_craft.element != None:
                            if menu_craft.element.nombre == obj.nombre:
                                self.cuadro_objetos.image.fill(GREEN)
                                for material in obj.materiales:
                                    if self.player.inventario.check_items(material):
                                        color = WHITE
                                    else:
                                        color = RED
                                    self.display_text(self.cuadro_objetos.image, material.nombre + " " + str(material.cantidad) + "x", 18, color, 100, Distancia)
                                    Distancia += 30
                                self.surface.blit(self.cuadro_objetos.image, self.cuadro_objetos.rect)

                    if self.buttom_salir.rect.collidepoint(pygame.mouse.get_pos()):
                        menu_craft.element = None
                        self.back_game()
                        self.state = "Playing"
                        crafting = False

                    elif self.buttom_build.rect.collidepoint(pygame.mouse.get_pos()):
                        if menu_craft.element != None:
                            for obj in self.player.inventario.objetos:
                                if menu_craft.element.nombre == obj.nombre:
                                    if obj in self.player.objetos_crafteables:
                                        for item in obj.materiales:
                                            self.player.inventario.removeItemInv(item, item.cantidad)
                                        self.player.inventario.addItemInv(obj)
                                        self.back_game()
                                        menu_craft.element = None
                                        self.state = "Playing"
                                        crafting = False
                                        break

            pygame.display.flip()

    def create_menuBiologist(self):
        alto = 30

        if self.fernan.following:
            for interaccion in self.fernan.inter_follow:
                alto += 22
            self.menu_biologo = menu(self.fernan.pos_x + self.current_camera.offset.x, self.fernan.pos_y + self.current_camera.offset.y, self.fernan.inter_follow, height=alto)
        elif self.fernan.wait:
            for interaccion in self.fernan.inter_wait:
                alto += 22
            self.menu_biologo = menu(self.fernan.pos_x + self.current_camera.offset.x, self.fernan.pos_y + self.current_camera.offset.y, self.fernan.inter_wait, height=alto)

        group = pygame.sprite.GroupSingle(self.menu_biologo)

        self.stop_characters()
        Distancia = 10
        for button in self.menu_biologo.lista:
            self.display_text(self.menu_biologo.image, button.element, 10, WHITE, 50, Distancia)
            Distancia += 30

        self.surface.blit(self.menu_biologo.image, self.menu_biologo.rect)

        pause = True

        while pause:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pause = False
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.menu_biologo._on_click(Event(event))
                    if self.menu_biologo.element == "Espera aqui":
                        pause = False
                        self.back_game()
                        self.stop_characters()
                        self.fernan.waiting()
                        self.state = "Playing"
                    elif self.menu_biologo.element == "Sigueme":
                        pause = False
                        self.back_game()
                        self.stop_characters()
                        self.fernan.swap_follow()
                        self.fernan.follow(self.player)
                        self.state = "Playing"
                    elif self.menu_biologo.element == "Regresa al pueblo":
                        pause = False
                        self.back_game()
                        self.stop_characters()
                        self.fernan.free()
                        self.state = "Playing"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pause = False
                        self.back_game()
                        self.stop_characters()
                        self.state = "Playing"

            pygame.display.flip()

    def create_inventario(self):  #Función para mostrar el inventario en el juego
        self.stop_characters()
        self.player.inventario.display_inventory()
        inventary = True

        while inventary:
            self.clock.tick(FPS)
            self.draw()
            self.player.update_toolbar()
            mouse = pygame.mouse.get_pos()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    inventary = False
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.map.update()
                        self.player.inventario.display_inventory()
                        self.back_game()
                        self.stop_characters()
                        self.state = "Playing"
                        inventary = False

                if event.type == pygame.MOUSEMOTION:
                    self.player.inventario.show_info(self.surface)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.player.inventario.moving:
                    self.player.inventario.moveItem(self.surface)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.player.inventario.moving:
                    self.player.inventario.placeItem(self.surface, self.items)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.player.inventario.buttom_craft.rect.collidepoint(mouse):
                        self.player.inventario.display_inventory()
                        self.state = "crafting"
                        inventary = False

    def create_inventario_cofre(self):
        self.stop_characters()
        self.obj.inventario.display_inventory()
        inventary = True

        while inventary:
            self.clock.tick(FPS)
            self.draw()
            self.player.update_toolbar()
            mouse = pygame.mouse.get_pos()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    inventary = False
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        self.map.update()
                        self.obj.inventario.display_inventory()
                        self.back_game()
                        self.stop_characters()
                        self.state = "Playing"
                        inventary = False

    def back_game(self):
        self.playing = True
        for sprite in self.current_camera.sprites():
            sprite.playing = True

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            mouse = self.cursor.rect.center

            self.player.handle_event()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    for npc in self.npcs:
                        if npc.rect.collidepoint(mouse):
                            if npc != self.fernan or self.fernan.freedom:
                                npc.talking = True
                                self.state = "menu_npc"
                            elif npc == self.fernan and not self.fernan.freedom:
                                self.state = "menu_fernan"
                            break
                    for object in self.objects:
                        if object.rect.collidepoint(mouse):
                            self.obj = object
                            self.state = object.on_click()
                elif pygame.mouse.get_pressed()[2]:
                    self.player.put_item(self.map.tile_select, self.objects)

            if event.type == pygame.MOUSEMOTION:
                if not self.cursor.initial:
                    self.cursor.initial = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.use_tool(self.seeds, self.recursos, self.map.sprites(), self.items)
                if event.key == pygame.K_e:
                    self.map.update()
                    self.state = "Inventario"
                if event.key == pygame.K_1:
                    self.player.select_slot(0)
                    self.slot_select = 0
                elif event.key == pygame.K_2:
                    self.player.select_slot(1)
                    self.slot_select = 1
                elif event.key == pygame.K_3:
                    self.player.select_slot(2)
                    self.slot_select = 2
                elif event.key == pygame.K_4:
                    self.player.select_slot(3)
                    self.slot_select = 3
                elif event.key == pygame.K_5:
                    self.player.select_slot(4)
                    self.slot_select = 4

                if event.key == pygame.K_RIGHT and self.slot_select < 4:
                    self.slot_select += 1
                    self.player.select_slot(self.slot_select)
                elif event.key == pygame.K_LEFT and self.slot_select > 0:
                    self.slot_select -= 1
                    self.player.select_slot(self.slot_select)

    def menu_build(self):
        self.cuadro_estructuras = Text_Rect(width=300, height=200, left=400, bottom=20)
        self.cuadro_texto = Text_Rect(width=300, height=100,left=400, bottom=200)
        self.menu_estructuras = menu_estructuras(left=100, bottom=20, height=200, interaccion=self.map.estructuras_disp)
        self.buttom_salir = Button_parent(rect=pygame.rect.Rect(90, 200, 70, 40), color=PINK, element="Salir")
        self.buttom_build = Button_parent(rect=pygame.rect.Rect(250, 200, 70, 40), color=BLUE_Light, element="Build")
        self.buttom_salir.repaint()
        self.buttom_build.repaint()

        self.stop_characters()

        distancia_letras_x = 50
        distancia_letras_y = 50
        temp = None
        found = False
        tiempo_letras = datetime.timedelta(seconds=Tiempo_dialogos)
        cont_letras = tiempo_letras
        cont = 0
        texto = ""

        Distancia = 10

        for button in self.menu_estructuras.lista:
            self.display_text(self.menu_estructuras.image, button.element.nombre, 10, WHITE, 123, Distancia)
            Distancia += 30


        self.display_text(self.cuadro_texto.image, "Quieres construir algo?", 18, WHITE, 150, 10)
        self.surface.blit(self.menu_estructuras.image, self.menu_estructuras.rect)
        self.surface.blit(self.cuadro_estructuras.image, self.cuadro_estructuras.rect)
        self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)
        self.surface.blit(self.buttom_salir.image, self.buttom_salir.rect)
        self.surface.blit(self.buttom_build.image, self.buttom_build.rect)

        building = True

        while building:
            self.clock.tick(FPS)


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    building = False
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    Distancia = 10
                    self.menu_estructuras._on_click(Event(event))
                    if self.menu_estructuras.element != None:
                        self.cuadro_texto.image.fill(GREEN)
                        distancia_letras_x = 50
                        cont = 0
                    for estructura in self.map.estructuras_disp:
                        if self.menu_estructuras.element != None:
                            if self.menu_estructuras.element.nombre == estructura.nombre:
                                self.cuadro_estructuras.image.fill(GREEN)
                                texto = estructura.desc
                                temp = self.menu_estructuras.element
                                for material in estructura.materials:
                                    if self.player.inventario.check_items(material):
                                        color = WHITE
                                    else:
                                        color = RED
                                    self.display_text(self.cuadro_estructuras.image,material.nombre + " " + str(material.cantidad) + "x", 18, color, 150, Distancia)
                                    Distancia += 20
                                self.surface.blit(self.cuadro_estructuras.image, self.cuadro_estructuras.rect)
                                self.surface.blit(estructura.icon, (self.cuadro_estructuras.rect.x + 30, self.cuadro_estructuras.rect.y + 20))

                    if self.buttom_salir.rect.collidepoint(pygame.mouse.get_pos()):
                        self.player.vel_x = 0
                        self.player.vel_y = 0
                        self.back_game()
                        self.stop_characters()
                        self.state = "Playing"
                        building = False

                    elif self.buttom_build.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.menu_estructuras.element != None:
                            for est in self.map.estructuras_disp:
                                if self.menu_estructuras.element.nombre == est.nombre:
                                    for material in est.materials:
                                        if self.player.inventario.check_items(material):
                                            found = True
                                        else:
                                            found = False
                        if not found:
                            self.cuadro_texto.image.fill(GREEN)
                            cont = 0
                            distancia_letras_x = 50
                            texto = "No tienes suficientes materiales"
                        else:
                            for est in self.map.estructuras_disp:
                                if self.menu_estructuras.element.nombre == est.nombre:
                                    for material in est.materials:
                                            self.player.inventario.removeItemInv(material, material.cantidad)
                                    est.builded = True
                            self.back_game()
                            self.stop_characters()
                            self.current_camera.add(est)
                            self.map.estructuras.append(est)
                            self.map.estructuras_disp.remove(est)
                            self.state = "Playing"
                            building = False
                            break

            if self.menu_estructuras.element == temp:
                if cont < len(texto):
                    cont_letras -= datetime.timedelta(milliseconds=500)
                    if cont_letras <= datetime.timedelta(seconds=0):
                        if self.cuadro_texto.check_distance(distancia_letras_x):
                            distancia_letras_x = 50
                            distancia_letras_y += 10
                        self.cuadro_texto.draw_text(texto[cont], distancia_letras_x, distancia_letras_y)
                        distancia_letras_x += 10
                        self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)
                        pygame.display.flip()
                        cont += 1
                        cont_letras = tiempo_letras
                else:
                    texto = ""
                    cont = 0
                    distancia_letras_x = 50

            pygame.display.flip()

    def stop_characters(self):
        for npc in self.npcs:
            npc.can_move = not npc.can_move

        self.player.can_move = not self.player.can_move

    def stop(self):
        self.playing = False
        for sprite in self.current_camera.sprites():
            sprite.playing = not sprite.playing

    def update_conversation(self, frase):
        texto = ""
        for letra in frase:
            texto += letra
        return texto

    def text_rect_cinematic(self):
        talking = False
        npc_talking = None
        self.cuadro_texto = Text_Rect()
        Distancia = 60
        cont_npcs = 0
        tiempo_letras = datetime.timedelta(seconds=Tiempo_dialogos)
        cont_letras = tiempo_letras
        for npc in self.npcs:
            if npc.talking and npc.in_cinematic:
                npc_talking = npc
                npc_talking.update_conv()

        if npc_talking != None:
            texto = self.update_conversation(npc_talking.frase_cinematic)
            cont = 0
            self.cuadro_texto.draw_text(npc_talking.nombre, pos_x=40, pos_y=30)
            self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)
            talking = True
        while talking:
            self.clock.tick(FPS)
            npc_talking.update_conv()
            if texto != "XN":
                if cont < len(texto):
                    cont_letras -= datetime.timedelta(milliseconds=500)
                    if cont_letras <= datetime.timedelta(seconds=0):
                        self.cuadro_texto.draw_text(texto[cont], Distancia)
                        Distancia += 12
                        self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)
                        pygame.display.flip()
                        cont += 1
                        cont_letras = tiempo_letras
                else:
                    texto = ""
                    cont = 0
            else:
                texto = ""
                cont = 0
                cont_npcs += 1
                if cont_npcs < len(self.manager_cinematic.cinematic_now.npcs):
                    npc_talking.cant_in_cinematic += 1
                    npc_talking = self.manager_cinematic.cinematic_now.npcs[cont_npcs]
                    self.cuadro_texto.image.fill(GREEN)
                    self.cuadro_texto.draw_text(npc_talking.nombre, pos_x=40, pos_y=30)
                    npc_talking.talking = True
                    npc_talking.in_cinematic = True
                    npc_talking.update_conv()
                    texto = self.update_conversation(npc_talking.frase_cinematic)
                    continue
                else:
                    npc_talking.talking = False
                    npc_talking.in_cinematic = False
                    self.manager_cinematic.cinematic_now.end_dialogue = True
                    self.wait_cinematic()
                    self.manager_cinematic.finish_cinematic()
                    if self.filter_animals():
                        self.player.animals_knows.append(self.manager_cinematic.cinematic_now.target.nombre)
                    self.playing = True
                    self.state = "Playing"
                    talking = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    talking = False
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        if cont >= len(texto):
                            Distancia = 60
                            self.cuadro_texto.image.fill(GREEN)
                            self.cuadro_texto.draw_text(npc_talking.nombre, pos_x=40, pos_y=30)
                            npc_talking.cant_in_cinematic += 1
                            npc_talking.update_conv()
                            texto = self.update_conversation(npc_talking.frase_cinematic)
                            self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)

            pygame.display.flip()

    def text_rect(self): #Funcion para crear un cuadro de texto cuando un npc esta hablando fuera de una cinematica
        talking = False
        npc_talking = None
        self.cuadro_texto = Text_Rect()
        Distancia = 60
        tiempo_letras = datetime.timedelta(seconds=Tiempo_dialogos)
        cont_letras = tiempo_letras#Es el tiempo en el que tardan las letras en aparecer
        for npc in self.npcs:
            if npc.talking:
                npc_talking = npc
                npc_talking.update_conv()

        if npc_talking != None:
            texto = self.update_conversation(npc_talking.frase)
            cont = 0
            self.cuadro_texto.draw_text(npc_talking.nombre, pos_x=40, pos_y=30)
            self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)
            talking = True
        while talking:
            self.clock.tick(FPS)
            npc_talking.update_conv()
            if texto != "XN": #XN es solo un string que uso para indicar que el npc no va a hablar mas
                if cont < len(texto):
                    cont_letras -= datetime.timedelta(milliseconds=500)
                    if cont_letras <= datetime.timedelta(seconds=0):
                        self.cuadro_texto.draw_text(texto[cont], Distancia)
                        Distancia += 12
                        self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)
                        pygame.display.flip()
                        cont += 1
                        cont_letras = tiempo_letras
                else:
                    texto = ""
                    cont = 0
            else:
                texto = ""
                cont = 0
                npc_talking.cant_in -= 1
                npc_talking.talking = False
                self.state = "Playing"
                self.playing = True
                talking = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    talking = False
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        if cont >= len(texto):
                            Distancia = 60
                            self.cuadro_texto.image.fill(GREEN)
                            self.cuadro_texto.draw_text(npc_talking.nombre, pos_x=40, pos_y=30)
                            npc_talking.cant_in += 1
                            npc_talking.update_conv()
                            texto = self.update_conversation(npc_talking.frase)
                            self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)

            pygame.display.flip()

    def wait_cinematic(self): #Funcion para esperar a que termine una cinematica para que se vuelva al estado normal
        wait = True

        while wait:
            self.clock.tick(FPS)
            self.current_camera.draws()
            self.manager_cinematic.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    wait = False
                    self.running = False
                    pygame.quit()
                    sys.exit()
            if not self.manager_cinematic.camera.in_cinematic:
                self.current_camera = self.camera
                wait = False
            pygame.display.flip()

    def wait(self):
        wait = True
        cont = 0

        while wait:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    wait = False
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    wait = False

    def convert_dict(self, dic):
        texto = ""
        if type(dic) == dic:
            items = dic.get("item")
            cantidades = dic.get("cantidad")
            cont = len(items)
            for item in items:
                res = ', '.join(dic)
                objects = tuple(res.split(', '))
                for cantidad in cantidades:
                    cantidad = str(cantidad)
                    texto += item.nombre + " " + cantidad + "x"
                if cont > 1:
                    texto += ", "
                cont -= 1
            return texto
        else:
            for obj in dic:
                cont = len(dic)
                texto += obj.nombre + " " + str(obj.cantidad) + "x"
                if cont > 1:
                    texto += ", "
                cont -= 1
            return texto


    def create_cinematic(self): #Funcion del clase juego para crear las cinematicas, aun en proceso
        '''
        for id, animal in enumerate(self.animals):
            cinematica_biologo = {"player": self.player, "target": search_npc("Roberto"), "id": id,
                                      "condition": str(("self.player.biologo and self.player.check_animals(?)", animal))}
            new_cinematica_biologo = (Cinematic(**cinematica_biologo))
            self.listas_cinematicas.append(new_cinematica_biologo)
        '''

        for id, animal in enumerate(self.animals):
            cinematica_biologo = {"player": self.player, "target": animal, "id": id,
                                  "condition": "self.player.check_animals(self.target) and self.player.biologo", "npcs":[search_npc("Fernan"), search_npc("Roberto"), search_npc("Fernan")]}
            new_cinematica_biologo = (Cinematic(**cinematica_biologo))
            self.listas_cinematicas.append(new_cinematica_biologo)

def search_npc(nombre):
    for npc in lista_npcs:
        if npc.nombre == nombre:
            return npc
