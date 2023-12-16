import pygame
from .Cuadro_Texto import TextRectInv
from .Config import *

class Inventario:
    def __init__(self, player, totalslots, cols, rows):
        self.player = player
        self.totalSlots = totalslots
        self.cols = cols
        self.rows = rows
        self.inventory_slots = []
        self.appendSlots()

        self.movingitem = None
        self.movingitemslot = None
        self.display = False
        self.moving = False

    def appendSlots(self):
        while len(self.inventory_slots) != self.totalSlots:
            for y in range(UIHEIGTH, UIHEIGTH + INVTILESIZE * self.rows, INVTILESIZE + 5):
                for x in range(WIDTH // 2 - ((INVTILESIZE + 5) * self.cols) // 2, WIDTH // 2 + ((INVTILESIZE + 5) * self.cols) // 2, INVTILESIZE + 5):
                    self.inventory_slots.append(InventorySlot(x, y))

    def display_inventory(self):
        self.display = not self.display

    def draw(self, surface):
        if self.display:
            for slot in self.inventory_slots:
                slot.draw(surface)
                slot.drawItems(surface)

            for slot in self.inventory_slots:
                slot.text_rect.draw(surface)

    def addItemInv(self, item, slot=None):

        if slot == None:
            for slots in self.inventory_slots:
                if slots.item == None:
                    slots.item = item
                    slots.cant += 1
                    slots.update()
                    break
                else:
                    if slots.item.id == item.id:
                        if slots.item.is_acum and slots.cant < item.max_acum:
                            slots.cant += 1
                            break
                        elif slots.cant > item.max_acum:
                            break


        if slot != None:
            if slot.item != None:
                self.swap_items(slot)
            else:
                slot.item = item
                slot.update()
                slot.cant = self.slot_cant
                self.moving = False

    def removeItemInv(self, item):
        for slot in self.inventory_slots:
            if slot.item == item:
                if slot.item.is_acum:
                    slot.cant = 0
                slot.item = None
                break

    def swap_items(self, slot):
        res = None
        if self.movingitem != None:
            if slot.item != None:
                res = self.movingitem
                self.movingitem = slot.item
                slot.item = res
                res.is_moving = True

    def moveItem(self, screen):
        mouse = pygame.mouse.get_pos()
        for slot in self.inventory_slots:
            if slot.draw(screen).collidepoint(mouse):
                if slot.item != None:
                    slot.item.is_moving = True
                    self.movingitem = slot.item
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

    def placeItem(self, screen, grupo):
        mouse = pygame.mouse.get_pos()
        enter = True
        cant = 0

        for slots in self.inventory_slots:
            if slots.draw(screen).collidepoint(mouse) and self.movingitem != None:
                enter = True
                self.removeItemInv(self.movingitem)
                self.addItemInv(self.movingitem, slots)
                break
            elif not slots.draw(screen).collidepoint(mouse):
                enter = False
                if self.movingitem.is_acum:
                    cant = self.slot_cant
                continue

        if not enter:
            self.removeItemInv(self.movingitem)
            self.player.drop(self.movingitem, grupo, cant)

        if self.movingitem != None:
            self.movingitem.is_moving = False
            self.movingitem = None
            self.movingitemslot = None


class InventorySlot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.item = None
        self.value = 0
        self.font = pygame.font.match_font(FONT)
        self.cant = 0
        self.text_rect = TextRectInv(self)

    def display_text(self, surface, text, size, color, pos_x, pos_y):
        font = pygame.font.Font(self.font, size)

        text = font.render(text, True, color)
        rect = text.get_rect()
        rect.midtop = (pos_x, pos_y)

        surface.blit(text, rect)

    def draw(self, screen):
        return pygame.draw.rect(screen, WHITE, (self.x, self.y, 40, 40))

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

class Item:
    def __init__(self, nombre, id, type, desc=DESC):
        self.nombre = nombre
        self.image = pygame.Surface((30, 30))
        self.image.fill(YELLOW)
        self.is_moving = False
        self.id = id
        self.type = type
        self.is_acum = False
        self.desc = desc
        self.rect = self.image.get_rect()

class Item_acum(Item):
    def __init__(self, nombre, id, max_acum=200, tool="hacha"):
        super(Item_acum, self).__init__(nombre, id, "material")
        self.max_acum = max_acum
        self.is_acum = True
        self.tool = tool

class Tool(Item):
    def __init__(self, nombre, id, stregth):
        super(Tool, self).__init__(nombre, id, "tool")
        self.streght = stregth
        self.is_acum = False

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
            for y in range(TBHEIGHT, TBHEIGHT + INVTILESIZE * self.rows, INVTILESIZE + 5):
                for x in range(WIDTH // 2 - ((INVTILESIZE + 5) * self.cols) // 2,
                               WIDTH // 2 + ((INVTILESIZE + 5) * self.cols) // 2, INVTILESIZE + 5):
                    self.bar_slots.append(barSlot(x, y))

    def draw(self, surface):
        for slot in self.bar_slots:
            slot.draw(surface)
            slot.drawItems(surface)



