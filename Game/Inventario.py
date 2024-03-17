from .Cuadro_Texto import TextRectInv
from .Boton_independiente import Button_parent
from .Objetos import *
from .load_bar import Load_Bar

class Inventario:
    def __init__(self, player, totalslots, cols, rows, craft_disp=True, color=WHITE, separacion=5):
        self.player = player
        self.totalSlots = totalslots
        self.cols = cols
        self.rows = rows
        self.craft_disp = craft_disp
        self.objetos = [Tool("Pico", 10, materiales=[Craft_Item(MADERA, 5)]), Tool("Azada", 8, materiales=[Craft_Item(PIEDRA, 5), Craft_Item(MADERA, 10)])]
        if self.craft_disp:
            self.buttom_craft = Button_parent(rect=pygame.Rect(200, UIHEIGTH, 50, 40), color=RED, element="craftear")
        self.inventory_slots = []
        self.cofre = False
        self.appendSlots(separacion=separacion)
        self.color = color

        self.movingitem = None
        self.movingitemslot = None
        self.display = False
        self.moving = False
        self.select = False

    def appendSlots(self, uiheight=UIHEIGTH, uiwidth=WIDTH, separacion=5):
        while len(self.inventory_slots) != self.totalSlots:
            for y in range(uiheight, uiheight + INVTILESIZE * self.rows, INVTILESIZE + separacion):
                for x in range(uiwidth // 2 - ((INVTILESIZE + 2) * self.cols) // 2, uiwidth // 2 + ((INVTILESIZE + 2) * self.cols) // 2, INVTILESIZE + 2):
                    self.inventory_slots.append(InventorySlot(x, y))

    def add_slots(self):
        self.totalSlots += 5
        max_distance = 0
        if len(self.inventory_slots) != self.totalSlots:
            for slot in self.inventory_slots:
                slot.y -= INVTILESIZE // 2
                if slot.y > max_distance:
                    max_distance = slot.y
            for x in range(WIDTH // 2 - ((INVTILESIZE + 5) * self.cols) // 2, WIDTH // 2 + ((INVTILESIZE + 5) * self.cols) // 2, INVTILESIZE + 5):
                    self.inventory_slots.append(InventorySlot(x, max_distance + INVTILESIZE))

    def move(self, dir="right"):
        for slot in self.inventory_slots:
            if dir == "right":
                slot.x += INVTILESIZE * 3
            else:
                slot.x -= INVTILESIZE * 3

    def display_inventory(self, cofre=False):
        if cofre:
            self.cofre = True
        if not cofre:
            self.cofre = False
            for slot in self.inventory_slots:
                slot.return_pos()
            if self.craft_disp:
                self.buttom_craft.repaint()
        self.display = not self.display

    def draw(self, surface):
        if self.display:
            if self.craft_disp and not self.cofre:
                surface.blit(self.buttom_craft.image, self.buttom_craft.rect)
            for slot in self.inventory_slots:
                slot.draw(surface, self.color)
                slot.drawItems(surface)

            for slot in self.inventory_slots:
                slot.text_rect.draw(surface)

    def addItemInv(self, item, slot=None, add=False):

        if slot == None:
            for slots in self.inventory_slots:
                if slots.item == None:
                    slots.item = item
                    slots.cant += 1
                    slots.update()
                    break
                else:
                    if slots.item.id == item.id:
                        if slots.item.is_acum and slots.cant < slots.item.max_acum:
                            slots.cant += 1
                            break
                        elif slots.item.is_acum and slots.cant > slots.item.max_acum:
                            break
                        elif not slots.item.is_acum:
                            continue


        if slot != None:
            if not add:
                if slot.item != None:
                    self.movingitemslot.item = slot.item
                    slot.item = item
                else:
                    slot.item = item
            else:
                slot.item = item

    def removeItemInv(self, item, cantidad=None):
        if item != None:
            if item.is_acum:
                if cantidad:
                    for slot in self.inventory_slots:
                        if slot.item != None:
                            if slot.item.nombre == item.nombre:
                                slot.cant -= cantidad
                                if slot.cant == 0:
                                    slot.item = None
                                break
                else:
                    for slot in self.inventory_slots:
                        if slot.item != None:
                            if slot.item == item:
                                slot.cant = 0
                                slot.item = None
                                break
            else:
                for slot in self.inventory_slots:
                    if slot.item == item:
                        slot.item = None
                        break

    def update_crafting(self):
        self.player.objetos_crafteables.clear()
        for object in self.objetos:
            objetos_disponible = []
            for item in object.materiales:
                for slot in self.inventory_slots:
                    if slot.item != None:
                        if slot.item.id == item.id:
                            if slot.cant >= item.cantidad:
                                objetos_disponible.append(slot.item.nombre)

            lista_materiales = [material.nombre for material in object.materiales]

            if lista_materiales == objetos_disponible:
                self.player.objetos_crafteables.append(object)
            else:
                if object in self.player.objetos_crafteables:
                    self.player.objetos_crafteables.remove(object)

    def check_items(self, item):
        for slot in self.inventory_slots:
            if slot.item != None:
                if slot.item.id == item.id:
                    if slot.cant >= item.cantidad:
                        return True
        return False

    def swap_items(self, slot):
        res = None
        if self.movingitem != None:
            if slot.item != None:
                res = self.movingitem
                self.movingitem = slot.item
                slot.item = res
                res.is_moving = True

    def check_select(self, screen):
        mouse = pygame.mouse.get_pos()
        for slot in self.inventory_slots:
            if slot.draw(screen).collidepoint(mouse):
                self.select = True

    def moveItem(self, screen):
        mouse = pygame.mouse.get_pos()
        for slot in self.inventory_slots:
            if slot.draw(screen).collidepoint(mouse):
                if slot.item != None:
                    self.movingitem = slot.item
                    self.movingitem.is_moving = True
                    self.movingitemslot = slot
                    self.slot_cant = slot.cant
                    self.movingitemslot.cant = 0
                    self.moving = True
                    break

    def check(self, screen):
        mouse = pygame.mouse.get_pos()

        for slots in self.inventory_slots:
            if slots.item != None:
                if (slots.draw(screen).collidepoint(mouse) and not slots.text_rect.display) or (not slots.draw(screen).collidepoint(mouse) and slots.text_rect.display):
                    return slots

    def show_info(self, screen):
        if self.check(screen) != None:
            self.check(screen).text_rect.add_text(self.check(screen).item.desc)
            self.check(screen).text_rect.show_info()

    def placeItem(self, screen, grupo, inventario=None):
        mouse = pygame.mouse.get_pos()
        enter = True
        cant = 0

        if inventario != None:
            for slot in inventario.inventory_slots:
                if self.movingitem != None and slot.draw(screen).collidepoint(mouse):
                    if slot.enable:
                        self.removeItemInv(self.movingitem)
                        inventario.addItemInv(self.movingitem, slot)
                        if self.movingitem.is_acum:
                            slot.cant = self.slot_cant
                        break

        for slots in self.inventory_slots:
            if inventario != None:
                if (inventario.movingitem != None) and slots.draw(screen).collidepoint(mouse):
                    if slots.enable:
                        enter = True
                        self.addItemInv(inventario.movingitem, slots)
                        inventario.removeItemInv(inventario.movingitem)
                        if inventario.movingitem.is_acum:
                            slots.cant = inventario.slot_cant
                        break
            if slots.draw(screen).collidepoint(mouse) and self.movingitem != None:
                if slots.enable:
                    enter = True
                    self.removeItemInv(self.movingitem)
                    self.addItemInv(self.movingitem, slots)
                    if self.movingitem.is_acum:
                        slots.cant = self.slot_cant
                    break
            elif not slots.draw(screen).collidepoint(mouse):
                enter = False
                if self.movingitem != None:
                    if self.movingitem.is_acum:
                        cant = self.slot_cant
                continue

        if not enter:
            if inventario == None:
                if self.movingitem != None:
                    self.removeItemInv(self.movingitem)
                    self.player.drop(self.movingitem, grupo, cant)

        if self.movingitem != None:
            self.moving = False
            self.movingitem.is_moving = False
            self.movingitem = None
            self.movingitemslot = None

        if inventario != None:
            if inventario.movingitem != None:
                inventario.moving = False
                inventario.movingitem.is_moving = False
                inventario.movingitem = None
                inventario.movingitemslot = None

    def update(self):
        if self.load_bar != None:
            self.load_bar.update()


class InventorySlot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.real_x = x
        self.real_y = y
        self.item = None
        self.value = 0
        self.font = pygame.font.match_font(FONT)
        self.cant = 0
        self.text_rect = TextRectInv(self)
        self.enable = True

    def return_pos(self):
        if self.x != self.real_x:
            self.x = self.real_x

    def display_text(self, surface, text, size, color, pos_x, pos_y):
        font = pygame.font.Font(self.font, size)

        text = font.render(text, True, color)
        rect = text.get_rect()
        rect.midtop = (pos_x, pos_y)

        surface.blit(text, rect)

    def draw(self, screen, color=WHITE):
        return pygame.draw.rect(screen, color, (self.x, self.y, 40, 40))

    def drawItems(self, screen):
        if self.item != None and not self.item.is_moving:
            self.image = self.item.image
            screen.blit(self.image, (self.x + 5, self.y + 5))
            if self.item.is_acum:
                self.display_text(screen, str(self.cant), 14, BLUE_Light, self.x + 30, self.y + 25)
        if self.item != None and self.item.is_moving:
            mousepos1 = pygame.mouse.get_pos()
            self.image = pygame.Surface((40, 40))
            self.image.fill(DARK_GREEN)
            screen.blit(self.image, (mousepos1[0] - 20, mousepos1[1] - 20))

    def update(self):
        self.text_rect.update()


class barSlot(InventorySlot):
    def __init__(self, x, y):
        super(barSlot, self).__init__(x, y)
        self.select = False

    def update(self, screen):
        if self.select:
            return pygame.draw.rect(screen, BLUE, (self.x, self.y, 10, 10))
        else:
            return

class Toolbar:
    def __init__(self, player, totalslots, cols, rows):
        self.player = player
        self.totalslots = totalslots
        self.cols = cols
        self.rows = rows
        self.bar_slots = []
        self.appendSlots()
        self.bar_slots[0].select = True

    def appendSlots(self):
        while len(self.bar_slots) != self.totalslots:
            for y in range(TBHEIGHT, TBHEIGHT + INVTILESIZE * self.rows, INVTILESIZE + 2):
                for x in range(WIDTH // 2 - ((INVTILESIZE + 2) * self.cols) // 2,
                               WIDTH // 2 + ((INVTILESIZE + 2) * self.cols) // 2, INVTILESIZE + 2):
                    self.bar_slots.append(barSlot(x, y))

    def draw(self, surface):
        for slot in self.bar_slots:
            slot.draw(surface)
            slot.drawItems(surface)

class Cofre(Object):
    def __init__(self):
        Object.__init__(self, nombre="Cofre")
        self.inventario = Inventario(self, 20, 5, 4, craft_disp=False, color=RED)
        self.inventario.addItemInv(Tool("Azada", 9, materiales=[Craft_Item(PIEDRA, 5), Craft_Item(MADERA, 10)]))
        self.screen = pygame.display.get_surface()

    def on_click(self):
        return "Cofre"

class Horno(Object):
    def __init__(self):
        Object.__init__(self, nombre="Horno", load_bar=Load_Bar())
        self.inventario = Inventario(self, 2, 1, 2, craft_disp=False, color=BLUE_Light, separacion=45)
        self.screen = pygame.display.get_surface()

    def on_click(self):
        return "Cofre"

    def update(self):
        if self.inventario.inventory_slots[0].item != None and self.inventario.inventory_slots[1].item == None:
            if self.inventario.inventory_slots[0].item.process != None:
                self.load_bar.get_progression(self.inventario.inventory_slots[0].item.progression)
                self.load_bar.begin = True

        if self.load_bar.begin:
            if self.inventario.inventory_slots[0].item.is_acum:
                if self.inventario.inventory_slots[0].cant == 0:
                    self.inventario.inventory_slots[0].item = None
                    self.load_bar.new()
                    return

        if self.load_bar.finish:
            if self.inventario.inventory_slots[0].item != None:
                if self.inventario.inventory_slots[0].item.is_acum:
                    self.inventario.inventory_slots[0].cant -= 1
                    self.inventario.addItemInv(self.inventario.inventory_slots[0].item.process)
                    self.load_bar.new()
                    self.load_bar.begin = True
                    
                else:
                    self.inventario.addItemInv(self.inventario.inventory_slots[0].item.process)
                    self.inventario.removeItemInv(self.inventario.inventory_slots[0].item)
                    self.load_bar.new()

        self.load_bar.update()

