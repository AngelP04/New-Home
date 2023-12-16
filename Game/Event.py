import pygame.sprite


class Event:
    def __init__(self, event):
        self.pygame_event = event
        self.x = event.pos[0]
        self.y = event.pos[1]


    """def get_collision_position(self, player_rect, build_rect):
        if not player_rect.colliderect(build_rect):
            return None
        else:
            self.x = max(player_rect.left, build_rect.left)
            self.y = max(player_rect.top, build_rect.top)
    """

class Collision_event:
    def __init__(self, player, recurso):
        self.player = player
        self.recurso = recurso
        self.x, self.y = self.create_colision()

    def create_colision(self):
        result = pygame.sprite.collide_mask(self.player, self.recurso)
        if not result:
            return [0, 0]
        if result:
            return result
