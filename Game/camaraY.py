import pygame

class Ycamara(pygame.sprite.Group):
    def __init__(self):
        pygame.sprite.Group.__init__(self)
        self.screen = pygame.display.get_surface()
        self.half_width = self.screen.get_size()[0] // 2
        self.half_height = self.screen.get_size()[1] // 2
        self.offset = pygame.math.Vector2()
        self.lista = []
        self.camera_borders = {"left": 75, "right": 75, "top": 50, "bottom": 50}
        l = self.camera_borders["left"]
        t = self.camera_borders["top"]
        w = self.screen.get_size()[0] - (self.camera_borders["left"] + self.camera_borders["right"])
        h = self.screen.get_size()[1] - (self.camera_borders["top"] + self.camera_borders["bottom"])
        self.camera_rect = pygame.Rect(l, t, w, h)


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


