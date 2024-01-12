import os
import sys
import datetime
from .Player import Player
from .Recursos import *
from .npc import NPC, Construtor, Biologo
from .Menu_Constructor import menu
from .Event import *
from .Cuadro_Texto import Text_Rect
from .camaraY import Ycamara
from .menu_estructuras import menu_estructuras
from .Boton_independiente import Button_parent
from .Inventario import *
from .map import Map
from .Cinematics import Cinematic
from .Animales import Animal

npc_basico = {"left": 200, "bottom": 300, "nombre": "Fernan", "guion": DIALOGOS_NPC, "interactuar": INTERACTUAR_NPC, "dialogos_cinematicas": DIALOGOS_BIOLOGO_CINEMATICA}
npc_constructor = {"left": 750, "bottom": 100, "nombre":"Roberto", "guion": DIALOGOS_ROBERTO, "interactuar": INTEREACTUAR_CONSTRUCTOR, "dialogos_cinematicas": DIALOGOS_BIOLOGO_CINEMATICA}
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

        for recurso in self.recursos:
            self.map.add(recurso)

    def generate_elements(self):

        self.player = Player(100, 300)

        self.animal = Animal(-100, 100, "Señor de la montaña")

        self.animals = pygame.sprite.Group()

        self.animals.add(self.animal)

        self.npcs = pygame.sprite.Group()

        self.fernan = Biologo(200, 50)

        self.arbol = Recurso(200, 70, 5, "Arbol", item=Item_acum("madera", 1), item_second=Item_acum("semilla", 2))

        self.roca = Recurso(200, 120, 5, "Roca", item=Item_acum("piedra", 3))

        self.sprites_inside = pygame.sprite.Group()

        self.sprites_inside_tall = Ycamara()

        self.Jugador = pygame.sprite.Group()

        self.Cursor = pygame.sprite.Group()

        self.recursos = pygame.sprite.Group()

        self.estructuras = pygame.sprite.Group()

        self.items = pygame.sprite.Group()

        self.seeds = pygame.sprite.Group()

        self.doors = pygame.sprite.Group()

        self.create_cinematic()

        self.map = Map(self.player, self.listas_cinematicas)

        for estructura in self.map.estructuras:
            self.estructuras.add(estructura)

        for npc in lista_npcs:
            self.npcs.add(npc)
            self.map.add(npc)

        self.map.add(self.player)
        self.map.add(self.fernan)
        self.map.add(self.animal)
        self.Jugador.add(self.player)
        self.map.add(self.arbol)
        self.map.add(self.roca)
        self.recursos.add(self.arbol)
        self.recursos.add(self.roca)
        self.npcs.add(self.fernan)
        self.cursor = self.map.mouse

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
        if isinstance(self.map.cinematica_now.target, Animal):
            return True

    def update(self):
        if not self.playing:
            return

        self.update_day()

        for animal in self.player.animals_knows:
            if animal not in self.fernan.animals:
                self.fernan.animals.append(animal)

        for cinematica in self.map.cinematicas:
            if cinematica.moved:
                self.state = "Cinematic"

        self.map.update()

        self.fernan.follow(self.player)

        for tile in self.map.lista:
            self.player.validate_colision_tiles(tile)


        build = self.player.collide_with(self.map.estructuras)
        if build:
            for estructura in self.map.estructuras:
                event = Collision_event(self.player, estructura)
                estructura.collide_player(event)
                if pygame.sprite.collide_mask(self.player, estructura.door):
                    estructura.enter = True
                if estructura.collide_player(event):
                    self.player.validate_colision_estructura(estructura)

        for estructura in self.estructuras:
            if estructura.enter:
                if estructura.size == "small":
                    self.sprites_inside.add(self.player)
                    self.sprites_inside.add(self.cursor)
                else:
                    self.sprites_inside_tall.add(self.player)
                    self.sprites_inside_tall.add(self.cursor)
                self.build_enter = estructura
                self.state = "inside-build"
                break

        for seed in self.seeds:
            self.map.add(seed)

        for slot in self.player.toolbar.bar_slots:
            slot.update(self.surface)

        for item in self.items:
            if self.player.verify_inventory(item):
                self.player.collide_items(self.items)

        for recurso in self.recursos:
            self.player.validate_colision(recurso)

        for npc in self.npcs:
            for estructura in self.estructuras:
                npc.validate_colision(estructura)
            for recurso in self.recursos:
                npc.validate_colision(recurso)

        if self.state == "Talking":
            self.text_rect()
        elif self.state == "Playing":
            self.player.playing = True
            self.fernan.playing = True
            self.map.update()
        elif self.state == "menu_npc":
            self.create_menu_npc()
        elif self.state == "Cinematic":
            self.text_rect_cinematic()
        elif self.state == "Building":
            self.menu_build()
        elif self.state == "Inventario":
            self.create_inventario()
        elif self.state == "inside-build":
            self.player.playing = True
            self.inside_build()
        elif self.state == "menu_fernan":
            self.create_menuBiologist()
        elif self.state == "ajusting":
            self.map.cinematic.ajust_camera()
        elif self.state == "Tienda":
            self.create_menu_tienda()

    def draw(self):
        if self.drawing:
            self.surface.fill(BLACK)
            self.map.custom_draw()
            for item in self.items:
                self.map.add(item)
            for recurso in self.recursos:
                self.map.add(recurso)
            self.player.toolbar.draw(self.surface)
            for slot in self.player.toolbar.bar_slots:
                slot.update(self.surface)
            self.player.inventario.draw(self.surface)
        else:
            self.surface.fill(BLACK)
            if self.build_enter.size == "small":
                self.build_enter.interior.draw(self.surface)
                self.sprites_inside.draw(self.surface)
            else:
                self.build_enter.interior.draws(self.player)
                self.sprites_inside_tall.draw(self.surface)
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
        self.build_enter.load_inside()
        self.stop_draw()
        inside = True

        while inside:
            self.clock.tick(FPS)
            self.draw()
            if self.build_enter.size == "small":
                self.cursor.can_move = False
                self.cursor.pos_x = pygame.mouse.get_pos()[0]
                self.cursor.pos_y = pygame.mouse.get_pos()[1]
                self.sprites_inside.update()
            else:
                self.sprites_inside_tall.update()
            self.events()

            for tile in self.build_enter.interior.sprites():
                self.player.validate_colision_tiles(tile)

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
                    self.sprites_inside_tall.remove(self.player)
                    self.sprites_inside_tall.remove(self.cursor)
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

        distancia_letras = 60
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
                        print(self.menu_animals.element)
                        distancia_letras = 60
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
                self.menu_npc = menu(npc.pos_x + self.map.offset.x + 15, npc.pos_y + self.map.offset.y - 90, npc.interacciones, height=alto)
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

    def create_menuBiologist(self):
        alto = 30

        if self.fernan.following:
            for interaccion in self.fernan.inter_follow:
                alto += 22
            self.menu_biologo = menu(self.fernan.pos_x + self.map.offset.x, self.fernan.pos_y + self.map.offset.y, self.fernan.inter_follow, height=alto)
        elif self.fernan.wait:
            for interaccion in self.fernan.inter_wait:
                alto += 22
            self.menu_biologo = menu(self.fernan.pos_x + self.map.offset.x, self.fernan.pos_y + self.map.offset.y, self.fernan.inter_wait, height=alto)

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
        mouse = pygame.mouse.get_pos()

        while inventary:
            self.draw()
            self.clock.tick(FPS)
            self.player.update_toolbar()
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

    def back_game(self):
        self.playing = True
        for sprite in self.map.sprites():
            sprite.playing = True

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()

            key = pygame.key.get_pressed()
            mouse = self.cursor.rect.center

            self.player.vel_x = 0
            self.player.vel_y = 0

            if key[pygame.K_w] & key[pygame.K_LCTRL]:
                self.player.run(-2)
            elif key[pygame.K_w]:
                self.player.move(-2)
            elif key[pygame.K_s] & key[pygame.K_LCTRL]:
                self.player.run(2)
            elif key[pygame.K_s]:
                self.player.move(2)
            elif key[pygame.K_a] & key[pygame.K_LCTRL]:
                self.player.run(-1)
            elif key[pygame.K_a]:
                self.player.move(-1)
            elif key[pygame.K_d] & key[pygame.K_LCTRL]:
                self.player.run(1)
            elif key[pygame.K_d]:
                self.player.move(1)

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
                elif pygame.mouse.get_pressed()[2]:
                    self.player.cultive(self.seeds, (self.npcs, self.recursos, self.estructuras), self.day)

            if event.type == pygame.MOUSEMOTION:
                if not self.cursor.initial:
                    self.cursor.initial = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.use_tool(self.seeds, self.recursos, self.map.lista, self.items)
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
        self.cuadro_texto = Text_Rect()
        self.menu_estructuras = menu_estructuras(left=100, bottom=20, height=200, interaccion=self.map.estructuras_disp)
        self.buttom_salir = Button_parent(rect=pygame.rect.Rect(90, 200, 70, 40), color=PINK, element="Salir")
        self.buttom_build = Button_parent(rect=pygame.rect.Rect(250, 200, 70, 40), color=BLUE_Light, element="Build")
        self.buttom_salir.repaint()
        self.buttom_build.repaint()

        self.stop_characters()

        distancia_letras = 60
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
                    self.menu_estructuras._on_click(Event(event))
                    if self.menu_estructuras.element != None and self.menu_estructuras.element != temp:
                        self.cuadro_texto.image.fill(GREEN)
                        distancia_letras = 60
                        cont = 0
                    for estructura in self.map.estructuras_disp:
                        if self.menu_estructuras.element != None:
                            if self.menu_estructuras.element.nombre == estructura.nombre:
                                self.cuadro_estructuras.image.fill(GREEN)
                                texto = estructura.desc
                                temp = self.menu_estructuras.element
                                self.display_text(self.cuadro_estructuras.image, self.convert_dict(estructura.materials), 18, WHITE, 100, 10)
                                self.surface.blit(self.cuadro_estructuras.image, self.cuadro_estructuras.rect)
                                self.surface.blit(estructura.icon, (self.cuadro_estructuras.rect.x + 30, self.cuadro_estructuras.rect.y + 40))

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
                                    for slot in self.player.inventario.inventory_slots:
                                        if slot.item != None:
                                            if slot.item.nombre == est.materials:
                                                if slot.cant >= est.cantidadM:
                                                    est.builded = True
                                                    found = True
                                                    self.back_game()
                                                    self.stop_characters()
                                                    self.menu_estructuras.element = None
                                                    self.state = "Playing"
                                                    building = False
                                                    break
                                                else:
                                                    self.cuadro_texto.image.fill(GREEN)
                                                    cont = 0
                                                    distancia_letras = 60
                                                    texto = "No tienes suficientes materiales"
                                    if not found:
                                        self.cuadro_texto.image.fill(GREEN)
                                        cont = 0
                                        distancia_letras = 60
                                        texto = "No tienes suficientes materiales"

            if self.menu_estructuras.element == temp:
                if cont < len(texto):
                    cont_letras -= datetime.timedelta(milliseconds=500)
                    if cont_letras <= datetime.timedelta(seconds=0):
                        self.cuadro_texto.draw_text(texto[cont], distancia_letras)
                        distancia_letras += 12
                        self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)
                        pygame.display.flip()
                        cont += 1
                        cont_letras = tiempo_letras
                else:
                    texto = ""
                    cont = 0
                    distancia_letras = 60




            pygame.display.flip()

    def stop_characters(self):
        for npc in self.npcs:
            npc.can_move = not npc.can_move

        self.player.can_move = not self.player.can_move

    def stop(self):
        self.playing = False
        for sprite in self.map.sprites():
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
        tiempo_letras = datetime.timedelta(seconds=Tiempo_dialogos)
        cont_letras = tiempo_letras
        for npc in self.npcs:
            if npc.talking and npc.in_cinematic:
                npc_talking = npc
                npc_talking.update_conv()

        if npc_talking != None:
            texto = self.update_conversation(npc_talking.frase_cinematic)
            cont = 0
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
                npc_talking.talking = False
                npc_talking.in_cinematic = False
                self.map.cinematica_now.end_dialogue = True
                self.wait_cinematic()
                if self.filter_animals():
                    self.player.animals_knows.append(self.map.cinematica_now.target.nombre)
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
                            npc_talking.cant_in += 1
                            npc_talking.update_conv()
                            texto = self.update_conversation(npc_talking.frase)
                            self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)

            pygame.display.flip()

    def wait_cinematic(self): #Funcion para esperar a que termine una cinematica para que se vuelva al estado normal
        wait = True

        while wait:
            self.clock.tick(FPS)
            self.map.custom_draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    wait = False
                    self.running = False
                    pygame.quit()
                    sys.exit()
            if self.map.cinematica_now.finish:
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
        res = ', '.join(dic)
        objects = tuple(res.split(', '))
        cont = len(objects)
        for obj in objects:
            texto += obj + " " + str(dic.get(obj)) + "x"
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
                                  "condition": "self.player.check_animals(self.target) and self.player.biologo", "npc":search_npc("Fernan")}
            new_cinematica_biologo = (Cinematic(**cinematica_biologo))
            self.listas_cinematicas.append(new_cinematica_biologo)

def search_npc(nombre):
    for npc in lista_npcs:
        if npc.nombre == nombre:
            return npc
