import pygame
from .Config import BLUE, FONT

class Widget(pygame.sprite.Sprite):
    def __init__(self, parent=None, *, rect, color, element=None, lista=None, select=None):
        pygame.sprite.Sprite.__init__(self)

        self.parent = parent
        self.element = element
        self.lista = lista
        self.select = select
        self.font = pygame.font.match_font(FONT)

        if (self.parent is not None):
            self.parent.children.add(self)

        self.image = pygame.surface.Surface(rect.size)
        self.rect = rect
        self.color = color

        self.children = pygame.sprite.OrderedUpdates()

    def _on_mouse_motion(self, event):
        event.x -= self.rect.left
        event.y -= self.rect.top

        for sprite in self.children:
            if isinstance(sprite, Widget):
                if (sprite.rect.collidepoint((event.x, event.y))):
                    sprite._on_mouse_motion(event)
                    break
        else:
            self.on_mouse_motion(event)

    def on_mouse_motion(self, event):
        pass

    def _on_click(self, event):
        event.x -= self.rect.left
        event.y -= self.rect.top
        for sprite in self.children:
            if isinstance(sprite, Widget):
                if sprite.rect.collidepoint(event.x, event.y):
                    sprite._on_click(event)
                    break

        else:
            self.on_click(event)

    def on_click(self, event):
        pass

    def repaint(self):

        self.image.fill(self.color)

        if self.select:
            self.image.fill(BLUE)
        else:
            self.image.fill(self.color)

        self.children.draw(self.image)

        if (self.parent is not None):
            self.parent.repaint()

    def update(self):
        self.children.update()
        self.select = False

    def display_text(self, surface, text, size, color, pos_x, pos_y):
        font = pygame.font.Font(self.font, size)

        text = font.render(text, True, color)
        rect = text.get_rect()
        rect.midtop = (pos_x, pos_y)

        surface.blit(text, rect)

