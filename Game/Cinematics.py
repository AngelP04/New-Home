import pygame

class Cinematic:
    def __init__(self, player, target, map, id):
        self.id = id
        self.player = player
        self.target = target
        self.map = map
        self.begin = False
        self.finish = False
        self.moved = False
        self.end_dialogue = False
        self.temp_x = self.map.half_width - self.player.rect.centerx
        self.cont = 0

    def ajust_camera(self):
        temp = 0
        dx = abs(self.player.rect.left - self.target.rect.left)

        if not self.finish:
            if dx < 200 and not self.end_dialogue:
                self.target.in_cinematic = True
                self.get_offset()
                self.begin = True

            if self.begin:
                self.player.can_move = False
                #time = pygame.time.get_ticks() // 1000
                if self.target.pos_x > self.player.pos_x and not self.end_dialogue:
                    if self.map.camera_rect.left > 550 - self.target.rect.right:
                        temp = pygame.time.get_ticks() // 500
                        self.map.camera_rect.x -= temp
                        if self.map.camera_rect.x <= self.temp_x - 5:
                            self.map.offset.x = self.map.camera_rect.left - self.map.camera_borders["left"]
                        else:
                            self.map.camera_rect.x -= temp + 50
                    elif self.map.camera_rect.left <= 550 - self.target.rect.right:
                        self.map.offset.x = self.map.camera_rect.left - self.map.camera_borders["left"]
                        self.target.talking = True
                        self.moved = True

            if self.end_dialogue:
                if self.map.camera_rect.x != self.temp_x:
                    temp = pygame.time.get_ticks() // 1000
                    self.map.camera_rect.x += temp
                    self.map.offset.x = self.map.camera_rect.left - self.map.camera_borders["left"]
                if self.map.offset.x >= self.temp_x + 5:
                    self.map.offset.x = self.temp_x
                    self.begin = False
                    self.player.can_move = True
                    self.finish = True

                '''
                else:
                    if self.map.offset.x != self.temp_x:
                        temp += 3
                        self.map.camera_rect.x += temp
                        self.map.offset.x = self.map.camera_rect.left - self.map.camera_borders["left"]
                    if self.map.offset.x >= self.temp_x:
                        temp = 0
                        self.map.offset.x = self.temp_x
                        self.begin = False
                        self.finish = True
                        self.player.can_move = True
                '''
                '''
                if time < 5:
                    temp -= 3
                    self.map.camera_rect.left += temp
                    self.map.offset.x = self.map.camera_rect.left - self.map.camera_borders["left"]
                    if self.map.camera_rect.left <= self.target.rect.left - 450:
                        print(True)
                    else:
                        print(False)

                else:
                    self.moved = True
                    self.map.offset.x = self.map.camera_rect.left - self.map.camera_borders["left"]
                    if time > 6:
                        if self.map.offset.x != self.temp_x:
                            temp += 3
                            self.map.camera_rect.x += temp
                            self.map.offset.x = self.map.camera_rect.left - self.map.camera_borders["left"]
                        if self.map.offset.x >= self.temp_x:
                            temp = 0
                            self.map.offset.x = self.temp_x
                            self.begin = False
                            self.finish = True
                            self.player.can_move = True
                '''

    def get_offset(self):
        self.temp_x = self.map.half_width - self.player.rect.centerx

    def finish_cinematic(self):
        self.finish = True