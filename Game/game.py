import os
import sys
import datetime
from .Player import Player
from .Recursos import *
from .npc import NPC
from .Constructor import Construtor, Biologo
from .Menu_Constructor import menu
from .Event import *
from .Cuadro_Texto import Text_Rect
from .Estructuras import Estructura
from .camaraY import Ycamara
from .menu_estructuras import menu_estructuras
from .Boton_independiente import Button_parent
from .Inventario import *
from .Tiles import Map

class game:
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))  # Crea la ventana
        pygame.display.set_caption(TITLE)  # Le da sombre de la ventana
        pygame.mouse.set_visible(True)

        self.running = True  # Permit saber si el program se esta cutaneous

        self.clock = pygame.time.Clock()

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

        self.npc = NPC(200, 300, interaccones=INTERACTUAR_NPC)

        self.fernan = Biologo(200, 50)

        self.roberto = Construtor(750, 100)

        self.arbol = Recurso(200, 70, 5, "Arbol", item=Item_acum("madera", 1), item_second=Item_acum("semilla", 2))

        self.roca = Recurso(200, 120, 5, "Roca", item=Item_acum("piedra", 3))

        self.sprites_inside = pygame.sprite.Group()

        self.sprites_inside_tall = Ycamara()

        self.Jugador = pygame.sprite.Group()

        self.Cursor = pygame.sprite.Group()

        self.npcs = pygame.sprite.Group()

        self.recursos = pygame.sprite.Group()

        self.estructuras = pygame.sprite.Group()

        self.items = pygame.sprite.Group()

        self.seeds = pygame.sprite.Group()

        self.doors = pygame.sprite.Group()

        self.map = Map(self.player, Estructura, self.roberto)

        self.map.add(self.player)
        self.map.add(self.fernan)
        self.Jugador.add(self.player)
        self.map.add(self.npc)
        self.map.add(self.roberto)
        self.map.add(self.arbol)
        self.map.add(self.roca)
        self.recursos.add(self.arbol)
        self.recursos.add(self.roca)
        self.npcs.add(self.npc)
        self.npcs.add(self.roberto)
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

    def update(self):
        if not self.playing:
            return

        self.update_day()

        self.map.update()

        self.fernan.follow(self.player)

        for tile in self.map.lista:
            self.player.validate_colision_tiles(tile)


        build = self.player.collide_with(self.map.estructuras)
        if build:
            for estructura in self.map.estructuras:
                event = Collision_event(self.player, estructura)
                estructura.collide_player(event)
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
            self.npc.validate_colision(recurso)

        for npc in self.npcs:
            for estructura in self.estructuras:
                npc.validate_colision(estructura)
            for recurso in self.recursos:
                npc.validate_colision(recurso)

        if self.map.cinematic != None:
            if self.map.cinematic.moved:
                self.state = "Talking"

        if self.state == "Talking":
            self.text_rect()
        elif self.state == "Playing":
            self.player.playing = True
            self.npc.playing = True
            self.roberto.playing = True
            self.fernan.playing = True
            self.map.update()
        elif self.state == "menu_npc":
            self.crear_menu_npc()
        elif self.state == "Building":
            self.menu_construccion()
        elif self.state == "Inventario":
            self.crear_inventario()
        elif self.state == "inside-build":
            self.player.playing = True
            self.inside_build()
        elif self.state == "menu_fernan":
            self.crear_menuBiologo()
        elif self.state == "ajusting":
            self.map.cinematic.ajust_camera()

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
                self.player.pos_y = self.build_enter.pos_y + 30
                self.cursor.pos_x = self.player.pos_x
                self.cursor.pos_y = self.player.pos_y
                self.build_enter = None
                inside = False
                self.state = "Playing"
                self.stop_draw()

            pygame.display.flip()

    def crear_menu_npc(self):
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

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for npc in self.npcs:
                            npc.talking = False
                        pause = False
                        self.back_game()
                        self.stop_characters()
                        self.state = "Playing"

            pygame.display.flip()

    def crear_menuBiologo(self):
        alto = 30

        if self.fernan.following:
            for interaccion in self.fernan.inter_follow:
                alto += 22
            self.menu_biologo = menu(self.fernan.rect.x + 10, self.fernan.rect.y - 60, self.fernan.inter_follow, height=alto)
        elif self.fernan.wait:
            for interaccion in self.fernan.inter_wait:
                alto += 22
            self.menu_biologo = menu(self.fernan.rect.x + 10, self.fernan.rect.y - 60, self.fernan.inter_wait, height=alto)

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

            pygame.display.flip()

    def crear_inventario(self):  #Función para mostrar el inventario en el juego
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
                    self.player.use_tool(self.seeds, self.recursos, self.items)
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

    def menu_construccion(self):
        self.cuadro_estructuras = Text_Rect(width=300, height=200, left=400, bottom=20)
        self.cuadro_texto = Text_Rect()
        self.menu_estructuras = menu_estructuras(left=100, bottom=20, height=200, interaccion=ESTRUCTURAS)
        self.buttom_salir = Button_parent(rect=pygame.rect.Rect(90, 200, 70, 40), color=PINK, element="Salir")
        self.buttom_build = Button_parent(rect=pygame.rect.Rect(250, 200, 70, 40), color=BLUE_Light, element="Build")
        self.buttom_salir.repaint()
        self.buttom_build.repaint()

        self.stop_characters()

        distancia_letras = 60
        temp = None
        tiempo_letras = datetime.timedelta(seconds=Tiempo_dialogos)
        cont_letras = tiempo_letras
        cont = 0
        texto = ""

        Distancia = 10

        for button in self.menu_estructuras.lista:
            self.display_text(self.menu_estructuras.image, button.element, 10, WHITE, 123, Distancia)
            Distancia += 30


        self.display_text(self.cuadro_texto.image, "Quieres construir algo?", 18, WHITE, 150, 10)
        self.surface.blit(self.menu_estructuras.image, self.menu_estructuras.rect)
        self.surface.blit(self.cuadro_estructuras.image, self.cuadro_estructuras.rect)
        self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)
        self.surface.blit(self.buttom_salir.image, self.buttom_salir.rect)
        self.surface.blit(self.buttom_build.image, self.buttom_build.rect)

        building = True

        '''
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
                    for estructura in ESTRUCTURAS:
                        if self.menu_estructuras.element == estructura:
                            self.cuadro_estructuras.image.fill(GREEN)
                            pos = ESTRUCTURAS.index(estructura)
                            texto = UTILIDAD[pos]
                            temp = self.menu_estructuras.element
                            distancia_materiales = self.menu_estructuras.lista[pos].rect.top
                            self.display_text(self.cuadro_estructuras.image, MATERIALES_ESTRUCTURAS[pos] + " x" + str(CANTIDAD_MATERIALES[pos]), 14, WHITE, 50, distancia_materiales)
                            self.surface.blit(self.cuadro_estructuras.image, self.cuadro_estructuras.rect)

                    if self.buttom_salir.rect.collidepoint(pygame.mouse.get_pos()):
                        self.player.vel_x = 0
                        self.player.vel_y = 0
                        self.back_game()
                        self.stop_characters()
                        self.state = "Playing"
                        building = False

                    elif self.buttom_build.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.menu_estructuras.element != None:
                            for est in lista:
                                if self.menu_estructuras.element == est.nombre:
                                    for slot in self.player.inventario.inventory_slots:
                                        if slot.item != None:
                                            if slot.item.nombre == est.materials:
                                                if slot.cant >= est.cantidadM:
                                                    nueva_estructura = est
                                                    self.sprites.add(nueva_estructura)
                                                    self.estructuras.add(nueva_estructura)
                                                    slot.cant -= est.cantidadM
                                                    self.back_game()
                                                    self.stop_characters()
                                                    self.menu_estructuras.element = None
                                                    self.state = "Playing"
                                                    building = False


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
        '''

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

    '''
    def text_rect_cinematic(self):
        self.cuadro_texto = Text_Rect()
        Distancia = 60
        tiempo_letras = datetime.timedelta(seconds=Tiempo_dialogos)
        cont_letras = tiempo_letras
        texto = self.update_conversation(self.map.cinematic.text)
        cont = 0
        self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)
        talking = True
        while talking:
            self.clock.tick(FPS)
            self.map.cinematic.update_conversation()
            if cont < len(texto):
                cont_letras -= datetime.timedelta(milliseconds=500)
                if cont_letras <= datetime.timedelta(seconds=0):
                    self.cuadro_texto.draw_text(texto[cont], Distancia)
                    Distancia += 12
                    self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)
                    pygame.display.flip()
                    cont += 1
                    cont_letras = tiempo_letras

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
                            texto = self.update_conversation(self.map.cinematic.text)
                            self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)

                        self.playing = True
                        self.state = "Playing"
                        texto = ""
                        cont = 0
                        talking = False
                        self.map.cinematic.finish = True

            pygame.display.flip()
            
    '''

    def text_rect(self):
        talking = False
        npc_talking = None
        self.cuadro_texto = Text_Rect()
        Distancia = 60
        tiempo_letras = datetime.timedelta(seconds=Tiempo_dialogos)
        cont_letras = tiempo_letras
        for npc in self.npcs:
            if npc.talking:
                npc_talking = npc
                npc_talking.update_conv()

        if npc_talking != None:
            if npc_talking.in_cinematic:
                texto = self.update_conversation(npc_talking.frase_cinematic)
            else:
                texto = self.update_conversation(npc_talking.frase)
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
                self.state = "Playing"
                self.playing = True
                talking = False
                if not npc_talking.in_cinematic:
                    npc_talking.cant_in -= 1
                    npc_talking.talking = False
                else:
                    self.map.cinematic.end_dialogue = True
                    self.wait_cinematic()
                    npc_talking.talking = False
                    npc_talking.in_cinematic = False

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
                            if not npc_talking.in_cinematic:
                                npc_talking.cant_in += 1
                                npc_talking.update_conv()
                                texto = self.update_conversation(npc_talking.frase)
                            else:
                                npc_talking.cant_in_cinematic += 1
                                npc_talking.update_conv()
                                texto = self.update_conversation(npc_talking.frase_cinematic)
                            self.surface.blit(self.cuadro_texto.image, self.cuadro_texto.rect)

            pygame.display.flip()

    def wait_cinematic(self):
        wait = True
        cont = 0

        while wait:
            self.clock.tick(FPS)
            self.map.custom_draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    wait = False
                    self.running = False
                    pygame.quit()
                    sys.exit()
            if self.map.cinematic.finish:
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

